# Deploy Firebase rules and indexes
$ErrorActionPreference = "Stop"

Write-Host "Deploying Firebase rules and indexes..."
Set-Location "c:\Users\mekha\AegisLocal\firebase"
firebase deploy --only firestore:rules,firestore:indexes

Write-Host "Firebase deployment complete."
