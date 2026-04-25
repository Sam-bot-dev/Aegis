#!/usr/bin/env pwsh
<#
.SYNOPSIS
    One-time setup: fetch Firebase credentials and update apphosting.yaml files.
.DESCRIPTION
    Gets Firebase Web app config (API key, Auth domain, App ID, etc.) from
    Firebase Console and updates both staff and dashboard apphosting.yaml files.
    Then deploys both apps.
#>

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "🔧 Aegis Frontend Setup & Deploy" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Gray

# ── Check prerequisites ─────────────────────────────────────────────────────
$prereqs = @("gcloud", "firebase")
foreach ($cmd in $prereqs) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "❌ Required command not found: $cmd. Please install it first."
    }
}

# ── Authenticate ────────────────────────────────────────────────────────────
Write-Host "`n[1/3] Ensuring gcloud and firebase are authenticated..." -ForegroundColor Yellow

gcloud auth list --filter="status:ACTIVE" --format="value(account)" | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "gcloud not authenticated. Run: gcloud auth login" }

firebase projects:list | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "firebase CLI not authenticated. Run: firebase login" }

Write-Host "  ✅ Authenticated" -ForegroundColor Green

# ── Fetch Cloud Run backend URLs ────────────────────────────────────────────
Write-Host "`n[2/3] Fetching Cloud Run backend URLs..." -ForegroundColor Yellow

$region = "asia-south1"
$services = @("ingest", "vision", "orchestrator", "dispatch")
$backendUrls = @{}

foreach ($svc in $services) {
    $url = gcloud run services describe $svc --region=$region --format="value(status.url)" 2>&1 | Trim
    if (-not $url -or $url -match "ERROR|NOT_FOUND") {
        Write-Warning "  Could not get URL for $svc — service may not be deployed yet"
        $backendUrls[$svc] = "https://$svc-placeholder.run.app"
    } else {
        $backendUrls[$svc] = $url
        Write-Host "  $svc`t$url" -ForegroundColor Green
    }
}

# ── Get Firebase Web App credentials ───────────────────────────────────────
Write-Host "`n[3/3] Firebase Web App Configuration" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Gray
Write-Host "You need these from Firebase Console → Project Settings → Web app:" -ForegroundColor Cyan
Write-Host "  1. apiKey" -ForegroundColor White
Write-Host "  2. authDomain" -ForegroundColor White
Write-Host "  3. storageBucket" -ForegroundColor White
Write-Host "  4. messagingSenderId" -ForegroundColor White
Write-Host "  5. appId" -ForegroundColor White
Write-Host ""

$firebaseConfig = @{
    apiKey            = Read-Host "Enter API Key"
    authDomain        = Read-Host "Enter Auth Domain (e.g., aegis-gsc-2026.firebaseapp.com)"
    storageBucket     = Read-Host "Enter Storage Bucket (e.g., aegis-gsc-2026.appspot.com)"
    messagingSenderId = Read-Host "Enter Messaging Sender ID"
    appId             = Read-Host "Enter App ID"
}

# Validate
foreach ($kvp in $firebaseConfig.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace($kvp.Value)) {
        Write-Error "Firebase config value '$($kvp.Key)' cannot be empty."
    }
}

# ── Update staff apphosting.yaml ────────────────────────────────────────────
Write-Host "`n[4/4] Updating apphosting.yaml files..." -ForegroundColor Yellow

$staffConfigPath = "apps/staff/apphosting.yaml"
$staffConfig = Get-Content $staffConfigPath

