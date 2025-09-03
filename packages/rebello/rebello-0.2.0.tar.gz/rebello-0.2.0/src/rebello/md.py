import re
from pathlib import Path

from .models import Board, CardNoID, CardWithID, List


def render_board(path: Path, board: Board[CardWithID | CardNoID]):
    with path.open("w") as f:
        f.write(f"# [{board.id}] {board.name}\n")

        for col in board.lists:
            f.write("\n")
            f.write(f"## [{col.id}] {col.name}\n")
            f.write("\n")

            for card in col.cards:
                if isinstance(card, CardWithID):
                    f.write(f"* [{card.id}] {card.name}\n")
                else:
                    f.write(f"* {card.name}\n")


def parse_board(path: Path) -> Board[CardWithID | CardNoID]:
    with path.open() as f:
        board_id: str | None = None
        board_name: str | None = None

        lists: list[List] = []

        for line_with_n in f:
            line = line_with_n.strip()
            if (h1_match := re.match(r"^\s*# \[(\w+)\] (.*)$", line)) is not None:
                board_id = h1_match.group(1)
                board_name = h1_match.group(2)

            elif (h2_match := re.match(r"^\s*## \[(\w+)\] (.*)$", line)) is not None:
                # We'll embrace deeply mutable data structures. Normally I don't do it but it's handy here. We create
                # `cards=[]` ahead of time and will mutate it later on.
                lists.append(
                    List(id=h2_match.group(1), name=h2_match.group(2), cards=[])
                )

            elif (li_match := re.match(r"^\s*[*-] \[(\w+)\] (.*)$", line)) is not None:
                try:
                    latest_list = lists[-1]
                except IndexError:
                    # TODO: add error handling
                    pass

                latest_list.cards.append(
                    CardWithID(id=li_match.group(1), name=li_match.group(2))
                )

            elif (li_match := re.match(r"^\s*[*-] (.*)$", line)) is not None:
                try:
                    latest_list = lists[-1]
                except IndexError:
                    # TODO: add error handling
                    pass

                latest_list.cards.append(CardNoID(name=li_match.group(1)))

    if not board_id or not board_name:
        raise ValueError("No valid board header in file", path)

    return Board(id=board_id, name=board_name, lists=lists)
