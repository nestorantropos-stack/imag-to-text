"""Bundle the official Python runtime without generating a custom executable."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).parent
target = root / "dist" / "ImagToText-Runtime"
runtime = target / "runtime"
runtime.mkdir(parents=True, exist_ok=True)
base = Path(sys.base_prefix)
for file in base.iterdir():
    if file.is_file() and (file.suffix.lower() in (".exe", ".dll") or file.name == "LICENSE.txt"):
        shutil.copy2(file, runtime / file.name)
for name in ("DLLs", "tcl", "Lib"):
    shutil.copytree(base / name, runtime / name, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("site-packages", "__pycache__", "test", "tests", "idle_test"))
shutil.copytree(Path(sys.prefix) / "Lib" / "site-packages", runtime / "Lib" / "site-packages",
                dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
for name in ("app.py", "core.py", "smoke.py", "README.md", "THIRD_PARTY_NOTICES.md", "Install.ps1", "Install.cmd", "Uninstall.ps1"):
    shutil.copy2(root / name, target / name)
shutil.copytree(root / "licenses", target / "licenses", dirs_exist_ok=True)
shutil.make_archive(str(root / "dist" / "Imag-to-Text-1.0.0-Windows"), "zip", target)
print(target)
