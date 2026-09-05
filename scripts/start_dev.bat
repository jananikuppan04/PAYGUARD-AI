@echo off
echo ===================================================
echo   PayGuard AI — Starting Development Environment
echo ===================================================
echo.

cd /d "%~dp0.."

echo [1/2] Starting PayGuard AI FastAPI Backend on http://localhost:8000 ...
start "PayGuard Backend" cmd /k "cd backend && python main.py"

echo [2/2] Starting PayGuard AI Vite Frontend on http://localhost:5173 ...
start "PayGuard Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All services launched!
echo - API Docs: http://localhost:8000/docs
echo - UI Dashboard: http://localhost:5173
echo.
pause
