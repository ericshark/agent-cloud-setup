#!/usr/bin/env python3
"""
Production-Readiness Scanner
============================

A dependency-free (stdlib-only) static scanner that gives a fast, deterministic
first pass over a codebase across security, reliability, testing, data/compliance,
operations, and documentation dimensions.

It is intentionally conservative: it reports *signals* and *gaps*, not verdicts.
Treat every finding as a lead to confirm by reading the code, not as ground truth.
The accompanying reference checklists (references/*.md) carry the depth; this script
just tells you where to point them.

Usage:
    python3 scan.py [TARGET_DIR] [--json OUT.json] [--md OUT.md] [--quiet]

Defaults to the current directory. Exit code is 0 unless --strict is passed and
any HIGH-severity finding is present (useful as a CI gate).

Design notes:
- No network calls. No writes outside the chosen output files.
- External tools (npm audit, pip-audit, gitleaks, ...) are invoked ONLY if already
  installed and ONLY in read-only / report modes. Their absence is reported, never
  fatal.
- Secret detection uses high-signal regexes; expect false positives and triage them.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ----------------------------------------------------------------------------- #
# Configuration
# ----------------------------------------------------------------------------- #

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}

# Directories never worth scanning.
SKIP_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist",
    "build", "target", "out", ".next", ".nuxt", ".cache", "vendor", "coverage",
    ".idea", ".vscode", ".terraform", ".gradle", ".mvn", "Pods", ".tox",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "bin", "obj",
}

# File extensions that are source-ish and worth reading for patterns.
SOURCE_EXT = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".go", ".rb", ".php",
    ".java", ".kt", ".kts", ".cs", ".rs", ".scala", ".swift", ".c", ".cpp",
    ".h", ".hpp", ".sh", ".bash", ".sql", ".yml", ".yaml", ".toml", ".env",
    ".tf", ".html", ".vue", ".svelte",
}

MAX_FILE_BYTES = 2_000_000  # skip files larger than ~2MB (likely generated/data)

# High-signal secret patterns. Keep these specific to limit false positives.
SECRET_PATTERNS = [
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS secret access key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z\-_]{35}")),
    ("Slack token", re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}")),
    ("Stripe secret key", re.compile(r"sk_live_[0-9A-Za-z]{20,}")),
    ("GitHub token", re.compile(r"gh[pousr]_[0-9A-Za-z]{36,}")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("JWT (hardcoded)", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("Generic assigned secret", re.compile(
        r"(?i)(password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)"
        r"\s*[:=]\s*['\"][^'\"\s]{8,}['\"]")),
]

# Substrings that mark a likely-placeholder secret -> downgrade to avoid noise.
PLACEHOLDER_HINTS = (
    "example", "changeme", "your_", "xxxx", "placeholder", "dummy", "test",
    "sample", "<", "}}", "${", "process.env", "os.environ", "getenv", "redacted",
    "fake", "todo", "null", "none", "******",
)

# Dangerous-pattern heuristics: (label, regex, severity, advice)
# NOTE: The strings below (e.g. "eval(", "os.system(") are REGEX LITERALS used to
# DETECT these sinks in scanned code. This scanner never calls eval/exec/os.system
# itself; it only matches those tokens as text. (Static analysis hooks may flag the
# literals — that is a false positive on the detector's own ruleset.)
RISK_PATTERNS = [
    ("eval() on dynamic input", re.compile(r"\beval\s*\("), "MEDIUM",
     "Avoid eval/exec on untrusted input; use safe parsers."),
    ("Python exec()", re.compile(r"\bexec\s*\("), "MEDIUM",
     "Avoid exec on untrusted input."),
    ("shell=True subprocess", re.compile(r"subprocess\.[A-Za-z_]+\([^)]*shell\s*=\s*True"), "HIGH",
     "shell=True with interpolated input enables command injection; pass arg lists."),
    ("os.system()", re.compile(r"\bos\.system\s*\("), "MEDIUM",
     "os.system invokes a shell; prefer subprocess with an argument list."),
    ("SQL string concatenation", re.compile(
        r"(?i)(execute|query)\s*\(\s*[f]?['\"].*(select|insert|update|delete).*['\"]\s*[+%]"),
     "HIGH", "Use parameterized queries / prepared statements, never string building."),
    ("React dangerouslySetInnerHTML", re.compile(r"dangerouslySetInnerHTML"), "MEDIUM",
     "Sanitize HTML (e.g. DOMPurify) before injecting; otherwise XSS."),
    (".innerHTML assignment", re.compile(r"\.innerHTML\s*="), "LOW",
     "innerHTML with untrusted data is an XSS vector; prefer textContent / sanitize."),
    ("TLS verification disabled", re.compile(
        r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify\s*:\s*true|CURLOPT_SSL_VERIFY(PEER|HOST)\s*,\s*(0|false))"),
     "HIGH", "Never disable TLS certificate verification in production."),
    ("Weak hash (md5/sha1)", re.compile(r"(?i)\b(md5|sha1)\s*\("), "LOW",
     "MD5/SHA1 are unfit for passwords/signatures; use bcrypt/argon2/SHA-256+."),
    ("Permissive CORS (*)", re.compile(
        r"(?i)(Access-Control-Allow-Origin['\"]?\s*[:,]\s*['\"]?\*|cors\(\s*\)|origin\s*:\s*['\"]\*['\"])"),
     "MEDIUM", "Avoid wildcard CORS on authenticated endpoints; allowlist origins."),
    ("Bind to 0.0.0.0", re.compile(r"0\.0\.0\.0"), "INFO",
     "Confirm binding to all interfaces is intended and firewalled."),
    ("Debug mode enabled", re.compile(r"(?i)(DEBUG\s*=\s*True|app\.run\([^)]*debug\s*=\s*True)"), "MEDIUM",
     "Ensure DEBUG is off in production; it can leak stack traces/secrets."),
    ("TODO/FIXME/HACK marker", re.compile(r"\b(TODO|FIXME|HACK|XXX)\b"), "INFO",
     "Track and resolve outstanding markers before shipping critical paths."),
]

# Hygiene files we expect in a production-ready repo: (label, [candidate paths/globs], severity, dimension)
EXPECTED_FILES = [
    ("README", ["README.md", "README.rst", "README.txt", "readme.md"], "LOW", "Documentation"),
    ("License", ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"], "LOW", "Documentation"),
    (".gitignore", [".gitignore"], "MEDIUM", "Security"),
    ("Dependency lockfile", [
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
        "Pipfile.lock", "go.sum", "Cargo.lock", "Gemfile.lock", "composer.lock",
        "requirements.txt",
    ], "MEDIUM", "Security"),
    ("CI pipeline", [
        ".github/workflows", ".gitlab-ci.yml", "azure-pipelines.yml",
        "Jenkinsfile", ".circleci/config.yml", "bitbucket-pipelines.yml",
    ], "MEDIUM", "Testing"),
    ("Test directory/config", [
        "tests", "test", "__tests__", "spec", "pytest.ini", "jest.config.js",
        "jest.config.ts", "vitest.config.ts", "go.mod",
    ], "MEDIUM", "Testing"),
    ("Dependabot/renovate", [
        ".github/dependabot.yml", "renovate.json", ".renovaterc",
        ".github/renovate.json",
    ], "LOW", "Security"),
    ("Security policy", ["SECURITY.md", ".github/SECURITY.md"], "LOW", "Security"),
    ("Containerfile", ["Dockerfile", "Containerfile", "docker-compose.yml"], "INFO", "Operations"),
    ("Env example (not real .env)", [".env.example", ".env.sample", ".env.template"], "INFO", "Security"),
]


# ----------------------------------------------------------------------------- #
# Data model
# ----------------------------------------------------------------------------- #

@dataclass
class Finding:
    dimension: str
    severity: str
    title: str
    detail: str
    location: str = ""
    advice: str = ""


@dataclass
class Report:
    target: str
    stacks: list = field(default_factory=list)
    findings: list = field(default_factory=list)
    tool_runs: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- #
# Helpers
# ----------------------------------------------------------------------------- #

def iter_files(root: Path):
    """Yield candidate source files under root, skipping noise directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".cache")]
        for name in filenames:
            p = Path(dirpath) / name
            ext = p.suffix.lower()
            if ext in SOURCE_EXT or name in {"Dockerfile", "Containerfile", ".env"}:
                try:
                    if p.stat().st_size <= MAX_FILE_BYTES:
                        yield p
                except OSError:
                    continue


