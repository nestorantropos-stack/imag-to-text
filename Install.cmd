@echo off
powershell.exe -NoProfile -File "%~dp0Install.ps1"
if errorlevel 1 (
  echo No se pudo instalar. Revisa el mensaje anterior.
) else (
  echo Instalacion completa. Abre Imag to Text desde el escritorio.
)
pause
