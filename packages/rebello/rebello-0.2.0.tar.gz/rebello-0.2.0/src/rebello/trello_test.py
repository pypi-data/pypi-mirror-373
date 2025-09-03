import json
import re
from pathlib import Path

import pytest
from aioresponses import aioresponses

from .trello import TrelloClient


class TestTrelloClient:
    @staticmethod
    @pytest.fixture
    async def client(monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("TRELLO_API_KEY", "api-key")
        monkeypatch.setenv("TRELLO_API_SECRET", "api-secret")
        monkeypatch.setenv("TRELLO_BOARD_ID", "boardid1")
        client = TrelloClient.from_env()
        async with client:
            yield client

    @staticmethod
    def test_init_from_env_vars(client: TrelloClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("TRELLO_API_KEY", "api-key2")
        monkeypatch.setenv("TRELLO_API_SECRET", "api-secret2")
        client2 = TrelloClient.from_env()

        assert client is not None
        assert client2 is not None

        assert client._api_key != client2._api_key
        assert client._api_secret != client2._api_secret

    @staticmethod
    async def test_list_boards(client: TrelloClient):
        with (Path(__file__).parent / "trello_responses" / "boards.json").open() as f:
            boards_json = json.load(f)

        with aioresponses() as m:
            m.get(re.compile(r"https://api.trello.com/.*"), payload=boards_json)
            boards = await client.list_boards()

        assert len(boards) == 1
        assert boards[0].id == "5abbe4b7ddc1b351ef961414"
        assert boards[0].name == "Trello Platform Changes"

    @staticmethod
    async def test_get_board(client: TrelloClient):
        base = Path(__file__).parent / "trello_responses"
        board_json = json.load((base / "board.json").open())
        lists_json = json.load((base / "lists.json").open())
        cards_json = json.load((base / "cards.json").open())

        with aioresponses() as m:
            m.get(
                re.compile(r"https://api.trello.com/1/boards/\w+[^/]+$"),
                payload=board_json,
            )
            m.get(
                re.compile(r"https://api.trello.com/1/boards/\w*/lists"),
                payload=lists_json,
            )
            m.get(
                re.compile(r"https://api.trello.com/1/boards/\w*/cards"),
                payload=cards_json,
            )

            board = await client.get_board()

        assert board.id == "idboard1"
        assert board.name == "Trello Platform Changes"
        assert len(board.lists) > 0

    @staticmethod
    async def test_create_card(client: TrelloClient):
        name, list_id = "foo bar", "abc123"
        card_json = json.load(
            (Path(__file__).parent / "trello_responses" / "cards.json").open()
        )[0]

        with aioresponses() as m:
            m.post(
                re.compile(r"https://api.trello.com/1/cards[^/]+$"), payload=card_json
            )
            card_id = await client.create_card(name=name, list_id=list_id)

        assert card_id == "idcard2"

    @staticmethod
    async def test_change_parent(client: TrelloClient):
        card_id, new_list_id = "cardid1", "newlistid"
        card_json = {"id": card_id, "idList": new_list_id, "name": "trello CLI"}

        with aioresponses() as m:
            m.put(
                re.compile(r"https://api.trello.com/1/cards/cardid1[^/]+$"),
                payload=card_json,
            )
            await client.change_parent(card_id=card_id, new_list_id=new_list_id)

    @staticmethod
    async def test_rename_card(client: TrelloClient):
        card_id, new_name = "cardid1", "new name"
        card_json = {"id": card_id, "name": new_name, "idList": "oldlistid"}

        with aioresponses() as m:
            m.put(
                re.compile(r"https://api.trello.com/1/cards/cardid1[^/]+$"),
                payload=card_json,
            )
            await client.rename_card(card_id=card_id, new_name=new_name)

    @staticmethod
    async def test_archive_card(client: TrelloClient):
        card_id = "cardid1"
        card_json = {"id": card_id, "closed": True}

        with aioresponses() as m:
            m.put(
                re.compile(r"https://api.trello.com/1/cards/cardid1[^/]+$"),
                payload=card_json,
            )
            await client.archive_card(card_id=card_id)
