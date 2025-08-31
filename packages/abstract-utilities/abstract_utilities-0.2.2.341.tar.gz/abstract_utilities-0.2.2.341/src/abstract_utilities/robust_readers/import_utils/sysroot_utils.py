import os
from pathlib import Path
from .utils import *
from .dot_utils import *
def _find_top_package_dir(p: Path) -> Path | None:
    """Walk upward while there's an __init__.py; return the highest such dir."""
    p = p.resolve()
    if p.is_file():
        p = p.parent
    top = None
    while (p / "__init__.py").exists():
        top = p
        if p.parent == p:
            break
        p = p.parent
    return top
def _ensure_on_path(p: Path):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
def get_sysroot(filepath,i):
    for j in range(i):
        filepath = os.path.dirname(filepath)
    return filepath




