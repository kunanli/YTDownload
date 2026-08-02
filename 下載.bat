@echo off
REM Thin launcher. All menu text lives in Python (ytmusic/menu.py) because
REM cmd.exe mangles UTF-8 batch files. Keep this file pure ASCII.
chcp 65001 >nul 2>&1
cd /d "%~dp0"

set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py"

if not defined PY (
  echo.
  echo   [ERROR] Python not found.
  echo   Install it first:  winget install Python.Python.3.12
  echo   Then close this window, open a new one, and try again.
  echo.
  pause
  exit /b 3
)

"%PY%" -m ytmusic menu
if errorlevel 1 (
  echo.
  echo   [ERROR] Something went wrong. See the message above.
  echo.
  pause
)
exit /b 0
