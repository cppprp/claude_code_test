# Setup script for heart tissue tensor visualization environment (Windows)
# Uses uv for fast package management

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Heart Tissue Tensor Visualization Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
try {
    $uvVersion = uv --version 2>$null
    Write-Host "✓ uv is installed ($uvVersion)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ uv is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing uv..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
    Write-Host ""
    Write-Host "✓ uv installed successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Please restart your PowerShell window and run this script again." -ForegroundColor Yellow
    exit 0
}

# Create virtual environment
Write-Host "[1/3] Creating virtual environment..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "  Virtual environment already exists, skipping creation" -ForegroundColor Yellow
} else {
    uv venv
    Write-Host "  ✓ Virtual environment created in .venv/" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "[2/3] Activating virtual environment..." -ForegroundColor Cyan
& .venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "[3/3] Installing dependencies..." -ForegroundColor Cyan
uv pip install -r requirements.txt
Write-Host "  ✓ All dependencies installed" -ForegroundColor Green
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the environment in the future, run:"
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Quick start:"
Write-Host "  python visualize_heart_tissue.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Inspect your data:"
Write-Host "  python inspect_pickle_data.py <path_to_pickle>" -ForegroundColor Yellow
Write-Host ""