def exists_any(root: Path, candidates) -> str:
    for c in candidates:
        if (root / c).exists():
            return c
    return ""


def looks_placeholder(line: str) -> bool:
    low = line.lower()
    return any(h in low for h in PLACEHOLDER_HINTS)


# ----------------------------------------------------------------------------- #
# Detection passes
# ----------------------------------------------------------------------------- #

def detect_stacks(root: Path) -> list:
    markers = {
        "Node/JS": ["package.json"],
        "Python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
        "Go": ["go.mod"],
        "Rust": ["Cargo.toml"],
        "Ruby": ["Gemfile"],
        "PHP": ["composer.json"],
        "Java/Maven": ["pom.xml"],
        "Java/Gradle": ["build.gradle", "build.gradle.kts"],
        ".NET": ["*.csproj", "*.sln"],
        "Docker": ["Dockerfile", "docker-compose.yml"],
        "Kubernetes": ["k8s", "kustomization.yaml", "helm"],
        "Terraform": ["*.tf"],
    }
    found = []
    for stack, files in markers.items():
        for f in files:
            if "*" in f:
                if list(root.rglob(f))[:1]:
                    found.append(stack)
                    break
            elif (root / f).exists() or list(root.glob(f"**/{f}"))[:1]:
                found.append(stack)
                break
    return sorted(set(found))


