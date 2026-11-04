#!/usr/bin/env bash
set -Eeuo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# Priority: explicit override > current non-root user > uniquely identifiable
# non-root runtime account. Never silently install into root's home.
if [[ -n "${AGENT_SETUP_USER:-}" ]]; then
  target_user="$AGENT_SETUP_USER"
elif [[ "$(id -u)" -ne 0 ]]; then
  target_user="$(id -un)"
else
  # Root-run setup: identify a single normal account with a usable home.
  # Ambiguity is unsafe; specify AGENT_SETUP_USER instead.
  mapfile -t candidates < <(
    getent passwd | awk -F: '$3 >= 1000 && $3 < 65534 && $6 ~ /^\// && $6 != "/" && $7 !~ /(nologin|false)$/ {print $1}'
  )
  if [[ "${#candidates[@]}" -ne 1 ]]; then
    printf 'Cannot identify one runtime user (found %s: %s).\n' \
      "${#candidates[@]}" "${candidates[*]:-none}" >&2
    echo "Set AGENT_SETUP_USER to the cloud task's actual username." >&2
    exit 1
  fi
  target_user="${candidates[0]}"
fi

entry="$(getent passwd "$target_user")" || {
  echo "Unknown runtime user: $target_user" >&2
  exit 1
}
IFS=: read -r name _ uid _ _ target_home _ <<< "$entry"
[[ "$target_home" = /* && "$target_home" != "/" && -d "$target_home" ]] || {
  echo "Runtime user $name has no usable home: $target_home" >&2
  exit 1
}

if [[ "$(id -u)" -ne "$uid" ]]; then
  [[ "$(id -u)" -eq 0 ]] || {
    echo "Cannot install as $name from a different non-root account." >&2
    exit 1
  }
  command -v runuser >/dev/null || {
    echo "runuser is required to switch from root to $name." >&2
    exit 1
  }
  # The checkout must be readable by the target user.
  exec runuser -u "$name" -- env \
    AGENT_SETUP_USER="$name" \
    HOME="$target_home" \
    CODEX_HOME="$target_home/.codex" \
    bash "$repo_dir/cloud-install.sh"
fi

export HOME="$target_home"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export AGENT_SETUP_HOME="$HOME"
export AGENT_SETUP_CODEX_HOME="$CODEX_HOME"

mkdir -p "$HOME/.agent-cloud-setup"
log="$HOME/.agent-cloud-setup/install.log"
{
  printf 'Runtime user=%s uid=%s HOME=%s CODEX_HOME=%s\n' \
    "$name" "$uid" "$HOME" "$CODEX_HOME"
  date -u
  git -c safe.directory="$repo_dir" -C "$repo_dir" rev-parse HEAD
  bash "$repo_dir/bootstrap.sh"
} 2>&1 | tee "$log"
