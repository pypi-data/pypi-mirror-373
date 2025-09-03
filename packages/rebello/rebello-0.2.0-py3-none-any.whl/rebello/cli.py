import asyncio
from argparse import ArgumentParser

from .diff import find_changeset
from .edi import open_in_editor, temp_path
from .md import parse_board, render_board
from .models import ArchiveCard, ChangeList, CreateCard, RewordCard
from .trello import TrelloClient


async def async_main():
    parser = ArgumentParser(description="Edits a trello board")
    parser.parse_args()

    client = TrelloClient.from_env()
    async with client:
        board = await client.get_board()

        with temp_path(".md") as path:
            render_board(path, board)
            success = open_in_editor(path)
            if not success:
                print(f"Error editing {path}")
                exit(1)

            edited_board = parse_board(path)

        changeset = find_changeset(board, edited_board)
        print(f"Executing {len(changeset)} changes:")
        for change in changeset:
            if isinstance(change, ChangeList):
                print(
                    f"* for [{change.card_id}], "
                    f"change parent [{change.src_list_id}] -> [{change.dest_list_id}]"
                )
                await client.change_parent(
                    card_id=change.card_id, new_list_id=change.dest_list_id
                )
            elif isinstance(change, RewordCard):
                print(
                    f"* for [{change.card_id}], "
                    f"rename [{change.old_name}] -> [{change.new_name}]"
                )
                await client.rename_card(card_id=change.card_id, new_name=change.new_name)
            elif isinstance(change, ArchiveCard):
                print(f"* archive [{change.card_id}]")
                await client.archive_card(card_id=change.card_id)
            elif isinstance(change, CreateCard):
                print(f"* create '{change.name}' under [{change.list_id}]")
                await client.create_card(name=change.name, list_id=change.list_id)


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