def scan_patterns(root: Path, report: Report):
    secret_hits = 0
    risk_hits = 0
    files_scanned = 0
    for p in iter_files(root):
        files_scanned += 1
        rel = str(p.relative_to(root))
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            if len(line) > 1000:
                continue  # minified / data line
            # Secrets
            for label, rx in SECRET_PATTERNS:
                if rx.search(line):
                    sev = "LOW" if looks_placeholder(line) else "HIGH"
                    note = " (looks like a placeholder — confirm)" if sev == "LOW" else ""
                    report.findings.append(Finding(
                        "Security", sev, f"Possible {label}{note}",
                        "Hardcoded credential pattern matched in source.",
                        f"{rel}:{i}",
                        "Move secrets to a manager/env var; rotate if real; add to .gitignore."))
                    secret_hits += 1
                    break
            # Risky patterns
            for label, rx, sev, advice in RISK_PATTERNS:
                if rx.search(line):
                    # INFO markers are noisy; only count, don't spam one-per-line for TODO
                    if label.startswith("TODO") and risk_hits > 0 and (i % 1):
                        pass
                    report.findings.append(Finding(
                        _dimension_for(label), sev, label,
                        line.strip()[:160], f"{rel}:{i}", advice))
                    risk_hits += 1
                    break
    report.stats["files_scanned"] = files_scanned
    report.stats["secret_hits"] = secret_hits
    report.stats["risk_hits"] = risk_hits


def _dimension_for(label: str) -> str:
    l = label.lower()
    if any(k in l for k in ("sql", "xss", "cors", "tls", "hash", "shell", "eval",
                            "exec", "os.system", "innerhtml", "debug", "secret")):
        return "Security"
    if "todo" in l:
        return "Documentation"
    return "Security"