$staffConfig = $staffConfig `
    -replace "REPLACE_WITH_INGEST_RUN_URL", $backendUrls["ingest"] `
    -replace "REPLACE_WITH_VISION_RUN_URL", $backendUrls["vision"] `
    -replace "REPLACE_WITH_ORCHESTRATOR_RUN_URL", $backendUrls["orchestrator"] `
    -replace "REPLACE_WITH_DISPATCH_RUN_URL", $backendUrls["dispatch"] `
    -replace "REPLACE_WITH_FIREBASE_WEB_API_KEY", $firebaseConfig["apiKey"] `
    -replace "REPLACE_WITH_MESSAGING_SENDER_ID", $firebaseConfig["messagingSenderId"] `
    -replace "REPLACE_WITH_FIREBASE_APP_ID", $firebaseConfig["appId"]

Set-Content -Path $staffConfigPath -Value $staffConfig -NoNewline
Write-Host "  ✅ staff/apphosting.yaml updated" -ForegroundColor Green

# ── Update dashboard apphosting.yaml ────────────────────────────────────────
$dashboardConfigPath = "apps/dashboard/apphosting.yaml"
$dashboardConfig = Get-Content $dashboardConfigPath

$dashboardConfig = $dashboardConfig `
    -replace "REPLACE_WITH_INGEST_RUN_URL", $backendUrls["ingest"] `
    -replace "REPLACE_WITH_VISION_RUN_URL", $backendUrls["vision"] `
    -replace "REPLACE_WITH_ORCHESTRATOR_RUN_URL", $backendUrls["orchestrator"] `
    -replace "REPLACE_WITH_DISPATCH_RUN_URL", $backendUrls["dispatch"] `
    -replace "REPLACE_WITH_FIREBASE_WEB_API_KEY", $firebaseConfig["apiKey"] `
    -replace "REPLACE_WITH_MESSAGING_SENDER_ID", $firebaseConfig["messagingSenderId"] `
    -replace "REPLACE_WITH_FIREBASE_APP_ID", $firebaseConfig["appId"]

Set-Content -Path $dashboardConfigPath -Value $dashboardConfig -NoNewline
Write-Host "  ✅ dashboard/apphosting.yaml updated" -ForegroundColor Green

# ── Deploy Staff app ─────────────────────────────────────────────────────────
Write-Host "`n[5/6] Deploying Staff app..." -ForegroundColor Yellow
Set-Location "apps/staff"
$staffResult = firebase apphosting:deploy 2>&1
Set-Location ..

if ($LASTEXITCODE -ne 0) {
    Write-Error "Staff app deployment failed. Check Firebase Console for details."
}
Write-Host "  ✅ Staff app deployed" -ForegroundColor Green

# ── Extract Staff URL from deployment output ─────────────────────────────────
$staffUrl = $staffResult | Select-String -Pattern "https://aegis-staff--" | Select-Object -First 1 | ForEach-Object {
    $_.Line.Trim()
}

if (-not $staffUrl) {
    Write-Warning "Could not auto-detect Staff URL from deployment output."
    $staffUrl = Read-Host "Enter the Staff App URL manually (e.g., https://aegis-staff--aegis-gsc-2026.asia-southeast1.hosted.app)"
}

Write-Host "  Staff URL: $staffUrl" -ForegroundColor Green

# ── Update dashboard with Staff URL ─────────────────────────────────────────
Write-Host "`n[6/6] Updating dashboard with Staff URL and deploying..." -ForegroundColor Yellow

$dashboardConfig = Get-Content $dashboardConfigPath
$dashboardConfig = $dashboardConfig -replace "REPLACE_WITH_STAFF_APPHOSTING_URL", $staffUrl
Set-Content -Path $dashboardConfigPath -Value $dashboardConfig -NoNewline
Write-Host "  ✅ dashboard/apphosting.yaml updated with Staff URL" -ForegroundColor Green

# ── Deploy Dashboard app ─────────────────────────────────────────────────────
Set-Location "apps/dashboard"
$dashboardResult = firebase apphosting:deploy 2>&1
Set-Location ..

if ($LASTEXITCODE -ne 0) {
    Write-Error "Dashboard app deployment failed."
}
Write-Host "  ✅ Dashboard app deployed" -ForegroundColor Green

$dashboardUrl = "https://aegis-dashboard--aegis-gsc-2026.asia-southeast1.hosted.app"
Write-Host "`n`n🎉 ALL APPS DEPLOYED!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host "`nDashboard: $dashboardUrl"
Write-Host "Staff:     $staffUrl"
Write-Host "`nBackend Services:"
foreach ($kvp in $backendUrls.GetEnumerator()) {
    Write-Host "  $($kvp.Key)`t$($kvp.Value)"
}
Write-Host "`n'"
