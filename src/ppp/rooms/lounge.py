"""Room 27: the casino lounge. A comedian, a spotlight, and an audience of you."""

from __future__ import annotations

from ppp.const import (
    BLACK,
    BROWN,
    DGREY,
    LGREY,
    LRED,
    MAGENTA,
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

JOKES = [
    '"Anybody here on their honeymoon?" A pause. "Anybody here still on it?"',
    '"I got married in this town. Chapel on Fifth. Nice place. They validate parking and nothing else."',
    '"My wife tied me to a bed once. Turns out it was the honeymoon. Turns out it was the whole marriage."',
    '"Guy comes in here in a white leisure suit." He points. "No, seriously. Look at him. Look at him."',
    "\"Good night, everybody! Tip your waitress, she's the only one who'll take your money and stay.\"",
]


class Lounge(Room):
    number = 27
    name = "The lounge"
    description = (
        "The casino lounge: a stage with a red curtain, a microphone, and a comedian "
        "who has been on since the Carter administration. Small round tables, each with "
        "a candle and nobody. A spotlight that has found its mark and given up. The way "
        "out is at the bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 22}
    spawns = {"default": (76, 150), 22: (76, 156)}
    looks = {
        "lounge": "A comedian in a ruffled shirt and a bow tie that has seen combat. His act "
        "has three jokes and a reason not to go home.",
        "stage": "A low stage with a red curtain, a stool nobody sits on, and a microphone "
        "on a stand, leaning, like everyone here.",
        "stool": "Round tables with red candles in glass, and chairs that face the stage out of politeness.",
        "floor": "Sticky. Every floor in this city is sticky, but the lounge is the champion.",
        "bar": "A tiny bar at the back with a bartender who is also the sound man and, "
        "later, the comedian's ride home.",
        "window": "No windows. The comedian prefers it, and the audience agrees.",
    }

    def __init__(self) -> None:
        self.joke = 0

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 100, BLACK)
        pic.rect(0, 100, PIC_W, 68, DGREY)
        for y in range(106, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        # stage and curtain
        pic.rect(30, 12, 100, 60, RED)
        for x in range(34, 130, 8):
            pic.line([(x, 12), (x, 71)], MAGENTA)
        pic.rect(24, 72, 112, 28, BROWN, 0)
        pic.rect(24, 70, 112, 3, LGREY)
        # spotlight
        pic.ellipse(64, 30, 32, 44, YELLOW)
        # the comedian, then the mic in front of him
        draw_person(pic, 76, 40, suit=WHITE, skin=LRED, hair=BLACK)
        pic.rect(78, 47, 4, 2, RED)  # bow tie
        pic.rect(86, 52, 2, 20, DGREY)  # mic stand
        pic.rect(85, 50, 4, 4, BLACK)
        # tables
        for x, y in ((14, 118), (52, 130), (100, 130), (138, 118)):
            pic.rect(x, y, 18, 4, BROWN)
            pic.rect(x + 8, y + 4, 2, 10, BROWN)
            pic.rect(x + 7, y - 6, 4, 6, RED)
            pic.pixel(x + 8, y - 7, YELLOW)
            pic.rect(x, y + 12, 18, 4, None, 0)
        pic.walls(100)

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.joke = 0
        game.print(
            'The comedian squints past the spotlight. "Ladies and gentlemen, we have a guest. '
            'Sir, is that suit white, or did it give up?"'
        )

    def said(self, game: Game, p: Parsed) -> bool:
        if (
            p.said("sit", "rol")
            or p.said("sit")
            or p.said("look", "joke")
            or p.has("joke")
            and p.verb in ("look", "listen")
        ):
            self._show(game)
        elif p.said("look", "lounge", "rol"):
            game.print(self.looks["lounge"])
        elif p.has("heckle") or p.said("talk", "lounge") or p.said("talk", "lounge", "rol") or p.said("talk"):
            game.award("heckle")
            game.print(
                '"Oh, we got a talker." The comedian shades his eyes. "Sir, I don\'t come to where you '
                "work and knock the mop out of your hands.\" The bartender laughs. It's the first time tonight."
            )
        elif p.has("stage") and p.verb in ("enter", "climb", "use", "get"):
            game.print(
                "You put a foot on the stage. The bartender, who is also "
                "security, shakes his head once. You take it off."
            )
        elif p.said("buy", "rol") or p.said("buy"):
            game.print(
                "The bartender is running sound. He holds up one finger. The finger means later, and it means no."
            )
        elif p.said("smell"):
            game.print("Cigarettes, spilled bourbon, and flop sweat, which has its own smell, and it's this one.")
        elif p.said("listen"):
            game.print("The comedian, the hum of the amp, and one person laughing, who is the comedian.")
        else:
            return False
        return True

    def _show(self, game: Game) -> None:
        if self.joke >= len(JOKES):
            game.print("He's finished. He's packing up the one prop, which was a rubber chicken, which was you.")
            return
        text = JOKES[self.joke]
        self.joke += 1
        if self.joke == len(JOKES):
            game.award("lounge")
            game.print(f"{text}\n\nHe bows to nobody. The spotlight goes out. You've seen the whole act. That was it.")
        else:
            game.print(f"You sit. The comedian leans into the mic.\n\n{text}\n\n(SIT again for more. There is more.)")
