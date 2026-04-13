param(
    [string]$MediaRoot = 'F:\',
    [string]$OutputRoot = 'C:\SecureExam\driver-media-scan',
    [string[]]$Patterns = @('SR-3500', 'SR3500', 'Sekonic', 'Optical Mark', 'VID_0A41', 'VID_0461')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $MediaRoot)) {
    throw ("Medya yolu hazir degil veya okunamiyor: {0}" -f $MediaRoot)
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$sessionRoot = Join-Path $OutputRoot ("sr3500-media-scan-" + $timestamp)
$reportPath = Join-Path $sessionRoot 'report.txt'
$jsonPath = Join-Path $sessionRoot 'report.json'

New-Item -ItemType Directory -Path $sessionRoot -Force | Out-Null

$candidateFiles = Get-ChildItem -LiteralPath $MediaRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -match '^(\.inf|\.sys|\.cat|\.cab|\.exe|\.msi|\.dll|\.ini|\.txt)$' -or
        $_.Name -match 'driver|setup|install|sr|sekonic|omr'
    }

$patternRegex = [string]::Join('|', ($Patterns | ForEach-Object { [Regex]::Escape($_) }))

$matches = foreach ($file in $candidateFiles) {
    $matchedPatterns = @()
    if ($file.Name -match $patternRegex -or $file.DirectoryName -match $patternRegex) {
        $matchedPatterns += $Patterns | Where-Object {
            $file.Name -match [Regex]::Escape($_) -or $file.DirectoryName -match [Regex]::Escape($_)
        }
    }

    if (-not $matchedPatterns.Count -and $file.Extension -in '.inf', '.ini', '.txt') {
        try {
            $raw = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction Stop
            $matchedPatterns += $Patterns | Where-Object { $raw -match [Regex]::Escape($_) }
        }
        catch {
        }
    }

    [pscustomobject]@{
        FullName = $file.FullName
        Extension = $file.Extension
        Length = $file.Length
        MatchedPatterns = @($matchedPatterns | Select-Object -Unique)
    }
}

$strongMatches = @($matches | Where-Object { $_.MatchedPatterns.Count -gt 0 })

$report = [pscustomobject]@{
    CreatedAt = (Get-Date).ToString('s')
    MediaRoot = $MediaRoot
    Patterns = $Patterns
    CandidateFileCount = @($candidateFiles).Count
    StrongMatchCount = $strongMatches.Count
    StrongMatches = $strongMatches
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$lines = @(
    'SR-3500 media scan report',
    ('CreatedAt: ' + $report.CreatedAt),
    ('MediaRoot: ' + $MediaRoot),
    ('CandidateFileCount: ' + $report.CandidateFileCount),
    ('StrongMatchCount: ' + $report.StrongMatchCount),
    '',
    'Strong matches:'
)

if ($strongMatches.Count) {
    foreach ($match in $strongMatches) {
        $lines += ('- ' + $match.FullName)
        $lines += ('  ext=' + $match.Extension + ' size=' + $match.Length + ' matches=' + ($match.MatchedPatterns -join ', '))
    }
}
else {
    $lines += '- No strong match found. Inspect generic setup packages manually.'
}

$lines += ''
$lines += 'Next step:'
$lines += '- If INF files are found, do not install blindly on the production machine.'
$lines += '- First copy candidate folders to a safe workspace and compare model references.'
$lines += '- If only a setup EXE exists, inspect its contents or extract it on a sacrificial machine, then reuse export/install workflow.'

$lines | Set-Content -LiteralPath $reportPath -Encoding UTF8

Write-Output ('Report created: ' + $reportPath)
Write-Output ('JSON created: ' + $jsonPath)