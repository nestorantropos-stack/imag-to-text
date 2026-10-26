"""End-to-end offline test, also runnable from the frozen executable."""
from pathlib import Path
import json
import socket
import traceback
from PIL import Image, ImageDraw, ImageFont
from core import OCR, Page, render_pages, export, save_project, load_project


def run(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    report = {"passed": False, "network_disabled": True}
    previous_connect = socket.socket.connect
    def deny_network(*args, **kwargs):
        raise RuntimeError("Network disabled during OCR verification")
    socket.socket.connect = deny_network
    try:
        image = Image.new("RGB", (1500, 700), "white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 44)
        lines = ["DOCUMENTO DE PRUEBA", "Información para edición y exportación.",
                 "El pingüino camina junto al niño.", "Factura 12345 - Total 25000 pesos."]
        for i, line in enumerate(lines):
            draw.text((80, 80 + i * 110), line, fill="black", font=font)
        image.save(folder / "ejemplo.png")
        image.save(folder / "escaneado.pdf", save_all=True, append_images=[image], resolution=150)
        engine = OCR()
        pages = []
        for number, rendered in render_pages(folder / "escaneado.pdf"):
            text, regions = engine.recognize(rendered)
            assert "12345" in text and "25000" in text, text
            assert "pingüino" in text and "niño" in text, text
            image_path = folder / f"page-{number}.png"
            rendered.save(image_path)
            pages.append(Page("escaneado.pdf", number, str(image_path), text, regions))
        assert len(pages) == 2
        original, regions = engine.recognize(image)
        assert "Información" in original, original
        pages[0].text += "\nCorrección manual: verificación completada."
        for extension in ("md", "txt", "docx"):
            export(pages, folder / f"resultado.{extension}")
        from docx import Document
        word = "\n".join(p.text for p in Document(folder / "resultado.docx").paragraphs)
        assert "Corrección manual" in word
        assert "Corrección manual" in (folder / "resultado.md").read_text(encoding="utf-8")
        save_project(pages, folder / "proyecto.itxt")
        restored = load_project(folder / "proyecto.itxt", folder)
        assert [p.text for p in restored] == [p.text for p in pages]
        blank_text, blank_regions = engine.recognize(Image.new("RGB", (800, 800), "white"))
        assert not blank_text and not blank_regions
        report.update(passed=True, pages=len(pages), recognized_text=original,
                      checks=["PNG OCR", "two-page scanned PDF", "Spanish accents", "blank page",
                              "edited text in DOCX/Markdown/TXT", "project round-trip"])
    except Exception:
        report["error"] = traceback.format_exc()
        raise
    finally:
        socket.socket.connect = previous_connect
        (folder / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "work/smoke")
