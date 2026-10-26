[Setup]
AppId={{A714219E-8072-4B94-B9D1-3047148F132C}
AppName=Imag to Text
AppVersion=1.0.0
AppPublisher=nestorantropos-stack
AppPublisherURL=https://github.com/nestorantropos-stack/imag-to-text
DefaultDirName={localappdata}\Programs\Imag to Text
DefaultGroupName=Imag to Text
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=dist
OutputBaseFilename=Imag-to-Text-Setup-1.0.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\runtime\pythonw.exe
DisableProgramGroupPage=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; Flags: checkedonce

[Files]
Source: "dist\ImagToText-Runtime\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Imag to Text"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"
Name: "{autodesktop}\Imag to Text"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\app.py"""; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\app.py"""; Description: "Abrir Imag to Text"; Flags: nowait postinstall skipifsilent
