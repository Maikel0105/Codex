# Windows installer for Roleplay Abyss
$ErrorActionPreference = 'Stop'

$installDir = 'C:\Games\Roleplay Abyss'
if (-Not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
}

function Install-IfMissing {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Args
    )
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        $tmp = "$env:TEMP\$Name.exe"
        Write-Host "Installing $Name from $Url"
        Invoke-WebRequest $Url -OutFile $tmp
        Start-Process $tmp -ArgumentList $Args -Wait
    }
}

Install-IfMissing 'python' 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe' '/quiet InstallAllUsers=1 PrependPath=1'
Install-IfMissing 'git' 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe' '/VERYSILENT /NORESTART'
Install-IfMissing 'wget' 'https://eternallybored.org/misc/wget/releases/wget.exe' ''

$src = Split-Path -Parent $MyInvocation.MyCommand.Definition
Copy-Item -Path $src\* -Destination $installDir -Recurse -Force

Push-Location $installDir
python setup_env.py
Pop-Location

