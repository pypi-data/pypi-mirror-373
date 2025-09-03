import importlib
from pathlib import Path

import pytest

from .md import parse_board, render_board
from .models import Board, CardWithID

TEST_PKG = "rebello.md_test_files.pairs"
TEST_DIR = Path(__file__).parent / "md_test_files" / "pairs"
EXAMPLE_NAMES = [path.stem for path in TEST_DIR.glob("*.py")]
MALFORMED_DIRS = Path(__file__).parent / "md_test_files" / "malformed"


class TestRenderBoard:
    @staticmethod
    @pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
    def test_module_to_md(example_name: str, tmp_path: Path):
        input_module = importlib.import_module(f"{TEST_PKG}.{example_name}")
        board: Board[CardWithID] = getattr(input_module, "board")
        ref_out = (TEST_DIR / (example_name + ".md")).read_text()
        out_file = tmp_path / "out.md"

        render_board(out_file, board)

        rendered_text = out_file.read_text()
        assert rendered_text == ref_out


class TestParseBoard:
    @staticmethod
    @pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
    def test_md_to_module_contents(example_name: str):
        in_file = TEST_DIR / (example_name + ".md")
        module = importlib.import_module(f"{TEST_PKG}.{example_name}")
        ref_board: Board = getattr(module, "board")

        parsed_board = parse_board(in_file)

        assert parsed_board is not None
        assert parsed_board == ref_board

    @staticmethod
    @pytest.mark.parametrize("example_name", ["empty", "no_board_id"])
    def test_malformed_board(example_name: str):
        in_file = MALFORMED_DIRS / (example_name + ".md")

        with pytest.raises(ValueError) as e:
            _ = parse_board(in_file)

        assert e.match(r"No valid board header")

    @staticmethod
    @pytest.mark.parametrize("example_name", ["no_list_id"])
    def test_malformed_list(example_name: str):
        in_file = MALFORMED_DIRS / (example_name + ".md")

        board = parse_board(in_file)

        assert len(board.lists)
