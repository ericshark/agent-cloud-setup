#!/usr/bin/env bash
set -Eeuo pipefail
trap 'printf "Bootstrap failed at line %s\n" "$LINENO" >&2' ERR
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Explicit target paths avoid silently installing into a preparation user's home.
target_home="${AGENT_SETUP_HOME:-${HOME:?HOME must be set}}"
target_codex_home="${AGENT_SETUP_CODEX_HOME:-${CODEX_HOME:-$target_home/.codex}}"
printf 'Installer uid=%s caller_HOME=%s caller_CODEX_HOME=%s target_HOME=%s target_CODEX_HOME=%s\n' "$(id -u)" "$HOME" "${CODEX_HOME:-unset}" "$target_home" "$target_codex_home"
export HOME="$target_home"
export CODEX_HOME="$target_codex_home"
[[ "$HOME" = /* && "$HOME" != / ]] || { echo "HOME must be an absolute user directory" >&2; exit 1; }
codex_home="${CODEX_HOME:-$HOME/.codex}"
[[ "$codex_home" = /* ]] || { echo "CODEX_HOME must be absolute" >&2; exit 1; }
[[ -f "$repo_dir/AGENTS.md" && -f "$repo_dir/CLAUDE.md" && -d "$repo_dir/.agents/skills" ]]
# Preflight before changing the environment.
if find "$repo_dir/.agents" -type l -print -quit | grep -q .; then
  echo "Source skills must contain actual files, not symlinks" >&2
  exit 1
fi
backup_dir=""
install_file() {
  local source="$1" destination="$2" relative="$3"
  if [[ -f "$destination" ]] && cmp -s "$source" "$destination"; then return; fi
  if [[ -e "$destination" || -L "$destination" ]]; then
    if [[ -z "$backup_dir" ]]; then
      mkdir -p "$HOME/.agent-cloud-setup/backups"
      backup_dir="$(mktemp -d "$HOME/.agent-cloud-setup/backups/run.XXXXXXXX")"
    fi
    mkdir -p "$backup_dir/$(dirname "$relative")"
    cp -a -- "$destination" "$backup_dir/$relative"
  fi
  mkdir -p "$(dirname "$destination")"
  # Replace a destination symlink itself, never write through it.
  local temporary
  temporary="$(mktemp "$(dirname "$destination")/.agent-install.XXXXXXXX")"
  cp -- "$source" "$temporary"
  chmod --reference="$source" "$temporary"
  mv -fT -- "$temporary" "$destination"
}
install_file "$repo_dir/AGENTS.md" "$codex_home/AGENTS.md" codex/AGENTS.md
install_file "$repo_dir/CLAUDE.md" "$HOME/.claude/CLAUDE.md" claude/CLAUDE.md
for agent in shared claude; do
  if [[ "$agent" == shared ]]; then destination="$HOME/.agents/skills"; else destination="$HOME/.claude/skills"; fi
  while IFS= read -r -d '' source; do
    relative="${source#"$repo_dir/.agents/skills/"}"
    install_file "$source" "$destination/$relative" "$agent/skills/$relative"
  done < <(find "$repo_dir/.agents/skills" -type f -print0)
done
printf 'Installed instructions and skills for Codex and Claude.\n'
if [[ -n "$backup_dir" ]]; then printf 'Previous files backed up to %s\n' "$backup_dir"; fi

# Verify bytes, not just directory existence, before claiming success.
bash "$repo_dir/verify.sh"
