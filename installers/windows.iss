#ifndef AppVersion
  #define AppVersion "0.2.1"
#endif

[Setup]
AppId={{F18114CF-2382-40BD-98D2-C691D173BFF4}
AppName=QuietShot
AppVersion={#AppVersion}
AppPublisher=QuietShot contributors
AppPublisherURL=https://github.com/teremno/quietshot
DefaultDirName={localappdata}\Programs\QuietShot
DefaultGroupName=QuietShot
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=QuietShot-{#AppVersion}-Windows-x64-Setup
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\QuietShot.exe

[Files]
Source: "..\dist\QuietShot\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\QuietShot"; Filename: "{app}\QuietShot.exe"
Name: "{userdesktop}\QuietShot"; Filename: "{app}\QuietShot.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\QuietShot.exe"; Description: "Launch QuietShot"; Flags: nowait postinstall skipifsilent
