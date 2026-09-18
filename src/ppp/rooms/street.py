"""Room 10: the street outside Rooster's, the finest dive in town."""

from __future__ import annotations

from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    DGREY,
    LGREY,
    LMAGENTA,
    LRED,
    PIC_W,
    RED,
    WHITE,
    YELLOW,
)
from ppp.game import Game
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

DOOR_X = (70, 90)  # walk into this x range at the door line to enter


class Street(Room):
    number = 10
    name = "Outside Rooster's"
    description = (
        "You're standing on a sidewalk in the seedy part of a city that is all seedy "
        "part. A neon sign above the door says ROOSTER'S. A hydrant, a trash can, and "
        "some regrets keep you company."
    )
    horizon = 118
    edges = {"left": 10, "right": 10}
    spawns = {"default": (20, 150), 11: (76, 128)}
    looks = {
        "sign": "It says ROOSTER'S in pink neon. The second O is out, which is the "
        "kind of detail that tells you everything about the place.",
        "door": "A heavy wooden door with a small square window painted over from the inside.",
        "building": "A squat brick building that has seen better decades. All of them.",
        "hydrant": "A fire hydrant. It has a faint smell of dog.",
        "trash": "A dented trash can. Inside: a pizza box, a shoe, and a newspaper from before you were born.",
        "window": "The windows are boarded. Whoever's inside prefers it that way.",
        "floor": "The sidewalk is cracked and glittering with broken glass. Classy.",
        "dog": "There's no dog here, only the evidence of one.",
    }

    def draw(self, pic: Picture) -> None:
        # sky, building, sidewalk, road
        pic.rect(0, 0, PIC_W, 118, BLUE)
        pic.rect(0, 0, PIC_W, 100, DGREY)  # building face
        pic.rect(0, 100, PIC_W, 18, LGREY)  # base course
        pic.rect(0, 118, PIC_W, 22, LGREY)  # sidewalk
        pic.rect(0, 140, PIC_W, 28, BLACK)  # road
        pic.line([(0, 154), (PIC_W - 1, 154)], YELLOW)
        pic.line([(0, 118), (PIC_W - 1, 118)], WHITE)
        # brick courses
        for y in range(4, 100, 6):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        for y in range(4, 100, 12):
            for x in range(0, PIC_W, 10):
                pic.line([(x, y), (x, y + 5)], BLACK)
        for y in range(10, 100, 12):
            for x in range(5, PIC_W, 10):
                pic.line([(x, y), (x, y + 5)], BLACK)
        # boarded windows
        for wx in (14, 118):
            pic.rect(wx, 30, 22, 26, BROWN)
            pic.line([(wx, 30), (wx + 21, 55)], BLACK)
            pic.line([(wx + 21, 30), (wx, 55)], BLACK)
        # door
        pic.rect(68, 60, 24, 58, BROWN, 0)  # unwalkable wall
        pic.rect(70, 62, 20, 56, RED)
        pic.rect(76, 70, 8, 8, BLACK)
        pic.pixel(87, 92, YELLOW)
        # neon sign
        pic.rect(52, 14, 56, 14, BLACK)
        pic.rect(54, 16, 52, 10, LMAGENTA)
        pic.rect(58, 18, 44, 6, BLACK)
        # hydrant & trash can
        pic.rect(24, 120, 6, 14, LRED)
        pic.rect(22, 122, 10, 3, LRED)
        pic.rect(130, 116, 14, 20, DGREY)
        pic.rect(128, 114, 18, 3, LGREY)
        # only the sidewalk and road are walkable
        pic.walls(118)
        pic.rect(20, 118, 14, 18, None, 0)  # hydrant blocks
        pic.rect(128, 114, 18, 24, None, 0)  # trash can blocks
        # make the door threshold a signal band
        pic.rect(DOOR_X[0], 118, DOOR_X[1] - DOOR_X[0], 2, None, 2)

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and DOOR_X[0] <= ego.centre_x <= DOOR_X[1] and ego.y <= self.horizon + 1:
            game.new_room(11)
        elif ego.direction and ego.y >= 158 and game.cycle_count % 40 == 0:
            game.print("Paul wanders into traffic. Traffic wins. Try to stay on the sidewalk.")

    def said(self, game: Game, p: Parsed) -> bool:
        if p.said("open", "door") or p.said("enter", "door") or p.said("enter", "bar") or p.said("enter"):
            game.print("Walk up to the door and it'll open. Even doors have standards, and you meet them.")
        elif p.said("knock", "door"):
            game.print("You knock. A voice inside yells something about a cover charge. There is no cover charge.")
        elif p.said("get", "trash") or p.said("look", "trash", "can"):
            game.print("You root through the trash. You find nothing, and a bystander finds you disgusting.")
        elif p.said("kick", "hydrant"):
            game.print("Ow. The hydrant is unmoved. Your toe is not.")
        elif p.said("call", "cab") or p.said("look", "cab"):
            game.print("You wave at the empty street. No cab. Maybe later, when you have somewhere to be.")
        elif p.said("smell"):
            game.print("Stale beer, hot asphalt, and a hint of something the city would rather not discuss.")
        elif p.said("listen"):
            game.print("A muffled jukebox thumps from inside. It's playing something with a saxophone.")
        else:
            return False
        return True