def check_expected_files(root: Path, report: Report):
    for label, candidates, sev, dim in EXPECTED_FILES:
        hit = exists_any(root, candidates)
        if hit:
            report.findings.append(Finding(
                dim, "INFO", f"Present: {label}", f"Found '{hit}'.", hit))
        else:
            report.findings.append(Finding(
                dim, sev, f"Missing: {label}",
                "No matching file found in repository root/known locations.",
                "", _advice_for_missing(label)))


def _advice_for_missing(label: str) -> str:
    advice = {
        "README": "Add a README covering setup, run, and deploy.",
        "License": "Add a LICENSE so usage terms are explicit.",
        ".gitignore": "Add .gitignore to keep secrets/build artifacts out of VCS.",
        "Dependency lockfile": "Commit a lockfile so builds are reproducible.",
        "CI pipeline": "Add CI to run tests, linters, and security scans on each PR.",
        "Test directory/config": "Add automated tests; gate merges on them.",
        "Dependabot/renovate": "Enable automated dependency-update PRs.",
        "Security policy": "Add SECURITY.md with a vulnerability-disclosure process.",
        "Env example (not real .env)": "Provide .env.example documenting required vars.",
    }
    return advice.get(label, "")


def check_committed_secrets_files(root: Path, report: Report):
    """A real .env tracked in git is a classic leak."""
    env = root / ".env"
    gitignore = root / ".gitignore"
    if env.exists():
        ignored = False
        if gitignore.exists():
            gi = gitignore.read_text(encoding="utf-8", errors="ignore")
            ignored = any(line.strip() in (".env", "*.env", ".env*") for line in gi.splitlines())
        if not ignored:
            report.findings.append(Finding(
                "Security", "HIGH", ".env present and not gitignored",
                "A .env file exists and does not appear to be ignored by git.",
                ".env",
                "Add .env to .gitignore, remove from history if committed, rotate secrets."))


def run_external_tools(root: Path, report: Report):
    """Invoke installed audit tools in read-only/report mode. Never fatal."""
    tools = [
        ("npm audit", ["npm", "audit", "--audit-level=high", "--json"],
         (root / "package.json").exists()),
        ("pip-audit", ["pip-audit", "-f", "json"],
         (root / "requirements.txt").exists() or (root / "pyproject.toml").exists()),
        ("govulncheck", ["govulncheck", "./..."], (root / "go.mod").exists()),
        ("cargo audit", ["cargo", "audit"], (root / "Cargo.toml").exists()),
        ("gitleaks", ["gitleaks", "detect", "--no-banner", "-s", str(root)], True),
        ("bundler-audit", ["bundle", "audit", "check"], (root / "Gemfile.lock").exists()),
    ]
    for name, cmd, applicable in tools:
        binary = cmd[0]
        if not applicable:
            continue
        if shutil.which(binary) is None:
            report.tool_runs.append({"tool": name, "status": "not-installed",
                                     "hint": f"Install '{binary}' for deeper scanning."})
            continue
        try:
            proc = subprocess.run(cmd, cwd=str(root), capture_output=True,
                                  text=True, timeout=180)
            status = "clean" if proc.returncode == 0 else "findings"
            summary = (proc.stdout or proc.stderr or "").strip()
            report.tool_runs.append({
                "tool": name, "status": status, "exit_code": proc.returncode,
                "output_excerpt": summary[:1500],
            })
            if proc.returncode != 0:
                report.findings.append(Finding(
                    "Security", "HIGH", f"{name} reported issues",
                    "External scanner exited non-zero — review its output.",
                    "", f"Run `{' '.join(cmd[:-1]) if cmd[-1]=='--json' else ' '.join(cmd)}` and triage."))
        except subprocess.TimeoutExpired:
            report.tool_runs.append({"tool": name, "status": "timeout"})
        except Exception as e:  # noqa: BLE001 - tool diversity, stay non-fatal
            report.tool_runs.append({"tool": name, "status": f"error: {e}"})


# ----------------------------------------------------------------------------- #
# Scoring + rendering
# ----------------------------------------------------------------------------- #

