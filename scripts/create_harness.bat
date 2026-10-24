@echo off
REM ==============================================================================
REM Script: create_harness.bat
REM Description: Windows CMD launcher to generate Python harness files
REM Usage: create_harness.bat [PROJECT_NAME] [TARGET_DIR]
REM Example: create_harness.bat my_app C:\Projects\my_app
REM ==============================================================================

setlocal

set PROJECT_NAME=%~1
if "%PROJECT_NAME%"=="" set PROJECT_NAME=my_python_app

set TARGET_DIR=%~2
if "%TARGET_DIR%"=="" set TARGET_DIR=.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_harness.ps1" -ProjectName "%PROJECT_NAME%" -TargetDir "%TARGET_DIR%"

endlocal
