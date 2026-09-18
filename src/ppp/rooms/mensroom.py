"""Room 14: the men's room at Rooster's. Read the wall; one line matters.

In Pauline's game it is the ladies' room, and the urinal is a dispenser that has been empty for years.
"""

from __future__ import annotations

from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    CYAN,
    DGREY,
    GREEN,
    LCYAN,
    LGREY,
    LRED,
    MAGENTA,
    PIC_W,
    RED,
    WHITE,
)
from ppp.game import Game
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

GRAFFITI: list[str] = [
    "For a good time call anyone. Anyone at all. Please.",
    "[Paul] was here. Twice. It went badly both times.",
    "The back door password is ROOSTER SENT ME. Tell them Rooster sent you. -R.",
    "Kilroy was here and would like to go home now.",
    "Flush twice. It's a long way to the kitchen.",
    "If you can read this you're standing too close to the [urinal|dispenser].",
]
PASSWORD_LINE = 2


class MensRoom(Room):
    number = 14
    name = "The men's room"
    description = (
        "[A men's room in the tradition of great men's rooms|A ladies' room in the tradition of great ladies' rooms]: "
        "one stall with no door, [a urinal with a cigarette in it|a dispenser with a cigarette in its coin slot], "
        "a sink under a mirror that has given up, "
        "and a wall of graffiti that would take a week to read. The way out is at the "
        "bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 11}
    spawns = {"default": (76, 150), 11: (76, 156)}
    looks = {
        "wall": "Every inch is written on. You could read the graffiti for hours. Try READ GRAFFITI.",
        "sink": "A cracked sink with one tap, a sliver of grey soap, and a drain that gurgles "
        "when you aren't looking at it.",
        "mirror": "The mirror is mostly scratches. What's left shows [a man|a woman] in a white suit "
        "who should know better. You wave. [He|She] waves back, reluctantly.",
        "bathroom": "The stall has no door. The toilet has no seat. The situation has no upside.",
        "stool": "The stall has no door. The toilet has no seat. The situation has no upside.",
        "floor": "Sticky tiles. You are choosing not to think about why.",
        "door": "The way out. It's behind you, at the bottom of the screen.",
        "urinal": "[A urinal. Someone has stubbed out a cigarette in it|A dispenser, empty since 1979. "
        "Someone has stubbed out a cigarette in its coin slot], which is at least tidy.",
        "cigarette": "A cigarette butt, in the [urinal|dispenser's coin slot], which is where cigarettes go to think.",
        "soap": "A sliver of grey soap that has washed hands you don't want to know about.",
        "window": "No window. The room prefers it.",
    }

    def __init__(self) -> None:
        self.line = 0

    def draw(self, pic: Picture) -> None:
        # tiled wall
        pic.rect(0, 0, PIC_W, 100, LCYAN)
        for y in range(0, 100, 10):
            pic.line([(0, y), (PIC_W - 1, y)], CYAN)
        for x in range(0, PIC_W, 10):
            pic.line([(x, 0), (x, 99)], CYAN)
        # floor
        pic.rect(0, 100, PIC_W, 68, LGREY)
        for y in range(100, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], DGREY)
        for x in range(0, PIC_W, 12):
            pic.line([(x, 100), (x, 167)], DGREY)
        # stall on the left (no door)
        pic.rect(4, 20, 44, 84, DGREY, 0)
        pic.rect(6, 22, 40, 80, LGREY)
        pic.rect(14, 74, 24, 14, WHITE)  # toilet
        pic.rect(18, 62, 16, 14, WHITE)  # tank
        pic.rect(16, 88, 20, 8, WHITE)
        if pic.pauline:
            # a wall dispenser in the middle, long since empty
            pic.rect(66, 50, 18, 34, LGREY, 0)
            pic.rect(68, 52, 14, 8, WHITE)  # a label nobody has read
            pic.rect(68, 62, 14, 14, DGREY)  # the window, showing nothing
            pic.rect(72, 78, 6, 3, BLACK)  # coin slot
            pic.pixel(74, 78, BROWN)  # the cigarette
        else:
            # urinal in the middle
            pic.rect(66, 50, 18, 34, WHITE, 0)
            pic.rect(68, 52, 14, 22, LGREY)
            pic.rect(72, 46, 6, 6, DGREY)  # flush pipe
            pic.pixel(74, 70, BROWN)  # the cigarette
        # sink and mirror on the right
        pic.rect(112, 26, 34, 30, LGREY)  # mirror
        pic.rect(114, 28, 30, 26, DGREY)
        for i, y in enumerate((30, 36, 42, 48)):
            pic.line([(116 + i * 5, y), (140, y + 4)], LGREY)
        pic.rect(110, 70, 38, 16, WHITE, 0)  # sink
        pic.rect(114, 74, 30, 8, LGREY)
        pic.rect(126, 62, 6, 8, DGREY)  # tap
        pic.rect(116, 86, 26, 14, DGREY, 0)  # pedestal
        # graffiti: scrawls in many colours between the fixtures
        scrawls = (
            ((52, 14), (64, 12), (60, 18), (70, 16), RED),
            ((54, 24), (62, 28), (74, 22), MAGENTA),
            ((90, 14), (102, 18), (96, 24), (108, 20), BLUE),
            ((88, 32), (100, 30), (94, 38), GREEN),
            ((90, 62), (104, 60), (98, 68), (106, 66), BLACK),
            ((52, 40), (60, 44), (56, 48), RED),
            ((52, 80), (64, 84), (60, 90), BLUE),
            ((150, 14), (156, 20), (152, 26), MAGENTA),
            ((90, 84), (104, 80), (98, 90), BLACK),
        )
        for *points, colour in scrawls:
            pic.line(points, colour)
        pic.rect(94, 46, 12, 4, LRED)  # a lipstick kiss, of all things
        pic.walls(100)
        pic.rect(4, 100, 44, 6, None, 0)  # stall footprint
        pic.rect(110, 100, 38, 4, None, 0)  # sink footprint

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if not game.flags.get("seen_mensroom"):
            game.flags["seen_mensroom"] = True
            game.print("The smell arrives before you do. It has been waiting. It is glad you came.")

    def said(self, game: Game, p: Parsed) -> bool:
        reads_wall = p.said("look", "graffiti") or p.said("look", "wall", "rol") or p.said("look", "graffiti", "rol")
        if reads_wall or p.said("look", "writing") or p.said("look", "wall") and self.line:
            self._read(game)
        elif game.pauline and p.said("use", "urinal"):
            game.print("You feed it a quarter, out of habit. It keeps the quarter, also out of habit.")
        elif p.has("bathroom", "urinal") and p.verb in ("use", "sit") or p.said("sit"):
            game.award("toilet")
            game.print(
                "You take care of business. There's no paper, no seat, and no dignity, "
                "but there is, for one shining moment, relief."
            )
        elif p.said("push", "bathroom") or p.said("use", "flush") or p.said("flush") or p.said("flush", "rol"):
            game.award("flush")
            game.print("It flushes with a sound like a whale clearing its throat. Nothing else happens. Yet.")
        elif p.said("look", "bathroom", "rol") or p.said("search", "bathroom"):
            game.print("You look into the bowl. The bowl looks into you. Nobody wins.")
        elif p.verb == "wash" or p.said("use", "sink"):
            game.award("wash")
            game.print("You wash your hands with the grey sliver. You feel marginally less like a bar. Marginally.")
        elif p.said("get", "soap"):
            game.print("You leave the soap. Some things belong to the room.")
        elif p.said("get", "cigarette"):
            game.print("It's in a [urinal|coin slot in a ladies' room], [Paul]. Even you have a floor, and that's it.")
        elif p.said("drink", "rol"):
            game.die(
                "You drink from the sink. Then, because it's there, from the [urinal|toilet]. "
                "The city health department later names a pathogen after you. [Paul] dies "
                "of curiosity, and of many, many other things."
            )
        elif p.said("kiss", "mirror"):
            game.award("kiss_mirror")
            game.print("You kiss the mirror. It's the most action either of you has had in months.")
        elif p.said("look", "self"):
            game.print(self.looks["mirror"])
        elif p.said("smell"):
            game.print("A swimming pool had a fight with a barn and both of them lost.")
        elif p.said("listen"):
            game.print("Dripping. Gurgling. The jukebox through the wall, playing something with a saxophone.")
        else:
            return False
        return True

    def _read(self, game: Game) -> None:
        text = GRAFFITI[self.line]
        if self.line == PASSWORD_LINE:
            game.flags["knows_password"] = True
            game.award("password")
        self.line = (self.line + 1) % len(GRAFFITI)
        if self.line == 0:
            game.award("graffiti_all")
        game.print(f'Scrawled on the wall in marker:\n\n"{text}"\n\n(There\'s more. Keep reading.)')
