#ifndef AppVersion
  #define AppVersion "1.0.1"
#endif
#define AppName "Chrome Hop"
#define HostName "io.github.aspendesign.chrome_hop"
#define AddonID "chrome-hop@aspendesign.github.io"

[Setup]
AppId={{811C254E-68FA-4C2D-B271-91EC8EA8731F}
AppName={#AppName} Windows Helper
AppVersion={#AppVersion}
AppPublisher=aspendesign
AppPublisherURL=https://github.com/aspendesign/chrome-hop
AppSupportURL=https://github.com/aspendesign/chrome-hop/issues
AppUpdatesURL=https://github.com/aspendesign/chrome-hop/releases
DefaultDirName={localappdata}\Programs\Chrome Hop
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.22000
OutputDir=..\dist
OutputBaseFilename=ChromeHop-Setup-{#AppVersion}-windows-x64
SetupIconFile=..\assets\chrome-hop.ico
UninstallDisplayIcon={app}\chrome-hop.exe
LicenseFile=..\LICENSE
InfoBeforeFile=install-info.txt
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=no
CloseApplications=no
RestartApplications=no
SetupLogging=no
Uninstallable=yes
UninstallFilesDir={app}
AppMutex=ChromeHopInstaller

[Files]
Source: "..\.local\build\chrome-hop.exe"; DestDir: "{app}"; Flags: ignoreversion notimestamp
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion notimestamp
Source: "..\docs\INSTALL.md"; DestDir: "{app}"; Flags: ignoreversion notimestamp

[Registry]
Root: HKCU; Subkey: "Software\Mozilla\NativeMessagingHosts\{#HostName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#HostName}.json"; Flags: uninsdeletekey

[UninstallDelete]
Type: files; Name: "{app}\{#HostName}.json"

[Messages]
WelcomeLabel2=This helper connects the Chrome Hop Firefox toolbar button to Google Chrome.%n%nIt installs for your Windows account only. No administrator access, background service, runtime download, or browser setting change is needed.%n%nInstall the Chrome Hop Firefox add-on separately from Mozilla Add-ons.
FinishedLabel=Chrome Hop is ready for your Windows account.%n%nReturn to a web page in Firefox and click the Chrome Hop toolbar button. If you have not installed the Firefox add-on yet, follow the instructions in the release page.%n%nGoogle Chrome Stable must be installed in its normal Windows location.

[Code]
function JSONPath(Value: String): String;
begin
  StringChangeEx(Value, '\', '\\', True);
  StringChangeEx(Value, '"', '\"', True);
  Result := Value;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Manifest, Path: String;
begin
  if CurStep = ssPostInstall then begin
    Path := ExpandConstant('{app}\{#HostName}.json');
    Manifest := '{' + #13#10 +
      '  "name": "{#HostName}",' + #13#10 +
      '  "description": "Chrome Hop: open one HTTP(S) URL in Google Chrome",' + #13#10 +
      '  "path": "' + JSONPath(ExpandConstant('{app}\chrome-hop.exe')) + '",' + #13#10 +
      '  "type": "stdio",' + #13#10 +
      '  "allowed_extensions": ["{#AddonID}"]' + #13#10 + '}';
    if not SaveStringToFile(Path, UTF8Encode(Manifest), False) then
      RaiseException('Could not write Chrome Hop connection information. Run Setup again to repair it.');
  end;
end;
