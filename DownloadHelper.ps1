<#
.SYNOPSIS
Downloads the PastPapersDownloader GitHub repository archive and extracts it locally.

.DESCRIPTION
This script is intended to be run from Win+R with PowerShell, for example:
  powershell -ExecutionPolicy Bypass -File "C:\Path\To\download_pastpapers_downloader.ps1"

.PARAMETER Destination
Optional output folder where the repository is extracted. Defaults to the user's Downloads folder.
#>

param(
    [string]$Destination = "$env:USERPROFILE\Downloads\PastPapersDownloader"
)

$repoUrl = 'https://github.com/alejandroc5604-cyber/PastPapersDownloader/archive/refs/heads/main.zip'
$zipPath = Join-Path -Path $env:TEMP -ChildPath 'PastPapersDownloader-main.zip'

Write-Host "Downloading PastPapersDownloader from GitHub..."
Write-Host "Source: $repoUrl"
Write-Host "Destination: $Destination"

if (Test-Path -Path $Destination) {
    Write-Host "Destination already exists. Existing files may be overwritten." -ForegroundColor Yellow
}
else {
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
}

try {
    Invoke-WebRequest -Uri $repoUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "Download complete. Extracting archive..."

    Expand-Archive -Path $zipPath -DestinationPath $Destination -Force

    # If archive creates a nested folder, move its contents up one level.
    $nestedFolder = Join-Path -Path $Destination -ChildPath 'PastPapersDownloader-main'
    if (Test-Path -Path $nestedFolder) {
        Get-ChildItem -Path $nestedFolder -Force | Move-Item -Destination $Destination -Force
        Remove-Item -Path $nestedFolder -Recurse -Force
    }

    Write-Host "Repository downloaded and extracted successfully." -ForegroundColor Green
    Write-Host "Open the folder and run `python CLI.py` to start the project."
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    if (Test-Path -Path $zipPath) {
        Remove-Item -Path $zipPath -Force
    }
}
