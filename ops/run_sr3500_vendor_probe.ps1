param(
    [string]$SdkBin = 'C:\SecureExam\vendor-media\English\English\API Library\Bin',
    [ValidateSet('probe', 'mark-once', 'mark-batch')]
    [string]$Action = 'probe',
    [string]$OutputPath = '',
    [int]$MaxSheets = 0,
    [int]$Columns = 48,
    [int]$ReadingMethod = 3,
    [int]$ThicknessType = 0,
    [switch]$BacksideReading
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourcePath = Join-Path $PSScriptRoot 'sr3500_vendor_probe_x86.cs'
$buildDir = Join-Path $repoRoot 'build\sr3500-vendor-probe'
$exePath = Join-Path $buildDir 'sr3500_vendor_probe_x86.exe'
$cscPath = 'C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe'

New-Item -ItemType Directory -Path $buildDir -Force | Out-Null

if (-not (Test-Path $cscPath)) {
    throw "C# compiler not found at $cscPath"
}

& $cscPath /nologo /target:exe /platform:x86 /out:$exePath $sourcePath
if ($LASTEXITCODE -ne 0) {
    throw "Compilation failed with exit code $LASTEXITCODE"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $buildDir 'last-mark-read.txt'
}

& $exePath $SdkBin $Action $OutputPath $MaxSheets $Columns $ReadingMethod $ThicknessType $(if ($BacksideReading) { 1 } else { 0 })
exit $LASTEXITCODE