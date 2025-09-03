from rebello.models import Board, CardWithID, List

board = Board(
    id="1",
    name="Simple kanban",
    lists=[
        List(
            id="2",
            name="To Do",
            cards=[
                CardWithID(id="21", name="Say hello"),
                CardWithID(id="22", name="Say goodnight"),
            ],
        ),
        List(
            id="3",
            name="Done",
            cards=[
                CardWithID(id="31", name="Basic project setup"),
            ],
        ),
    ],
)
