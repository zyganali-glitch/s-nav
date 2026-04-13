param(
    [string]$ConfigPath = 'C:\SecureExam\secure_pc_config.json',
    [string]$ScriptPath = '.\ops\watch_vendor_export.ps1'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$config = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$taskName = $config.bridge.taskName
$minutes = [int]$config.bridge.pollMinutes
$resolvedScriptPath = (Resolve-Path $ScriptPath).Path
$actionArgs = @(
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    ('"{0}"' -f $resolvedScriptPath),
    '-InputFolder',
    ('"{0}"' -f $config.paths.incoming),
    '-ExamCode',
    ('"{0}"' -f $config.bridge.examCode),
    '-ApiBaseUrl',
    ('"{0}"' -f $config.app.baseUrl),
    '-ArchiveFolder',
    ('"{0}"' -f $config.paths.processed),
    '-ErrorFolder',
    ('"{0}"' -f $config.paths.error)
)

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ($actionArgs -join ' ')
$trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes $minutes) -RepetitionDuration (New-TimeSpan -Days 1)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Output ("Scheduled task registered: {0}" -f $taskName)