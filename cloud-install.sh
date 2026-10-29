#!/usr/bin/env bash
set -Eeuo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# The reported runtime identity is agent. Fail rather than guess another user.
target_user="${AGENT_SETUP_USER:-agent}"
entry="$(getent passwd "$target_user")" || { echo "Missing runtime user: $target_user" >&2; exit 1; }
IFS=: read -r name _ uid _ _ target_home _ <<< "$entry"
if [[ "$(id -u)" != "$uid" ]]; then
  [[ "$(id -u)" == 0 ]] || { echo "Run as $target_user or root; refusing wrong-user installation" >&2; exit 1; }
  # Repository must be readable/traversable by the target user.
  exec runuser -u "$name" -- env HOME="$target_home" CODEX_HOME="$target_home/.codex" bash "$repo_dir/cloud-install.sh"
fi
export HOME="$target_home" CODEX_HOME="$target_home/.codex"
export AGENT_SETUP_HOME="$HOME" AGENT_SETUP_CODEX_HOME="$CODEX_HOME"
mkdir -p "$HOME/.agent-cloud-setup"
log="$HOME/.agent-cloud-setup/install.log"
{
  date -u
  git -c safe.directory="$repo_dir" -C "$repo_dir" rev-parse HEAD
  bash "$repo_dir/bootstrap.sh"
} 2>&1 | tee "$log"
