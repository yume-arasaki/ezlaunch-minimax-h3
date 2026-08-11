@echo off
REM Start ComfyUI only (after first full install). Ships t2v / i2v / ref2v workflows.
setlocal EnableExtensions
cd /d "%~dp0\.."

set "PY=python"
where py >nul 2>&1 && set "PY=py -3"

set "PYTHONPATH=%CD%;%PYTHONPATH%"
set "HF_HUB_DISABLE_SYMLINKS=1"

echo.
echo  EZlaunch comfy-up  (t2v / i2v / ref2v)
echo  =====================================
echo.

%PY% -m ezlaunch --launch %*
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
  echo.
  echo [ERROR] comfy-up failed with code %ERR%
  echo If you have not installed yet, double-click EZlaunch.bat first.
  echo See docs\TROUBLESHOOTING.md
  pause
)
endlocal & exit /b %ERR%
