# Mentor Connect — Local Development Startup Script (Windows PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting Mentor Connect (Mesa School of Business)     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check Python environment
if (!(Test-Path "backend\.venv\Scripts\python.exe")) {
    Write-Host "[!] Virtual environment not found. Setting up backend..." -ForegroundColor Yellow
    python -m venv backend\.venv
    backend\.venv\Scripts\pip.exe install -r backend\requirements.txt
}

# Run database migrations
Write-Host "[*] Applying database migrations..." -ForegroundColor Green
Set-Location backend
.\.venv\Scripts\alembic.exe upgrade head
Set-Location ..

# Start Backend Server in a new window
Write-Host "[*] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000"

# Start Frontend Dev Server in a new window
Write-Host "[*] Launching Vite React Frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "[✓] Mentor Connect is running!" -ForegroundColor Green
Write-Host "    Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "    Backend:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
