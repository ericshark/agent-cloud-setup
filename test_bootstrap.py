"""Exercise the local installer with temporary homes and simulated accounts."""

import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent

with TemporaryDirectory(prefix="agent-setup-test-") as tmp:
    base = Path(tmp)
    runtime = base / "runtime"
    runtime.mkdir()
    commands = base / "bin"
    commands.mkdir()
    env = {**os.environ, "PATH": f"{commands}:{os.environ['PATH']}",
           "TEST_RUNTIME_HOME": str(runtime)}
    for name in ("CODEX_HOME", "AGENT_SETUP_HOME", "AGENT_SETUP_CODEX_HOME",
                 "AGENT_SETUP_USER", "TEST_AS_RUNTIME", "TEST_ROOT"):
        env.pop(name, None)

    def stub(name, body):
        path = commands / name
        path.write_text("#!/bin/bash\n" + body)
        path.chmod(0o755)

    stub("id", """
if [[ "$1" == -un ]]; then echo runtime
elif [[ "${TEST_ROOT:-}" == 1 && "${TEST_AS_RUNTIME:-}" != 1 ]]; then echo 0
else echo 1000
fi
""")
    stub("getent", """
[[ "$1" == passwd && ( -z "${2:-}" || "$2" == runtime ) ]] || exit 2
printf 'runtime:x:1000:1000::%s:/bin/bash\\n' "$TEST_RUNTIME_HOME"
""")
    stub("runuser", """
[[ "$1 $2 $3" == '-u runtime --' ]] || exit 2
shift 3
export TEST_AS_RUNTIME=1
exec "$@"
""")

    def run(script, expected=0, **overrides):
        result = subprocess.run(
            ["bash", str(ROOT / script)], env={**env, **overrides},
            text=True, capture_output=True,
        )
        assert result.returncode == expected, result.stdout + result.stderr

    unrelated = runtime / ".agents/skills/unrelated/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("preserve")
    codex = runtime / ".codex/AGENTS.md"
    codex.parent.mkdir()
    codex.write_text("old instructions")

    run("cloud-install.sh")
    installed = {codex: ROOT / "AGENTS.md",
                 runtime / ".claude/CLAUDE.md": ROOT / "CLAUDE.md"}
    skills = ROOT / ".agents/skills"
    for source in skills.rglob("*"):
        if source.is_file():
            for target in (".agents/skills", ".claude/skills"):
                installed[runtime / target / source.relative_to(skills)] = source
    for dest, source in installed.items():
        assert dest.read_bytes() == source.read_bytes(), dest
    assert unrelated.read_text() == "preserve"

    for path in installed:
        os.utime(path, ns=(1_000_000_000, 1_000_000_000))
    run("cloud-install.sh", TEST_ROOT="1")
    assert all(path.stat().st_mtime_ns == 1_000_000_000 for path in installed)

    codex.write_text("mismatch")
    run("verify.sh", expected=1, HOME=str(runtime))
    run("cloud-install.sh", TEST_ROOT="1", AGENT_SETUP_USER="runtime")
    assert codex.read_bytes() == (ROOT / "AGENTS.md").read_bytes()
    assert "Runtime user=runtime" in (
        runtime / ".agent-cloud-setup/install.log"
    ).read_text()

print("PASS: local installation, all bundled files, repeat install, verification failure, runtime detection and override")
