<#
.SYNOPSIS
    Launches the Harness Utils Windows Script Installer GUI.
.DESCRIPTION
    Scans the script directory, opens the Tkinter graphical installer wizard,
    allowing users to select scripts, add new custom scripts, and install them to PATH.
#>

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Launching Harness Utils Installer" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

# Check if python is available
if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m harness_utils.cli install-scripts --script-dir "$ScriptDir" --gui
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    py -m harness_utils.cli install-scripts --script-dir "$ScriptDir" --gui
} else {
    Write-Error "Python is required to run the Harness Utils Installer."
}
