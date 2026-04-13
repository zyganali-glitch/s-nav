param(
    [int]$DurationSeconds = 120,
    [string]$OutputPath = 'C:\SecureExam\probe-output\sr3500-live-trace.log'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
$scriptPath = Join-Path $PSScriptRoot 'trace_sr3500_input.py'

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw ("Python bulunamadi: {0}" -f $pythonExe)
}

if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw ("Trace scripti bulunamadi: {0}" -f $scriptPath)
}

& $pythonExe $scriptPath --duration $DurationSeconds --output $OutputPath
