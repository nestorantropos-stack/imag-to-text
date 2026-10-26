"""Collect redistribution notices shipped by every installed dependency."""
from importlib.metadata import distributions
from pathlib import Path
import shutil
import sys

root = Path(__file__).parent / "licenses"
root.mkdir(exist_ok=True)
for distribution in distributions():
    name = distribution.metadata["Name"]
    for entry in distribution.files or []:
        if any(term in str(entry).lower() for term in ("license", "licence", "notice", "copying", "copyright")) and entry.suffix.lower() not in (".py", ".pyc"):
            source = Path(distribution.locate_file(entry))
            if source.is_file():
                target = root / name / str(entry).replace("..", "_")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
python_root = Path(sys.base_prefix)
for source in [python_root / "LICENSE.txt", *python_root.glob("tcl/*/license*")]:
    if source.is_file():
        target = root / "Python-Tcl-Tk" / source.parent.name / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
