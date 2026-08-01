# Builds the STZ Clicker release artifacts.
#   .\build.ps1            -> installer + portable exe
#   .\build.ps1 -Portable  -> portable one-file exe only
#   .\build.ps1 -Installer -> standalone build + Inno Setup installer only

param(
    [switch]$Portable,
    [switch]$Installer
)

$ErrorActionPreference = "Stop"

if (-not $Portable -and -not $Installer) {
    $Portable = $true
    $Installer = $true
}

$common = @(
    "--windows-console-mode=disable",
    "--enable-plugin=tk-inter",
    "--include-package=customtkinter",
    "--include-data-dir=assets=assets",
    "--windows-icon-from-ico=assets/stz-clicker.ico",
    "--company-name=STZ Labs",
    "--product-name=STZ Clicker",
    "--file-description=STZ Clicker - auto clicker",
    "--product-version=1.1.0",
    "--output-filename=STZ Clicker.exe",
    "--assume-yes-for-downloads"
)

if ($Portable) {
    Write-Host "Building portable one-file executable..."
    python -m nuitka --onefile @common --output-dir=dist gui.py
    Write-Host "-> dist\STZ Clicker.exe"
}

if ($Installer) {
    # The installed build is standalone (no per-launch unpacking) and carries an
    # admin manifest, since WH_MOUSE_LL cannot see input aimed at elevated windows
    # from a non-elevated process.
    Write-Host "Building standalone payload..."
    python -m nuitka --standalone --windows-uac-admin @common --output-dir=dist/standalone gui.py

    $iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (-not (Test-Path $iscc)) {
        throw "Inno Setup 6 not found at $iscc. Install it from https://jrsoftware.org/isdl.php"
    }

    Write-Host "Compiling installer..."
    & $iscc "installer\stz-clicker.iss"
    Write-Host "-> dist\STZ Clicker Setup 1.1.0.exe"
}
