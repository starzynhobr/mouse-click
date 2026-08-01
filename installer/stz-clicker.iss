; Inno Setup script for STZ Clicker.
; Build the standalone payload first (see build.ps1), then compile with:
;   & "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" installer\stz-clicker.iss

#define AppName "STZ Clicker"
#define AppVersion "1.1.0"
#define AppPublisher "STZ Labs"
#define AppExeName "STZ Clicker.exe"
#define SourceDir "..\dist\standalone\gui.dist"

[Setup]
AppId={{8F3C1E27-9B4D-4A6E-B0C5-2D7A1F5E9C34}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\STZ Labs\{#AppName}
DefaultGroupName=STZ Labs
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputDir=..\dist
OutputBaseFilename=STZ Clicker Setup {#AppVersion}
SetupIconFile=..\assets\stz-clicker.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
; The WH_MOUSE_LL hook needs elevation to see input aimed at elevated windows,
; so both the installer and the app itself run as administrator.
PrivilegesRequired=admin

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent runascurrentuser

; Settings in %APPDATA%\STZClicker are deliberately left in place on uninstall:
; this is a machine-wide (admin) install, so {userappdata} would resolve to
; whoever ran the uninstaller rather than to each user who used the app.
