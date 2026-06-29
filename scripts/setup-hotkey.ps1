<#
  Bind a global Windows hotkey to the one-key ATS launcher (scripts\ats-clip.cmd).

  Creates a Start-Menu shortcut whose HotKey property Windows registers globally.
  Run in a normal PowerShell session (not as SYSTEM):

      powershell -ExecutionPolicy Bypass -File scripts\setup-hotkey.ps1
      powershell -ExecutionPolicy Bypass -File scripts\setup-hotkey.ps1 -HotKey "CTRL+ALT+J"

  Then copy a job description anywhere and press the hotkey.
  Remove it later by deleting the shortcut printed below.
#>
param([string]$HotKey = "CTRL+ALT+1")
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $PSScriptRoot "ats-clip.cmd"
if (-not (Test-Path $launcher)) { throw "Launcher not found: $launcher" }

$programs = [Environment]::GetFolderPath("Programs")
$lnk = Join-Path $programs "ATS Resume.lnk"

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($lnk)
$sc.TargetPath = $launcher
$sc.WorkingDirectory = $root
$sc.WindowStyle = 7              # minimized
$sc.HotKey = $HotKey
$sc.Description = "ATS Resume - generate from clipboard JD"
$sc.Save()

Write-Output "Created shortcut: $lnk"
Write-Output "Global hotkey:    $HotKey   (copy a JD, then press it)"
Write-Output "To remove:        Remove-Item `"$lnk`""