"""Room 17: the street outside the Kwik-Snak. A cab stop, a pay phone, a paper box."""

from __future__ import annotations

import pygame

from ppp.cab import Curb
from ppp.const import (
    BLACK,
    BLUE,
    DGREY,
    LBLUE,
    LCYAN,
    LGREY,
    PIC_W,
    RED,
    WHITE,
    YELLOW,
)
from ppp.game import Game
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

DOOR_X = (70, 90)
CURB_Y = 118
ROAD_Y = 140


class StoreStreet(Room):
    number = 17
    name = "Outside the Kwik-Snak"
    description = (
        "A brighter, emptier street. The Kwik-Snak glows behind a wall of glass, "
        "selling everything you need at three in the morning and nothing you need "
        "at any other time. A pay phone leans by the corner. A newspaper box guards "
        "the curb. Cabs stop here, if you ask nicely."
    )
    horizon = CURB_Y
    edges = {}
    spawns = {"default": (100, 136), 13: (100, 136), 18: (76, 128)}
    looks = {
        "store": "The Kwik-Snak: fluorescent light, a wall of glass, and a sign whose "
        "second K has never worked. Open all night, like your problems.",
        "building": "A flat-roofed box built to be a store and nothing else, ever.",
        "sign": "KWIK-SNAK, in yellow letters on red. Below it, smaller: OPEN 24 HRS. "
        "Below that, smaller still: NO SHIRT NO SHOES NO CREDIT.",
        "window": "Through the glass: shelves, a cooler, a magazine rack, and a clerk "
        "who has seen you coming since the cab.",
        "door": "Glass doors with a bell. Walk up and they'll open; they open for anyone.",
        "phone": "A pay phone on a post. The receiver is on the hook, which around here counts as a miracle.",
        "newspaper": "A newspaper box. The headline is about a [man|woman] who did something "
        "foolish in a [leisure suit|pantsuit]. Not you. Not yet.",
        "floor": "Clean sidewalk. Somebody sweeps here. Imagine.",
        "alley": "No alley here. This street is too respectable, which is to say it has a working streetlight.",
    }

    def __init__(self) -> None:
        self.curb = Curb(ROAD_Y)

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, CURB_Y, BLUE)
        pic.rect(0, 0, PIC_W, 100, LGREY)  # stucco front
        pic.rect(0, 0, PIC_W, 8, DGREY)  # roof line
        pic.rect(0, 100, PIC_W, 18, DGREY)  # base
        pic.rect(0, CURB_Y, PIC_W, ROAD_Y - CURB_Y, LGREY)
        pic.rect(0, ROAD_Y, PIC_W, 28, BLACK)
        pic.line([(0, 154), (PIC_W - 1, 154)], YELLOW)
        pic.line([(0, CURB_Y), (PIC_W - 1, CURB_Y)], WHITE)
        # the sign
        pic.rect(40, 12, 80, 16, RED)
        pic.rect(42, 14, 76, 12, YELLOW)
        for i in range(8):  # blocky letters
            pic.rect(46 + i * 9, 17, 6, 6, RED)
        pic.rect(46, 17, 6, 6, RED)
        # glass wall with shelves seen through it
        pic.rect(8, 34, 144, 66, LCYAN)
        pic.rect(8, 34, 144, 2, DGREY)
        for x in (56, 104):
            pic.line([(x, 34), (x, 99)], DGREY)
        for y in (52, 70, 88):
            pic.line([(12, y), (54, y)], DGREY)
            pic.line([(108, y), (148, y)], DGREY)
        for x in range(14, 54, 8):
            pic.rect(x, 46, 4, 6, RED)
            pic.rect(x + 2, 64, 4, 6, LBLUE)
            pic.rect(x, 82, 4, 6, YELLOW)
        for x in range(110, 148, 8):
            pic.rect(x, 46, 4, 6, LBLUE)
            pic.rect(x + 2, 64, 4, 6, RED)
        # glass door
        pic.rect(DOOR_X[0] - 2, 40, 24, 78, DGREY, 0)
        pic.rect(DOOR_X[0], 42, 20, 76, LCYAN)
        pic.line([(80, 42), (80, 117)], DGREY)
        pic.rect(74, 78, 3, 6, DGREY)
        pic.rect(83, 78, 3, 6, DGREY)
        # pay phone
        pic.rect(14, 60, 14, 22, BLUE, 0)
        pic.rect(16, 62, 10, 12, LBLUE)
        pic.rect(20, 82, 2, 36, DGREY, 0)
        pic.rect(18, 66, 2, 8, BLACK)  # receiver
        # newspaper box
        pic.rect(132, 104, 14, 18, RED, 0)
        pic.rect(134, 106, 10, 8, WHITE)
        pic.rect(130, 122, 18, 2, DGREY, 0)
        pic.walls(CURB_Y)
        pic.rect(12, CURB_Y, 12, 4, None, 0)
        pic.rect(130, CURB_Y, 18, 8, None, 0)
        pic.rect(DOOR_X[0], CURB_Y, DOOR_X[1] - DOOR_X[0], 2, None, 2)

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        return self.curb.objects()

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.curb.on_enter(game, from_room)
        if not game.flags.get("seen_storestreet"):
            game.flags["seen_storestreet"] = True
            game.print("A cleaner street. A lit street. You feel underdressed, which for you is a new direction.")

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and DOOR_X[0] <= ego.centre_x <= DOOR_X[1] and ego.y <= self.horizon + 1:
            game.new_room(18)
            return
        self.curb.update(game)

    def said(self, game: Game, p: Parsed) -> bool:
        near_phone = self.near(game, 8, 36, 130)
        if p.has("phone") and p.verb in ("use", "get", "call", "push", "talk", "open"):
            if not near_phone:
                game.print("Walk over to the phone. It's on the left, by the corner, and it's not cordless.")
            else:
                game.award("phone_time")
                game.print(
                    "You lift the receiver. It's sticky. You realise you have nobody to call, "
                    "so you call the time. It is later than you thought. It always is."
                )
        elif p.said("call", "time"):
            game.print("It's late. It's always late. Go inside; they have clocks.")
        elif self.curb.said(game, p):
            pass
        elif p.said("open", "door") or p.said("enter", "door") or p.said("enter", "store") or p.said("enter"):
            if self.curb.near(game):
                game.new_room(13)
            elif self.near(game, DOOR_X[0], DOOR_X[1], 130):
                game.new_room(18)
            else:
                game.print("Walk up to the glass doors. They slide open for anyone; it's a low bar, and you clear it.")
        elif p.said("get", "newspaper") or p.said("look", "newspaper", "rol") or p.said("open", "newspaper"):
            game.award("newspaper")
            game.print("The box wants a quarter. You want the quarter more. You read the headline through the glass.")
        elif p.said("smell"):
            game.print("Bleach, fryer grease, and the cold electric smell of a cooler working too hard.")
        elif p.said("listen"):
            game.print("The hum of fluorescent tubes. A bell on the door. A cab, somewhere, not for you.")
        else:
            return False
        return True
