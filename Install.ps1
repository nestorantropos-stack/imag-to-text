$ErrorActionPreference = 'Stop'
$taskInstallDir = Join-Path $env:LOCALAPPDATA 'Programs\Imag to Text'
if (Test-Path -LiteralPath $taskInstallDir) {
    throw 'Ya existe una instalación. Desinstálala antes de instalar de nuevo.'
}
New-Item -ItemType Directory -Path $taskInstallDir | Out-Null
Copy-Item -Path (Join-Path $PSScriptRoot '*') -Destination $taskInstallDir -Recurse
$taskShell = New-Object -ComObject WScript.Shell
$taskLinks = @(
    (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Imag to Text.lnk'),
    (Join-Path ([Environment]::GetFolderPath('Programs')) 'Imag to Text.lnk')
)
foreach ($taskLinkPath in $taskLinks) {
    $taskShortcut = $taskShell.CreateShortcut($taskLinkPath)
    $taskShortcut.TargetPath = Join-Path $taskInstallDir 'runtime\pythonw.exe'
    $taskShortcut.Arguments = '"' + (Join-Path $taskInstallDir 'app.py') + '"'
    $taskShortcut.WorkingDirectory = $taskInstallDir
    $taskShortcut.Description = 'OCR local de imágenes y PDF; edición y exportación Word y Markdown'
    $taskShortcut.Save()
}
$taskKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\ImagToText'
New-Item -Path $taskKey -Force | Out-Null
New-ItemProperty -Path $taskKey -Name DisplayName -Value 'Imag to Text' -Force | Out-Null
New-ItemProperty -Path $taskKey -Name DisplayVersion -Value '1.0.0' -Force | Out-Null
New-ItemProperty -Path $taskKey -Name Publisher -Value 'nestorantropos-stack' -Force | Out-Null
New-ItemProperty -Path $taskKey -Name InstallLocation -Value $taskInstallDir -Force | Out-Null
New-ItemProperty -Path $taskKey -Name UninstallString -Value ('powershell.exe -NoProfile -File "' + (Join-Path $taskInstallDir 'Uninstall.ps1') + '"') -Force | Out-Null
Write-Output "Instalado: $taskInstallDir"
