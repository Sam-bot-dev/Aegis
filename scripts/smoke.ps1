# scripts/smoke.ps1 — Clean Windows smoke test (PowerShell 7+)

$ErrorActionPreference = "Stop"

$Ingest = "http://localhost:8001"
$Vision = "http://localhost:8002"
$Orch   = "http://localhost:8003"
$Disp   = "http://localhost:8004"

function Bold($msg) { Write-Host ""; Write-Host "== $msg ==" -ForegroundColor Cyan }
function OK($msg)   { Write-Host "  OK  $msg" -ForegroundColor Green }
function Fail($msg) { Write-Host "  ERR $msg" -ForegroundColor Red; exit 1 }

# --------------------------------------------------
Bold "1/5  Health checks"
foreach ($url in @("$Ingest/health", "$Vision/health", "$Orch/health", "$Disp/health")) {
    try {
        Invoke-RestMethod -Uri $url | Out-Null
        OK $url
    } catch {
        Fail "$url -> $($_.Exception.Message)"
    }
}

# --------------------------------------------------
Bold "2/5  Frame ingest"

# create a temp binary file (1KB)
$tmp = [System.IO.Path]::GetTempFileName()
[byte[]]$bytes = 0..1023 | ForEach-Object { 0xFF }
[System.IO.File]::WriteAllBytes($tmp, $bytes)

$form = @{
    venue_id  = "taj-ahmedabad"
    camera_id = "K-12"
    frame     = Get-Item $tmp
}

try {
    $r = Invoke-RestMethod -Uri "$Ingest/v1/frames" -Method Post -Form $form
    if ($r.frame_id) {
        OK "ingest accepted: $($r.frame_id)"
    } else {
        Fail "no frame_id in response"
    }
} catch {
    Fail $_.Exception.Message
}

Remove-Item $tmp -ErrorAction SilentlyContinue

# --------------------------------------------------
Bold "3/5  Vision classify"

$bytes = [byte[]](0..512 | ForEach-Object { 0xFF })
$b64 = [Convert]::ToBase64String($bytes)

$body = @{
    venue_id     = "taj-ahmedabad"
    camera_id    = "K-12"
    zone_id      = "kitchen-main"
    frame_base64 = $b64
} | ConvertTo-Json

try {
    $r = Invoke-RestMethod -Uri "$Vision/v1/analyze" -Method Post -Body $body -ContentType "application/json"
    if ($r.signal.category_hint -and $null -ne $r.signal.confidence) {
        OK "vision classified $($r.signal.category_hint) (used_gemini=$($r.used_gemini))"
    } else {
        Fail "vision response missing category/confidence"
    }
} catch {
    Fail $_.Exception.Message
}

# --------------------------------------------------
Bold "4/5  Orchestrator handle"

$signal = @{
    venue_id      = "taj-ahmedabad"
    zone_id       = "kitchen-main"
    modality      = "VISION"
    category_hint = "FIRE"
    confidence    = 0.9
} | ConvertTo-Json

try {
    $r = Invoke-RestMethod -Uri "$Orch/v1/handle" -Method Post -Body $signal -ContentType "application/json"

    if ($r.classification.severity -eq "S2") {
        OK "classified S2"
    } else {
        Fail "expected S2 got $($r.classification.severity)"
    }

    if ($r.dispatched) {
        OK "dispatched"
    } else {
        Fail "expected dispatch"
    }
} catch {
    Fail $_.Exception.Message
}

# --------------------------------------------------
Bold "5/5  Dispatch state machine"

$did = "DSP-smoke-001"

foreach ($action in @("ack", "enroute", "arrived")) {
    try {
        $r = Invoke-RestMethod -Uri "$Disp/v1/dispatches/$did/$action" -Method Post
        OK "$action -> $($r.status)"
    } catch {
        Fail $_.Exception.Message
    }
}

# --------------------------------------------------
Bold "Done"
Write-Host "  All systems nominal. You just ran the full Aegis pipeline." -ForegroundColor Green
