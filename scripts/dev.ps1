# scripts/dev.ps1 — Windows equivalent of dev.sh.
# Starts every Aegis Python service in its own PowerShell window.
#
# Prereq: `make emulators` (or equivalent docker-compose up) is running.

$ErrorActionPreference = "Stop"

# Repo root = parent of this script's directory.
$root = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $root

# Load .env into the current session so services see the emulator hosts.
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*#") { return }
        if ($_ -match "^\s*$") { return }
        if ($_ -match "^\s*([^=\s]+)\s*=\s*(.*)\s*$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
    Write-Host ">> Loaded .env" -ForegroundColor Green
}

$services = @(
    @{ Name = "ingest";       Dir = "services\ingest";       Port = 8001 },
    @{ Name = "vision";       Dir = "services\vision";       Port = 8002 },
    @{ Name = "orchestrator"; Dir = "services\orchestrator"; Port = 8003 },
    @{ Name = "dispatch";     Dir = "services\dispatch";     Port = 8004 }
)

foreach ($svc in $services) {
    $title = "Aegis $($svc.Name)"
    $venvPython = "$root\.venv\Scripts\python.exe"
    $cmd = "cd `"$root\$($svc.Dir)`"; & `"$venvPython`" -m uvicorn main:app --reload --host 0.0.0.0 --port $($svc.Port)"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle = '$title'; $cmd"
    Write-Host ">> Started $($svc.Name) on :$($svc.Port)" -ForegroundColor Cyan
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host "  Aegis local dev stack"                                   -ForegroundColor Yellow
Write-Host "--------------------------------------------------------"
Write-Host "  Ingest:       http://localhost:8001/docs"
Write-Host "  Vision:       http://localhost:8002/docs"
Write-Host "  Orchestrator: http://localhost:8003/docs"
Write-Host "  Dispatch:     http://localhost:8004/docs"
Write-Host ""
Write-Host "  Smoke test:   scripts\smoke.ps1"
Write-Host ""
Write-Host "  Each service is in its own window. Close the window to stop."
Write-Host "========================================================" -ForegroundColor Yellow
