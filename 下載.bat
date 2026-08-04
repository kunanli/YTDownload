@echo off
REM Thin launcher. All menu text lives in Python (ytmusic/menu.py) because
REM cmd.exe mangles UTF-8 batch files. Keep this file pure ASCII.
REM
REM Everything here is first-run setup. Once Python and the package are in
REM place this file just starts the menu and gets out of the way.
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
cd /d "%~dp0"

REM --------------------------------------------------------------------
REM Step 1: find a Python that actually RUNS.
REM
REM "where python" is not enough. Windows ships an App Execution Alias at
REM %LOCALAPPDATA%\Microsoft\WindowsApps\python.exe that IS on PATH but only
REM prints "Python was not found..." when you run it. Checking the name gave
REM a false positive and setup failed one step later with a confusing error.
REM So: run each candidate and keep the first one that really works.
REM --------------------------------------------------------------------
set "PY="
for %%C in ("py -3" "py" "python" "python3") do (
  if not defined PY (
    %%~C -c "import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
    if not errorlevel 1 set "PY=%%~C"
  )
)

if not defined PY (
  for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if not defined PY if exist "%%~D\python.exe" (
      "%%~D\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
      if not errorlevel 1 set "PY=%%~D\python.exe"
    )
  )
)

if not defined PY goto :install_python

REM --------------------------------------------------------------------
REM Step 2: make sure the package itself is installed.
REM --------------------------------------------------------------------
%PY% -c "import ytmusic" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   [SETUP] First run - installing the downloader and its dependencies...
  echo   This takes a minute. You only have to do it once.
  echo.
  %PY% -m pip install -e .
  if errorlevel 1 (
    echo.
    echo   [ERROR] Install failed.
    echo.
    echo   Try these two lines by hand in this window:
    echo       %PY% -m ensurepip --upgrade
    echo       %PY% -m pip install -e .
    echo.
    echo   If it mentions a proxy or SSL, you are probably behind a company
    echo   network. Try again on a home network or a phone hotspot.
    echo.
    pause
    exit /b 3
  )
  echo.
  echo   [SETUP] Done.
  echo.
)

REM --------------------------------------------------------------------
REM Step 3: hand over to Python. Anything still missing (ffmpeg, mutagen,
REM curl_cffi) is checked there, in the user's own language.
REM --------------------------------------------------------------------
%PY% -m ytmusic menu
if errorlevel 1 (
  echo.
  echo   [ERROR] Something went wrong. See the message above.
  echo.
  pause
)
exit /b 0


REM ====================================================================
REM No working Python. Walk the user through it instead of just failing.
REM ====================================================================
:install_python
echo.
echo   ================================================
echo      Setup - step 1 of 2:  install Python
echo   ================================================
echo.

REM The Store alias is the most common trap: the name resolves, the program
REM does not run. Say so explicitly, or people insist "but I have Python".
where python >nul 2>&1
if not errorlevel 1 (
  echo   NOTE: Windows has a placeholder called "python" that is not a real
  echo   Python. That is why you may have seen:
  echo       "Python was not found; run without arguments to install from
  echo        the Microsoft Store"
  echo   Installing the real thing below fixes it.
  echo.
)

where winget >nul 2>&1
if errorlevel 1 goto :manual_python

echo   I can install it for you now with winget.
echo   Nothing else on your computer is touched.
echo.
set "ANSWER="
set /p "ANSWER=  Install Python 3.12 now? [Y/n] "
if /i "!ANSWER!"=="n" goto :manual_python

echo.
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
if errorlevel 1 (
  echo.
  echo   winget could not install it.
  goto :manual_python
)

echo.
echo   ================================================
echo      Setup - step 2 of 2:  reopen this window
echo   ================================================
echo.
echo   Python is installed, but THIS window still does not know where it is.
echo.
echo     1. Close this window.
echo     2. Double-click the same file again.
echo.
echo   That is it - the rest is automatic.
echo.
pause
exit /b 0

:manual_python
echo.
echo   Install Python by hand:
echo.
echo     1. Open  https://www.python.org/downloads/
echo     2. Click the big yellow "Download Python" button.
echo     3. Run the installer. On the FIRST screen, tick
echo            [x] Add python.exe to PATH
echo        It is at the bottom and easy to miss. Then click "Install Now".
echo     4. Close this window and double-click the same file again.
echo.
echo   If you keep seeing "Python was not found", turn off the Store
echo   placeholder:  Settings ^> Apps ^> Advanced app settings ^>
echo   App execution aliases  ^-  switch off both "python" entries.
echo.
pause
exit /b 3
