# Agent Cloud Setup

Install the shared global instructions and all bundled skills for Codex and
Claude Code. Project files and unrelated files in the destination directories
are preserved.

| Agent | Instructions | Skills |
| --- | --- | --- |
| Codex | `$CODEX_HOME/AGENTS.md` (defaults to `~/.codex/AGENTS.md`) | `~/.agents/skills/` |
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/skills/` |

## Install

Use a Linux environment with Bash, Git, GNU coreutils, find, grep, getent, and
awk. Root setup also needs runuser and a checkout readable by the target user.

From a checkout of this repository, run this in your cloud environment's setup
step:

```bash
bash cloud-install.sh
```

The installer uses the current account when run as a non-root user. When run
as root, it looks for exactly one normal account with an absolute home path
and a login shell. If detection is ambiguous or selects the wrong account,
specify the actual runtime username:

```bash
AGENT_SETUP_USER=your-runtime-user bash cloud-install.sh
```

Root setup runs the installer as the selected user and uses that user's
`~/.codex` directory. When run directly as the target user, the installer
honors an existing `CODEX_HOME`. The log is written to
`~/.agent-cloud-setup/install.log` in the selected user's home. Repeating the
install leaves identical files untouched and replaces changed managed files.

## Verify

The installer runs verification automatically. To check again, run
`bash verify.sh` from the same checkout as the runtime user, with the same
`CODEX_HOME` if customized. This compares the installed files with the checkout.
Filesystem verification does not guarantee that a fresh agent session loads
the instructions or discovers the skills.

Run `python3 test_bootstrap.py` to test the local checkout in temporary directories.
