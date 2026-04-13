param(
    [Parameter(Mandatory = $true)]
    [string]$InputFolder,

    [Parameter(Mandatory = $true)]
    [string]$ExamCode,

    [string]$ApiBaseUrl = "http://127.0.0.1:8140",
    [string]$FilePattern = "*.txt",
    [string]$ArchiveFolder = "",
    [string]$ErrorFolder = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Get-UniquePath {
    param(
        [string]$Folder,
        [string]$Name
    )

    $candidate = Join-Path $Folder $Name
    if (-not (Test-Path -LiteralPath $candidate)) {
        return $candidate
    }

    $stem = [System.IO.Path]::GetFileNameWithoutExtension($Name)
    $extension = [System.IO.Path]::GetExtension($Name)
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    return (Join-Path $Folder ("{0}-{1}{2}" -f $stem, $timestamp, $extension))
}

function Invoke-ExamImport {
    param(
        [string]$FilePath,
        [string]$Uri
    )

    $client = New-Object System.Net.Http.HttpClient
    try {
        $content = New-Object System.Net.Http.MultipartFormDataContent
        $stream = [System.IO.File]::Open($FilePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        try {
            $fileContent = New-Object System.Net.Http.StreamContent($stream)
            $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/octet-stream")
            $content.Add($fileContent, "file", [System.IO.Path]::GetFileName($FilePath))

            $response = $client.PostAsync($Uri, $content).GetAwaiter().GetResult()
            $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            if (-not $response.IsSuccessStatusCode) {
                throw ("HTTP {0}: {1}" -f [int]$response.StatusCode, $body)
            }
            return $body
        }
        finally {
            $stream.Dispose()
            $content.Dispose()
        }
    }
    finally {
        $client.Dispose()
    }
}

if (-not $ArchiveFolder) {
    $ArchiveFolder = Join-Path $InputFolder "_processed"
}

if (-not $ErrorFolder) {
    $ErrorFolder = Join-Path $InputFolder "_error"
}

Ensure-Directory -Path $InputFolder
Ensure-Directory -Path $ArchiveFolder
Ensure-Directory -Path $ErrorFolder

$normalizedExamCode = $ExamCode.Trim().ToUpperInvariant()
$normalizedApiBase = $ApiBaseUrl.TrimEnd("/")
$uri = "{0}/api/exams/{1}/imports" -f $normalizedApiBase, $normalizedExamCode
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$files = Get-ChildItem -LiteralPath $InputFolder -Filter $FilePattern -File | Sort-Object LastWriteTime, Name

foreach ($file in $files) {
    try {
        $responseBody = Invoke-ExamImport -FilePath $file.FullName -Uri $uri
        $archivedFile = Get-UniquePath -Folder $ArchiveFolder -Name $file.Name
        Move-Item -LiteralPath $file.FullName -Destination $archivedFile

        $jsonName = ([System.IO.Path]::GetFileNameWithoutExtension($file.Name) + ".json")
        $jsonPath = Get-UniquePath -Folder $ArchiveFolder -Name $jsonName
        [System.IO.File]::WriteAllText($jsonPath, $responseBody, $utf8NoBom)

        Write-Output ("[OK] {0} -> {1}" -f $file.Name, $archivedFile)
    }
    catch {
        $failedFile = Get-UniquePath -Folder $ErrorFolder -Name $file.Name
        if (Test-Path -LiteralPath $file.FullName) {
            Move-Item -LiteralPath $file.FullName -Destination $failedFile
        }

        $errorName = ([System.IO.Path]::GetFileNameWithoutExtension($file.Name) + ".error.txt")
        $errorPath = Get-UniquePath -Folder $ErrorFolder -Name $errorName
        [System.IO.File]::WriteAllText($errorPath, $_.Exception.Message, $utf8NoBom)

        Write-Error ("[FAIL] {0} -> {1}`n{2}" -f $file.Name, $failedFile, $_.Exception.Message)
    }
}param(
    [Parameter(Mandatory = $true)]
    [string]$ExamCode,

    [Parameter(Mandatory = $true)]
    [string]$WatchPath,

    [string]$ApiBaseUrl = "http://127.0.0.1:8140",
    [string]$Filter = "*.txt",
    [string]$ArchivePath = "",
    [int]$PollMilliseconds = 1000,
    [int]$ReadyCheckCount = 2,
    [int]$ReadyCheckDelayMs = 400
)

$ErrorActionPreference = "Stop"

$resolvedWatchPath = (Resolve-Path -LiteralPath $WatchPath).Path
$script:processedFingerprints = @{}

if ($ArchivePath) {
    New-Item -ItemType Directory -Force -Path $ArchivePath | Out-Null
    $resolvedArchivePath = (Resolve-Path -LiteralPath $ArchivePath).Path
}

function Write-BridgeLog {
    param([string]$Message)

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Get-FileFingerprint {
    param([string]$Path)

    $item = Get-Item -LiteralPath $Path
    return "{0}|{1}" -f $item.Length, $item.LastWriteTimeUtc.Ticks
}

function Test-FileReady {
    param([string]$Path)

    $stableCount = 0
    $lastFingerprint = ""

    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if (-not (Test-Path -LiteralPath $Path)) {
            return $false
        }

        try {
            $fingerprint = Get-FileFingerprint -Path $Path
            $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
            $stream.Dispose()
        }
        catch {
            [System.Threading.Thread]::Sleep($ReadyCheckDelayMs)
            continue
        }

        if ($fingerprint -eq $lastFingerprint) {
            $stableCount++
            if ($stableCount -ge $ReadyCheckCount) {
                return $true
            }
        }
        else {
            $stableCount = 1
            $lastFingerprint = $fingerprint
        }

        [System.Threading.Thread]::Sleep($ReadyCheckDelayMs)
    }

    return $false
}

function Invoke-ImportUpload {
    param([string]$Path)

    if (-not (Test-FileReady -Path $Path)) {
        throw "Dosya hazir hale gelmedi: $Path"
    }

    $fingerprint = Get-FileFingerprint -Path $Path
    $cacheKey = "{0}|{1}" -f $Path, $fingerprint
    if ($script:processedFingerprints.ContainsKey($cacheKey)) {
        return
    }

    $uri = "{0}/api/exams/{1}/imports" -f $ApiBaseUrl.TrimEnd('/'), $ExamCode.ToUpperInvariant()
    $client = New-Object System.Net.Http.HttpClient
    $multipart = New-Object System.Net.Http.MultipartFormDataContent

    try {
        $bytes = [System.IO.File]::ReadAllBytes($Path)
        $fileName = [System.IO.Path]::GetFileName($Path)
        $content = New-Object System.Net.Http.ByteArrayContent(, $bytes)
        $content.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("text/plain")
        $multipart.Add($content, "file", $fileName)

        $response = $client.PostAsync($uri, $multipart).GetAwaiter().GetResult()
        $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
        if (-not $response.IsSuccessStatusCode) {
            throw "Import basarisiz: $($response.StatusCode) $body"
        }

        $script:processedFingerprints[$cacheKey] = [DateTime]::UtcNow
        Write-BridgeLog "Import tamamlandi: $fileName"

        if ($ArchivePath) {
            $targetPath = Join-Path $resolvedArchivePath $fileName
            Copy-Item -LiteralPath $Path -Destination $targetPath -Force
            Write-BridgeLog "Arsiv kopyasi olusturuldu: $targetPath"
        }
    }
    finally {
        $multipart.Dispose()
        $client.Dispose()
    }
}

Write-BridgeLog "Bridge basladi. WatchPath=$resolvedWatchPath ExamCode=$ExamCode Filter=$Filter"

while ($true) {
    Get-ChildItem -LiteralPath $resolvedWatchPath -Filter $Filter -File |
        Sort-Object LastWriteTimeUtc |
        ForEach-Object {
            try {
                Invoke-ImportUpload -Path $_.FullName
            }
            catch {
                Write-BridgeLog "Hata: $($_.Exception.Message)"
            }
        }

    [System.Threading.Thread]::Sleep($PollMilliseconds)
}