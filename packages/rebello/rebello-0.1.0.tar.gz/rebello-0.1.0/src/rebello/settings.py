from pydantic_settings import BaseSettings


class TrelloSettings(BaseSettings):
    trello_api_key: str
    trello_api_secret: str
    trello_board_id: str
