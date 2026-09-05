# Groww Lens — Developer Quickstart (PowerShell)
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       Groww Lens Setup Script            " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Environment files
if (!(Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "[+] Created backend\.env from template" -ForegroundColor Yellow
}
if (!(Test-Path "frontend\.env.local")) {
    Copy-Item "frontend\.env.local.example" "frontend\.env.local"
    Write-Host "[+] Created frontend\.env.local from template" -ForegroundColor Yellow
}

# 2. Python Virtual Environment
Write-Host "[*] Checking Python backend..." -ForegroundColor Cyan
if (!(Test-Path "backend\venv")) {
    Write-Host "[*] Creating virtual environment in backend\venv..." -ForegroundColor Cyan
    python -m venv backend\venv
}

Write-Host "[*] Upgrading pip and installing backend dependencies..." -ForegroundColor Cyan
& ".\backend\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\backend\venv\Scripts\python.exe" -m pip install -r backend\requirements.txt

# 3. Node Dependencies
Write-Host "[*] Checking frontend dependencies..." -ForegroundColor Cyan
Set-Location frontend
npm install
Set-Location ..

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Setup Completed Successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "To start the backend:" -ForegroundColor White
Write-Host "  cd backend" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\activate" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor Yellow
Write-Host ""
Write-Host "To seed demo data:" -ForegroundColor White
Write-Host "  cd backend" -ForegroundColor Yellow
Write-Host "  python seed.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start the frontend:" -ForegroundColor White
Write-Host "  cd frontend" -ForegroundColor Yellow
Write-Host "  npm run dev" -ForegroundColor Yellow
