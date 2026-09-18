"""Room 19: outside the Boogie Palace. A velvet rope, a doorman, and a way past him."""

from __future__ import annotations

import pygame

from ppp.cab import Curb
from ppp.const import (
    BLACK,
    BLUE,
    DGREY,
    LBLUE,
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
from ppp.npc import draw_person
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

DOOR_X = (70, 90)
CURB_Y = 118
ROAD_Y = 140


class DiscoStreet(Room):
    number = 19
    name = "Outside the Boogie Palace"
    description = (
        "The Boogie Palace throbs behind a purple door. A velvet rope keeps the "
        "sidewalk in line and a doorman keeps the rope. Music leaks out every time "
        "the door opens, which is never for you. Cabs stop at the curb."
    )
    horizon = CURB_Y
    edges = {}
    spawns = {"default": (100, 136), 13: (100, 136), 20: (76, 128)}
    looks = {
        "building": "A black-painted front with a purple door and a lot of chrome. It was "
        "fashionable in the year it opened and has been waiting since.",
        "sign": "BOOGIE PALACE, in pink neon script that buzzes like a wasp in a jar.",
        "door": "A purple door with a porthole. Every time it opens you hear bass and see "
        "lights. Every time it closes you see the doorman.",
        "bouncer": "A doorman in a tuxedo two sizes too tight, with a clipboard he doesn't "
        "read and a face that has never been on a list either. He's bored, which is "
        "worse than mean.",
        "rope": "A velvet rope on brass posts. It is the most expensive thing on the block "
        "and it is here to keep you out.",
        "window": "No windows. Discos don't believe in outside.",
        "floor": "Sidewalk with a sprinkle of glitter that never quite sweeps up.",
        "pass": "You don't have a pass. Look at you. Of course you don't.",
        "magazine": "A brown-paper magazine. Not everyone reads it for the articles.",
    }

    def __init__(self) -> None:
        self.curb = Curb(ROAD_Y)

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, CURB_Y, BLUE)
        pic.rect(0, 0, PIC_W, 100, BLACK)  # painted front
        pic.rect(0, 100, PIC_W, 18, DGREY)
        pic.rect(0, CURB_Y, PIC_W, ROAD_Y - CURB_Y, LGREY)
        pic.rect(0, ROAD_Y, PIC_W, 28, BLACK)
        pic.line([(0, 154), (PIC_W - 1, 154)], YELLOW)
        pic.line([(0, CURB_Y), (PIC_W - 1, CURB_Y)], WHITE)
        for y in range(10, 100, 12):  # chrome strips
            pic.line([(0, y), (PIC_W - 1, y)], LGREY)
        # neon sign
        pic.rect(36, 16, 88, 20, DGREY)
        pic.rect(38, 18, 84, 16, BLACK)
        pic.line([(42, 30), (48, 22), (54, 30), (60, 22), (66, 30)], LMAGENTA)
        pic.line([(72, 22), (72, 30), (80, 30)], LMAGENTA)
        pic.line([(86, 22), (92, 30), (98, 22), (104, 30), (110, 22), (116, 30)], LMAGENTA)
        # purple door with porthole
        pic.rect(DOOR_X[0] - 2, 44, 24, 74, DGREY, 0)
        pic.rect(DOOR_X[0], 46, 20, 72, MAGENTA)
        pic.rect(76, 58, 8, 8, LCYAN)
        pic.rect(86, 84, 2, 6, YELLOW)
        # velvet rope on posts along the sidewalk
        for x in (40, 66, 96, 122):
            pic.rect(x, 106, 2, 14, YELLOW, 0)
        pic.line([(40, 108), (53, 112), (66, 108)], RED)
        pic.line([(96, 108), (109, 112), (122, 108)], RED)
        # the doorman beside the door
        draw_person(pic, 96, 84, suit=BLACK, skin=LRED, hair=BLACK)
        pic.rect(98, 92, 4, 6, WHITE)  # shirt front
        pic.rect(96, 108, 8, 12, None, 0)
        pic.rect(122, 60, 26, 30, LBLUE)  # a poster
        pic.rect(124, 62, 22, 26, LMAGENTA)
        pic.walls(CURB_Y)
        pic.rect(38, CURB_Y, 30, 4, None, 0)  # rope posts block
        pic.rect(94, CURB_Y, 30, 4, None, 0)
        pic.rect(DOOR_X[0], CURB_Y, DOOR_X[1] - DOOR_X[0], 2, None, 2)

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        return self.curb.objects()

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.curb.on_enter(game, from_room)
        if not game.flags.get("seen_discostreet"):
            game.flags["seen_discostreet"] = True
            game.print(
                "Bass through the pavement. Glitter in the gutter. The doorman looks at "
                "your suit, then at his clipboard, then at nothing, which is where you are on it."
            )

    def _at_door(self, game: Game) -> bool:
        return DOOR_X[0] <= game.ego.centre_x <= DOOR_X[1] and game.ego.y <= 130

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and DOOR_X[0] <= ego.centre_x <= DOOR_X[1] and ego.y <= self.horizon + 1:
            self._try_door(game)
            return
        self.curb.update(game)

    def _try_door(self, game: Game) -> None:
        if game.flags.get("disco_admitted"):
            game.new_room(20)
            return
        game.ego.stop()
        game.ego.y = 126
        game.print(
            'The doorman\'s arm drops like a toll gate. "Members only." You are not a '
            "member. You have never been a member of anything that had a door."
        )

    def said(self, game: Game, p: Parsed) -> bool:
        if self.curb.said(game, p):
            pass
        elif p.said("talk", "bouncer") or p.said("talk", "bouncer", "rol") or p.said("talk"):
            if game.flags.get("disco_admitted"):
                game.print('"Go on in, sir." He says sir the way other men say buddy.')
            else:
                game.print(
                    '"Members only." He taps the clipboard. "Or a pass. Or..." He looks at '
                    "you sideways. \"Or you make it worth my while, and I don't mean money, "
                    'I got money."'
                )
        elif p.said("give", "magazine") or p.said("give", "magazine", "rol") or p.said("give", "bouncer", "magazine"):
            self._bribe(game)
        elif p.said("give", "rol") and p.has("bouncer"):
            game.print('He glances at it. "Not that." His eyes drift, briefly, to your coat pocket. Interesting.')
        elif p.said("show", "pass") or p.said("give", "pass") or p.said("use", "pass"):
            game.print("You'd need a pass first. You don't. The doorman knows it. The rope knows it.")
        elif p.said("push", "bouncer") or p.said("kick", "bouncer") or p.said("kiss", "bouncer"):
            game.print(
                "You try to get past him. He lifts you with one hand and puts you back "
                "on the curb the way you'd set down a cup. Nothing spilled. Nothing gained."
            )
            game.ego.x, game.ego.y = 100, 136
        elif p.said("open", "door") or p.said("enter", "door") or p.said("enter", "disco") or p.said("enter"):
            if self.curb.near(game):
                game.new_room(13)
            elif self._at_door(game):
                self._try_door(game)
            else:
                game.print("Walk up to the purple door, if the doorman lets you.")
        elif p.said("open", "rope") or p.said("pull", "rope") or p.said("get", "rope"):
            game.print("You unhook the rope. The doorman re-hooks it, with your hand still on it.")
        elif p.said("dance"):
            game.print("You dance on the sidewalk. The doorman watches. Whatever chance you had, it's smaller now.")
        elif p.said("smell"):
            game.print("Dry ice, hairspray, and a cologne that should have been declared at customs.")
        elif p.said("listen"):
            game.print("Bass, bass, bass, and under it, faintly, a song you danced to once and shouldn't have.")
        else:
            return False
        return True

    def _bribe(self, game: Game) -> None:
        if not game.has("magazine"):
            game.print("You don't have a magazine. The doorman looks, briefly, disappointed in you.")
        elif not (80 <= game.ego.centre_x <= 120 and game.ego.y <= 130):
            game.print("Walk up to the doorman. Discreetly. This is a discreet kind of transaction.")
        elif game.flags.get("disco_admitted"):
            game.print("He's already got what he wanted. Don't push it; he's a page-turner.")
        else:
            game.take("magazine")
            game.flags["disco_admitted"] = True
            game.award("bribe_doorman", 2)
            game.print(
                "You slide the brown-paper magazine into the clipboard. The doorman does "
                'not look down. "Never seen you before," he says warmly, unhooking the rope. '
                '"Have a good night, sir."'
            )
