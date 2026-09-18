"""Room 25: the Golden Sock penthouse. The honeymoon, and how it ends."""

from __future__ import annotations

import pygame

from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    DGREY,
    LCYAN,
    LGREY,
    LMAGENTA,
    LRED,
    MAGENTA,
    PIC_W,
    RED,
    WHITE,
    YELLOW,
)
from ppp.game import Game
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room
from ppp.rooms.disco import GINGER_ART, GINGER_LEGEND
from ppp.sprite import from_ascii

BED = (72, 62, 80, 46)  # x, y, w, h
GINGER_POS = (118, 104)
TIED_POS = (78, 98)
MAID_CYCLES = 80

TIED_LEGEND = {"f": LRED, "h": BLACK, "w": WHITE, "r": BROWN, "b": BROWN, "k": BLACK}
TIED_ART = """
..ffff.wwwwwwwwwwwwwwwwww.bb.
.hffff.wwwrwwwwrwwwwrwwww.bb.
.hkfff.wwwrwwwwrwwwwrwwwwbbb.
..ffff.wwwrwwwwrwwwwrwwww.bb.
..ffff.wwwwwwwwwwwwwwwwww.bb.
"""


class Penthouse(Room):
    number = 25
    name = "The penthouse"
    description = (
        "The Golden Sock penthouse: a window the width of the city, a heart-shaped "
        "bed, a champagne bucket sweating on the nightstand beside a gold phone, and "
        "a balcony door onto the night. It is the nicest room you have ever been in "
        "and you can feel it deciding whether to let you stay. The elevator is at "
        "the bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 22}
    spawns = {"default": (76, 150), 22: (76, 156)}
    looks = {
        "hooker": "Ginger, on the bed, shoes off, veil gone, holding two glasses. Your wife. "
        "The word still doesn't fit in your mouth.",
        "bed": "A heart-shaped bed with satin sheets and more pillows than a person needs. "
        "It has seen honeymoons, and it has seen what comes after.",
        "window": "The city from twenty floors up: neon, headlights, the whole regrettable "
        "grid. From here it almost looks like it was planned.",
        "balcony": "A glass door onto a balcony with a rail and a view. A sign on it: ROOF "
        "POOL CLOSED FOR THE SEASON. It isn't the season. It's never the season.",
        "champagne": "A bottle of something with a French name in an ice bucket. It is the "
        "cheapest bottle the casino sells, and the ice is doing its best.",
        "phone": "A gold telephone on the nightstand. One button says DESK. It's the only "
        "button that has ever been pressed.",
        "nightstand": "A mirrored nightstand with the phone, the champagne, and, after the fact, a note.",
        "rug": "A white carpet so deep your shoes have gone.",
        "floor": "A white carpet so deep your shoes have gone.",
        "key": "The penthouse key, heart-shaped fob and all. You won't have it long.",
        "elevator": "The elevator, at the bottom of the screen. It goes down. Everything does, eventually.",
        "rope": "The chapel's bell rope, or one like it, in a great many knots, around you.",
        "self": "You are Paul, tied to a heart-shaped bed with a bell rope by your wife of "
        "one hour. Even for you this is a new low, and you have a basement.",
    }

    def __init__(self) -> None:
        self._ginger: pygame.Surface | None = None
        self._tied: pygame.Surface | None = None
        self.maid_timer = 0

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 100, LGREY)  # pale walls
        pic.rect(0, 100, PIC_W, 68, WHITE)  # deep carpet
        for y in range(104, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], LGREY)
        # the window across the back
        pic.rect(34, 8, 120, 50, BLACK)
        pic.rect(36, 10, 116, 46, BLUE)
        for x in range(40, 150, 6):
            h = 10 + (x * 7) % 22
            pic.rect(x, 56 - h, 4, h, DGREY)
            for yy in range(58 - h, 54, 4):
                if (x + yy) % 5:
                    pic.pixel(x + 1, yy, YELLOW)
        pic.line([(94, 10), (94, 55)], BLACK)
        # balcony door, back left
        pic.rect(4, 14, 26, 82, DGREY, 0)
        pic.rect(6, 16, 22, 78, LCYAN)
        pic.rect(8, 60, 18, 2, LGREY)  # rail
        pic.rect(9, 30, 10, 6, WHITE)  # the sign
        # heart-shaped bed
        x, y, w, h = BED
        pic.ellipse(x, y, w // 2 + 6, 24, RED)
        pic.ellipse(x + w // 2 - 6, y, w // 2 + 6, 24, RED)
        pic.poly([(x + 4, y + 18), (x + w - 4, y + 18), (x + w // 2, y + h)], RED)
        pic.rect(x + 10, y + 6, 16, 8, WHITE)  # pillows
        pic.rect(x + w - 26, y + 6, 16, 8, WHITE)
        pic.rect(x + 12, y + 20, w - 24, 14, LMAGENTA)  # satin
        pic.rect(x, y + h - 4, w, 6, None, 0)
        # nightstand with phone and champagne
        pic.rect(50, 74, 18, 26, LCYAN, 0)
        pic.rect(52, 76, 14, 2, WHITE)
        pic.rect(52, 66, 6, 8, YELLOW)  # gold phone
        pic.rect(51, 64, 8, 2, YELLOW)
        pic.rect(60, 62, 6, 12, LGREY)  # ice bucket
        pic.rect(62, 56, 2, 8, DGREY)  # the bottle
        pic.pixel(62, 55, YELLOW)
        pic.rect(50, 100, 18, 4, None, 0)
        # a lamp, right
        pic.rect(154, 40, 4, 60, DGREY, 0)
        pic.rect(148, 30, 12, 12, MAGENTA)
        pic.walls(100)

    # -- sprites -------------------------------------------------------------------

    def ginger(self) -> pygame.Surface:
        if self._ginger is None:
            self._ginger = from_ascii(GINGER_ART, GINGER_LEGEND)
        return self._ginger

    def tied(self) -> pygame.Surface:
        if self._tied is None:
            self._tied = from_ascii(TIED_ART, TIED_LEGEND)
        return self._tied

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        if game.flags.get("tied_up"):
            return [(self.tied(), TIED_POS[0], TIED_POS[1])]
        if game.flags.get("honeymoon_done"):
            return []
        return [(self.ginger(), GINGER_POS[0], GINGER_POS[1])]

    # -- logic ---------------------------------------------------------------------

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.maid_timer = 0
        if game.flags.get("honeymoon_done"):
            game.print("The penthouse, after. The bed is stripped, the champagne is gone, and so is she.")
        else:
            game.print(
                'Ginger is on the bed with two glasses. "Husband," she says, trying the word out. '
                '"Come here. Bring the wallet; I want to see what I married." She laughs. You laugh. '
                "One of you means it."
            )

    def update(self, game: Game) -> None:
        if self.maid_timer:
            self.maid_timer -= 1
            if self.maid_timer == 0:
                self._freed(game)

    def said(self, game: Game, p: Parsed) -> bool:
        if game.flags.get("tied_up"):
            return self._tied_said(game, p)
        if p.has("hooker") and p.verb in ("kiss", "love", "use", "undress") or p.said("love") or p.said("use", "bed"):
            self._honeymoon(game)
        elif p.said("talk", "hooker") or p.said("talk", "hooker", "rol") or p.said("talk"):
            if game.flags.get("honeymoon_done"):
                game.print("Nobody to talk to. The note on the nightstand says everything she had to say.")
            else:
                game.print(
                    '"Less talking, husband." She pats the bed, the way Dolores did. You notice. You come anyway.'
                )
        elif p.said("drink", "champagne") or p.said("get", "champagne") or p.said("open", "champagne"):
            if game.flags.get("honeymoon_done"):
                game.print("The bottle's gone. She took it. Of course she took it.")
            else:
                game.print(
                    'You pop the cork. It hits the window. "Careful," says Ginger, '
                    "\"that's the only thing in here that's paid for.\""
                )
        elif p.said("look", "note") or p.said("look", "note", "rol") or p.said("get", "note"):
            if game.flags.get("freed"):
                if "note" not in game.scored:
                    game.vars["money"] = game.vars.get("money", 0) + 10
                game.award("note", 1)
                game.print(
                    "The note, in lipstick on hotel stationery: \"Sugar. It was fun. The ring's real; "
                    "the rest wasn't. Don't call. G. P.S. I took the key so you'd take the stairs. "
                    "P.P.S. Ten bucks for a cab. A girl isn't a monster.\" A ten is folded inside."
                )
            elif game.flags.get("honeymoon_done"):
                game.print("There's a note on the nightstand. You'll read it when your hands are free.")
            else:
                return False
        elif p.has("balcony") and p.verb in ("open", "enter", "use", "climb") or p.said("open", "window"):
            game.die(
                "The balcony door opens. The night air is wonderful. The rail is lower than it "
                "looks, the pool is closed for the season, and the city is beautiful from up "
                "here for about four seconds. Paul checks out early."
            )
        elif p.has("phone") and p.verb in ("use", "call", "get", "push"):
            game.print('You lift the gold phone. "Desk," says a voice. You have nothing to ask for. Yet.')
        elif p.said("sit", "rol") or p.said("sit"):
            game.print("You sit on the bed. It sighs. So does Ginger, differently.")
        elif p.said("smell"):
            game.print("Champagne, perfume, and satin that's been steamed by a professional.")
        elif p.said("listen"):
            game.print("The city, faintly. Ice settling in the bucket. Ginger, humming the wedding march wrong.")
        else:
            return False
        return True

    def _honeymoon(self, game: Game) -> None:
        if game.flags.get("honeymoon_done"):
            game.print("The bed is stripped and the moment has left the building, in a cab, with your money.")
            return
        if not self.near(game, 70, 156, 120):
            game.print("She's on the bed. Get over there; the carpet's doing its best to stop you.")
            return
        game.flags["honeymoon_done"] = True
        game.flags["tied_up"] = True
        game.award("honeymoon", 10)
        taken = game.vars.get("money", 0)
        game.vars["money"] = 0
        game.take("key")
        game.ego.visible = False
        game.ego.frozen = True
        game.print("Ginger turns off the lamp. The city glitters. The screen, once again, does the decent thing.")
        game.print(
            '"Hold still, sugar," she says, in the dark, "I\'ve got a surprise." Something soft and '
            "ropey goes around your wrists. You assume the best. You always do."
        )
        game.print(
            "The lamp comes back on. You are tied to the heart-shaped bed with what looks like a "
            "chapel bell rope. Ginger is dressed, packed, and holding your wallet. "
            f'"Thanks for the ring, husband. And the ${taken}." She blows a kiss and takes the key. '
            "The elevator dings. You are married, broke, and tied to a bed, in that order."
        )

    def _tied_said(self, game: Game, p: Parsed) -> bool:
        if self.maid_timer:
            game.print("Help is on its way. Lie still; it's the one thing you're good at.")
        elif (
            p.has("phone")
            and p.verb in ("kick", "push", "use", "get", "call")
            or p.said("call", "maid")
            or p.said("call", "rol")
        ):
            self.maid_timer = MAID_CYCLES
            game.print(
                "You stretch a foot, hook the cord, and drag the gold phone off the nightstand. It "
                'lands face up. A tiny voice: "Desk?" You explain, mostly. "Someone will be right '
                'up," says the voice, in the tone of a desk that has done this before.'
            )
        elif p.has("untie") or p.has("rope") and p.verb in ("get", "pull", "open", "untie", "kick"):
            game.print("You struggle. The knots are excellent. Ginger was clearly a Scout, and clearly the best one.")
        elif p.has("scream") or p.said("help") or p.said("talk"):
            game.print("You yell. The penthouse is soundproofed; that's what the money was for, when you had money.")
        elif p.has("note"):
            game.print("There's a note on the nightstand. You'll read it when your hands are free.")
        elif p.said("look") or p.said("look", "room") or p.said("look", "around"):
            game.print("The ceiling. A mirror on it, unfortunately. You close your eyes; that doesn't help either.")
        elif p.verb == "look":
            return False
        elif p.said("inventory"):
            game.print("You are carrying nothing. She was thorough. Also, your hands are tied.")
        elif p.said("wait"):
            game.print("Time passes. You have a lot of it. Perhaps a foot could reach something.")
        else:
            game.print("You're tied to a bed, Paul. Your options are limited and mostly involve your feet.")
        return True

    def _freed(self, game: Game) -> None:
        game.flags["tied_up"] = False
        game.flags["freed"] = True
        game.award("freed", 5)
        game.ego.visible = True
        game.ego.frozen = False
        game.ego.x, game.ego.y = 84, 118
        game.ego.facing = "down"
        game.ego.stop()
        game.print(
            "The elevator dings. A maid comes in, takes in the scene, and unties you without a "
            "word, as though it's on the checklist. She takes the rope, leaves a mint on the "
            "pillow, and goes. You are free, broke, and married. There's a note on the nightstand."
        )
