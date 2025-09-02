"""
EDI = Editor Driven Interface
"""

from pathlib import Path
import os
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
import subprocess


@contextmanager
def temp_path(ext: str):
    with NamedTemporaryFile(suffix=ext) as file:
        yield Path(file.name)


def open_in_editor(path: Path):
    cmd = [os.environ["EDITOR"], str(path)]
    print(f"Running '{cmd}'")
    proc = subprocess.run(cmd)

    return proc.returncode == 0
