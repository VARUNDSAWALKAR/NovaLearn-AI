@echo off
setlocal
cd /d "%~dp0"
echo =======================================
echo    NovaLearn AI - UNLOX Mini Project
 echo =======================================
if not exist "app.py" (
  echo ERROR: app.py not found. Extract the entire ZIP first.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating isolated Python 3.11 environment...
  py -3.11 -m venv .venv
  if errorlevel 1 (
    echo Could not create Python 3.11 environment. Install Python 3.11 and retry.
    pause
    exit /b 1
  )
)
echo Installing or updating dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. See errors above.
  pause
  exit /b 1
)
echo Opening NovaLearn in your browser...
".venv\Scripts\python.exe" -m streamlit run app.py
pause
