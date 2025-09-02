from rebello.models import Board, CardNoID, List

board = Board(
    id="1",
    name="Board",
    lists=[
        List(
            id="2",
            name="Col",
            cards=[
                CardNoID(name="Say hello"),
            ],
        ),
    ],
)
