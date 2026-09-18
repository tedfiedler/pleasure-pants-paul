"""Room 26: the casino's executive floor. Hope at reception, a fruit bowl, and the pool door."""

from __future__ import annotations

import pygame

from ppp import sound
from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    DGREY,
    GREEN,
    LBLUE,
    LCYAN,
    LGREEN,
    LGREY,
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
from ppp.sprite import from_ascii

# Hope: brown hair in a clip, white blouse, blue blazer. Drawn before the desk, which hides her lap.
HOPE_LEGEND = {"b": BROWN, "y": YELLOW, "f": LRED, "k": BLACK, "w": WHITE, "u": BLUE}
HOPE_ART = """
.....byyb.....
....bbbbbb....
...bbbbbbbb...
...bbbbbbbb...
...bbffffbb...
...bbfkfkbb...
...bbffffbb...
....bfffffb...
.....ffff.....
....wwwwww....
..uuwwwwwwuu..
.uuuuwwwwuuuu.
.uuuuuwwuuuuu.
.uuuuuuuuuuuu.
.uuuuuuuuuuuu.
fuuuuuuuuuuuuf
.uuuuuuuuuuuu.
..kkkkkkkkkk..
..kkkkkkkkkk..
"""
# Chance, at the same desk in Pauline's game: short brown hair, a yellow tie, the same blazer.
CHANCE_ART = """
..............
.....bbbb.....
....bbbbbb....
....bbbbbb....
....bffffb....
....bfkfkb....
.....ffff.....
.....ffff.....
.....ffff.....
....wwyyww....
..uuuwyywuuu..
.uuuuwyywuuuu.
.uuuuuyyuuuuu.
.uuuuuuuuuuuu.
.uuuuuuuuuuuu.
fuuuuuuuuuuuuf
.uuuuuuuuuuuu.
..kkkkkkkkkk..
..kkkkkkkkkk..
"""
HOPE_POS = (73, 53)  # top-left; the desk top at y=70 cuts her at the blazer
POOL_DOOR = (4, 30)
DESK = (56, 108)


