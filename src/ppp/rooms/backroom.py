"""Room 15: the back room behind the alley door. Brick, a couch, a TV, and stairs."""

from __future__ import annotations

import pygame

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
from ppp.sprite import from_ascii, from_rows, rows_of

STAIRS_X = (126, 158)
TV_X, TV_Y = 24, 62  # top-left of the screen area, in picture coords
BRICK_X, BRICK_BASE = 66, 95

BRICK_LEGEND = {"k": BLACK, "f": LRED, "s": LMAGENTA, "j": DGREY, "g": YELLOW}  # grey jeans read against the blue couch
BRICK_SITTING = """
....kkkkkk..........
...kkkkkkkk.........
...ffffffkk.........
...fkffffkk.........
...ffffffk..........
....fffff...........
.....fff............
..sssgsssssss.......
.ssssssssssssss.....
.ssssssssssssss.....
.sssssssssssssss....
.sssssssssssssss....
.fsssssssssssssss...
.ssssssssssssssss...
..jjjjjjjjjjjjjjjj..
..jjjjjjjjjjjjjjjj..
.jjjj.........jjjj..
.jjjj.........jjjj..
.jjjj.........jjjj..
.jjjj.........jjjj..
kkkkk.........kkkkk.
kkkkk.........kkkkk.
"""

SCREEN_LEGEND = {"b": LBLUE, "g": GREEN, "w": WHITE, "k": BLACK, "r": RED, "f": LRED, "y": YELLOW, "l": LGREY}
FISHING = (
    """
bbbbbbbbbbbb
bbbbbbbbbbbb
bbbbbkkbbbbb
bbbbkkkkbbbb
bbbbbbbbbbbb
ggggggggbbbb
gggggggggggg
gggggggggggg
""",
    """
bbbbbbbbbbbb
bbbbbbbbbbbb
bbbbbbkkbbbb
bbbbbkkkkbbb
bbbbbbbbbbbb
gggggggbbbbb
gggggggggggg
gggggggggggg
""",
)
BOXING = (
    """
llllllllllll
lwwwwwwwwwwl
lwffwwwwffwl
lwrrwwwwrrwl
lwrrwwrrrrwl
lwkkwwwwkkwl
lwwwwwwwwwwl
llllllllllll
""",
    """
llllllllllll
lwwwwwwwwwwl
lwwffwwffwwl
lwwrrrrrrwwl
lwwrrwwrrwwl
lwwkkwwkkwwl
lwwwwwwwwwwl
llllllllllll
""",
)


