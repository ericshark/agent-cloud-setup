#!/usr/bin/env bash
set -euo pipefail
cd /workspace/liquid-portfolio
node --version
tools_dir=/workspace/.cloud-tools
pnpm_bin="$tools_dir/node_modules/.bin/pnpm"
if [[ ! -x "$pnpm_bin" ]] || [[ "$("$pnpm_bin" --version)" != 12.10.1 ]]; then
  npm install --prefix "$tools_dir" --cache /workspace/.cache/npm --no-save --package-lock=false pnpm@12.10.1
fi
CI=true "$pnpm_bin" install --frozen-lockfile --store-dir /workspace/.cache/pnpm/store

setup_dir="$(mktemp -d)"
trap 'rm -rf -- "$setup_dir"' EXIT
git clone --depth 1 https://github.com/ericshark/agent-cloud-setup.git "$setup_dir"
chmod 755 "$setup_dir"
bash "$setup_dir/cloud-install.sh"
echo "=== CLOUD SETUP COMPLETE ==="
