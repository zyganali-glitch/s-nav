param(
    [Parameter(Mandatory = $true)]
    [string]$DriverBundlePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Get-Command pnputil.exe -ErrorAction SilentlyContinue)) {
    throw 'pnputil.exe bulunamadi.'
}

if (-not (Test-Path -LiteralPath $DriverBundlePath)) {
    throw ("Driver bundle yolu bulunamadi: {0}" -f $DriverBundlePath)
}

$infFiles = Get-ChildItem -LiteralPath $DriverBundlePath -Recurse -Filter '*.inf' -File
if (-not $infFiles.Count) {
    throw ("INF dosyasi bulunamadi: {0}" -f $DriverBundlePath)
}

foreach ($inf in $infFiles) {
    Write-Output ("Installing: {0}" -f $inf.FullName)
    & pnputil.exe /add-driver $inf.FullName /install
}

Write-Output 'Driver install run tamamlandi. Aygiti cikarip tekrar tak ve ardindan trace/probe scriptlerini yeniden kos.'