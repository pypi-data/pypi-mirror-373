# ==========================================================
# reset_cua_client.ps1 · clean-slate deploy  (ON-DEMAND, HIDDEN)
# July 2025
# ==========================================================

$repo       = 'C:\Program Files\Python313\Lib\site-packages\cua-client'
$mgmt       = 'C:\cua-management'
$scriptsDir = Join-Path $mgmt 'scripts'
$logsDir    = Join-Path $mgmt 'logs'
$cleanupPs1 = Join-Path $scriptsDir 'cleanup-old-logs.ps1'
$taskName   = 'CUAClient (Interactive)'
$user       = 'azureadmin'                       # auto-log-on account
# New: path for wrapper script that handles auto-restart
$runnerPs1  = Join-Path $scriptsDir 'run-cua-client.ps1'
# Locate pythonw.exe in PATH; fallback to plain command
$pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $pythonw) { $pythonw = 'pythonw.exe' }

# Also locate cua-client.exe (should be in Scripts folder next to pythonw.exe)
$cuaClient = (Get-Command cua-client.exe -ErrorAction SilentlyContinue).Source
if (-not $cuaClient) { 
    # Try to find it in the Scripts folder next to Python
    $pythonDir = Split-Path (Get-Command python.exe -ErrorAction SilentlyContinue).Source -Parent
    if ($pythonDir) {
        $cuaClient = Join-Path $pythonDir 'Scripts\cua-client.exe'
        if (-not (Test-Path $cuaClient)) {
            $cuaClient = 'cua-client.exe'  # fallback
        }
    } else {
        $cuaClient = 'cua-client.exe'  # fallback
    }
}

Write-Host "Using cua-client at: $cuaClient"

# Locate python.exe for pip upgrade command
$python = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = 'python.exe' }

# ScheduledTaskAction to upgrade cua-client before launch
$upgradeAction = New-ScheduledTaskAction `
                    -Execute  'pip' `
                    -Argument 'install --upgrade cua-client' `
                    -WorkingDirectory $mgmt

# 0 ─────────────────────────────────────────────────────────
#   Remove old tasks / services
# ───────────────────────────────────────────────────────────
Write-Host "`n*** Cleaning old artefacts ..."
Import-Module ScheduledTasks -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName 'CUAClient Log Cleanup' -Confirm:$false -ErrorAction SilentlyContinue
sc.exe delete 'CUAClient' 2>$null   # legacy NSSM service, ignore if absent

# 1 ─────────────────────────────────────────────────────────
#   Re-create folders
# ───────────────────────────────────────────────────────────
Write-Host "*** Creating fresh folders ..."
New-Item -ItemType Directory -Path $scriptsDir,$logsDir -Force | Out-Null
Remove-Item "$logsDir\*" -Force -ErrorAction SilentlyContinue

# 2 ─────────────────────────────────────────────────────────
#   Write cleanup-old-logs.ps1  (14-day retention)
# ───────────────────────────────────────────────────────────
Write-Host "*** Writing cleanup-old-logs.ps1 ..."
@"
param([string]`$LogDir = '$logsDir')
Get-ChildItem "`$LogDir\*.log" |
    Where-Object { `$\_.LastWriteTime -lt (Get-Date).AddDays(-14) } |
    Remove-Item -Force -ErrorAction SilentlyContinue
"@ | Set-Content $cleanupPs1 -Encoding UTF8

# 3 ─────────────────────────────────────────────────────────
#   Write run-cua-client.ps1  (auto-restart loop)
# ───────────────────────────────────────────────────────────
Write-Host "*** Writing run-cua-client.ps1 ..."
@"
param([string]`$ClientPath = '$cuaClient')
while (`$true) {
    try {
        & `$ClientPath
    } catch {
        Write-Host "cua-client crashed: `$(`$_.Exception.Message)"
    }
    Start-Sleep -Seconds 5
}
"@ | Set-Content $runnerPs1 -Encoding UTF8

# 4 ─────────────────────────────────────────────────────────
#   Register ON-DEMAND hidden task (NO triggers)
# ───────────────────────────────────────────────────────────
Write-Host "*** Creating '$taskName' task ..."

$action = New-ScheduledTaskAction `
            -Execute 'PowerShell.exe' `
            -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runnerPs1`"" `
            -WorkingDirectory $mgmt

$settings = New-ScheduledTaskSettingsSet `
              -RestartInterval (New-TimeSpan -Minutes 1) `
              -RestartCount    999 `
              -MultipleInstances IgnoreNew `
              -Hidden `
              -AllowStartIfOnBatteries `
              -DontStopIfGoingOnBatteries `
              -StartWhenAvailable `
              -ExecutionTimeLimit (New-TimeSpan -Seconds 0)

$principal = New-ScheduledTaskPrincipal `
              -UserId    $user `
              -LogonType Interactive `
              -RunLevel  Highest

# Added: Trigger task at user logon so it auto-starts after VM reboot
$logonTrig = New-ScheduledTaskTrigger -AtLogOn -User $user

Register-ScheduledTask -TaskName  $taskName `
                       -Action    $upgradeAction,$action `
                       -Trigger   $logonTrig `
                       -Settings  $settings `
                       -Principal $principal `
                       -Description 'CUA client auto-start at logon (hidden), auto-restarts on crash' `
                       -Force

# --- Diagnostics -----------------------------------------------------------
if (-not $?) {
    Write-Host "REGISTER_ERROR: $($Error[0])"
} else {
    Write-Host "REGISTER_OK"
}

# 3 ─────────────────────────────────────────────────────────
#   House-keeping task (log cleanup)
# ───────────────────────────────────────────────────────────
$cleanupAct  = New-ScheduledTaskAction -Execute 'PowerShell.exe' `
                 -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$cleanupPs1`""
$cleanupTrig = New-ScheduledTaskTrigger -Daily -At 03:00
$bootTrig    = New-ScheduledTaskTrigger -AtStartup

Register-ScheduledTask 'CUAClient Log Cleanup' `
    -Action  $cleanupAct `
    -Trigger $cleanupTrig,$bootTrig `
    -Principal $principal `
    -Description 'Delete logs older than 14 days' `
    -Force

Write-Host "`n✔  Reset complete — hidden, on-demand task registered."
