#!/usr/bin/env bash
# Build @aegis/ui-web and distribute the packed tgz to both apps.
# Run after any change under packages/ui-web before rebuilding the apps.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UI_ROOT="$REPO_ROOT/packages/ui-web"
TGZ_NAME="aegis-ui-web-0.1.0.tgz"

pushd "$UI_ROOT" > /dev/null

echo "==> Installing ui-web deps"
npm install --no-audit --no-fund

echo "==> Compiling TypeScript (emits dist/)"
npx tsc -p tsconfig.json

echo "==> npm pack"
npm pack

for app_dir in apps/staff apps/dashboard; do
  dest="$REPO_ROOT/$app_dir/$TGZ_NAME"
  cp -f "$UI_ROOT/$TGZ_NAME" "$dest"
  echo "Copied to $dest"
done

popd > /dev/null

echo
echo "Done. Re-run: cd apps/<app>; npm install; npm run build"
