import asyncio
from dataclasses import dataclass
from typing import cast

import aiohttp

from .models import Board, CardStored, List
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
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(raise_for_status=True)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        assert self._session is not None
        return self._session

    @classmethod
    def from_env(cls) -> "TrelloClient":
        settings = TrelloSettings()  # type: ignore
        return cls(
            board_id=settings.trello_board_id,
            api_key=settings.trello_api_key,
            api_secret=settings.trello_api_secret,
        )

    @property
    def auth_params(self) -> dict[str, str]:
        return {"key": self._api_key, "token": self._api_secret}

    async def list_boards(self) -> list[BoardShallow]:
        url = "https://api.trello.com/1/members/me/boards"
        async with self.session.get(url, params=self.auth_params) as response:
            boards_json = await response.json()

        return [
            BoardShallow(id=board["id"], name=board["name"]) for board in boards_json
        ]

    async def get_board(self) -> Board[CardStored]:

        async def _get_board():
            async with self.session.get(
                f"https://api.trello.com/1/boards/{self._board_id}",
                params={"fields": "name", **self.auth_params},
            ) as response_board:
                return await response_board.json()

        async def _get_lists():
            async with self.session.get(
                f"https://api.trello.com/1/boards/{self._board_id}/lists",
                params={"fields": "name", **self.auth_params},
            ) as response_lists:
                return await response_lists.json()

        async def _get_cards():
            async with self.session.get(
                f"https://api.trello.com/1/boards/{self._board_id}/cards",
                params={"fields": "name,idList,pos", **self.auth_params},
            ) as response_cards:
                return await response_cards.json()

        board_json, lists_json, cards_json = await asyncio.gather(
            _get_board(), _get_lists(), _get_cards()
        )

        grouped_cards: dict[ListID, list[dict]] = {}
        for card in cards_json:
            grouped_cards.setdefault(card["idList"], []).append(card)

        lists: list[List[CardStored]] = []
        for list_ in lists_json:
            cards_for_this_list = grouped_cards.get(list_["id"], [])
            cards = [
                CardStored(id=card["id"], name=card["name"], pos=card["pos"])
                for card in cards_for_this_list
            ]
            cards.sort(key=lambda c: c.pos)
            lists.append(List(id=list_["id"], name=list_["name"], cards=cards))

        return Board(
            id=cast(str, board_json["id"]), name=board_json["name"], lists=lists
        )

    async def create_card(self, name: str, list_id: str):
        url = "https://api.trello.com/1/cards"
        async with self.session.post(
            url, json={"name": name, "idList": list_id}, params=self.auth_params
        ) as response:
            card_json = await response.json()
        return card_json["id"]

    async def change_parent(self, card_id: str, new_list_id: str):
        url = f"https://api.trello.com/1/cards/{card_id}"
        async with self.session.put(
            url, json={"idList": new_list_id}, params=self.auth_params
        ):
            pass

    async def rename_card(self, card_id: str, new_name: str):
        url = f"https://api.trello.com/1/cards/{card_id}"
        async with self.session.put(
            url, json={"name": new_name}, params=self.auth_params
        ):
            pass

    async def archive_card(self, card_id: str):
        url = f"https://api.trello.com/1/cards/{card_id}"
        async with self.session.put(
            url, json={"closed": True}, params=self.auth_params
        ):
            pass


__all__ = ["TrelloClient"]
