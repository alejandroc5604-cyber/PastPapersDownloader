<#
.SYNOPSIS
Bootstrap installer for PastPapersDownloader.

.DESCRIPTION
This script downloads the latest `DownloadHelper.ps1` script from GitHub and runs it.

Run from Win+R with PowerShell:
  powershell -ExecutionPolicy Bypass -File "C:\Path\To\bootstrap_download.ps1"

.PARAMETER Destination
Optional output folder where the repository is extracted. Defaults to the user's Downloads folder.
#>

param(
    [string]$Destination = "$env:USERPROFILE\Downloads\PastPapersDownloader"
)

$helperUrl = 'https://raw.githubusercontent.com/alejandroc5604-cyber/PastPapersDownloader/main/DownloadHelper.ps1'
$helperPath = Join-Path -Path $env:TEMP -ChildPath 'DownloadHelper.ps1'

Write-Host "Fetching bootstrap helper from GitHub..."
Write-Host "Source: $helperUrl"
Write-Host "Destination: $Destination"

try {
    Invoke-WebRequest -Uri $helperUrl -OutFile $helperPath -UseBasicParsing
    Write-Host "Helper downloaded successfully. Running helper..."

    & powershell -NoProfile -ExecutionPolicy Bypass -File $helperPath -Destination $Destination
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    if (Test-Path -Path $helperPath) {
        Remove-Item -Path $helperPath -Force
    }
}