class ExecFloor(Room):
    number = 26
    name = "The executive floor"
    description = (
        "A hush of carpet and brass. A reception desk with a fruit bowl and a [woman|man] "
        "behind it whose name plate says [HOPE|CHANCE]. Elevator doors on the right, a coffee "
        "machine beside them, a potted palm doing its best. On the left, a glass door "
        "marked ROOF POOL: PASS HOLDERS ONLY. The stairs down are at the bottom of "
        "the screen."
    )
    horizon = 100
    edges = {"bottom": 22}
    spawns = {"default": (76, 150), 22: (76, 156), 28: (20, 120)}
    looks = {
        "hooker": "[Hope]. Brown hair [in a clip|cut short], a blue blazer, a wedding ring, and the "
        "expression of a [woman|man] who has been told every line in this building and "
        "has a stapler. [She|He] is not for you. [She|He] knows it. So, somewhere, do you.",
        "desk": "A reception desk in fake marble with a phone, a stapler, a fruit bowl, "
        "and a framed photo turned so you can't see it.",
        "apple": "A bowl of apples on the desk, red and polished, the kind nobody ever "
        "eats because they're for the look of the thing.",
        "coffee": "A coffee machine that gives out a cup for a dollar, or for nothing if "
        "you hit it right. It has been hit right many times.",
        "elevator": "Brass doors. The penthouse. Your [wife|husband] went down in it with your money.",
        "door": "A glass door marked ROOF POOL: PASS HOLDERS ONLY. Beyond it, stairs going "
        "up and a smell of chlorine and money.",
        "plant": "A potted palm. It's plastic. Everything on this floor is a little plastic.",
        "pass": "A laminated card on a lanyard: ROOF POOL, PRIVATE PARTY. You are, tonight, a pass holder.",
        "floor": "Carpet so thick it has a weather system.",
        "window": "No windows up here, only the one you're not allowed through.",
    }

    def __init__(self) -> None:
        self._hope: dict[bool, pygame.Surface] = {}  # keyed by the game's version

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 100, LGREY)
        pic.rect(0, 0, PIC_W, 6, DGREY)
        pic.rect(0, 100, PIC_W, 68, BLUE)  # thick carpet
        for y in range(104, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], LBLUE)
        # the pool door, left
        pic.rect(POOL_DOOR[0], 30, POOL_DOOR[1] - POOL_DOOR[0], 70, DGREY, 0)
        pic.rect(POOL_DOOR[0] + 2, 32, POOL_DOOR[1] - POOL_DOOR[0] - 4, 66, LCYAN)
        pic.rect(POOL_DOOR[0] + 6, 40, 14, 6, WHITE)  # the sign
        pic.rect(POOL_DOOR[0] + 6, 48, 14, 2, RED)
        # Hope first, then the reception desk in front of her
        pic.sprite(self.hope(pic.pauline), HOPE_POS[0], HOPE_POS[1])
        pic.rect(50, 70, 60, 30, WHITE)
        pic.rect(50, 68, 60, 3, LGREY)
        pic.rect(52, 74, 56, 24, DGREY)  # a dark front panel, so the desk reads as a desk
        pic.rect(54, 84, 52, 2, LGREY)  # a drawer line
        pic.rect(54, 62, 12, 6, WHITE)  # name plate
        pic.rect(96, 60, 10, 8, YELLOW)  # fruit bowl
        pic.rect(97, 57, 3, 3, RED)
        pic.rect(101, 56, 3, 3, RED)
        pic.rect(99, 55, 3, 3, RED)
        pic.rect(50, 100, 60, 4, None, 0)
        # elevator and coffee machine, right
        pic.rect(118, 10, 22, 60, YELLOW)
        pic.line([(129, 10), (129, 69)], BLACK)
        pic.rect(142, 40, 14, 60, DGREY, 0)
        pic.rect(144, 44, 10, 10, BLACK)
        pic.rect(146, 58, 6, 6, RED)  # the button
        pic.rect(144, 70, 10, 4, BLACK)  # the slot
        # potted palm
        pic.rect(36, 82, 10, 18, BROWN, 0)
        pic.rect(34, 100, 14, 4, None, 0)
        for dx, dy in ((-6, -8), (0, -12), (6, -8), (-3, -4), (3, -4)):
            pic.line([(41, 82), (41 + dx * 2, 82 + dy * 2)], GREEN)
            pic.pixel(41 + dx * 2, 82 + dy * 2, LGREEN)
        pic.walls(100)

    def hope(self, pauline: bool = False) -> pygame.Surface:
        if pauline not in self._hope:
            self._hope[pauline] = from_ascii(CHANCE_ART if pauline else HOPE_ART, HOPE_LEGEND)
        return self._hope[pauline]

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if not game.flags.get("seen_execfloor"):
            game.flags["seen_execfloor"] = True
            game.print(
                '[Hope] looks up from the desk. "Can I help you?" It is the least helpful sentence '
                "in the language and [she|he] has practised it."
            )

    def said(self, game: Game, p: Parsed) -> bool:
        at_desk = self.near(game, 46, 116, 118)
        at_machine = self.near(game, 130, 160, 118)
        if p.said("talk", "hooker") or p.said("talk", "hooker", "rol") or p.said("talk"):
            self._talk(game, at_desk)
        elif p.has("hooker") and p.verb in ("kiss", "love", "dance", "seduce"):
            game.print(
                '[Hope] lifts [her|his] left hand without looking up. The ring catches the light. "Married. '
                'Happily. To a [man|woman] who bench-presses receptionists." [She|He] goes back to typing.'
            )
        elif p.said("give", "rol") and p.has("hooker") and not p.has("coffee"):
            game.print("\"No thank you.\" [She|He] hasn't looked at what it is. [She|He] doesn't need to.")
        elif p.has("coffee") and p.verb in ("get", "use", "buy", "push", "kick", "make"):
            self._coffee(game, at_machine)
        elif p.said("give", "coffee", "rol") or p.said("give", "coffee") or p.said("give", "hooker", "coffee"):
            self._give_coffee(game, at_desk)
        elif p.said("get", "apple") or p.said("get", "apple", "rol") or p.said("eat", "apple"):
            self._apple(game, at_desk, eat=p.verb == "eat")
        elif (
            p.has("door")
            and p.verb in ("open", "enter", "use")
            or p.has("balcony")
            and p.verb in ("enter", "use", "open")
        ):
            self._pool_door(game)
        elif p.has("elevator") and p.verb in ("open", "enter", "use", "push", "call"):
            game.print("The doors don't open for you. You know why. Everybody on this floor knows why.")
        elif p.said("look", "photo") or p.said("look", "photo", "rol") or p.said("get", "photo"):
            if not at_desk:
                game.print("It's on the desk, turned away. Walk up if you must.")
            else:
                game.award("hope_photo")
                game.print(
                    "You lean over. The photo is [Hope] and a [man|woman] the size of a vending machine, both "
                    'laughing, on a beach. [Hope] turns it back around without looking up. "Yes," [she|he] says.'
                )
        elif p.said("get", "plant") or p.said("kick", "plant"):
            game.print("It's plastic and it's bolted. Somebody anticipated you.")
        elif p.said("smell"):
            game.print("Coffee, carpet, and a [perfume|cologne] that costs more than your suit did new.")
        elif p.said("listen"):
            game.print("Typing. The hum of the machine. Through the glass door, faintly, splashing and a laugh.")
        else:
            return False
        return True

    def _talk(self, game: Game, at_desk: bool) -> None:
        if not at_desk:
            game.print("Walk up to the desk. [She|He] doesn't raise [her|his] voice; [she|he] has a stapler for that.")
        elif game.has("pass") or game.flags.get("pool_pass"):
            game.print('"Enjoy the party. Try not to drown; the paperwork\'s on me."')
        elif game.flags.get("hope_coffee"):
            game.print(
                '"You brought me coffee. Nobody brings me coffee." [She|He] slides the '
                'pass across. "Go on. Before I think about it."'
            )
        elif game.flags.get("honeymoon_done"):
            game.print(
                '"You\'re the one from the penthouse." It isn\'t a question. "Oh, honey." [She|He] looks at '
                "you the way the whole city has been looking at you. \"There's a party on the roof. I "
                "could... no. I couldn't. I haven't had a coffee in six hours.\""
            )
        else:
            game.print('"The pool is for pass holders, the elevator is for guests, and the stairs are for you."')

    def _coffee(self, game: Game, at_machine: bool) -> None:
        if game.has("coffee"):
            game.print("You have a coffee. It's going cold, like most things you're holding.")
        elif not at_machine:
            game.print("The coffee machine is on the right, past the elevator. Walk over.")
        else:
            game.give("coffee")
            game.print(
                "You hit the machine where the dent is. It thinks about it and produces a cup of "
                "something hot and brown. Free. The first thing tonight that was."
            )

    def _give_coffee(self, game: Game, at_desk: bool) -> None:
        if not game.has("coffee"):
            game.print("You don't have a coffee. There's a machine on the right, and it has a dent.")
        elif not at_desk:
            game.print("Bring it to the desk. Coffee thrown across a lobby is assault.")
        elif not game.flags.get("honeymoon_done"):
            game.take("coffee")
            game.print('"Thanks." [She|He] drinks it. That\'s all. Nothing changes, except you have no coffee.')
        else:
            game.take("coffee")
            game.give("pass")
            game.flags["hope_coffee"] = True
            game.flags["pool_pass"] = True
            game.award("hope_coffee")
            game.print(
                '[Hope] takes the cup in both hands. "Nobody brings me coffee." [She|He] opens a drawer, '
                "takes out a laminated pass on a lanyard, and puts it on the desk between you. "
                "\"Roof pool. Private party. Don't make me regret this, and don't tell my [husband|wife], "
                '[he|she]\'ll want one." Take an apple, [she|he] adds. "For the look of the thing."'
            )

    def _apple(self, game: Game, at_desk: bool, eat: bool) -> None:
        if eat and game.has("apple"):
            game.print("You take a bite, then stop. Someone else might want the rest more. You wipe it on your suit.")
        elif game.has("apple"):
            game.print("You have one. The bowl has more, but [Hope] has a stapler.")
        elif not at_desk:
            game.print("The apples are on the desk. Walk over.")
        elif not game.flags.get("hope_coffee"):
            game.print('"Those are for the look of the thing," says [Hope], not looking up. You put it back. Slowly.')
        else:
            game.give("apple")
            game.award("apple")
            game.print("You take an apple from the bowl. Red, polished, and for once, for you.")

    def _pool_door(self, game: Game) -> None:
        if not self.near(game, 2, 40, 126):
            game.print("The pool door is on the left. Walk up to it.")
        elif game.has("pass") or game.flags.get("pool_pass"):
            sound.play("ding")
            game.new_room(28)
        else:
            game.print("Locked. A card reader blinks at you, red. PASS HOLDERS ONLY. You are not a holder of a pass.")
