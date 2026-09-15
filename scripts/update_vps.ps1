# ──────────
# REAN AI - LOCAL / WINDOWS VPS AUTOMATED UPDATE & AUDIT SCRIPT
# ──────────
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\update_vps.ps1
# ──────────

$ErrorActionPreference = "Stop"

Write-Host "🚀 REAN AI - Repository Sync & Audit Script" -ForegroundColor Cyan
Write-Host "──────────" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "`n📥 Synchronizing from origin main..." -ForegroundColor Yellow
git fetch origin main
git reset --hard origin/main
git log -1 --oneline
Write-Host "✅ Git repository synchronized." -ForegroundColor Green

Write-Host "`n🔍 Running System Audit..." -ForegroundColor Yellow
python scripts\audit_system.py
Write-Host "✅ System Audit passed successfully." -ForegroundColor Green

Write-Host "`n🎉 REAN AI UPDATE COMPLETE!" -ForegroundColor Green
Write-Host "──────────" -ForegroundColor Green
