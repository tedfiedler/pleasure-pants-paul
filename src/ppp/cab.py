"""The curb: a cab that can be called to any street room, shared by those rooms."""

from __future__ import annotations

import pygame

from ppp import sound
from ppp.const import BLACK, LBLUE, LCYAN, PIC_W, RED, WHITE, YELLOW
from ppp.game import Game
from ppp.parser import Parsed
from ppp.sprite import from_ascii

TAXI_ROOM = 13
CAB_STOP_X = 88
CAB_BASELINE = 152  # the near lane, just off the curb
CAB_WAIT_CYCLES = 300

CAB_LEGEND = {"k": BLACK, "y": YELLOW, "c": LCYAN, "w": WHITE, "r": RED, "b": LBLUE}
CAB_ART = """
..............kkkkkk................
...........kkkkyyyykkkk.............
.........kkkkkkkkkkkkkkkkkkkk.......
........kccccccccckkcccccccccck.....
.......kcccccccccckkccccccccccck....
......kccccccccccckkcccccccccccck...
.....kkkkkkkkkkkkkkkkkkkkkkkkkkkkk..
....kyyyyyyyyyyyyyyyyyyyyyyyyyyyyyk.
...kyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyk
kkkkyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyk
wwkyyyyyyyyykyyyyyyyyyykyyyyyyyyyyyk
wwkyyyyyyyyykyyyyyyyyyykyyyyyyyyyykr
kkkyyyyyyyyykyyyyyyyyyykyyyyyyyyyykr
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
....kkkkkk...............kkkkkk.....
...kkkwwkkk.............kkkwwkkk....
...kkkwwkkk.............kkkwwkkk....
....kkkkkk...............kkkkkk.....
"""

_sprite: pygame.Surface | None = None


def cab_sprite() -> pygame.Surface:
    global _sprite
    if _sprite is None:
        _sprite = from_ascii(CAB_ART, CAB_LEGEND)
    return _sprite


class Curb:
    """Cab state for one street room. The room forwards enter/update/said/objects."""

    def __init__(self, road_y: int) -> None:
        self.road_y = road_y
        self.state = "none"  # none | arriving | waiting | leaving
        self.x = PIC_W
        self.timer = 0

    def on_enter(self, game: Game, from_room: int | None) -> None:
        self.timer = 0
        if from_room == TAXI_ROOM:
            self.state = "leaving"
            self.x = CAB_STOP_X
        else:
            self.state = "none"

    def near(self, game: Game) -> bool:
        return (
            self.state == "waiting"
            and CAB_STOP_X - 8 <= game.ego.centre_x <= CAB_STOP_X + 44
            and game.ego.y <= self.road_y + 12
        )

    def call(self, game: Game) -> None:
        if self.state == "waiting":
            game.print("It's right there, [Paul]. Yellow, four wheels, hard to miss.")
        elif self.state == "arriving":
            game.print("Patience. It's coming as fast as the meter allows.")
        else:
            self.state = "arriving"
            self.x = PIC_W
            game.award("call_cab")
            game.print("You wave your arms like a [man|woman] drowning in polyester. A cab peels around the corner.")

    def board(self, game: Game) -> None:
        if self.state == "waiting" and not self.near(game):
            game.print("Walk over to the cab first. It won't come to you; it's a cab, not a dog.")
        elif self.state == "waiting":
            game.new_room(TAXI_ROOM)
        else:
            game.print("What cab? Try calling one. Waving works. Whistling works. Money works best.")

    def objects(self) -> list[tuple[pygame.Surface, int, int]]:
        if self.state == "none":
            return []
        return [(cab_sprite(), self.x, CAB_BASELINE)]

    def update(self, game: Game) -> None:
        if self.state == "arriving":
            self.x -= 2
            if self.x <= CAB_STOP_X:
                self.x = CAB_STOP_X
                self.state = "waiting"
                self.timer = 0
                sound.play("horn")
                game.print('The cab screeches to a stop at the curb. The driver leans over. "Well?"')
        elif self.state == "waiting":
            self.timer += 1
            if self.timer > CAB_WAIT_CYCLES:
                self.state = "leaving"
                game.print("The cabbie gets bored and peels off. Cabs have places to be. You don't.")
        elif self.state == "leaving":
            self.x -= 3
            if self.x < -40:
                self.state = "none"

    def said(self, game: Game, p: Parsed) -> bool:
        if p.said("call", "cab") or p.said("call") or p.said("call", "rol") and not p.has("phone"):
            self.call(game)
        elif p.has("cab") and p.verb in ("enter", "open", "sit", "get", "use"):
            self.board(game)
        elif p.said("look", "cab"):
            if self.state == "waiting":
                game.print(
                    "A yellow cab, dented on every panel, idling at the curb. The driver is reading a racing form."
                )
            elif self.state == "none":
                game.print("No cab in sight. You could call one.")
            else:
                game.print("A yellow blur with a taxi light on top.")
        else:
            return False
        return True
