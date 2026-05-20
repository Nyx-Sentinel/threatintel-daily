; ThreatIntel Daily Windows Installer
; Built with NSIS 3.x
; Download NSIS from: https://nsis.sourceforge.io

!include "MUI2.nsh"

; Basic settings
Name "ThreatIntel Daily v0.1.0"
OutFile "ThreatIntel-Daily-Setup.exe"
InstallDir "$PROGRAMFILES\ThreatIntel Daily"
RequestExecutionLevel admin

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy application files
  File /r "dist\ThreatIntel Daily\*.*"
  
  ; Copy config example
  File "config.example.yml"
  File "README.md"
  File "LICENSE"
  
  ; Create start menu shortcuts
  CreateDirectory "$SMPROGRAMS\ThreatIntel Daily"
  CreateShortcut "$SMPROGRAMS\ThreatIntel Daily\ThreatIntel Daily.lnk" "$INSTDIR\ThreatIntel Daily.exe"
  CreateShortcut "$SMPROGRAMS\ThreatIntel Daily\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
  ; Create desktop shortcut
  CreateShortcut "$DESKTOP\ThreatIntel Daily.lnk" "$INSTDIR\ThreatIntel Daily.exe"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ThreatIntel Daily" "DisplayName" "ThreatIntel Daily v0.1.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ThreatIntel Daily" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ThreatIntel Daily" "DisplayVersion" "0.1.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ThreatIntel Daily" "Publisher" "Alphonse"
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove shortcuts
  Delete "$SMPROGRAMS\ThreatIntel Daily\ThreatIntel Daily.lnk"
  Delete "$SMPROGRAMS\ThreatIntel Daily\Uninstall.lnk"
  RMDir "$SMPROGRAMS\ThreatIntel Daily"
  Delete "$DESKTOP\ThreatIntel Daily.lnk"
  
  ; Remove application files
  RMDir /r "$INSTDIR"
  
  ; Remove registry entries
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ThreatIntel Daily"
SectionEnd
