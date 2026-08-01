# Builds the one-file "STZ Clicker.exe" with Nuitka.
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"

python -m nuitka `
    --onefile `
    --windows-console-mode=disable `
    --enable-plugin=tk-inter `
    --include-package=customtkinter `
    --include-data-dir=assets=assets `
    --windows-icon-from-ico=assets/stz-clicker.ico `
    --company-name="StarzynhoBR" `
    --product-name="STZ Clicker" `
    --file-description="STZ Clicker - auto clicker" `
    --output-filename="STZ Clicker.exe" `
    --output-dir=dist `
    --assume-yes-for-downloads `
    gui.py

Write-Host "Build finished: dist/STZ Clicker.exe"
