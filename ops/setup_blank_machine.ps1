param(
    [string]$BaseFolder = 'C:\SecureExam',
    [string]$ConfigTemplatePath = '.\ops\secure_pc_config.template.json',
    [string]$ConfigOutputPath = '',
    [string]$ExamCode = 'TEKKITAPCIK'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

if (-not $ConfigOutputPath) {
    $ConfigOutputPath = Join-Path $BaseFolder 'secure_pc_config.json'
}

Ensure-Directory -Path $BaseFolder

$config = Get-Content -LiteralPath $ConfigTemplatePath -Raw | ConvertFrom-Json
$config.paths.root = $BaseFolder
$config.paths.incoming = Join-Path $BaseFolder 'incoming'
$config.paths.processed = Join-Path $config.paths.incoming '_processed'
$config.paths.error = Join-Path $config.paths.incoming '_error'
$config.paths.probeOutput = Join-Path $BaseFolder 'probe-output'
$config.paths.runtime = Join-Path $BaseFolder 'runtime'
$config.paths.logs = Join-Path $BaseFolder 'logs'
$config.app.bundleExe = Join-Path $config.paths.runtime 'SinavOkumaPlatformu.exe'
$config.bridge.examCode = $ExamCode.Trim().ToUpperInvariant()

Ensure-Directory -Path $config.paths.incoming
Ensure-Directory -Path $config.paths.processed
Ensure-Directory -Path $config.paths.error
Ensure-Directory -Path $config.paths.probeOutput
Ensure-Directory -Path $config.paths.runtime
Ensure-Directory -Path $config.paths.logs

$config | ConvertTo-Json -Depth 5 | Set-Content -Path $ConfigOutputPath -Encoding UTF8

Write-Output ("Config written: {0}" -f $ConfigOutputPath)
Write-Output ("Incoming folder: {0}" -f $config.paths.incoming)
Write-Output ("Probe output: {0}" -f $config.paths.probeOutput)