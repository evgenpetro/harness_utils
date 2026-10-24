@echo off
REM ==============================================================================
REM Script: install_scripts.bat
REM Description: Windows launcher for Harness Utils Script Installer GUI
REM Usage: install_scripts.bat
REM ==============================================================================

setlocal

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_scripts.ps1"

endlocal
