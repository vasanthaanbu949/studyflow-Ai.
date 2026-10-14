@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo       StudyFlow AI - Smart Study Planner
echo ==========================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or newer from https://www.python.org/downloads/
  echo During setup, select "Add Python to PATH".
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating a project environment...
  python -m venv .venv
)
call ".venv\Scripts\activate.bat"
echo Installing required packages (first run only)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Package installation failed. Check your internet connection and try again.
  pause
  exit /b 1
)
echo.
echo ------------------------------------------------------------
echo  TO OPEN ON YOUR PHONE (Android or iPhone):
echo  1. Connect the phone to the SAME Wi-Fi as this computer.
echo  2. In the phone browser, open  http://YOUR-IPV4-ADDRESS:8501
echo     Your computer's IPv4 address is listed below:
ipconfig | findstr /c:"IPv4"
echo  3. If Windows asks, allow Python through the firewall (Private networks).
echo ------------------------------------------------------------
echo.
python make_qr.py
if exist phone_qr.png start "" phone_qr.png
echo Starting StudyFlow AI...
python -m streamlit run app.py --server.address 0.0.0.0
pause
