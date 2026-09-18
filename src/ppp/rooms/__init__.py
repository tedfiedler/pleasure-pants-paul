"""All rooms, registered in order."""

from ppp.game import Game
from ppp.rooms.alley import Alley
from ppp.rooms.bar import Bar
from ppp.rooms.mensroom import MensRoom
from ppp.rooms.street import Street
from ppp.rooms.taxi import Taxi

START_ROOM = 10


def register(game: Game) -> None:
    for room in (Street(), Bar(), Alley(), Taxi(), MensRoom()):
        game.add_room(room)
