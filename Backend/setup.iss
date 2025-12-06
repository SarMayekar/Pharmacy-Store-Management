; Script generated for Astitva Drug House
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Astitva Drug House"
#define MyAppVersion "1.0"
#define MyAppPublisher "Astitva Drug House"
#define MyAppExeName "AstitvaDrugHouse.exe"
#define MyUpdaterName "AstitvaUpdater.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{8A9B3C2D-1234-5678-9ABC-DEF123456789}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; This ensures the app installs for the current user or all users correctly
PrivilegesRequired=lowest
OutputDir=E:\ASTITVA-DRUG-HOUSE\Installer_Output
OutputBaseFilename=AstitvaDrugHouse_Setup_v1.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT: Check that this path matches your actual folder structure!
Source: "E:\ASTITVA-DRUG-HOUSE\Backend\dist\AstitvaDrugHouse\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
; Create Shortcut in Start Menu
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Create Shortcut on Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Launch the app after installation finishes
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
