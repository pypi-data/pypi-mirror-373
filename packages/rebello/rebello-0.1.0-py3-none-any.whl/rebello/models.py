"""
The main models used across the app.

In bigger projects each "module" should depend on its own set of models for modularity, but it's a small project so
a single coupling point is fine.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass
class CardWithID:
    id: str
    name: str


@dataclass
class CardNoID:
    name: str


T = TypeVar("T", covariant=True)


@dataclass
class List(Generic[T]):
    id: str
    name: str
    cards: list[T]


@dataclass
class Board(Generic[T]):
    id: str
    name: str
    lists: list[List[T]]


@dataclass
class ChangeList:
    """Move card from one list to another."""

    card_id: str
    src_list_id: str
    dest_list_id: str


@dataclass
class RewordCard:
    card_id: str
    old_name: str
    new_name: str


@dataclass
class ArchiveCard:
    card_id: str


@dataclass
class CreateCard:
    list_id: str
    name: str


type Change = ChangeList | RewordCard | ArchiveCard | CreateCard
type Changeset = list[Change]