def score(report: Report) -> dict:
    weights = {"HIGH": 10, "MEDIUM": 4, "LOW": 1, "INFO": 0}
    penalty = sum(weights[f.severity] for f in report.findings)
    grade = max(0, 100 - penalty)
    counts = {s: 0 for s in SEVERITY_ORDER}
    for f in report.findings:
        counts[f.severity] += 1
    return {"score": grade, "counts": counts, "penalty": penalty}


def render_markdown(report: Report) -> str:
    s = score(report)
    report.stats["score"] = s["score"]
    report.stats["counts"] = s["counts"]
    lines = []
    lines.append("# Production-Readiness Scan Report\n")
    lines.append(f"- **Target:** `{report.target}`")
    lines.append(f"- **Stacks detected:** {', '.join(report.stacks) or 'unknown'}")
    lines.append(f"- **Heuristic score:** {s['score']}/100 "
                 f"(HIGH {s['counts']['HIGH']}, MEDIUM {s['counts']['MEDIUM']}, "
                 f"LOW {s['counts']['LOW']}, INFO {s['counts']['INFO']})")
    lines.append(f"- **Files scanned:** {report.stats.get('files_scanned', 0)}\n")
    lines.append("> This is a heuristic first pass. Confirm each finding by reading "
                 "the code; pair with the reference checklists for depth.\n")

    # External tools
    if report.tool_runs:
        lines.append("## External tool runs\n")
        for t in report.tool_runs:
            lines.append(f"- **{t['tool']}**: {t['status']}"
                         + (f" — {t.get('hint','')}" if t.get("hint") else ""))
        lines.append("")

    # Findings grouped by severity
    lines.append("## Findings\n")
    ordered = sorted(report.findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.dimension))
    current = None
    for f in ordered:
        if f.severity == "INFO":
            continue  # keep the main list actionable; INFO summarized below
        if f.severity != current:
            current = f.severity
            lines.append(f"\n### {current}\n")
        loc = f" — `{f.location}`" if f.location else ""
        lines.append(f"- **[{f.dimension}] {f.title}**{loc}")
        if f.detail:
            lines.append(f"  - {f.detail}")
        if f.advice:
            lines.append(f"  - _Fix:_ {f.advice}")

    infos = [f for f in ordered if f.severity == "INFO"]
    if infos:
        lines.append("\n### INFO (context)\n")
        for f in infos:
            loc = f" — `{f.location}`" if f.location else ""
            lines.append(f"- [{f.dimension}] {f.title}{loc}")

    lines.append("\n## Next steps\n")
    lines.append("1. Triage every HIGH finding first; confirm true/false positive by reading the cited line.")
    lines.append("2. Map remaining gaps to the reference checklists and open tracked issues.")
    lines.append("3. Re-run with external scanners installed for dependency CVE coverage.")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- #
# Main
# ----------------------------------------------------------------------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(description="Production-readiness static scanner.")
    ap.add_argument("target", nargs="?", default=".", help="Directory to scan (default: .)")
    ap.add_argument("--json", dest="json_out", help="Write JSON report to this path.")
    ap.add_argument("--md", dest="md_out", help="Write Markdown report to this path.")
    ap.add_argument("--no-tools", action="store_true", help="Skip external tool invocation.")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero if any HIGH finding.")
    ap.add_argument("--quiet", action="store_true", help="Suppress stdout report.")
    args = ap.parse_args(argv)

    root = Path(args.target).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    report = Report(target=str(root))
    report.stacks = detect_stacks(root)
    scan_patterns(root, report)
    check_expected_files(root, report)
    check_committed_secrets_files(root, report)
    if not args.no_tools:
        run_external_tools(root, report)

    md = render_markdown(report)

    if args.md_out:
        Path(args.md_out).write_text(md, encoding="utf-8")
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({**asdict(report), "summary": report.stats}, indent=2),
            encoding="utf-8")
    if not args.quiet:
        print(md)

    has_high = any(f.severity == "HIGH" for f in report.findings)
    if args.strict and has_high:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
