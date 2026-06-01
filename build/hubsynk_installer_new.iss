; ============================================================
;  HubSynk v2.0 — Inno Setup Script
;
;  PRÉ-REQUISITOS:
;    1. Rodar da RAIZ do repositório (onde está hubsynk.py)
;    2. PyInstaller já gerou: dist\HubSynk.exe
;    3. Arquivos de imagem em assets\
;
;  Compilar: abrir no Inno Setup Compiler → Compile
;  Saída: Output\HubSynk_Setup_v2.0.exe
; ============================================================

[Setup]
AppName=HubSynk
AppVersion=1.0
AppVerName=HubSynk v1.0
AppPublisher=Saulomgg
AppPublisherURL=https://github.com/saulomgg/hubsynk
AppSupportURL=https://github.com/saulomgg/hubsynk/issues
AppUpdatesURL=https://github.com/saulomgg/hubsynk/releases
AppCopyright=Copyright (C) 2026 Saulomgg — MIT License

DefaultDirName={autopf}\HubSynk
DefaultGroupName=HubSynk
AllowNoIcons=yes

OutputDir=Output
OutputBaseFilename=HubSynk_Setup_v1.0
SetupIconFile=assets\app_logo.ico

Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

WizardStyle=modern
WizardImageFile=assets\wizard_image.bmp
WizardSmallImageFile=assets\wizard_small_image.bmp

PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
AppMutex=HubSynkSetupMutex
CloseApplications=yes
CloseApplicationsFilter=HubSynk.exe
RestartApplications=yes
UninstallDisplayIcon={app}\HubSynk.exe
UninstallDisplayName=HubSynk v1.0
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\HubSynk.exe";        DestDir: "{app}"; Flags: ignoreversion
Source: "assets\app_logo.ico";     DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\HubSynk"; Filename: "{app}\HubSynk.exe"; WorkingDir: "{app}"; IconFilename: "{app}\app_logo.ico"; Tasks: desktopicon
Name: "{group}\HubSynk";       Filename: "{app}\HubSynk.exe"; WorkingDir: "{app}"; IconFilename: "{app}\app_logo.ico"
Name: "{group}\Uninstall HubSynk"; Filename: "{uninstallexe}"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\HubSynk.exe"; Description: "&Launch HubSynk"; Flags: postinstall skipifsilent nowait

[UninstallDelete]
; Type: filesandordirs; Name: "{localappdata}\HubSynk"

[Registry]
Root: HKCU; Subkey: "Software\HubSynk"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\HubSynk"; ValueType: string; ValueName: "Version";     ValueData: "2.0"

[Code]
procedure OpenGitHub(Sender: TObject);
var ErrorCode: Integer;
begin
  ShellExec('open', 'https://github.com/saulomgg/hubsynk', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

procedure OpenIssues(Sender: TObject);
var ErrorCode: Integer;
begin
  ShellExec('open', 'https://github.com/saulomgg/hubsynk/issues', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

procedure InitializeWizard;
var
  Page: TWizardPage;
  Memo: TNewMemo;
  LblVersion, LblGitHub, LblIssues: TNewStaticText;
begin
  Page := CreateCustomPage(wpWelcome, 'About HubSynk', 'What is HubSynk?');

  Memo := TNewMemo.Create(Page);
  Memo.Parent := Page.Surface;
  Memo.Left := ScaleX(0); Memo.Top := ScaleY(0);
  Memo.Width := Page.SurfaceWidth; Memo.Height := ScaleY(140);
  Memo.ScrollBars := ssVertical; Memo.ReadOnly := True;
  Memo.Text :=
    'HubSynk v1.0 — Your Essential Windows Productivity Hub' + #13#10 + #13#10 +
    'HubSynk centralizes, organizes and launches all your tools' + #13#10 +
    'from a single, clean interface.' + #13#10 + #13#10 +
    'Features:' + #13#10 +
    '  • Install official .hubsynk packages (signed & verified)' + #13#10 +
    '  • Add any custom .exe or Python script' + #13#10 +
    '  • Download tools directly from GitHub repositories' + #13#10 +
    '  • Cryptographic verification (RSA 4096 + SHA-256)' + #13#10 +
    '  • Favorites, search, Windows 11-inspired interface' + #13#10 + #13#10 +
    'Developed by @saulomg2 — open source, MIT License.' + #13#10 +
    'Thank you for choosing HubSynk!';

  LblVersion := TNewStaticText.Create(Page);
  LblVersion.Parent := Page.Surface;
  LblVersion.Caption := 'Version 2.0  •  MIT License  •  Windows 10+';
  LblVersion.Left := ScaleX(0);
  LblVersion.Top := Memo.Top + Memo.Height + ScaleY(12);

  LblGitHub := TNewStaticText.Create(Page);
  LblGitHub.Parent := Page.Surface;
  LblGitHub.Caption := 'GitHub: https://github.com/saulomgg/hubsynk';
  LblGitHub.Font.Color := clBlue; LblGitHub.Font.Style := [fsUnderline];
  LblGitHub.Cursor := crHand; LblGitHub.OnClick := @OpenGitHub;
  LblGitHub.Left := ScaleX(0);
  LblGitHub.Top := LblVersion.Top + LblVersion.Height + ScaleY(8);

  LblIssues := TNewStaticText.Create(Page);
  LblIssues.Parent := Page.Surface;
  LblIssues.Caption := 'Report a bug or request a feature';
  LblIssues.Font.Color := clBlue; LblIssues.Font.Style := [fsUnderline];
  LblIssues.Cursor := crHand; LblIssues.OnClick := @OpenIssues;
  LblIssues.Left := ScaleX(0);
  LblIssues.Top := LblGitHub.Top + LblGitHub.Height + ScaleY(6);
end;
