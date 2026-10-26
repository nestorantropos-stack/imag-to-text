param([string]$Iscc = "ISCC.exe")
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& .\.venv\Scripts\python.exe collect_licenses.py
if ($LASTEXITCODE -ne 0) { throw 'Falló la recopilación de licencias' }
& .\.venv\Scripts\python.exe package_runtime.py
if ($LASTEXITCODE -ne 0) { throw 'Falló el empaquetado' }
& $Iscc installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Falló Inno Setup' }
