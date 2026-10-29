# Agent Cloud Setup

Shared Linux cloud instructions and 11 skills for Codex and Claude Code.
This is a normal repository, not a GitHub template.

## Use in Codex Cloud

Paste this into the environment setup script (Git and network access required):

```bash
set -euo pipefail
setup_dir="$(mktemp -d)"
git clone --depth 1 https://github.com/ericshark/agent-cloud-setup.git "$setup_dir"
bash "$setup_dir/bootstrap.sh"
rm -rf -- "$setup_dir"
```

The command fetches the default branch. Pin a reviewed commit for reproducible
provisioning. Re-run during maintenance, or rebuild the environment, to refresh
cached environments. Existing repository instructions can override global rules.

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
