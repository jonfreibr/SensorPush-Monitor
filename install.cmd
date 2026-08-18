@echo off
setlocal enabledelayedexpansion
title Install SensorPush Monitor
echo Sourcing from: %~dp0

set "TARGET_VER=3.14.3"
set "PYTHON_SOURCE_DIR=Python314"

if "%SENSORPUSH_USER%" == "" (call setuser.bat)

:: Prevent early exit on errors
set "ERRORFLAG=0"

echo Checking for existing Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found.
    set "INSTALL=TRUE"
) else (
    for /f "tokens=2 delims= " %%a in ('python --version 2^>^&1') do set "VERSION=%%a"
    if !VERSION! equ !TARGET_VER! (
	echo Python %TARGET_VER% already installed
        set "PYTHON_PATH=%LocalAppData%\Programs\Python\%PYTHON_SOURCE_DIR%\python.exe"
	set "INSTALL=FALSE"
    ) else (
	echo Python !VERSION! installed. Installing required version %TARGET_VER%
	set "INSTALL=TRUE"
    )
)

if "%INSTALL%" equ "TRUE" (
	"%~dp0\python-%TARGET_VER%-amd64.exe" /passive
	set "PYTHON_PATH=%LocalAppData%\Programs\Python\%PYTHON_SOURCE_DIR%\python.exe"
)

set "PROJECT_DIR=%USERPROFILE%\SPM"
set "VENV_DIR=%PROJECT_DIR%\venv"

::==========

:: Determine where the Desktop directory is located!!! It's NOT always %USERPROFILE%\Desktop !!!

:: Define your target registry key and value name
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
set "REG_VALUE=Desktop"

:: Extract the value data
for /f "tokens=2*" %%A in ('reg query "%REG_KEY%" /v "%REG_VALUE%" 2^>nul') do (
    set "REG_DATA=%%B"
)

:: Verify and use your variable
if defined REG_DATA (
    set "DESKTOP_DIR=%REG_DATA%"
) else (
    set "DESKTOP_DIR=%USERPROFILE%\Desktop"
)
:: Expand the variables!
call set "DESKTOP_DIR=%DESKTOP_DIR%"

:: End of Desktop location determination

::==========

echo Creating project folder...
if not exist "%PROJECT_DIR%" md "%PROJECT_DIR%"

echo Creating virtual environment...
call "%PYTHON_PATH%" -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    set "ERRORFLAG=1"
    goto :END
)
echo Virtual environment created at: %VENV_DIR%

echo Activating virtual environment and upgrading pip...
call "%VENV_DIR%\Scripts\activate.bat"
call python -m pip install --upgrade pip

if exist "%~dp0\requirements.txt" (
    echo Installing required Python packages in venv...
    call python -m pip install -r "%~dp0\requirements.txt" --upgrade
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies.
        set "ERRORFLAG=1"
        goto :END
    )
) else (
    echo No requirements.txt found — skipping dependency install.
)

echo Copying files
copy /y "%~dp0\spm.py" %PROJECT_DIR%
copy /y "%~dp0\sensorpush-icon.ico" %PROJECT_DIR%
echo Finished copying files

echo Deactivating virtual environment...
call deactivate

echo Creating desktop shortcut...
set "SHORTCUT_PATH=%DESKTOP_DIR%\SensorPush Monitor.lnk"
set "TARGET_PATH=%PROJECT_DIR%\spm.py"
set "WORKING_DIR=%PROJECT_DIR%"
set "ICON_PATH=%PROJECT_DIR%\sensorpush-icon.ico"

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command ^
  "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%');" ^
  "$s.TargetPath='%VENV_DIR%\Scripts\pythonw.exe';" ^
  "$s.Arguments='\"%TARGET_PATH%\"';" ^
  "$s.WorkingDirectory='%WORKING_DIR%';" ^
  "if (Test-Path '%ICON_PATH%') {$s.IconLocation='%ICON_PATH%'};" ^
  "$s.Save()"
  echo Shortcut created successfully.

:END
if %ERRORFLAG% neq 0 (
    echo.
    echo ===============================
    echo   INSTALLATION FAILED 
    echo ===============================
    pause
) else (
    echo.
    echo ===============================
    echo   INSTALLATION COMPLETE 
    echo ===============================
    timeout /t 5
)
