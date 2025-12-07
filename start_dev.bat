@echo off
echo Starting Data Analyst Agent Environment...

:: Check if MongoDB is running (simple check if we can connect, optional, or just warn)
echo Ensure MongoDB is running on localhost:27017

:: Start Backend
echo Starting Backend...
start "Backend Server" cmd /k "cd backend && call venv\Scripts\activate && uvicorn server:app --reload --host 0.0.0.0 --port 8000"

:: Start Frontend
echo Starting Frontend...
start "Frontend App" cmd /k "cd frontend && npm start"

echo.
echo Integration Complete!
echo Backend running at http://localhost:8000
echo Frontend running at http://localhost:3000
echo.
pause
