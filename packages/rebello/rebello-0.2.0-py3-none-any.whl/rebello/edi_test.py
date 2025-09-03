from pathlib import Path

import pytest

from .edi import open_in_editor, temp_path


class TestTempPath:
    @staticmethod
    def test_sample():
        with temp_path(".md") as path:
            assert path is not None
            assert ".md" in str(path)

            path.write_text("hello")
            assert path.read_text() == "hello"


class TestOpenInEditor:
    @staticmethod
    def test_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        tmp_file = tmp_path / "hello.txt"
        tmp_file.write_text("hello")

        # Always returns status code 0.
        monkeypatch.setenv("EDITOR", "true")

        success = open_in_editor(tmp_file)

        assert success is True

    @staticmethod
    def test_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        tmp_file = tmp_path / "hello.txt"
        tmp_file.write_text("hello")

        # Always returns status code 0.
        monkeypatch.setenv("EDITOR", "false")

        success = open_in_editor(tmp_file)

        assert success is False
