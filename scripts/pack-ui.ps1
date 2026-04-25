# Build @aegis/ui-web and distribute the packed tgz to both apps.
#
# Run this whenever you change code under packages/ui-web before rebuilding
# or redeploying apps/staff or apps/dashboard.
#
# Usage:  .\scripts\pack-ui.ps1

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot\.."
$uiRoot = Join-Path $repoRoot "packages/ui-web"
$tgzName = "aegis-ui-web-0.1.0.tgz"

Push-Location $uiRoot
try {
  Write-Host "==> Installing ui-web deps" -ForegroundColor Cyan
  npm install --no-audit --no-fund

  Write-Host "==> Compiling TypeScript (emits dist/)" -ForegroundColor Cyan
  npx tsc -p tsconfig.json

  Write-Host "==> npm pack" -ForegroundColor Cyan
  npm pack

  $tgz = Join-Path $uiRoot $tgzName
  if (-not (Test-Path $tgz)) {
    throw "Expected $tgz to exist after npm pack"
  }

  foreach ($appDir in @("apps/staff", "apps/dashboard")) {
    $dest = Join-Path $repoRoot "$appDir/$tgzName"
    Copy-Item -Force $tgz $dest
    Write-Host "Copied to $dest" -ForegroundColor Green
  }
}
finally {
  Pop-Location
}

Write-Host "`nDone. Re-run:  cd apps/<app>; npm install; npm run build" -ForegroundColor Green
