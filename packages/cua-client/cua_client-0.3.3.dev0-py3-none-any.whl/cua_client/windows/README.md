# CUA Client Windows Setup

## The Console Window Problem & Solution

When running Python GUI automation libraries (like `pyautogui`) under `pythonw.exe`, they sometimes create a console window that appears on the taskbar. After trying many complex solutions, we found a simple fix:

**Solution**: Hide the console window immediately when the program starts.

```python
# In logging_config.py (imported first in main.py)
if platform.system() == "Windows":
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)  # 0 = SW_HIDE
```

This runs before any other code and hides any console window that might appear.

## Deployment

Run the reset script to deploy/update the CUA client:

```powershell
PowerShell.exe -ExecutionPolicy Bypass -File "C:\cua-management\scripts\reset_cua_client.ps1"
```

This script:
1. Removes old tasks/services
2. Creates folder structure
3. Installs Python dependencies
4. Registers scheduled task (runs `pythonw.exe -m client.main`)
5. Sets up log cleanup

## Task Management

The scheduled task is named "CUAClient (Interactive)" and can be controlled with:

```powershell
# Start
Start-ScheduledTask 'CUAClient (Interactive)'

# Stop
Stop-ScheduledTask 'CUAClient (Interactive)'

# Status
Get-ScheduledTaskInfo 'CUAClient (Interactive)'
```

## Status Detection

Because the scheduled task runs `pythonw.exe` directly (not through a launcher), the task shows as "READY" even when the client is running. The server detects the actual status by checking for the `pythonw.exe` process.

## Logs

All logs are written to: `C:\cua-management\logs\client.log`

Logs older than 14 days are automatically cleaned up. 