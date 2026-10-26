# Componentes de terceros

Imag to Text distribuye componentes y modelos de terceros sin modificarlos. Las licencias y avisos suministrados por las distribuciones se copian en `licenses/` al construir.

| Componente | Proyecto |
| --- | --- |
| Python / Tcl / Tk | https://www.python.org/ / https://www.tcl.tk/ |
| RapidOCR y modelos PP-OCR de PaddleOCR | https://github.com/RapidAI/RapidOCR / https://github.com/PaddlePaddle/PaddleOCR |
| ONNX Runtime | https://github.com/microsoft/onnxruntime |
| pypdfium2 / PDFium | https://github.com/pypdfium2-team/pypdfium2 / https://pdfium.googlesource.com/pdfium/ |
| Pillow | https://github.com/python-pillow/Pillow |
| python-docx / lxml | https://github.com/python-openxml/python-docx / https://lxml.de/ |
| OpenCV, NumPy, Shapely y otras dependencias | Véanse los avisos de cada distribución en `licenses/` |

El archivo `requirements-lock.txt` registra las versiones utilizadas. PyInstaller se utiliza con su excepción para aplicaciones empaquetadas. Inno Setup compila el instalador y conserva sus propios avisos en él.
