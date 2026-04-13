param(
    [string]$OutputFolder = ".\probe-output",
    [string[]]$ProgramKeywords = @("sr6000", "scan", "scanner", "optik", "omr"),
    [switch]$IncludeUsbDevices
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Directory {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Safe-Invoke {
    param(
        [string]$Name,
        [scriptblock]$Script
    )

    try {
        return & $Script
    }
    catch {
        return [pscustomobject]@{
            section = $Name
            error = $_.Exception.Message
        }
    }
}

function Get-TwainRegistryEntries {
    $paths = @(
        'HKLM:\SOFTWARE\TWAIN',
        'HKLM:\SOFTWARE\WOW6432Node\TWAIN',
        'HKLM:\SOFTWARE\TWAIN_32',
        'HKLM:\SOFTWARE\WOW6432Node\TWAIN_32'
    )

    $results = @()
    foreach ($path in $paths) {
        if (-not (Test-Path $path)) {
            continue
        }

        Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
            $item = $_
            $props = Get-ItemProperty -Path $item.PSPath -ErrorAction SilentlyContinue
            $results += [pscustomobject]@{
                RegistryPath = $item.PSPath
                PSChildName = $item.PSChildName
                ProductName = $props.ProductName
                Directory = $props.Directory
                Dll = $props.DLL
            }
        }
    }

    $results
}

function Get-WiaDevices {
    $manager = New-Object -ComObject WIA.DeviceManager
    $items = @()
    foreach ($deviceInfo in $manager.DeviceInfos) {
        $properties = @{}
        foreach ($property in $deviceInfo.Properties) {
            $properties[$property.Name] = $property.Value
        }
        $items += [pscustomobject]@{
            DeviceID = $deviceInfo.DeviceID
            Type = $deviceInfo.Type
            Properties = $properties
        }
    }
    $items
}

function Get-InstalledPrograms {
    param([string[]]$Keywords)

    $paths = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
    )

    $programs = foreach ($path in $paths) {
        Get-ItemProperty -Path $path -ErrorAction SilentlyContinue
    }

    $programs | Where-Object {
        if (-not $_.PSObject.Properties['DisplayName']) {
            return $false
        }
        $name = [string]$_.PSObject.Properties['DisplayName'].Value
        if (-not $name) {
            return $false
        }
        foreach ($keyword in $Keywords) {
            if ($name -match [regex]::Escape($keyword)) {
                return $true
            }
        }
        return $false
    } | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate, InstallLocation, UninstallString
}

function Get-ImageDevices {
    try {
        return Get-PnpDevice -PresentOnly -ErrorAction Stop | Where-Object {
            $_.Class -in @('Image', 'USB', 'WPD') -or $_.FriendlyName -match 'scan|scanner|image|twain|wia|sr6000'
        } | Select-Object Class, FriendlyName, InstanceId, Status, Problem, Manufacturer
    }
    catch {
        return Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -match 'scan|scanner|image|twain|wia|sr6000' -or $_.PNPClass -in @('Image', 'USB')
        } | Select-Object PNPClass, Name, DeviceID, Manufacturer, Status
    }
}

function Get-RecentTextExports {
    $roots = @(
        "$env:PUBLIC\Documents",
        "$env:USERPROFILE\Documents",
        "$env:ProgramData"
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

    $items = foreach ($root in $roots) {
        Get-ChildItem -Path $root -Filter *.txt -File -Recurse -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 20 FullName, Length, LastWriteTime
    }

    $items | Sort-Object LastWriteTime -Descending | Select-Object -First 20
}

Ensure-Directory -Path $OutputFolder
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$jsonPath = Join-Path $OutputFolder ("secure-pc-probe-{0}.json" -f $timestamp)
$txtPath = Join-Path $OutputFolder ("secure-pc-probe-{0}.txt" -f $timestamp)

$report = [ordered]@{
    generated_at = (Get-Date).ToString('s')
    computer_name = $env:COMPUTERNAME
    user_name = $env:USERNAME
    windows = Safe-Invoke -Name 'windows' -Script {
        Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture
    }
    image_devices = Safe-Invoke -Name 'image_devices' -Script { Get-ImageDevices }
    wia_devices = Safe-Invoke -Name 'wia_devices' -Script { Get-WiaDevices }
    twain_registry = Safe-Invoke -Name 'twain_registry' -Script { Get-TwainRegistryEntries }
    installed_programs = Safe-Invoke -Name 'installed_programs' -Script { Get-InstalledPrograms -Keywords $ProgramKeywords }
    recent_text_exports = Safe-Invoke -Name 'recent_text_exports' -Script { Get-RecentTextExports }
}

if ($IncludeUsbDevices) {
    $report['usb_devices'] = Safe-Invoke -Name 'usb_devices' -Script {
        Get-CimInstance Win32_PnPEntity | Where-Object {
            $_.PNPClass -eq 'USB' -or $_.Name -match 'usb|scanner|sr6000'
        } | Select-Object Name, DeviceID, Manufacturer, Status
    }
}

$report | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonPath -Encoding UTF8

$summary = @()
$summary += "Probe report written to: $jsonPath"
$summary += ""
$summary += "Windows"
$summary += ($report.windows | Out-String).TrimEnd()
$summary += ""
$summary += "Image devices"
$summary += ($report.image_devices | Out-String).TrimEnd()
$summary += ""
$summary += "WIA devices"
$summary += ($report.wia_devices | Out-String).TrimEnd()
$summary += ""
$summary += "TWAIN registry"
$summary += ($report.twain_registry | Out-String).TrimEnd()
$summary += ""
$summary += "Installed programs"
$summary += ($report.installed_programs | Out-String).TrimEnd()
$summary += ""
$summary += "Recent text exports"
$summary += ($report.recent_text_exports | Out-String).TrimEnd()

if ($IncludeUsbDevices) {
    $summary += ""
    $summary += "USB devices"
    $summary += ($report.usb_devices | Out-String).TrimEnd()
}

$summary -join [Environment]::NewLine | Set-Content -Path $txtPath -Encoding UTF8

Write-Output "Probe report written to: $jsonPath"
Write-Output "Probe summary written to: $txtPath"