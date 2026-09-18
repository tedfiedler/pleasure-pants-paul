"""Room 28: the roof pool. Dawn, a hot tub, an apple, and the end of the night."""

from __future__ import annotations

import pygame

from ppp.const import (
    BLACK,
    CYAN,
    DGREY,
    LBLUE,
    LCYAN,
    LGREY,
    LRED,
    PALETTE,
    PIC_W,
    WHITE,
    YELLOW,
)
from ppp.game import Game
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room
from ppp.sprite import from_ascii

TUB = (84, 100, 60, 28)  # x, y, w, h of the water
DAWN_POS = (108, 112)
DAWN_LEGEND = {"h": BLACK, "f": LRED, "k": BLACK, "w": WHITE}
DAWN_ART = """
..hhhhhh..
.hhhhhhhh.
.hhffffhh.
.hhfkfkhh.
.hhffffhh.
..hhffhh..
...ffff...
..ffffff..
.ffffffff.
"""


class Roof(Room):
    number = 28
    name = "The roof pool"
    description = (
        "The roof of the Golden Sock, under the whole sky. A pool, closed for the "
        "season and ignored, a bubbling hot tub that isn't, deck chairs, a bar cart "
        "with one bottle left, and, in the tub, a woman with dark hair and a look "
        "that has been waiting for a better offer than the city has made. The door "
        "back down is at the bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 26}
    spawns = {"default": (40, 150), 26: (20, 156)}
    looks = {
        "hooker": "Dark hair, wet, pushed back. A glass of something on the tub's edge. She "
        "watches you the way a cat watches weather: interested, uninvolved. Her name, "
        "she'll tell you if you ask, is Dawn.",
        "tub": "A hot tub, steaming, lit from beneath. It is the only warm thing on the roof and she is in it.",
        "balcony": "The pool, drained to a puddle, with a sign floating in it: CLOSED FOR THE SEASON.",
        "pool": "The pool, drained to a puddle, with a sign floating in it: CLOSED FOR THE SEASON.",
        "window": "No windows up here. Just the city, all of it, blinking.",
        "wine": "A bar cart with one bottle of champagne left, sweating, and two glasses.",
        "champagne": "A bar cart with one bottle of champagne left, sweating, and two glasses.",
        "stool": "Deck chairs, folded, stacked, done for the year.",
        "floor": "Wet tiles and the smell of chlorine. Mind your step; nobody else will.",
        "apple": "A red apple, polished, from Hope's bowl. It's the nicest thing you've ever held "
        "that wasn't a remote.",
        "sign": "CLOSED FOR THE SEASON, floating in the pool. The season, for once, has come to you.",
    }

    def __init__(self) -> None:
        self._dawn: pygame.Surface | None = None
        self._water: list[pygame.Surface] = []

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 60, BLACK)  # night
        for x, y in ((12, 8), (40, 18), (70, 6), (98, 14), (130, 10), (150, 22), (22, 30), (118, 28)):
            pic.pixel(x, y, WHITE)
        for x in range(0, PIC_W, 10):  # distant skyline
            h = 8 + (x * 3) % 16
            pic.rect(x, 60 - h, 8, h, DGREY)
            pic.pixel(x + 2, 58 - h // 2, YELLOW)
        pic.rect(0, 60, PIC_W, 4, LGREY)  # parapet
        pic.rect(0, 64, PIC_W, 104, LGREY)  # tiles
        for y in range(70, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], WHITE)
        for x in range(0, PIC_W, 12):
            pic.line([(x, 64), (x, 167)], WHITE)
        # the drained pool, left, with the sign in it
        pic.rect(6, 70, 60, 26, DGREY)
        pic.rect(8, 72, 56, 22, LBLUE)
        pic.rect(10, 88, 52, 4, CYAN)
        pic.rect(26, 78, 20, 6, WHITE)
        pic.rect(6, 70, 60, 30, None, 0)
        # the hot tub: rim, then water (animated as an underlay)
        x, y, w, h = TUB
        pic.rect(x - 6, y - 6, w + 12, h + 12, DGREY)
        pic.rect(x - 6, y - 6, w + 12, h + 12, None, 0)
        # deck chairs and the bar cart
        for cx in (8, 26):
            pic.rect(cx, 120, 14, 4, WHITE)
            pic.rect(cx, 124, 14, 8, LBLUE)
            pic.rect(cx, 128, 14, 6, None, 0)
        pic.rect(150, 96, 8, 20, LGREY, 0)
        pic.rect(152, 90, 2, 6, DGREY)
        pic.pixel(152, 89, YELLOW)
        pic.walls(64)
        pic.rect(0, 64, PIC_W, 36, None, 0)  # the parapet zone is not for walking

    def dawn(self) -> pygame.Surface:
        if self._dawn is None:
            self._dawn = from_ascii(DAWN_ART, DAWN_LEGEND)
        return self._dawn

    def water(self) -> list[pygame.Surface]:
        if not self._water:
            x, y, w, h = TUB
            for phase in range(2):
                surf = pygame.Surface((w, h))
                surf.fill(PALETTE[LCYAN])
                for row in range(0, h, 4):
                    for col in range(0, w, 8):
                        if (row // 4 + col // 8 + phase) % 2 == 0:
                            pygame.draw.rect(surf, PALETTE[CYAN], pygame.Rect(col, row, 4, 2))
                self._water.append(surf)
        return self._water

    def underlays(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        x, y, _w, _h = TUB
        return [(self.water()[(game.cycle_count // 8) % 2], x, y)]

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        if game.flags.get("won"):
            return []
        return [(self.dawn(), DAWN_POS[0], DAWN_POS[1])]

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if not game.flags.get("seen_roof"):
            game.flags["seen_roof"] = True
            game.print(
                "The roof. Wind, stars, chlorine. A private party of exactly one, in the hot tub, "
                'who looks over and says, "You\'re not the waiter."'
            )

    def _near_tub(self, game: Game) -> bool:
        x, y, w, h = TUB
        return self.near(game, x - 16, x + w + 16, y + h + 14)

    def said(self, game: Game, p: Parsed) -> bool:
        if p.said("talk", "hooker") or p.said("talk", "hooker", "rol") or p.said("talk"):
            self._talk(game)
        elif p.said("give", "apple", "rol") or p.said("give", "apple") or p.said("give", "hooker", "apple"):
            self._apple(game)
        elif p.said("give", "rol") and p.has("hooker"):
            game.print('"Sweet," says Dawn, meaning no. She has a glass. She has everything, except one thing.')
        elif p.has("tub") and p.verb in ("enter", "use", "climb", "get") or p.has("swim") or p.said("enter"):
            self._tub(game)
        elif p.has("hooker") and p.verb in ("kiss", "love", "undress"):
            if game.flags.get("dawn_apple"):
                self._tub(game)
            else:
                game.print("She lifts one eyebrow. It is the most effective thing anyone has done to you all night.")
        elif p.has("pool", "balcony") and p.verb in ("enter", "use", "swim", "climb") or p.said("climb", "rol"):
            game.die(
                "You climb the parapet for a better look at the city. The city looks back. The wind "
                "makes a suggestion and your suit, being polyester, agrees. Paul goes down in style, "
                "twenty floors of it."
            )
        elif p.said("drink", "rol") or p.said("drink"):
            game.print("You take a glass from the cart and drink. Champagne, real. Something in this city was.")
        elif p.said("smell"):
            game.print("Chlorine, champagne, and clean night air, which up here is a luxury item.")
        elif p.said("listen"):
            game.print("The tub bubbling. The city humming. A saxophone from somewhere, of course, of course.")
        else:
            return False
        return True

    def _talk(self, game: Game) -> None:
        if not self._near_tub(game):
            game.print("Walk over to the tub. She isn't going to shout; she's in water.")
        elif game.flags.get("dawn_apple"):
            game.print('"Are you getting in or not? The water\'s not going to stay this temperature and neither am I."')
        else:
            game.print(
                '"Dawn," she says, before you ask. "I know who you are. Everybody in the building knows '
                'who you are. The wedding, the rope, the maid." She sips. "You know what I haven\'t had '
                'all night, with all this?" She waves at the cart. "Something honest. Something simple."'
            )

    def _apple(self, game: Game) -> None:
        if not game.has("apple"):
            game.print(
                "You don't have an apple. You'd need to find one, somewhere polished and for the look of the thing."
            )
        elif not self._near_tub(game):
            game.print("Take it over to her. Apples thrown at hot tubs are how nights end early.")
        elif game.flags.get("dawn_apple"):
            game.print("She's already got the apple. She's got a bite out of it. What she wants now is you.")
        else:
            game.take("apple")
            game.flags["dawn_apple"] = True
            game.award("dawn_apple", 10)
            game.print(
                "You hold out the apple. Dawn looks at it for a long moment, then at you, then takes it "
                'and bites. "Huh," she says, with her mouth full. "Honest. Simple." She moves over. '
                '"Get in, Paul. Suit and all. Especially the suit."'
            )

    def _tub(self, game: Game) -> None:
        if not self._near_tub(game):
            game.print("The tub is in the middle of the roof. Walk over.")
        elif not game.flags.get("dawn_apple"):
            game.print('"Private party," says Dawn, not unkindly. "Bring something. Anything. Try honest."')
        else:
            game.flags["won"] = True
            game.award("ending", 25)
            game.ego.visible = False
            game.ego.frozen = True
            game.print(
                "You climb into the hot tub in a white leisure suit, which floats, briefly, then "
                "doesn't. Dawn laughs. It's a real laugh. You've been waiting all night for a real anything."
            )
            game.print(
                "The city blinks below. The season, it turns out, was never closed; it was waiting. "
                "Dawn puts her head on your shoulder. The saxophone, somewhere, finally stops."
            )
