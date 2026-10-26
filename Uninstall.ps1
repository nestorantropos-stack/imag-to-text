$ErrorActionPreference = 'Stop'
$taskExpectedDir = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs\Imag to Text'))
$taskActualDir = [IO.Path]::GetFullPath($PSScriptRoot)
if ($taskActualDir -ne $taskExpectedDir) { throw 'Ejecuta el desinstalador desde la instalación.' }
Add-Type -AssemblyName System.Windows.Forms
$taskAnswer = [System.Windows.Forms.MessageBox]::Show('¿Desinstalar Imag to Text? Los documentos guardados fuera de la carpeta de instalación se conservarán.', 'Imag to Text', 'YesNo')
if ($taskAnswer -ne 'Yes') { exit }
foreach ($taskFolder in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
    $taskLinkPath = Join-Path $taskFolder 'Imag to Text.lnk'
    if (Test-Path -LiteralPath $taskLinkPath) { Remove-Item -LiteralPath $taskLinkPath }
}
Remove-Item -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\ImagToText' -Recurse -ErrorAction SilentlyContinue
Set-Location $env:TEMP
Remove-Item -LiteralPath $taskActualDir -Recurse
