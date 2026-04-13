param(
    [string]$OutputRoot = 'C:\SecureExam\driver-recovery',
    [string[]]$Patterns = @('VID_0A41', 'VID_0461', 'Optical Mark Reader', 'Sekonic', 'SR-3500')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-UninstallEntries {
    $paths = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )

    foreach ($path in $paths) {
        Get-ItemProperty -Path $path -ErrorAction SilentlyContinue |
            Where-Object { $_.PSObject.Properties.Name -contains 'DisplayName' -and $_.DisplayName } |
            Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation
    }
}

if (-not (Get-Command pnputil.exe -ErrorAction SilentlyContinue)) {
    throw 'pnputil.exe bulunamadi.'
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$sessionRoot = Join-Path $OutputRoot ("sr3500-driver-export-" + $timestamp)
$exportDir = Join-Path $sessionRoot 'exported-drivers'
$reportPath = Join-Path $sessionRoot 'report.txt'
$jsonPath = Join-Path $sessionRoot 'report.json'
$setupApiPath = Join-Path $sessionRoot 'setupapi-hints.txt'

New-Item -ItemType Directory -Path $exportDir -Force | Out-Null

$regex = [string]::Join('|', ($Patterns | ForEach-Object { [Regex]::Escape($_) }))
$candidateInfs = @()

Get-ChildItem 'C:\Windows\INF' -Filter 'oem*.inf' -File | ForEach-Object {
    try {
        $raw = Get-Content -LiteralPath $_.FullName -Raw -ErrorAction Stop
        if ($raw -match $regex) {
            $matched = @($Patterns | Where-Object { $raw -match [Regex]::Escape($_) })
            $candidateInfs += [pscustomobject]@{
                InfName = $_.Name
                FullPath = $_.FullName
                MatchedPatterns = $matched
            }
        }
    }
    catch {
    }
}

$installedPrograms = @(Get-UninstallEntries | Where-Object {
    $_.DisplayName -match 'Sekonic|SR-3500|Optical Mark|OMR'
})

$setupApiHints = @()
if (Test-Path -LiteralPath 'C:\Windows\INF\setupapi.dev.log') {
    $setupApiHints = @(Select-String -Path 'C:\Windows\INF\setupapi.dev.log' -Pattern $Patterns -SimpleMatch -Context 0,2 -ErrorAction SilentlyContinue)
    $setupApiHints | ForEach-Object { $_.ToString() } | Set-Content -LiteralPath $setupApiPath -Encoding UTF8
}

$exportResults = @()
foreach ($candidate in $candidateInfs) {
    $output = & pnputil.exe /export-driver $candidate.InfName $exportDir 2>&1 | Out-String
    $exportResults += [pscustomobject]@{
        InfName = $candidate.InfName
        MatchedPatterns = $candidate.MatchedPatterns
        CommandOutput = $output.Trim()
    }
}

$report = [pscustomobject]@{
    CreatedAt = (Get-Date).ToString('s')
    Hostname = $env:COMPUTERNAME
    OutputRoot = $sessionRoot
    Patterns = $Patterns
    CandidateInfCount = $candidateInfs.Count
    CandidateInfs = $candidateInfs
    ExportResults = $exportResults
    InstalledPrograms = $installedPrograms
    SetupApiHintFile = $(if ($setupApiHints.Count) { $setupApiPath } else { $null })
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$lines = @(
    ('SR-3500 driver recovery export report')
    ('CreatedAt: ' + $report.CreatedAt)
    ('Hostname: ' + $report.Hostname)
    ('OutputRoot: ' + $report.OutputRoot)
    ('Patterns: ' + ($Patterns -join ', '))
    ('CandidateInfCount: ' + $candidateInfs.Count)
    ''
    'Candidate INF files:'
)

if ($candidateInfs.Count) {
    foreach ($candidate in $candidateInfs) {
        $lines += ('- ' + $candidate.InfName + ' | matches=' + ($candidate.MatchedPatterns -join ', '))
    }
}
else {
    $lines += '- No candidate INF files matched.'
}

$lines += ''
$lines += 'Installed programs:'
if ($installedPrograms.Count) {
    foreach ($program in $installedPrograms) {
        $lines += ('- ' + $program.DisplayName + ' | ' + $program.DisplayVersion + ' | ' + $program.Publisher)
    }
}
else {
    $lines += '- No matching installed program entry found.'
}

$lines += ''
$lines += 'Export results:'
if ($exportResults.Count) {
    foreach ($result in $exportResults) {
        $lines += ('- ' + $result.InfName)
        $lines += ('  ' + $result.CommandOutput)
    }
}
else {
    $lines += '- No INF export attempted.'
}

if ($setupApiHints.Count) {
    $lines += ''
    $lines += ('SetupAPI hints saved to: ' + $setupApiPath)
}

$lines += ''
$lines += 'Next step:'
$lines += '- Copy the whole export folder to the target machine and run install_exported_driver_bundle.ps1 against the exported-drivers directory.'

$lines | Set-Content -LiteralPath $reportPath -Encoding UTF8
Write-Output ('Report created: ' + $reportPath)
Write-Output ('JSON created: ' + $jsonPath)
Write-Output ('Export folder: ' + $exportDir)