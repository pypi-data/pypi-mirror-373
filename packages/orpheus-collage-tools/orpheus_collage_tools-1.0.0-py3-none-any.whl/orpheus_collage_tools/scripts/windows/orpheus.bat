@echo off
REM Orpheus Collage Tools - Windows Batch Launcher
REM This batch file is used when the package is installed via pip on Windows

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "PACKAGE_DIR=%SCRIPT_DIR%..\..\..\.."

REM Set Python path to include the lib directory
set "PYTHONPATH=%PACKAGE_DIR%lib;%PYTHONPATH%"

REM Run the Python CLI with all arguments passed to this batch file
python -m orpheus_collage_tools.cli %*

endlocal
