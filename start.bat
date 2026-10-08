@echo off

echo ================================
echo        Starting Mini-RAG
echo ================================

cd /d "%~dp0"

echo.
echo [1/2] Starting Docker...
docker compose -f docker\docker-compose.yml up -d --build

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker failed to start.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting FastAPI...

cd src

call ..\.venv\Scripts\activate

start "Mini-RAG FastAPI" cmd /k "uvicorn main:app --reload"

cd ..

echo.
echo ================================
echo Docker + FastAPI started!
echo ================================
echo.
echo Swagger: http://127.0.0.1:8000/docs

pause