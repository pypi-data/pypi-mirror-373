"""
EDI = Editor Driven Interface
"""

import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile


@contextmanager
def temp_path(ext: str):
    with NamedTemporaryFile(suffix=ext) as file:
        yield Path(file.name)


def open_in_editor(path: Path):
    cmd = [os.environ["EDITOR"], str(path)]
    print(f"Running '{cmd}'")
    proc = subprocess.run(cmd)

    return proc.returncode == 0
