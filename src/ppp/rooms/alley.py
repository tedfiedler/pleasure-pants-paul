"""Room 12: the alley beside Rooster's. A dumpster, a dog, a locked door, and a mugger."""

from __future__ import annotations

from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    DGREY,
    GREEN,
    LBLUE,
    LGREY,
    PIC_W,
    WHITE,
)
from ppp.game import Game
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

MUGGER_WARN = 400  # cycles in the alley before footsteps
MUGGER_ARRIVES = 500


class Alley(Room):
    number = 12
    name = "The alley"
    description = (
        "A dead-end alley wedged against the side of Rooster's. A dumpster hulks "
        "against the back wall, a dog sleeps beside it, and a steel door marked "
        "EMPLOYEES ONLY refuses to acknowledge you. Puddles reflect nothing good. "
        "The street is back to the east."
    )
    horizon = 104
    edges = {"right": 10}
    spawns = {"default": (140, 150)}
    looks = {
        "trash": "A green dumpster the size of a small apartment, and better furnished. The lid is open a crack.",
        "dog": "A scruffy brown dog, asleep against the dumpster. One ear twitches. "
        "It has the face of a dog that has already bitten someone today.",
        "door": "A steel door with no handle on this side and a sliding slot at eye level. A sign says EMPLOYEES ONLY.",
        "sign": "EMPLOYEES ONLY. Underneath, in marker: 'and you know who you are.'",
        "wall": "Brick, wet, and covered in decades of spray paint. Someone has drawn a very detailed rooster.",
        "puddle": "A puddle. Rainbow-slicked. You decide not to find out what's in it.",
        "floor": "Cracked concrete, puddles, and a chalk outline that someone has added a hat to.",
        "rose": "A single wilted red rose, in the dumpster, on top of the garbage. Romance!",
        "alley": "It's an alley. You're in it. Congratulations on your choices.",
    }

    def __init__(self) -> None:
        self.timer = 0

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 104, DGREY)  # back wall
        for y in range(2, 104, 6):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        for y in range(2, 104, 12):
            for x in range(3, PIC_W, 10):
                pic.line([(x, y), (x, y + 5)], BLACK)
        for y in range(8, 104, 12):
            for x in range(8, PIC_W, 10):
                pic.line([(x, y), (x, y + 5)], BLACK)
        pic.rect(0, 104, PIC_W, 64, LGREY)  # concrete
        pic.rect(0, 0, 6, 168, BLACK, 0)  # dead end at the left
        pic.rect(154, 0, 6, 104, BLUE)  # a slice of sky at the street end
        # puddles
        for px, py, w in ((30, 130, 26), (90, 150, 34), (120, 122, 18)):
            pic.rect(px, py, w, 4, LBLUE)
            pic.rect(px + 4, py + 4, w - 8, 2, LBLUE)
        # dumpster
        pic.rect(20, 70, 44, 36, GREEN, 0)
        pic.rect(20, 66, 44, 6, BLACK)  # lid
        pic.rect(22, 68, 40, 2, GREEN)
        pic.rect(24, 108, 6, 4, BLACK, 0)  # wheels
        pic.rect(54, 108, 6, 4, BLACK, 0)
        pic.rect(20, 106, 44, 6, None, 0)
        # dog
        pic.rect(68, 98, 16, 6, BROWN, 0)
        pic.rect(66, 96, 6, 6, BROWN, 0)
        pic.pixel(67, 97, BLACK)
        pic.rect(66, 104, 18, 6, None, 0)
        # steel door with slot and sign
        pic.rect(96, 44, 24, 60, LGREY, 0)
        pic.rect(98, 46, 20, 56, DGREY)
        pic.rect(102, 62, 12, 3, BLACK)  # slot
        pic.rect(100, 50, 16, 6, WHITE)  # sign
        # graffiti
        pic.line([(130, 30), (140, 22), (150, 30), (140, 38), (130, 30)], BLUE)
        pic.walls(104)

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.timer = 0

    def update(self, game: Game) -> None:
        self.timer += 1
        if self.timer == MUGGER_WARN:
            game.print(
                "Footsteps behind you. Slow ones. The kind that aren't in a hurry because they don't need to be."
            )
        elif self.timer >= MUGGER_ARRIVES:
            game.die(
                "A large man steps out of the shadows and relieves you of your wallet, "
                "your dignity, and, after some thought, your pulse. Paul dies in an "
                "alley, which is at least on brand."
            )

    def said(self, game: Game, p: Parsed) -> bool:
        if p.said("look", "trash", "rol") or p.said("search", "trash") or p.said("open", "trash"):
            self._search(game)
        elif p.said("get", "rose") or p.said("get", "rose", "rol"):
            if game.has("rose"):
                game.print("You already have the rose. One is plenty. One is, frankly, a lot.")
            elif not game.flags.get("rose_seen"):
                game.print("What rose? You haven't seen a rose. You might, if you looked around.")
            elif not (14 <= game.ego.centre_x <= 70 and game.ego.y <= 120):
                game.print("Get closer to the dumpster. Closer. Yes, that's the smell.")
            else:
                game.give("rose")
                game.award("rose", 2)
                game.print(
                    "You pluck the wilted rose from the garbage and shake off a noodle. "
                    "Romance is forty percent presentation, and you have the other sixty."
                )
        elif p.said("look", "rose"):
            if game.has("rose"):
                game.print("A wilted red rose. It has seen things. Then again, so have you.")
            elif game.flags.get("rose_seen"):
                game.print(self.looks["rose"])
            else:
                return False
        elif p.said("pet", "dog") or p.said("talk", "dog"):
            game.print("The dog opens one eye, growls from somewhere deep and ancient, and closes it again.")
        elif p.said("kick", "dog") or p.said("push", "dog") or p.said("get", "dog"):
            game.die(
                "The dog was not asleep. The dog was waiting. It has your ankle, then your "
                "calf, then your attention, and then it has all of you. Paul is dog food."
            )
        elif p.said("knock", "door") or p.said("push", "door"):
            game.print(
                'The slot slides open. Two eyes. "Password?" You offer your best smile. '
                "The slot slides shut. Evidently that's not the password."
            )
        elif p.said("open", "door") or p.said("enter", "door") or p.said("pull", "door"):
            game.print("No handle. Not for you, anyway. There's a slot; maybe try knocking.")
        elif p.said("talk", "rol") and p.has("password"):
            game.print("You'd need to know the password first. Someone around here must have written it down.")
        elif p.said("drink", "puddle"):
            game.print("You consider it, which says a great deal. You do not, which says slightly less.")
        elif p.said("smell"):
            game.print("Wet dog, old fish, and the sweet tang of a dumpster in its prime.")
        elif p.said("listen"):
            game.print("Dripping water. The dog snoring. Somewhere, distantly, a saxophone.")
        else:
            return False
        return True

    def _search(self, game: Game) -> None:
        if game.has("rose"):
            game.print("More garbage. You took the only thing worth having, which tells you about the rest.")
            return
        game.flags["rose_seen"] = True
        game.print(
            "You lift the lid and peer in. Chicken bones, a wig, several lifetimes of "
            "coffee grounds, and, lying on top like a promise, a single wilted rose."
        )
