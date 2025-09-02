param([string]$LogDir = 'C:\cua-management\logs')

Get-ChildItem "$LogDir\*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } |
    Remove-Item -Force -ErrorAction SilentlyContinue
