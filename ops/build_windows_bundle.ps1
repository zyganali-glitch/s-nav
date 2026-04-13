param(
    [string]$PythonExe = '.\.venv\Scripts\python.exe',
    [string]$OutputFolder = '.\dist\windows-bundle'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$python = Resolve-Path $PythonExe
& $python -m pip install pyinstaller

if (Test-Path -LiteralPath $OutputFolder) {
    Remove-Item -LiteralPath $OutputFolder -Recurse -Force
}

$pyInstallerArgs = @(
    '-m',
    'PyInstaller',
    '--noconfirm',
    '--onedir',
    '--name',
    'SinavOkumaPlatformu',
    '--add-data',
    'frontend;frontend',
    '--add-data',
    'backend/data;backend/data',
    '--add-data',
    'optik_kagit_formatlari;optik_kagit_formatlari',
    '--add-data',
    'ops/sr3500_vendor_probe_x86.cs;ops',
    'backend/run_local_server.py'
)

& $python @pyInstallerArgs

New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null
Copy-Item -Path '.\dist\SinavOkumaPlatformu\*' -Destination $OutputFolder -Recurse -Force
Copy-Item -Path '.\ops\watch_vendor_export.ps1' -Destination $OutputFolder -Force
Copy-Item -Path '.\ops\probe_secure_pc_reader.ps1' -Destination $OutputFolder -Force
Copy-Item -Path '.\ops\start_runtime_from_config.ps1' -Destination $OutputFolder -Force
Copy-Item -Path '.\ops\secure_pc_config.template.json' -Destination $OutputFolder -Force

Write-Output ("Windows bundle created in: {0}" -f (Resolve-Path $OutputFolder))