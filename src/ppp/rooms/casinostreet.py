"""Room 21: outside the Golden Sock Casino. Lights, a cab stop, and a doorman who doesn't care."""

from __future__ import annotations

import pygame

from ppp.cab import Curb
from ppp.const import (
    BLACK,
    BLUE,
    DGREY,
    LCYAN,
    LGREY,
    LRED,
    PIC_W,
    RED,
    WHITE,
    YELLOW,
)
from ppp.game import Game
from ppp.npc import draw_person
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

DOOR_X = (68, 92)
CURB_Y = 118
ROAD_Y = 140


class CasinoStreet(Room):
    number = 21
    name = "Outside the Golden Sock"
    description = (
        "The Golden Sock Casino: a wall of light bulbs, a red carpet that stops "
        "exactly at the curb, and doors that never close. A doorman in gold braid "
        "holds one open for everybody, even you. Cabs stop at the curb."
    )
    horizon = CURB_Y
    edges = {}
    spawns = {"default": (100, 136), 13: (100, 136), 22: (80, 128)}
    looks = {
        "building": "Bulbs, chrome, and a gold sock the size of a car, lit from inside. Taste was not consulted.",
        "sign": "THE GOLDEN SOCK, in bulbs. A few are out, which spells something ruder if you squint.",
        "door": "Glass doors, held open. Casinos want you in. Getting out is your problem.",
        "bouncer": "A doorman in gold braid with a smile for everyone. He is paid by the smile.",
        "floor": "Red carpet on the sidewalk, worn to pink where the losers walk out.",
        "window": "No windows, no clocks. The casino would prefer you didn't know either.",
    }

    def __init__(self) -> None:
        self.curb = Curb(ROAD_Y)

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, CURB_Y, BLUE)
        pic.rect(0, 0, PIC_W, 100, DGREY)
        pic.rect(0, 100, PIC_W, 18, LGREY)
        pic.rect(0, CURB_Y, PIC_W, ROAD_Y - CURB_Y, LGREY)
        pic.rect(0, ROAD_Y, PIC_W, 28, BLACK)
        pic.line([(0, 154), (PIC_W - 1, 154)], YELLOW)
        pic.line([(0, CURB_Y), (PIC_W - 1, CURB_Y)], WHITE)
        # bulbs everywhere
        for y in range(4, 100, 8):
            for x in range(2, PIC_W, 8):
                pic.pixel(x, y, YELLOW if (x // 8 + y // 8) % 2 == 0 else WHITE)
        # the sock
        pic.rect(40, 8, 80, 30, BLACK)
        pic.rect(42, 10, 76, 26, RED)
        pic.rect(52, 14, 14, 18, YELLOW)  # sock leg
        pic.rect(52, 26, 30, 8, YELLOW)  # sock foot
        pic.rect(70, 14, 44, 6, YELLOW)  # lettering bar
        for x in range(72, 112, 6):
            pic.rect(x, 15, 3, 4, RED)
        # doors and canopy
        pic.rect(DOOR_X[0] - 6, 44, DOOR_X[1] - DOOR_X[0] + 12, 6, RED)
        pic.rect(DOOR_X[0] - 2, 50, DOOR_X[1] - DOOR_X[0] + 4, 68, DGREY, 0)
        pic.rect(DOOR_X[0], 52, DOOR_X[1] - DOOR_X[0], 66, LCYAN)
        pic.line([(80, 52), (80, 117)], DGREY)
        pic.rect(DOOR_X[0], 100, DOOR_X[1] - DOOR_X[0], 18, RED)  # red carpet spill
        pic.rect(DOOR_X[0] - 4, CURB_Y, DOOR_X[1] - DOOR_X[0] + 8, ROAD_Y - CURB_Y, RED)
        # doorman
        draw_person(pic, 98, 86, suit=RED, skin=LRED, hair=BLACK)
        pic.rect(98, 94, 8, 2, YELLOW)  # braid
        pic.rect(96, 110, 12, 10, None, 0)
        pic.walls(CURB_Y)
        pic.rect(DOOR_X[0], CURB_Y, DOOR_X[1] - DOOR_X[0], 2, None, 2)

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        return self.curb.objects()

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.curb.on_enter(game, from_room)
        if not game.flags.get("seen_casinostreet"):
            game.flags["seen_casinostreet"] = True
            game.print(
                "Ten thousand light bulbs, and every one of them is looking at your wallet. "
                '"Welcome to the Golden Sock, sir," says the doorman, to the wallet.'
            )

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and DOOR_X[0] <= ego.centre_x <= DOOR_X[1] and ego.y <= self.horizon + 1:
            game.new_room(22)
            return
        self.curb.update(game)

    def said(self, game: Game, p: Parsed) -> bool:
        if self.curb.said(game, p):
            pass
        elif p.said("talk", "bouncer") or p.said("talk", "bouncer", "rol") or p.said("talk"):
            game.print('"Good luck in there, sir." He means it. He\'s seen the odds.')
        elif p.said("open", "door") or p.said("enter", "door") or p.said("enter", "casino") or p.said("enter"):
            if self.curb.near(game):
                game.new_room(13)
            elif self.near(game, DOOR_X[0], DOOR_X[1], 130):
                game.new_room(22)
            else:
                game.print("Walk up to the doors. They're open. They are always open. That's the trick.")
        elif p.said("smell"):
            game.print("Cigar smoke, carpet shampoo, and money, mostly other people's.")
        elif p.said("listen"):
            game.print("Bells. Coins. A woman somewhere screaming with joy or the other thing.")
        else:
            return False
        return True
