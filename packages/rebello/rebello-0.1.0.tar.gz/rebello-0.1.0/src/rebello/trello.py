from dataclasses import dataclass
from typing import cast

import requests

from .models import Board, CardWithID, List
from .settings import TrelloSettings


@dataclass
class BoardShallow:
    id: str
    name: str


type ListID = str


class TrelloClient:
    def __init__(self, board_id: str, api_key: str, api_secret: str):
        self._board_id = board_id
        self._api_key = api_key
        self._api_secret = api_secret
        self._session = requests.Session()
        self._session.params.update({"key": self._api_key, "token": self._api_secret})

    @classmethod
    def from_env(cls) -> "TrelloClient":
        settings = TrelloSettings()  # type: ignore
        return cls(
            board_id=settings.trello_board_id,
            api_key=settings.trello_api_key,
            api_secret=settings.trello_api_secret,
        )

    def list_boards(self) -> list[BoardShallow]:
        url = "https://api.trello.com/1/members/me/boards"
        response = self._session.get(url)
        response.raise_for_status()
        boards_json = response.json()
        return [
            BoardShallow(id=board["id"], name=board["name"]) for board in boards_json
        ]

    def get_board(self) -> Board:
        response_board = self._session.get(
            f"https://api.trello.com/1/boards/{self._board_id}",
            params={"fields": "name"},
        )
        response_board.raise_for_status()
        board_json = response_board.json()

        response_lists = self._session.get(
            f"https://api.trello.com/1/boards/{self._board_id}/lists",
            params={"fields": "name"},
        )
        response_lists.raise_for_status()
        lists_json = response_lists.json()

        response_cards = self._session.get(
            f"https://api.trello.com/1/boards/{self._board_id}/cards",
            params={"fields": "name,idList"},
        )
        response_cards.raise_for_status()
        cards_json = response_cards.json()

        grouped_cards: dict[ListID, list[dict]] = {}
        for card in cards_json:
            grouped_cards.setdefault(card["idList"], []).append(card)

        lists: list[List] = []
        for list_ in lists_json:
            cards_for_this_list = grouped_cards.get(list_["id"], [])
            cards = [
                CardWithID(id=card["id"], name=card["name"])
                for card in cards_for_this_list
            ]
            lists.append(List(id=list_["id"], name=list_["name"], cards=cards))

        return Board(
            id=cast(str, board_json["id"]), name=board_json["name"], lists=lists
        )

    def create_card(self, name: str, list_id: str):
        url = "https://api.trello.com/1/cards"
        response = self._session.post(url, json={"name": name, "idList": list_id})
        response.raise_for_status()
        card_json = response.json()
        return card_json["id"]

    def change_parent(self, card_id: str, new_list_id: str):
        url = f"https://api.trello.com/1/cards/{card_id}"
        response = self._session.put(url, json={"idList": new_list_id})
        response.raise_for_status()

    def rename_card(self, card_id: str, new_name: str):
        url = f"https://api.trello.com/1/cards/{card_id}"
        response = self._session.put(url, json={"name": new_name})
        response.raise_for_status()

    def archive_card(self, card_id: str):
        url = f"https://api.trello.com/1/cards/{card_id}"
        response = self._session.put(url, json={"closed": True})
        response.raise_for_status()


__all__ = ["TrelloClient"]
