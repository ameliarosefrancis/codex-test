# AmeliaRoseCo Toolkit - PowerShell Launch Script
# This script activates the venv and runs the application

param(
    [switch]$SkipPause = $false
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AmeliaRoseCo Toolkit - Launching..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Set location to script directory
Set-Location $PSScriptRoot

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "`nTo create venv, run:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor White
    Write-Host "`n"
    if (-not $SkipPause) { Read-Host "Press Enter to exit" }
    exit 1
}

# Activate virtual environment
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if (-not $SkipPause) { Read-Host "Press Enter to exit" }
    exit 1
}

Write-Host "`nStarting application...`n" -ForegroundColor Cyan

# Run the application
& python app_gui.py

# Pause to see any errors
if (-not $SkipPause) {
    Read-Host "Press Enter to exit"
}
