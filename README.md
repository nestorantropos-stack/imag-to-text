# Imag to Text

Aplicación de escritorio para Windows 10/11 de 64 bits: convierte imágenes y PDF escaneados en texto seleccionable y editable. Interfaz en español, OCR local y exportación a Word, Markdown y texto plano.

## Instalación y uso

1. Ejecuta `Imag-to-Text-Setup-1.0.0.exe` desde la sección [Releases](https://github.com/nestorantropos-stack/imag-to-text/releases).
2. Abre **Imag to Text** desde Inicio o el acceso directo del escritorio.
3. Pulsa **Abrir archivos** y selecciona uno o varios PDF, PNG, JPG, TIFF, BMP o WEBP.
4. Selecciona una página en la lista. Pulsa un recuadro del original para identificar el texto reconocido. Los recuadros ámbar indican confianza inferior al 80%; es una estimación del motor, no una garantía de precisión.
5. Corrige el panel **Texto editable**. Puedes seleccionar, copiar, pegar y deshacer con Ctrl+Z.
6. **Exportar texto…** guarda todas las páginas como `.docx`, `.md` o `.txt`, incluyendo tus correcciones. Cambia el tipo de archivo en el diálogo de guardado.
7. **Guardar proyecto** conserva las imágenes y correcciones en un archivo `.itxt`. **Abrir proyecto** permite retomarlas sin repetir OCR.

El instalador incluye Python, el motor y los modelos. No requiere Python, Word, Tesseract, GPU, cuentas ni conexión a Internet para reconocer documentos. Se instala por usuario y se desinstala desde Configuración → Aplicaciones.

## Alcance

- Español e inglés impresos; el modelo multilingüe también reconoce otros idiomas.
- PDF y TIFF de varias páginas, imágenes con transparencia y orientación EXIF.
- Trabajo en segundo plano, cancelación entre páginas y recuperación de resultados parciales si un archivo falla.
- Exportación del **texto** con encabezados y separación de páginas; no reconstruye exactamente tablas, columnas, tipografía ni el diseño original.
- No modifica el PDF original ni genera un PDF con capa de texto. El texto seleccionable está en el editor y en los archivos exportados.
- Escritura manuscrita, fotos borrosas y documentos de varias columnas pueden necesitar correcciones importantes. Los PDF protegidos deben desbloquearse antes de importarlos.
- Las imágenes de trabajo se limitan a 3200 píxeles por lado; el motor aplica su propio límite. Para letra muy pequeña conviene recortar el original.
- Los proyectos conservan las imágenes y las rutas de origen; tenlo en cuenta al compartirlos. El programa no envía documentos a servicios externos.

## Desarrollo

Python 3.11 de 64 bits en Windows, con Tcl/Tk:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe app.py
```

Pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=work/pytest-temp
.\.venv\Scripts\python.exe smoke.py work/smoke
```

`smoke.py` genera documentos sintéticos, bloquea las conexiones de red y comprueba OCR en PNG/PDF, acentos, páginas vacías, exportaciones y persistencia. El ejecutable también admite `ImagToText.exe --self-test <carpeta>`; escribe `report.json`.

## Crear el instalador

Instala [Inno Setup 6](https://jrsoftware.org/isinfo.php) y ejecuta:

```powershell
.\.venv\Scripts\python.exe collect_licenses.py
.\build.ps1 -Iscc 'C:\ruta\Inno Setup 6\ISCC.exe'
```

El resultado queda en `dist/Imag-to-Text-Setup-1.0.0.exe`. La carpeta `dist/ImagToText` es la versión portátil completa. Debe distribuirse completa, incluyendo `_internal` y las licencias. Los binarios no están firmados digitalmente.

## Arquitectura

- `app.py`: interfaz Tkinter y cola de eventos; el hilo de OCR no accede a widgets.
- `core.py`: renderizado PDFium, normalización Pillow, OCR RapidOCR/ONNX Runtime, exportación y proyectos ZIP.
- `smoke.py`, `tests/`: verificaciones de integración y manejo de archivos.
- `installer.iss`, `build.ps1`: distribución para Windows.

Los modelos se toman de la distribución fijada de RapidOCR y se comprueba su existencia antes de iniciar OCR. Las rutas explícitas evitan descargar modelos en ejecución. Los archivos se guardan mediante reemplazo atómico para proteger una exportación anterior si ocurre un error.

Consulta [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) y `licenses/` para las licencias de terceros.
