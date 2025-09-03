from rebello.models import Board, CardWithID, List

board = Board(
    id="1",
    name="One of everything",
    lists=[
        List(
            id="2",
            name="Col",
            cards=[
                CardWithID(id="3", name="Say hello"),
            ],
        ),
    ],
)
