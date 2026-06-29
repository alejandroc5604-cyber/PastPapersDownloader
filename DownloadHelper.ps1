
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

    $nestedFolder = Join-Path -Path $Destination -ChildPath 'PastPapersDownloader-main'
    if (Test-Path -Path $nestedFolder) {
        Get-ChildItem -Path $nestedFolder -Force | Move-Item -Destination $Destination -Force
        Remove-Item -Path $nestedFolder -Recurse -Force
    }

    Write-Host "Repository downloaded and extracted successfully." -ForegroundColor Green

    $setupPath = Join-Path -Path $Destination -ChildPath 'setup.py'
    if (Test-Path -Path $setupPath) {
        Write-Host "Running setup.py to install requirements..."
        $pythonExe = Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
        if (-not $pythonExe) {
            $pythonExe = Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
        }

        if ($pythonExe) {
            & $pythonExe $setupPath
            if ($LASTEXITCODE -ne 0) {
                Write-Host "setup.py finished with errors. Check the output above." -ForegroundColor Yellow
            }
            else {
                Write-Host "setup.py completed successfully." -ForegroundColor Green
            }
        }
        else {
            Write-Host "Python executable not found in PATH. Please install Python and run setup.py manually." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "setup.py not found at $Destination. Please run setup.py manually if needed." -ForegroundColor Yellow
    }

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
