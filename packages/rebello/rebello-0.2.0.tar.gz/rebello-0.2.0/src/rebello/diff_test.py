from copy import deepcopy

from .diff import find_changeset
from .models import (
    ArchiveCard,
    Board,
    CardNoID,
    CardWithID,
    ChangeList,
    CreateCard,
    List,
    RewordCard,
)

BOARD = Board(
    id="a1",
    name="Simple kanban",
    lists=[
        List(
            id="b2",
            name="To Do",
            cards=[
                CardWithID(id="c21", name="Say hello"),
                CardWithID(id="c22", name="Say goodnight"),
            ],
        ),
        List(
            id="b3",
            name="Done",
            cards=[
                CardWithID(id="c31", name="Basic project setup"),
            ],
        ),
    ],
)


class TestFindChangeset:
    @staticmethod
    def test_no_changes():
        assert find_changeset(board1=BOARD, board2=BOARD) == []

    @staticmethod
    def test_missing_list():
        board1 = BOARD
        board2 = deepcopy(board1)
        board2.lists[:] = []

        assert find_changeset(board1, board2) == []

    @staticmethod
    def test_removed_card():
        board1 = BOARD
        board2 = deepcopy(board1)
        archived_card = board2.lists[0].cards.pop(-1)

        assert find_changeset(board1, board2) == [ArchiveCard(card_id=archived_card.id)]

    @staticmethod
    def test_reword():
        board1 = BOARD
        board2 = deepcopy(board1)
        card = board2.lists[0].cards[0]
        old_name = card.name
        card.name = "changed"

        assert find_changeset(board1, board2) == [
            RewordCard(card_id=card.id, old_name=old_name, new_name=card.name)
        ]

    @staticmethod
    def test_creating_card_in_non_empty_list():
        board1: Board[CardNoID | CardWithID] = BOARD
        board2: Board[CardNoID | CardWithID] = deepcopy(board1)

        new_card = CardNoID(name="new name")
        cards = board2.lists[0].cards
        cards.append(new_card)  # type: ignore

        assert find_changeset(board1, board2) == [
            CreateCard(list_id=board2.lists[0].id, name=new_card.name)
        ]

    @staticmethod
    def test_creating_card_in_empty_list():
        board1: Board[CardNoID | CardWithID] = Board(
            id="a1",
            name="a1",
            lists=[List(id="b1", name="b1", cards=[])],
        )
        board2: Board[CardNoID | CardWithID] = deepcopy(board1)

        new_card = CardNoID(name="new name")
        cards = board2.lists[0].cards
        cards.append(new_card)  # type: ignore

        assert find_changeset(board1, board2) == [
            CreateCard(list_id=board2.lists[0].id, name=new_card.name)
        ]

    @staticmethod
    def test_move_card():
        board1: Board[CardNoID | CardWithID] = BOARD
        board2: Board[CardNoID | CardWithID] = deepcopy(board1)

        card = board2.lists[0].cards.pop(-1)
        board2.lists[1].cards.append(card)

        assert find_changeset(board1, board2) == [
            ChangeList(
                card_id=card.id,
                src_list_id=board1.lists[0].id,
                dest_list_id=board2.lists[1].id,
            )
        ]
