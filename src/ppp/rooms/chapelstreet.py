"""Room 23: outside the Chapel of Eternal Regret. Walk-ins welcome."""

from __future__ import annotations

import pygame

from ppp.cab import Curb
from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    DGREY,
    GREEN,
    LBLUE,
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

DOOR_X = (70, 90)
CURB_Y = 118
ROAD_Y = 140


class ChapelStreet(Room):
    number = 23
    name = "Outside the chapel"
    description = (
        "A small white chapel with a steeple that leans, a heart-shaped sign, and "
        "window boxes of plastic flowers. CHAPEL OF ETERNAL REGRET, says the sign, "
        "and under it: WALK-INS WELCOME. NO REFUNDS. Cabs stop at the curb."
    )
    horizon = CURB_Y
    edges = {}
    spawns = {"default": (100, 136), 13: (100, 136), 24: (76, 128)}
    looks = {
        "building": "A clapboard chapel painted white last decade, with a steeple, a bell, "
        "and a neon heart that flickers between pink and off.",
        "sign": "A heart-shaped sign: CHAPEL OF ETERNAL REGRET. WALK-INS WELCOME. NO REFUNDS. "
        "Somebody has scratched a small 'help' into the paint.",
        "door": "A white door with a brass heart for a knocker. It's unlocked. It's always unlocked.",
        "rose": "Window boxes of plastic flowers, faded to the colour of old gum.",
        "window": "Stained glass, seen from outside: a heart, an arrow, and what might be a dollar sign.",
        "bell": "A bell in the steeple, rung after every wedding, which is why the neighbours moved.",
        "floor": "Clean sidewalk with a scatter of rice that the pigeons have given up on.",
    }

    def __init__(self) -> None:
        self.curb = Curb(ROAD_Y)

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, CURB_Y, BLUE)
        pic.rect(0, 100, PIC_W, 18, LGREY)
        pic.rect(0, CURB_Y, PIC_W, ROAD_Y - CURB_Y, LGREY)
        pic.rect(0, ROAD_Y, PIC_W, 28, BLACK)
        pic.line([(0, 154), (PIC_W - 1, 154)], YELLOW)
        pic.line([(0, CURB_Y), (PIC_W - 1, CURB_Y)], WHITE)
        # neighbours, dim
        pic.rect(0, 40, 30, 60, DGREY)
        pic.rect(130, 36, 30, 64, DGREY)
        # the chapel: white clapboard, roof, steeple
        pic.rect(32, 44, 96, 56, WHITE)
        for y in range(48, 100, 6):
            pic.line([(32, y), (127, y)], LGREY)
        pic.poly([(28, 44), (80, 20), (132, 44)], BROWN)
        pic.rect(72, 4, 16, 18, WHITE)
        pic.poly([(70, 4), (80, -6), (90, 4)], BROWN)
        pic.rect(78, 10, 4, 6, BLACK)  # bell slot
        pic.pixel(80, 13, YELLOW)
        # stained glass either side of the door
        for wx in (42, 100):
            pic.rect(wx, 54, 18, 26, BLACK)
            pic.rect(wx + 2, 56, 6, 10, LRED)
            pic.rect(wx + 10, 56, 6, 10, LBLUE)
            pic.rect(wx + 2, 68, 6, 10, YELLOW)
            pic.rect(wx + 10, 68, 6, 10, GREEN)
            pic.rect(wx - 2, 82, 22, 4, GREEN)  # window box
            pic.rect(wx, 80, 3, 2, LMAGENTA)
            pic.rect(wx + 8, 80, 3, 2, LRED)
            pic.rect(wx + 15, 80, 3, 2, LMAGENTA)
        # heart sign
        pic.ellipse(60, 26, 20, 14, LMAGENTA)
        pic.ellipse(80, 26, 20, 14, LMAGENTA)
        pic.poly([(62, 36), (98, 36), (80, 50)], LMAGENTA)
        pic.rect(70, 34, 20, 4, WHITE)
        # door
        pic.rect(DOOR_X[0] - 2, 58, 24, 60, DGREY, 0)
        pic.rect(DOOR_X[0], 60, 20, 58, WHITE)
        pic.rect(78, 80, 4, 4, YELLOW)  # brass heart
        pic.rect(66, 100, 28, 18, RED)  # runner
        pic.walls(CURB_Y)
        pic.rect(DOOR_X[0], CURB_Y, DOOR_X[1] - DOOR_X[0], 2, None, 2)

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        return self.curb.objects()

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.curb.on_enter(game, from_room)
        if not game.flags.get("seen_chapelstreet"):
            game.flags["seen_chapelstreet"] = True
            game.print(
                "A chapel, in the way a hot dog is a meal. The neon heart above the door "
                "flickers. Rice crunches under your shoes. Someone, somewhere, is crying, "
                "and it may be from happiness."
            )

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and DOOR_X[0] <= ego.centre_x <= DOOR_X[1] and ego.y <= self.horizon + 1:
            game.new_room(24)
            return
        self.curb.update(game)

    def said(self, game: Game, p: Parsed) -> bool:
        if self.curb.said(game, p):
            pass
        elif p.said("open", "door") or p.said("enter", "door") or p.said("enter", "chapel") or p.said("enter"):
            if self.curb.near(game):
                game.new_room(13)
            elif self.near(game, DOOR_X[0], DOOR_X[1], 130):
                game.new_room(24)
            else:
                game.print("Walk up to the white door. Everyone else who did is either married or in a cab.")
        elif p.said("knock", "door"):
            game.print("You knock with the brass heart. A voice inside: \"It's open! It's always open!\"")
        elif p.said("get", "rose") or p.said("smell", "rose"):
            game.print("Plastic. They smell of nothing, which, given the neighbourhood, is a mercy.")
        elif p.said("smell"):
            game.print(
                "Rice, plastic flowers, and a hint of the organist's [aftershave|perfume] from the last service."
            )
        elif p.said("listen"):
            game.print("An organ inside, wheezing through something that was a hymn once.")
        else:
            return False
        return True
