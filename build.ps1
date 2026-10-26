param([string]$Iscc = "ISCC.exe")
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
& .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --name ImagToText --collect-all rapidocr --collect-all onnxruntime --collect-all pypdfium2 --hidden-import rapidocr.main --hidden-import rapidocr.inference_engine.onnxruntime --add-data 'THIRD_PARTY_NOTICES.md;.' --add-data 'licenses;licenses' app.py
if ($LASTEXITCODE -ne 0) { throw 'Falló PyInstaller' }
& $Iscc installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Falló Inno Setup' }
