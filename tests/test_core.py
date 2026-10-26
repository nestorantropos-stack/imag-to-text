from pathlib import Path
import json
import zipfile
import pytest
from PIL import Image
from core import Page, export, save_project, load_project, render_pages, atomic_write


def test_multipage_tiff_and_transparency(tmp_path):
    path = tmp_path / "pages.tiff"
    Image.new("RGB", (100, 200), "white").save(path, save_all=True, append_images=[Image.new("RGB", (100, 200))])
    assert [n for n, _ in render_pages(path)] == [1, 2]
    png = tmp_path / "transparent.png"
    Image.new("RGBA", (20, 20), (0, 0, 0, 0)).save(png)
    assert next(render_pages(png))[1].getpixel((0, 0)) == (255, 255, 255)


def test_export_and_project_preserve_edits(tmp_path):
    image = tmp_path / "image.png"
    Image.new("RGB", (100, 200), "white").save(image)
    pages = [Page("niño.pdf", 1, str(image), "Texto corregido: áéíóú ñ\nSegunda línea")]
    project = tmp_path / "p.itxt"
    save_project(pages, project)
    result = load_project(project, tmp_path)
    assert result[0].text == pages[0].text
    for extension in ("md", "txt", "docx"):
        target = tmp_path / f"export.{extension}"
        export(result, target)
        if extension == "docx":
            from docx import Document
            assert "áéíóú ñ" in "\n".join(p.text for p in Document(target).paragraphs)
        else:
            assert pages[0].text in target.read_text(encoding="utf-8")


def test_failed_write_preserves_previous_file(tmp_path):
    target = tmp_path / "existing.md"
    target.write_text("keep me")
    def fail(path):
        path.write_text("partial")
        raise RuntimeError("failure")
    with pytest.raises(RuntimeError):
        atomic_write(target, fail)
    assert target.read_text() == "keep me"


def test_invalid_project_version(tmp_path):
    target = tmp_path / "invalid.itxt"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("project.json", json.dumps({"version": 99}))
    with pytest.raises(ValueError, match="Versión"):
        load_project(target, tmp_path)


def test_invalid_pdf(tmp_path):
    path = tmp_path / "broken.pdf"
    path.write_text("not a PDF")
    with pytest.raises(Exception):
        list(render_pages(path))
