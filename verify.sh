#!/usr/bin/env bash
set -Eeuo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
target_home="${AGENT_SETUP_HOME:-${HOME:?HOME must be set}}"
codex_home="${AGENT_SETUP_CODEX_HOME:-${CODEX_HOME:-$target_home/.codex}}"
printf 'VERIFY uid=%s HOME=%s CODEX_HOME=%s\n' "$(id -u)" "$target_home" "$codex_home"
failed=0
check() {
  if [[ -r "$2" ]] && cmp -s "$1" "$2"; then
    return
  else
    printf 'MISSING/DIFFERENT/UNREADABLE: %s\n' "$2" >&2
    failed=1
  fi
}
check "$repo_dir/AGENTS.md" "$codex_home/AGENTS.md"
check "$repo_dir/CLAUDE.md" "$target_home/.claude/CLAUDE.md"
if [[ -s "$codex_home/AGENTS.override.md" ]]; then
  echo "WARNING: AGENTS.override.md takes precedence over installed AGENTS.md" >&2
fi
count=0
for skill in "$repo_dir"/.agents/skills/*; do
  [[ -f "$skill/SKILL.md" ]] || { echo "Invalid skill source: $skill" >&2; exit 1; }
  count=$((count + 1))
done
while IFS= read -r -d '' source; do
  relative="${source#"$repo_dir/.agents/skills/"}"
  check "$source" "$target_home/.agents/skills/$relative"
  check "$source" "$target_home/.claude/skills/$relative"
done < <(find "$repo_dir/.agents/skills" -type f -print0)
[[ "$failed" == 0 ]] || exit 1
printf 'PASS: instructions and every file in %s skills match for both agents.\n' "$count"
echo "Filesystem verification does not prove the cloud harness loaded instructions or registered skills."