class BackRoom(Room):
    number = 15
    name = "The back room"
    description = (
        "A back room that is mostly couch. A television flickers on a milk crate. "
        "A staircase climbs the back wall toward somewhere with better lighting. "
        "Between you and the stairs, filling the couch, sits a man called Brick, "
        "watching a show about fishing with the concentration of a surgeon. The "
        "alley is back the way you came, at the bottom of the screen."
    )
    horizon = 96
    edges = {"bottom": 12}
    spawns = {"default": (104, 150), 12: (104, 156), 16: (STAIRS_X[0] + 8, 104)}
    looks = {
        "bouncer": "Brick. Six and a half feet of bouncer folded onto a couch, in a pink "
        "shirt that nobody has ever laughed at twice. He is watching the fishing show "
        "the way other men watch their children being born.",
        "tv": "A television older than you, on a milk crate. A man in waders is "
        "holding up a fish. Brick nods slowly, as if he knew the fish.",
        "couch": "A couch the colour of a bruise, built around Brick. There is room for "
        "one more person, if that person were much smaller and much braver.",
        "crate": "A milk crate doing the work of a TV stand. Somewhere a dairy is missing it.",
        "stairs": "Steep wooden stairs up the back wall. Music, laughter, and a smell "
        "of perfume drift down. Everything you came for is up there. Brick is down here.",
        "floor": "Bare boards, a rug that has given up, and cigarette burns arranged like constellations.",
        "wall": "Wood panelling and a calendar from a tyre company, still on the month with the best picture.",
        "door": "The alley door is behind you, at the bottom of the screen.",
        "remote": "A TV remote with three working buttons. One of them is CHANNEL.",
        "window": "No windows. Rooms like this don't have windows. That's the point of them.",
    }

    def __init__(self) -> None:
        self._brick: list[pygame.Surface] = []
        self._screens: dict[str, list[pygame.Surface]] = {}

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 96, BROWN)  # panelling
        for x in range(0, PIC_W, 8):
            pic.line([(x, 0), (x, 95)], DGREY)
        pic.rect(0, 96, PIC_W, 72, DGREY)  # boards
        for y in range(100, 168, 6):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        pic.rect(30, 116, 70, 30, RED)  # a sad rug
        pic.rect(34, 120, 62, 22, LMAGENTA)
        # calendar
        pic.rect(6, 14, 14, 18, WHITE)
        pic.rect(8, 16, 10, 8, LBLUE)
        # TV on a milk crate
        pic.rect(18, 80, 26, 16, DGREY, 0)  # crate
        for y in (84, 88, 92):
            pic.line([(18, y), (43, y)], BLACK)
        pic.rect(18, 56, 26, 24, BLACK)  # TV body
        pic.rect(TV_X - 2, TV_Y - 2, 16, 12, LGREY)  # bezel
        pic.rect(20, 66, 3, 3, LGREY)  # dials
        pic.rect(20, 71, 3, 3, LGREY)
        pic.line([(30, 56), (26, 46)], LGREY)  # rabbit ears
        pic.line([(32, 56), (36, 46)], LGREY)
        # couch: back, seat, arms
        pic.rect(56, 66, 68, 30, BLUE)
        pic.rect(56, 62, 68, 6, LBLUE)
        pic.rect(56, 84, 68, 12, LBLUE)
        pic.rect(52, 70, 8, 26, LBLUE)
        pic.rect(120, 70, 8, 26, LBLUE)
        pic.rect(52, 90, 76, 10, None, 0)  # couch footprint
        # stairs up the back wall
        for i in range(7):
            x = STAIRS_X[0] + i * 4
            y = 96 - i * 10
            pic.rect(x, y - 10, STAIRS_X[1] - x, 10, BROWN)
            pic.line([(x, y - 10), (STAIRS_X[1] - 1, y - 10)], YELLOW)
            pic.line([(x, y - 10), (x, y - 1)], BLACK)
        pic.rect(STAIRS_X[0] - 2, 20, 2, 76, BLACK)  # banister post
        pic.rect(STAIRS_X[0], 12, STAIRS_X[1] - STAIRS_X[0], 8, BLACK)  # the dark top
        pic.walls(96)
        pic.rect(STAIRS_X[0], 96, STAIRS_X[1] - STAIRS_X[0], 2, None, 2)  # threshold signal

    # -- sprites -----------------------------------------------------------------

    def brick_frames(self) -> list[pygame.Surface]:
        if not self._brick:
            rows = rows_of(BRICK_SITTING)
            lean = [(r[2:] + "..") if i < 7 else r for i, r in enumerate(rows)]  # head forward
            self._brick = [from_rows(rows, BRICK_LEGEND), from_rows(lean, BRICK_LEGEND)]
        return self._brick

    def screen_frames(self, show: str) -> list[pygame.Surface]:
        if show not in self._screens:
            self._screens[show] = [from_ascii(a, SCREEN_LEGEND) for a in (FISHING if show == "fishing" else BOXING)]
        return self._screens[show]

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        distracted = bool(game.flags.get("brick_distracted"))
        flicker = (game.cycle_count // 6) % 2
        screen = self.screen_frames("boxing" if distracted else "fishing")[flicker]
        brick = self.brick_frames()[1 if distracted else 0]
        return [
            (screen, TV_X, TV_Y + screen.get_height() - 1),
            (brick, BRICK_X, BRICK_BASE),
        ]

    # -- logic -------------------------------------------------------------------

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if not game.flags.get("seen_backroom"):
            game.flags["seen_backroom"] = True
            game.print(
                "Brick doesn't look up. \"You're in the way of the fish,\" he says. You "
                "step aside. You were not, in fact, in the way of the fish."
            )

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and STAIRS_X[0] <= ego.centre_x <= STAIRS_X[1] and ego.y <= self.horizon + 1:
            self._try_stairs(game)

    def said(self, game: Game, p: Parsed) -> bool:
        near_stairs = self.near(game, STAIRS_X[0] - 10, STAIRS_X[1], 112)
        if (
            p.said("use", "remote")
            or p.said("push", "remote")
            or p.said("use", "remote", "rol")
            or p.said("change", "rol")
            or p.said("change")
        ):
            self._remote(game)
        elif p.said("use", "tv") or p.said("push", "tv") or p.said("open", "tv"):
            if game.flags.get("brick_distracted"):
                game.print("Leave it. It's on the right channel now, and Brick agrees.")
            else:
                game.print(
                    "You reach for the dial. Brick's hand closes over your wrist without "
                    "his eyes leaving the screen. \"Don't.\" You don't."
                )
        elif p.said("talk", "bouncer") or p.said("talk", "bouncer", "rol") or p.said("talk"):
            if game.flags.get("brick_distracted"):
                game.print('"Shh. Third round." He does not blink. He may never blink again.')
            else:
                game.print('"Fish," says Brick, by way of conversation. It is the whole conversation.')
        elif (
            p.said("enter", "stairs")
            or p.said("enter", "stairs", "rol")
            or p.said("climb", "rol")
            or p.said("enter", "up")
        ):
            if near_stairs:
                self._try_stairs(game)
            else:
                game.print("Walk over to the stairs first. They're on the right, past the couch, past Brick.")
        elif p.said("sit", "rol") or p.said("sit"):
            game.print('"That\'s my spot," says Brick. It is all his spot.')
        elif p.said("give", "rol") and p.has("bouncer"):
            game.print("Brick looks at your offering, then at you, then back at the fish. The fish wins.")
        elif (
            p.said("kiss", "bouncer")
            or p.said("push", "bouncer")
            or p.said("kick", "bouncer")
            or p.said("get", "bouncer")
        ):
            game.die(
                "Brick stands up. This takes a while. Then he removes you from the couch, "
                "the room, the building, and, on reflection, the world. Paul is a rumour."
            )
        elif p.said("get", "tv") or p.said("get", "crate"):
            game.print("It's heavier than it looks, and it looks like a television. Also, Brick.")
        elif p.said("look", "channel") or p.said("look", "tv", "rol"):
            game.print(
                self.looks["tv"]
                if not game.flags.get("brick_distracted")
                else "Two large men are hitting each other. Brick approves of both."
            )
        elif p.said("smell"):
            game.print("Cigarettes, cheap aftershave, and a fish smell that may be coming from the television.")
        elif p.said("listen"):
            game.print("A man on TV explaining lures. Brick breathing. Upstairs, faintly, music and laughter.")
        else:
            return False
        return True

    def _remote(self, game: Game) -> None:
        if not game.has("remote"):
            game.print("You mime a remote control. Brick, without looking, mimes not caring.")
            return
        if game.flags.get("brick_distracted"):
            game.print("The boxing is on. Brick is gone to a better place. Don't push your luck, or the button.")
            return
        game.flags["brick_distracted"] = True
        game.award("distract_brick", 4)
        game.print(
            "You aim the remote over Brick's shoulder and press CHANNEL. The fish vanishes. "
            "Two enormous men in shorts appear, hitting each other. Brick leans forward "
            "until the couch creaks. He is no longer in this room. He is ringside."
        )

    def _try_stairs(self, game: Game) -> None:
        game.ego.stop()
        if game.flags.get("brick_distracted"):
            game.award("stairs", 5)
            game.new_room(16)
        else:
            game.print(
                "Brick's arm comes out sideways like a railway barrier. \"Where you going, "
                'tiger?" He stands, lifts you by the lapels, and posts you back through the '
                "alley door like a letter nobody wanted."
            )
            game.new_room(12)
