@echo off
echo ===================================================
echo   PayGuard AI — Running Comprehensive Verification
echo ===================================================
echo.

cd /d "%~dp0.."

echo [1/2] Running Backend Pytest Suite...
pytest backend/tests/test_payguard.py -v
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend tests failed!
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running Frontend Production Build...
cd frontend
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend build failed!
    exit /b %ERRORLEVEL%
)

echo.
echo ===================================================
echo   ALL TESTS AND BUILDS PASSED SUCCESSFULLY!
echo ===================================================
pause
