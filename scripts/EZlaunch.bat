@echo off
REM Double-click entrypoint for Windows (keep window open on errors)
setlocal EnableExtensions
cd /d "%~dp0\.."

echo.
echo  EZlaunch MiniMax-H3
echo  ===================
echo.

REM Prefer the `py` launcher (more reliable on Windows than bare `python`;
REM also avoids the Microsoft Store "python" stub that opens the Store)
set "PY=python"
where py >nul 2>&1 && set "PY=py -3"

REM Refuse Microsoft Store app-execution-alias stubs early
%PY% -c "import sys; p=sys.executable.lower().replace('/','\\'); raise SystemExit(2 if 'windowsapps' in p else (0 if sys.version_info>=(3,10) else 1))" >nul 2>&1
if errorlevel 2 (
  echo [ERROR] Microsoft Store Python stub detected — not a real CPython.
  echo.
  echo Fix:
  echo  1. Settings -^> Apps -^> App execution aliases
  echo  2. Turn OFF python.exe and python3.exe
  echo  3. Install 64-bit Python 3.10-3.12 from python.org
  echo  4. Tick "Add python.exe to PATH", open a NEW window, re-run this file
  echo.
  echo See docs\TROUBLESHOOTING.md  "Microsoft Store Python"
  echo.
  pause
  exit /b 1
)
if errorlevel 1 (
  echo [ERROR] Python 3.10+ 64-bit is required.
  echo.
  echo 1. Download Python from https://www.python.org/downloads/windows/
  echo 2. During setup, tick "Add python.exe to PATH"
  echo 3. Choose the 64-bit installer (not the Microsoft Store app)
  echo 4. Close this window, open a NEW one, run EZlaunch.bat again
  echo.
  echo Tip: after install, "py -3 --version" should work.
  echo.
  pause
  exit /b 1
)

REM Make sure this repo is importable without a global pip install
set "PYTHONPATH=%CD%;%PYTHONPATH%"
REM Hugging Face: avoid Windows symlink / Developer Mode pain
set "HF_HUB_DISABLE_SYMLINKS=1"

echo Installing tiny launcher libraries if needed...
%PY% -m pip install -q pyyaml "huggingface_hub>=0.23" requests
if errorlevel 1 (
  echo [ERROR] pip install failed. Try:  %PY% -m pip install --upgrade pip
  echo Then re-run this file.
  pause
  exit /b 1
)

echo Starting EZlaunch...
%PY% -m ezlaunch %*
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] EZlaunch exited with code %ERR%
  echo See the messages above. Common fixes are in docs\TROUBLESHOOTING.md
  pause
)
endlocal & exit /b %ERR%
