"""All rooms, registered in order."""

from ppp.game import Game
from ppp.rooms.bar import Bar
from ppp.rooms.street import Street

START_ROOM = 10


def register(game: Game) -> None:
    for room in (Street(), Bar()):
        game.add_room(room)
