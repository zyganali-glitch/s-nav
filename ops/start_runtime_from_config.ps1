param(
    [string]$ConfigPath = 'C:\SecureExam\secure_pc_config.json'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$env:SINAV_OKUMA_HOST = [string]$config.app.host
$env:SINAV_OKUMA_PORT = [string]$config.app.port
$dataDir = Join-Path $config.paths.root 'data'
if (-not (Test-Path -LiteralPath $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
}
$env:SINAV_OKUMA_STATE_FILE = Join-Path $dataDir 'app_state.json'

$bundleExe = $config.app.bundleExe
if (-not (Test-Path -LiteralPath $bundleExe)) {
    throw ("Bundle exe bulunamadi: {0}" -f $bundleExe)
}

Write-Output ("Runtime starting: {0}" -f $bundleExe)
& $bundleExe