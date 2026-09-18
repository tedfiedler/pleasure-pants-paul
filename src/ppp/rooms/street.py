"""Room 10: the street outside Rooster's, the finest dive in town. Cabs stop here."""

from __future__ import annotations

import pygame

from ppp.cab import Curb
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
CURB_Y = 118
ROAD_Y = 140
FAR_LANE_Y = 156  # standing this deep in the road is fatal


class Street(Room):
    number = 10
    name = "Outside Rooster's"
    description = (
        "You're standing on a sidewalk in the seedy part of a city that is all seedy "
        "part. A neon sign above the door says ROOSTER'S. A hydrant, a trash can, and "
        "some regrets keep you company. An alley opens off to the west."
    )
    horizon = CURB_Y
    edges = {"left": 12, "right": 10}
    spawns = {"default": (20, 150), 11: (76, 128), 13: (100, 136)}
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
        "alley": "To the west, a dark alley. It has the look of a place where things happen to people.",
    }

    def __init__(self) -> None:
        self.curb = Curb(ROAD_Y)
        self.road_timer = 0

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, CURB_Y, BLUE)
        pic.rect(0, 0, PIC_W, 100, DGREY)  # building face
        pic.rect(0, 100, PIC_W, 18, LGREY)  # base course
        pic.rect(0, CURB_Y, PIC_W, ROAD_Y - CURB_Y, LGREY)  # sidewalk
        pic.rect(0, ROAD_Y, PIC_W, 28, BLACK)  # road
        pic.line([(0, 154), (PIC_W - 1, 154)], YELLOW)
        pic.line([(0, CURB_Y), (PIC_W - 1, CURB_Y)], WHITE)
        for y in range(4, 100, 6):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        for y in range(4, 100, 12):
            for x in range(0, PIC_W, 10):
                pic.line([(x, y), (x, y + 5)], BLACK)
        for y in range(10, 100, 12):
            for x in range(5, PIC_W, 10):
                pic.line([(x, y), (x, y + 5)], BLACK)
        for wx in (14, 118):
            pic.rect(wx, 30, 22, 26, BROWN)
            pic.line([(wx, 30), (wx + 21, 55)], BLACK)
            pic.line([(wx + 21, 30), (wx, 55)], BLACK)
        pic.rect(68, 60, 24, 58, BROWN, 0)
        pic.rect(70, 62, 20, 56, RED)
        pic.rect(76, 70, 8, 8, BLACK)
        pic.pixel(87, 92, YELLOW)
        pic.rect(52, 14, 56, 14, BLACK)
        pic.rect(54, 16, 52, 10, LMAGENTA)
        pic.rect(58, 18, 44, 6, BLACK)
        pic.rect(24, 120, 6, 14, LRED)
        pic.rect(22, 122, 10, 3, LRED)
        pic.rect(130, 116, 14, 20, DGREY)
        pic.rect(128, 114, 18, 3, LGREY)
        pic.walls(CURB_Y)
        pic.rect(20, CURB_Y, 14, 18, None, 0)
        pic.rect(128, 114, 18, 24, None, 0)
        pic.rect(DOOR_X[0], CURB_Y, DOOR_X[1] - DOOR_X[0], 2, None, 2)

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        return self.curb.objects()

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.road_timer = 0
        self.curb.on_enter(game, from_room)

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and DOOR_X[0] <= ego.centre_x <= DOOR_X[1] and ego.y <= self.horizon + 1:
            game.new_room(11)
            return
        self.curb.update(game)
        # traffic
        if ego.y >= FAR_LANE_Y:
            self.road_timer += 1
            if self.road_timer == 12:
                game.print("Horns. Headlights. This is not a place to stand, [Paul].")
            elif self.road_timer >= 40:
                game.die(
                    "A bus, a delivery van and a moped hit you in that order. The moped "
                    "is the one that does it. [Paul] is now a stain with excellent tailoring."
                )
        else:
            self.road_timer = 0

    def said(self, game: Game, p: Parsed) -> bool:
        if self.curb.said(game, p):
            pass
        elif p.said("open", "door") or p.said("enter", "door") or p.said("enter", "bar") or p.said("enter"):
            if self.curb.near(game):
                game.new_room(13)
            else:
                game.print("Walk up to the door and it'll open. Even doors have standards, and you meet them.")
        elif p.said("knock", "door"):
            game.print("You knock. A voice inside yells something about a cover charge. There is no cover charge.")
        elif p.said("get", "trash") or p.said("search", "trash") or p.said("look", "trash", "can"):
            game.print("You root through the trash. You find nothing, and a bystander finds you disgusting.")
        elif p.said("kick", "hydrant"):
            game.print("Ow. The hydrant is unmoved. Your toe is not.")
        elif p.said("smell"):
            game.print("Stale beer, hot asphalt, and a hint of something the city would rather not discuss.")
        elif p.said("listen"):
            game.print("A muffled jukebox thumps from inside. It's playing something with a saxophone.")
        else:
            return False
        return True
