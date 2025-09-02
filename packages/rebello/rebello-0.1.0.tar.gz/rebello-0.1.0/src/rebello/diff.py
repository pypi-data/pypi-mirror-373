from dataclasses import dataclass
from typing import Protocol
from .models import (
    ArchiveCard,
    Board,
    CardNoID,
    CardWithID,
    ChangeList,
    Changeset,
    CreateCard,
    RewordCard,
)


class HasID(Protocol):
    @property
    def id(self) -> str: ...


@dataclass
class CardShallow:
    id: str
    name: str
    list_id: str


def find_changeset(
    board1: Board[CardWithID], board2: Board[CardWithID | CardNoID]
) -> Changeset:
    list1_ids = {a_list.id for a_list in board1.lists}
    list2_ids = {a_list.id for a_list in board2.lists}
    common_list_ids = list1_ids.intersection(list2_ids)

    cards1 = {
        card.id: CardShallow(id=card.id, name=card.name, list_id=a_list.id)
        for a_list in board1.lists
        if a_list.id in common_list_ids
        for card in a_list.cards
    }
    cards2 = {
        card.id: CardShallow(id=card.id, name=card.name, list_id=a_list.id)
        for a_list in board2.lists
        if a_list.id in common_list_ids
        for card in a_list.cards
        if isinstance(card, CardWithID)
    }

    changeset = []

    removed_ids = set(cards1.keys()).difference(cards2.keys())
    for removed_id in removed_ids:
        changeset.append(ArchiveCard(card_id=removed_id))

    common_ids = set(cards1.keys()).intersection(cards2.keys())
    for common_id in common_ids:
        card1 = cards1[common_id]
        card2 = cards2[common_id]

        if card2.name != card1.name:
            changeset.append(
                RewordCard(
                    card_id=common_id,
                    old_name=card1.name,
                    new_name=card2.name,
                )
            )

        if card2.list_id != card1.list_id:
            changeset.append(
                ChangeList(
                    card_id=common_id,
                    src_list_id=card1.list_id,
                    dest_list_id=card2.list_id,
                )
            )

    for a_list in board2.lists:
        for card in a_list.cards:
            if not isinstance(card, CardNoID):
                continue
            changeset.append(CreateCard(list_id=a_list.id, name=card.name))

    return changeset
