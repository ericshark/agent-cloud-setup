# Agent Cloud Setup

Shared Linux cloud instructions and 11 skills for Codex and Claude Code.
This is a normal repository, not a GitHub template.

## Use in Codex Cloud

Use the current **Install script** workflow, not legacy maintenance-script guidance.
Saving a command is not evidence it executed. During environment setup, ask Codex
to run the complete install script, show its output, and verify the files before
republishing. A fresh task must then verify persistence and agent discovery.

Paste this reusable block into the Install script after project dependency setup:

```bash
set -euo pipefail
setup_dir="$(mktemp -d)"
trap 'rm -rf -- "$setup_dir"' EXIT
git clone --depth 1 https://github.com/ericshark/agent-cloud-setup.git "$setup_dir"
# Allow the runtime user to traverse the temporary clone when setup runs as root.
chmod 755 "$setup_dir"
bash "$setup_dir/cloud-install.sh"
```

The wrapper explicitly targets the reported runtime account `agent`, using its
passwd home. It runs as that user (root uses runuser); other users fail clearly.
It does not infer the cloud identity from the setup user's HOME. Set
`AGENT_SETUP_USER` only if diagnostics establish a different runtime account.
Log: `/home/agent/.agent-cloud-setup/install.log` for the reported account.

## What is confirmed, and what is not

The original bootstrap reproducibly installs into the caller's HOME. Its old
existence checks therefore could succeed for the wrong user. No cloud install log
has established that this caused the reported failure. Skipped execution, snapshot
exclusions, stale publication, and platform issues remain possible.

Current official docs describe snapshots of prepared files, not automatic replay
of install/start commands on repository refresh. They do not specify the install
UID, guarantee preservation of each home path, or promise that a custom global
skill directory is registered by the cloud harness. A Start skill is documented
for starting services; it is NOT treated as a guaranteed pre-discovery installer.

- https://learn.chatgpt.com/docs/environments/cloud-environments
- https://learn.chatgpt.com/docs/agent-configuration/agents-md
- https://learn.chatgpt.com/docs/build-skills

Do not claim this fixes cloud discovery until a real new task passes the checks.
Local filesystem success proves file installation only.

## Fresh-task diagnostic procedure

Before any repair in a new task, run:

```bash
id
printf 'HOME=%s CODEX_HOME=%s\n' "$HOME" "${CODEX_HOME:-unset}"
getent passwd agent
for file in "$HOME/.codex/AGENTS.md" "${CODEX_HOME:-$HOME/.codex}/AGENTS.md" "$HOME/.claude/CLAUDE.md" "$HOME/.agent-cloud-setup/install.log"; do
  if test -r "$file"; then stat "$file"; else printf 'MISSING/UNREADABLE %s\n' "$file"; fi
done
find "$HOME/.agents/skills" "$HOME/.claude/skills" -name SKILL.md -print 2>/dev/null || true
```

Fetch this repo to a temporary directory and run `bash verify.sh` from it (do NOT
run bootstrap first). This compares all installed bytes with the fetched version;
a newer main version may legitimately differ, so compare the install log commit.
Then ask the task to list its active instruction sources and available skills.
A file listing does not prove those sources were loaded. Check for nonempty
`AGENTS.override.md`, which overrides global AGENTS.md. Start a fresh session
after changes; loading instructions after startup cannot retroactively affect
the initial request.

Interpretation:
- No install output: execution is unproven; rerun explicitly during setup.
- Verified files during setup but missing in a new task: persistence/snapshot or
  environment selection issue; collect the commit, environment, and publication
  evidence for support. Do not keep changing bootstrap.
- Files present but not listed as active: discovery/harness issue.
- Permission errors: compare UID, ownership and directory traversal permissions.
- Clone failures: investigate GitHub network access, not skill discovery.

If global provisioning is not preserved/loaded, the documented fallback is
repository skills. To keep project repositories clean, add the central setup
repository as another repository in the environment and use setup instructions to
read its guidance explicitly. Automatic cross-repository global discovery is not
documented, so verify it rather than promise it. The fully documented repository
fallback requires project-level instructions/skills and conflicts with the
no-project-copy goal.

## Regression tests

Run `python3 test_bootstrap.py` and `bash -n bootstrap.sh verify.sh cloud-install.sh`.
Tests clone the public repo, overlay local scripts, and use temporary homes.
ShellCheck is recommended when available. No real global configuration is touched.

## Installed paths

- `~/.codex/AGENTS.md` (or `$CODEX_HOME/AGENTS.md` when set)
- `~/.claude/CLAUDE.md`
- `~/.agents/skills/<skill>` for Codex
- `~/.claude/skills/<skill>` for Claude

The two instruction files are regular files. Skills have one canonical source
under `.agents/skills/`; the installer copies it to both global skill locations.
No project files are changed. Unrelated skills and extra files are retained.
Changed destination files are backed up under
`~/.agent-cloud-setup/backups/`. Identical files are left alone.

Run `bash bootstrap.sh` from any working directory. Requires Bash, find, grep,
and standard GNU file utilities. Errors stop installation; partial installs can
be retried. Use a fresh agent session after provisioning.

## Tool dependencies

Bootstrap installs definitions only. It does not install Node.js, npm,
Playwright, Chromium, Lighthouse, or MCP servers. For browser tasks, provision
these separately; see the Playwright skill's setup instructions. Performance
audits are invoked only when explicitly requested.

## Check locally without changing global configuration

```bash
bash -n bootstrap.sh
test_home="$(mktemp -d)"
env -u CODEX_HOME HOME="$test_home" bash bootstrap.sh
env -u CODEX_HOME HOME="$test_home" bash bootstrap.sh
rm -rf -- "$test_home"
```

## Existing liquid-portfolio environment

The complete example is [examples/liquid-portfolio-install.sh](examples/liquid-portfolio-install.sh).
It preserves the supplied pnpm 12.10.1 setup. Its syntax has been checked;
project dependency installation and execution inside the actual cloud environment
remain unverified. Copy it into that environment's Install script only after
reviewing the paths. Leave the project Start skill unchanged.

## Local verification record

- Bash syntax: PASS.
- Public GitHub clone and isolated bootstrap regression tests: PASS.
- All 11 skills, file bytes, modes and current-user ownership: PASS.
- Default HOME, explicit CODEX_HOME, independent caller/target homes: PASS.
- Repeated runs, backups, preexisting/unrelated files and project sentinel: PASS.
- Invalid destinations and failed Git clone: fail with nonzero status as expected.
- Root-owned checkout to a real unprivileged process: PASS in WSL using nobody,
  an isolated home and a test-only passwd lookup; installed files/log owned by nobody.
- ShellCheck: SKIPPED, unavailable.
- Actual Codex Cloud publication, persistence and harness discovery: NOT VERIFIED.
- Actual cloud tool availability is unknown; scripts require Bash, Git, coreutils,
  find, grep, getent and tee; runuser is required only for root setup.
