# GRNet UV Setup Script for PowerShell
# This script automates the complete setup process with better error handling

Write-Host "`n" -NoNewline
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  GRNet Project Setup with UV Package Manager" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "`n"

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check if UV is installed
Write-Host "🔍 Checking if UV is installed..." -ForegroundColor Yellow
if (Test-Command "uv") {
    $uvVersion = uv --version
    Write-Host "✅ UV is installed: $uvVersion" -ForegroundColor Green
}
else {
    Write-Host "❌ UV is not installed!" -ForegroundColor Red
    Write-Host "`nWould you like to install UV now? (Y/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "`n📦 Installing UV..." -ForegroundColor Yellow
        try {
            Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
            Write-Host "✅ UV installed successfully!" -ForegroundColor Green
            Write-Host "⚠️  You may need to restart your terminal or run: refreshenv" -ForegroundColor Yellow
        }
        catch {
            Write-Host "❌ Failed to install UV" -ForegroundColor Red
            Write-Host "Please install manually from: https://docs.astral.sh/uv/" -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        Write-Host "`nPlease install UV first:" -ForegroundColor Yellow
        Write-Host "  powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host "`n"

# Create virtual environment
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🔧 Creating virtual environment with Python 3.8" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "`n"

try {
    uv venv --python 3.8
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Virtual environment creation had issues, but continuing..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️  Could not create virtual environment" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n"

# Sync dependencies
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "📦 Installing project dependencies" -ForegroundColor Cyan
Write-Host "   (This may take a few minutes...)" -ForegroundColor Gray
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "`n"

try {
    uv sync
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ All dependencies installed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "`n⚠️  Some dependencies might have failed to install" -ForegroundColor Yellow
        Write-Host "You can try reinstalling them manually with: uv sync --reinstall" -ForegroundColor Gray
    }
}
catch {
    Write-Host "⚠️  Dependency installation had issues" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n"
Write-Host "===============================================" -ForegroundColor Green
Write-Host "           Setup Complete! ✅" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "`n"

Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "`n"
Write-Host "1. Activate the virtual environment:" -ForegroundColor Yellow
Write-Host "   .venv\Scripts\activate" -ForegroundColor White
Write-Host "`n"
Write-Host "2. Start Jupyter Lab:" -ForegroundColor Yellow
Write-Host "   uv run jupyter lab" -ForegroundColor White
Write-Host "`n"
Write-Host "3. Open the notebook:" -ForegroundColor Yellow
Write-Host "   code/GRNet_approach.ipynb" -ForegroundColor White
Write-Host "`n"

Write-Host "📚 For more information:" -ForegroundColor Cyan
Write-Host "   - Quick start: UV_SETUP.md" -ForegroundColor Gray
Write-Host "   - Quick reference: UV_QUICKREF.md" -ForegroundColor Gray
Write-Host "   - Migration guide: MIGRATION_GUIDE.md" -ForegroundColor Gray
Write-Host "`n"

Write-Host "💡 Tip: Add to your PATH to use 'uv' from anywhere" -ForegroundColor Cyan
Write-Host "`n"

# Optional: Ask if user wants to start Jupyter Lab now
Write-Host "Would you like to start Jupyter Lab now? (Y/N): " -NoNewline -ForegroundColor Yellow
$launchJupyter = Read-Host

if ($launchJupyter -eq "Y" -or $launchJupyter -eq "y") {
    Write-Host "`n🚀 Starting Jupyter Lab..." -ForegroundColor Green
    try {
        Set-Location -Path "code"
        uv run jupyter lab
    }
    catch {
        Write-Host "Failed to start Jupyter Lab" -ForegroundColor Red
        Write-Host "You can start it manually with: uv run jupyter lab" -ForegroundColor Gray
    }
}
else {
    Write-Host "`nHappy coding! 🎉" -ForegroundColor Green
}
