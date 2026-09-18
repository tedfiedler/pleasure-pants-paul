"""Room 24: the Chapel of Eternal Regret. A preacher, an altar, and, with luck, a bride.

In Pauline's game she is the bride, and it's Rusty who waits at the altar, in a top hat.
"""

from __future__ import annotations

import pygame

from ppp import sound
from ppp.const import (
    BLACK,
    BROWN,
    DGREY,
    LBLUE,
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
from ppp.rooms.disco import GINGER_LEGEND, ginger_art
from ppp.sprite import from_rows, rows_of

FEE = 50
AISLE_X = (66, 94)
GINGER_POS = (52, 100)


def _veiled() -> list[str]:
    """Ginger's disco sprite with a white veil over the hair."""
    rows = rows_of(ginger_art(False)[0])
    return [r.replace("h", "v") for r in rows[:7]] + rows[7:]


def _top_hatted() -> list[str]:
    """Rusty's disco sprite dressed for a wedding: a top hat, and the open shirt closed with a black tie."""
    rows = rows_of(ginger_art(True)[0])
    hat = ["....kkkk...."] * 3 + ["..kkkkkkkk.."]  # crown, then a brim where the top of his hair was
    return hat + rows[1:7] + [r.replace("ww", "kk") for r in rows[7:8]] + rows[8:]


class Chapel(Room):
    number = 24
    name = "The Chapel of Eternal Regret"
    description = (
        "A chapel the size of a garage, which it was. Pews in two rows, an aisle of "
        "red carpet, an altar under a stained-glass window of a heart with a dollar "
        "sign in it. A preacher in a purple robe waits behind the altar with the "
        "patience of a [man|woman] paid by the ceremony. An organ wheezes in the corner. "
        "A collection box by the door. The way out is at the bottom of the screen."
    )
    horizon = 98
    edges = {"bottom": 23}
    spawns = {"default": (76, 150), 23: (76, 156)}
    looks = {
        "preacher": "A preacher in a purple robe with a gold sash and a tan that stops at "
        "the collar. [His|Her] smile has married four hundred couples and remembers none.",
        "altar": "A card table under a lace cloth, with a plastic candelabra and a book that "
        "might be a Bible or might be a phone book. Both work here.",
        "glass": "The stained-glass window: a heart, pierced by an arrow, with a dollar sign "
        "where the arrow goes in. Subtle as a brick.",
        "window": "The stained-glass window: a heart, pierced by an arrow, with a dollar sign "
        "where the arrow goes in. Subtle as a brick.",
        "pew": "Pews with cushions in a red that was cheaper than the other reds.",
        "organ": "An electric organ with a cigarette burn on middle C. The organist has stepped out, or been asked to.",
        "bell": "A rope hangs from a hole in the ceiling. Pull it and the bell in the "
        "steeple rings. Tradition says after the vows. Tradition says a lot of things.",
        "collection": "A wooden box by the door, slotted, padlocked, and heavier than it "
        "looks, with a sign: FOR THE NEEDY. The needy have a lawyer.",
        "floor": "Red carpet down the aisle, wearing a path to the altar and a wider one back.",
        "ring": "A diamond ring, still in your pocket, waiting for a finger.",
        "key": "A brass key on a heart-shaped fob: GOLDEN SOCK, PENTHOUSE. Your honeymoon suite.",
        "door": "The way out. Bottom of the screen. Nobody's stopping you; that's the tragedy.",
    }

    def __init__(self) -> None:
        self._ginger: dict[bool, pygame.Surface] = {}  # by version: a restored game may switch

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 98, LBLUE)  # pale blue plaster
        for y in range(8, 98, 12):
            pic.line([(0, y), (PIC_W - 1, y)], WHITE)
        pic.rect(0, 98, PIC_W, 70, BROWN)  # boards
        for y in range(104, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        pic.rect(AISLE_X[0], 98, AISLE_X[1] - AISLE_X[0], 70, RED)  # aisle runner
        # stained glass: a heart with a dollar sign in it
        pic.rect(60, 6, 40, 52, BLACK)
        pic.rect(62, 8, 36, 48, LBLUE)
        pic.ellipse(64, 14, 16, 14, LRED)
        pic.ellipse(80, 14, 16, 14, LRED)
        pic.poly([(66, 24), (94, 24), (80, 46)], LRED)
        pic.rect(78, 22, 4, 16, YELLOW)
        pic.rect(74, 26, 12, 3, YELLOW)
        pic.rect(74, 32, 12, 3, YELLOW)
        pic.line([(62, 30), (97, 30)], BLACK)
        pic.line([(80, 8), (80, 55)], BLACK)
        # preacher, then the altar in front of him (her, for Pauline: draw_person swaps everybody)
        draw_person(pic, 76, 40, suit=MAGENTA, skin=LRED, hair=LGREY)
        pic.rect(78, 50, 4, 10, YELLOW)  # sash
        pic.rect(60, 74, 40, 24, WHITE)  # altar
        pic.rect(60, 96, 40, 2, LGREY)
        pic.rect(70, 66, 20, 8, LGREY)  # candelabra base
        for x in (72, 79, 86):
            pic.rect(x, 60, 2, 8, WHITE)
            pic.pixel(x, 59, YELLOW)
        pic.rect(64, 80, 12, 8, BLACK)  # the book
        pic.rect(60, 98, 40, 4, None, 0)
        # organ, back right
        pic.rect(120, 40, 34, 58, DGREY, 0)
        pic.rect(122, 42, 30, 20, BLACK)
        pic.rect(124, 66, 26, 6, WHITE)
        for x in range(126, 150, 4):
            pic.rect(x, 66, 2, 4, BLACK)
        pic.rect(120, 98, 34, 4, None, 0)
        # bell rope, left
        pic.line([(20, 0), (20, 60)], BROWN)
        pic.rect(18, 60, 4, 6, RED)
        # pews: two rows each side of the aisle
        for y in (112, 132):
            for x0, x1 in ((6, AISLE_X[0] - 6), (AISLE_X[1] + 6, 154)):
                pic.rect(x0, y - 8, x1 - x0, 6, BROWN)  # back
                pic.rect(x0, y - 2, x1 - x0, 6, RED)  # cushion
                pic.rect(x0, y - 8, x1 - x0, 14, None, 0)
        # collection box by the door, bottom right
        pic.rect(132, 150, 14, 12, BROWN, 0)
        pic.rect(134, 152, 10, 2, BLACK)
        pic.rect(138, 156, 3, 3, YELLOW)
        pic.walls(98)

    def ginger(self, pauline: bool = False) -> pygame.Surface:
        if pauline not in self._ginger:
            legend = dict(GINGER_LEGEND)
            legend["v"] = WHITE
            self._ginger[pauline] = from_rows(_top_hatted() if pauline else _veiled(), legend)
        return self._ginger[pauline]

    def bride_present(self, game: Game) -> bool:
        return bool(game.flags.get("ginger_danced")) and not game.flags.get("ginger_married")

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        if not self.bride_present(game):
            return []
        return [(self.ginger(game.pauline), GINGER_POS[0], GINGER_POS[1])]

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if self.bride_present(game):
            game.print(
                "[Ginger] is at the altar in a [veil she must have brought with her. She|top hat he must "
                "have brought with him. He] turns. "
                '"Took you long enough," [she|he] says, fondly, or something near it.'
            )
        elif game.flags.get("ginger_married"):
            game.print(
                "The chapel is empty. Your [wife|husband] has gone ahead to the penthouse. "
                "Your [wife|husband]. Say it again."
            )
        elif not game.flags.get("seen_chapel"):
            game.flags["seen_chapel"] = True
            game.print(
                '"Welcome, welcome," says the preacher. "[Bride|Groom]?" [He|She] looks past you. "Ah. Browsing."'
            )

    def _at_altar(self, game: Game) -> bool:
        return self.near(game, 56, 104, 112)

    def said(self, game: Game, p: Parsed) -> bool:
        bride = self.bride_present(game)
        if p.said("talk", "preacher") or p.said("talk", "preacher", "rol") or p.said("talk"):
            self._talk_preacher(game, bride)
        elif p.said("talk", "hooker") or p.said("talk", "hooker", "rol"):
            if bride:
                game.print(
                    '"Pay the [man|lady], give me the ring, say yes." [Ginger] counts them off '
                    'on [her|his] fingers. "Three things."'
                )
            elif game.flags.get("ginger_married"):
                game.print(
                    "[She|He]'s not here. [She|He]'s at the penthouse. You have the key; you have a [wife|husband]. Go."
                )
            else:
                game.print(
                    "There's no [bride|groom] here. There's a preacher, an organ, and you. "
                    "It's not enough for a wedding."
                )
        elif p.said("pay", "rol") or p.said("pay") or p.said("give", "money", "rol"):
            self._pay(game, bride)
        elif p.has("marry") or p.said("give", "ring", "rol") or p.said("give", "ring") or p.said("use", "ring"):
            self._marry(game, bride)
        elif p.has("bell", "rope") and p.verb in ("pull", "use", "push"):
            self._bell(game)
        elif p.has("collection") and p.verb in ("get", "open", "steal", "push", "look") and p.verb != "look":
            game.die(
                "You lift the collection box. Lightning comes through the stained glass, "
                "which was not designed for it. The preacher does not look surprised. [Paul] "
                "is a small pile of ash in a [leisure suit|pantsuit], which is at least easy to sweep."
            )
        elif p.said("play", "organ") or p.said("use", "organ"):
            game.award("organ")
            sound.play("buzz")
            game.print("You press a key. The organ plays a chord that sounds like a question nobody wants answered.")
        elif p.said("dance", "rol") or p.said("dance"):
            if bride:
                game.award("dance_aisle")
                game.print(
                    "You dance [Ginger] down the aisle. The preacher taps [his|her] watch, which is a wedding ring."
                )
            else:
                game.print("You dance alone in the aisle. The organ does not join in. Neither does anyone.")
        elif p.said("sit", "rol") or p.said("sit"):
            game.award("pew")
            game.print("You sit in a pew. It's the loneliest seat in the city, and you know from lonely seats.")
        elif p.said("kiss", "hooker"):
            game.print(
                '"After," says [Ginger]. "Pay the [man|lady] first."'
                if bride
                else "Nobody to kiss. The preacher has a policy."
            )
        elif p.said("smell"):
            game.print("Candle wax, carpet cleaner, and plastic lilies.")
        elif p.said("listen"):
            game.print(
                "The organ, idling. The preacher humming the fee to [himself|herself]. "
                "Outside, a cab that isn't waiting."
            )
        else:
            return False
        return True

    def _talk_preacher(self, game: Game, bride: bool) -> None:
        if game.flags.get("honeymoon_done"):
            game.award("confess")
            game.print(
                "You tell [him|her] about the rope, the wallet, [the maid|housekeeping]. [He|She] nods through "
                'all of it. "[Son|Child]," '
                '[he|she] says, "that\'s every marriage. Yours was just faster." [He|She] does not offer a refund.'
            )
        elif game.flags.get("ginger_married"):
            game.print('"Congratulations, [son|child]. Come back any time. Statistically, you will."')
        elif not bride:
            game.print(
                '"No [bride|groom], no wedding," says the preacher. "I did one the other way once. '
                'The paperwork was murder." [He|She] looks at [his|her] watch, which is a wedding ring.'
            )
        elif not game.flags.get("chapel_paid"):
            game.print(
                "\"Fifty dollars for the ceremony, [son|child]. And a ring; I don't "
                'rent them any more. Not since the incident."'
            )
        elif not game.has("ring"):
            game.print('"Paid up. Now the ring." [He|She] looks at your hands. "The ring, [son|child]."')
        else:
            game.print(
                "\"Paid, ringed, and a [bride|groom] who's stopped checking [her|his] watch. "
                'Say the word. The word is MARRY."'
            )

    def _pay(self, game: Game, bride: bool) -> None:
        money = game.vars.get("money", 0)
        if game.flags.get("chapel_paid"):
            game.print(
                "You've paid. The preacher keeps the receipt in [his|her] heart and the money in [his|her] sock."
            )
        elif not bride:
            game.print('"Pay for what? Bring a [bride|groom]. I\'m not a wishing well."')
        elif not self._at_altar(game):
            game.print("Walk up to the altar. [He|She] doesn't do curbside either.")
        elif money < FEE:
            game.print(
                f'"Fifty." You have ${money}. "The casino\'s that way," [he|she] says, and blesses you, briefly.'
            )
        else:
            game.vars["money"] = money - FEE
            game.flags["chapel_paid"] = True
            game.print(
                f"You hand over ${FEE}. It vanishes into the robe. You have ${game.vars['money']} left, and a preacher."
            )

    def _marry(self, game: Game, bride: bool) -> None:
        if game.flags.get("ginger_married"):
            game.print("You're married. Once is the tradition. Twice is a hobby.")
        elif not bride:
            game.print("Marry whom? The preacher is spoken for, and the organ is only mildly interested.")
        elif not self._at_altar(game):
            game.print("At the altar, [Paul]. Weddings are location-sensitive.")
        elif not game.flags.get("chapel_paid"):
            game.print('"Fifty dollars first," says the preacher, gently, the way a bouncer is gentle.')
        elif not game.has("ring"):
            game.print(
                "[Ginger] holds out [her|his] hand. You have nothing to put on it. "
                '"[Paul]," [she|he] says. That\'s all. "[Paul]."'
            )
        else:
            game.take("ring")
            sound.play("wedding")
            game.flags["ginger_married"] = True
            game.give("key")
            game.award("wedding")
            game.print(
                'The preacher opens the book. "Dearly beloved, and [Paul]." [Ginger] takes your hand. '
                "The organ finds a chord. The candelabra, somehow, lights itself."
            )
            game.print(
                '"Do you?" "I do." "Do you?" "Sure." You slide the ring onto [her|his] finger. It fits, '
                "which you take as a sign, because you take everything as a sign."
            )
            game.print(
                '"I now pronounce you," says the preacher, and pauses to see if either of you '
                'objects. [Ginger] kisses you. It lasts. "Golden Sock, penthouse," [she|he] says, pressing '
                'a brass key into your hand. "Don\'t keep a [girl|guy] waiting." [She|He] goes. '
                "The organ plays [her|him] out."
            )

    def _bell(self, game: Game) -> None:
        if not self.near(game, 8, 34, 116):
            game.print("The rope is on the left wall. Walk over; it doesn't stretch.")
        elif game.flags.get("ginger_married"):
            game.award("bell")
            game.print(
                "You pull the rope. The bell rings out over the street, once, "
                "twice. Somewhere a neighbour swears. You are married."
            )
        else:
            game.print(
                "You pull the rope. The bell rings. The preacher clears [his|her] throat: "
                '"After, [son|child]. It\'s for after."'
            )
