import json
from pathlib import Path
import re
import pytest
import responses
from .trello import TrelloClient


class TestTrelloClient:
    @staticmethod
    @pytest.fixture
    def client(monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("TRELLO_API_KEY", "api-key")
        monkeypatch.setenv("TRELLO_API_SECRET", "api-secret")
        monkeypatch.setenv("TRELLO_BOARD_ID", "boardid1")
        return TrelloClient.from_env()

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
    def test_list_boards(client: TrelloClient):
        with (Path(__file__).parent / "trello_responses" / "boards.json").open() as f:
            boards_json = json.load(f)

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, re.compile(r"https://api.trello.com/"), json=boards_json
            )
            boards = client.list_boards()

        assert len(boards) == 1
        assert boards[0].id == "5abbe4b7ddc1b351ef961414"
        assert boards[0].name == "Trello Platform Changes"

    @staticmethod
    def test_get_board(client: TrelloClient):
        with (Path(__file__).parent / "trello_responses" / "board.json").open() as f:
            board_json = json.load(f)

        with (Path(__file__).parent / "trello_responses" / "lists.json").open() as f:
            lists_json = json.load(f)

        with (Path(__file__).parent / "trello_responses" / "cards.json").open() as f:
            cards_json = json.load(f)

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                re.compile(r"https://api.trello.com/1/boards/\w+[^/]+$"),
                json=board_json,
            )
            rsps.add(
                responses.GET,
                re.compile(r"https://api.trello.com/1/boards/\w*/lists"),
                json=lists_json,
            )
            rsps.add(
                responses.GET,
                re.compile(r"https://api.trello.com/1/boards/\w*/cards"),
                json=cards_json,
            )

            board = client.get_board()

        assert board.id == "boardid1"
        assert board.name == "Trello Platform Changes"

        assert len(board.lists) > 0
        a_list = board.lists[0]
        assert a_list.id == "list-id"
        assert a_list.name == "Things to buy today"

        assert len(a_list.cards) > 0
        assert a_list.cards[0].id == "cardid1"
        assert a_list.cards[0].name == "trello CLI with editor interface"

    @staticmethod
    def test_create_card(client: TrelloClient):
        name = "foo bar"
        list_id = "abc123"

        with (Path(__file__).parent / "trello_responses" / "cards.json").open() as f:
            card_json = json.load(f)[0]

        with responses.RequestsMock() as rsps:
            rsps.post(
                re.compile(r"https://api.trello.com/1/cards[^/]+$"),
                match=[
                    responses.json_params_matcher({"name": name, "idList": list_id})
                ],
                json=card_json,
            )
            card_id = client.create_card(name=name, list_id=list_id)

        assert card_id == "cardid1"

    @staticmethod
    def test_change_parent(client: TrelloClient):
        card_id = "cardid1"
        card_json = {
            "id": card_id,
            "name": "trello CLI with editor interface",
            "idList": "oldlistid",
        }
        new_list_id = "newlistid"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.PUT,
                re.compile(r"https://api.trello.com/1/cards/cardid1[^/]+$"),
                match=[responses.json_params_matcher({"idList": new_list_id})],
                json={**card_json, "idList": new_list_id},
            )

            client.change_parent(card_id=card_id, new_list_id=new_list_id)

    @staticmethod
    def test_rename_card(client: TrelloClient):
        card_id = "cardid1"
        old_card_json = {
            "id": card_id,
            "name": "trello CLI with editor interface",
            "idList": "oldlistid",
        }
        new_name = "new name"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.PUT,
                re.compile(r"https://api.trello.com/1/cards/cardid1[^/]+$"),
                match=[responses.json_params_matcher({"name": new_name})],
                json={**old_card_json, "name": new_name},
            )

            client.rename_card(card_id=card_id, new_name=new_name)

    @staticmethod
    def test_archive_card(client: TrelloClient):
        card_id = "cardid1"
        old_card_json = {
            "id": card_id,
            "name": "trello CLI with editor interface",
            "idList": "oldlistid",
            "closed": False,
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.PUT,
                re.compile(r"https://api.trello.com/1/cards/cardid1[^/]+$"),
                match=[responses.json_params_matcher({"closed": True})],
                json={**old_card_json, "closed": True},
            )

            client.archive_card(card_id=card_id)
