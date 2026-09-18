"""Room 20: inside the Boogie Palace. A lit floor, a mirror ball, a DJ, and Ginger."""

from __future__ import annotations

import pygame

from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    CYAN,
    DGREY,
    LBLUE,
    LCYAN,
    LGREEN,
    LGREY,
    LMAGENTA,
    LRED,
    MAGENTA,
    PALETTE,
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
from ppp.sprite import from_ascii

FLOOR = (40, 104, 80, 40)  # x, y, w, h of the lit dance floor
TABLE_X, TABLE_Y = 12, 120
GINGER_TABLE = (16, 132)
GINGER_FLOOR = (92, 140)
DANCE_CYCLES = 120
LADIES_X = (104, 124)

GINGER_LEGEND = {"r": LRED, "f": LRED, "g": LGREEN, "k": BLACK, "w": WHITE, "h": RED}
GINGER_ART = """
...hhhhhh...
..hhhhhhhh..
..hhffffhh..
..hhfkfkhh..
..hhffffhh..
..hhhffhhh..
..hh.ff.hh..
....gggg....
...gggggg...
..gggggggg..
..gggggggg..
.fgggggggg..
..gggggggg..
..gggggggg..
..gggggggg..
...gggggg...
...ffff.....
...ffff.....
...ffff.....
...ffff.....
...ffff.....
...ffff.....
..kkkk......
..kkkk......
"""
GINGER_DANCE = """
...hhhhhh...
..hhhhhhhh..
..hhffffhh..
..hhfkfkhh..
..hhffffhh..
..hhhffhhh..
f.hh.ff.hh.f
.g..gggg..g.
..ggggggggg.
..gggggggg..
..gggggggg..
..gggggggg..
..gggggggg..
..gggggggg..
..gggggggg..
...gggggg...
..ff..ff....
..ff...ff...
..ff...ff...
.ff.....ff..
.ff.....ff..
.ff.....ff..
kkk.....kkk.
kkk.....kkk.
"""
FLOOR_COLOURS = (MAGENTA, CYAN, YELLOW, LMAGENTA, LBLUE, LGREEN, RED, LCYAN)


class Disco(Room):
    number = 20
    name = "The Boogie Palace"
    description = (
        "The Boogie Palace, at full throb. A lit dance floor pulses in the middle, a "
        "mirror ball throws light on everyone but you, and a DJ in a booth on the "
        "right is playing something with a saxophone. There's a bar along the back "
        "and a table by the left wall where a redhead in green sits alone, which is "
        "a temporary condition she seems fine with. A door at the back right says "
        "LADIES. The exit is at the bottom of the screen."
    )
    horizon = 98
    edges = {"bottom": 19}
    spawns = {"default": (76, 150), 19: (76, 156)}
    looks = {
        "hooker": "Red hair, green dress, a drink with an umbrella in it and a look that "
        "has already priced you. Her name, the napkin says, is Ginger. She has "
        "written it herself, and underlined it.",
        "floor": "The dance floor is a grid of glass squares lit from below, pulsing in "
        "colours that don't occur in nature or in good taste.",
        "ball": "A mirror ball, turning slowly, throwing a thousand tiny spotlights "
        "on people who are having a better night than you.",
        "dj": "A DJ with headphones around his neck and sunglasses on, indoors, at "
        "night. He is nodding to a beat that is not the one playing.",
        "bar": "A chrome bar along the back wall with bottles lit from below. The bartender "
        "is a silhouette and prefers it that way.",
        "stool": "A small round table by the wall, with a candle in a red jar and Ginger.",
        "door": "A door at the back right marked LADIES. It's not for you. Nothing here is, yet.",
        "wall": "Black walls, chrome trim, and a smell that clings.",
        "candy": "A heart-shaped box of chocolates, two missing. Someone in here might like them.",
        "wine": "A bottle of Chateau Kwik. In this light it's almost champagne.",
        "ring": "You don't have a ring. You have a sense that you'll need one.",
    }

    def __init__(self) -> None:
        self._ginger: list[pygame.Surface] = []
        self._floor: list[pygame.Surface] = []
        self.dance_timer = 0

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 98, BLACK)
        pic.rect(0, 98, PIC_W, 70, DGREY)
        for y in range(98, 168, 10):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        # back bar with lit bottles
        pic.rect(20, 40, 76, 30, DGREY)
        pic.rect(22, 42, 72, 26, BLACK)
        for i, c in enumerate((LMAGENTA, LCYAN, YELLOW, LGREEN, LRED, LBLUE, LMAGENTA)):
            pic.rect(28 + i * 10, 50, 3, 14, c)
        pic.rect(16, 70, 84, 12, LGREY)  # chrome bar top
        pic.rect(16, 82, 84, 16, DGREY)
        pic.rect(16, 82, 84, 18, None, 0)
        draw_person(pic, 52, 46, suit=BLACK, skin=DGREY, hair=BLACK)  # silhouette bartender
        # ladies room door, between the bar and the booth
        pic.rect(LADIES_X[0], 40, LADIES_X[1] - LADIES_X[0], 58, MAGENTA)
        pic.rect(LADIES_X[0] + 4, 46, 12, 6, WHITE)
        pic.pixel(LADIES_X[1] - 3, 72, YELLOW)
        # DJ booth on the right, the DJ drawn before the booth hides his legs
        draw_person(pic, 136, 36, suit=RED, skin=LRED, hair=BLACK)
        pic.rect(136, 38, 8, 3, BLACK)  # sunglasses
        pic.rect(126, 60, 32, 40, BLUE, 0)
        pic.rect(128, 62, 28, 6, LBLUE)
        pic.rect(130, 72, 10, 8, BLACK)  # turntables
        pic.rect(144, 72, 10, 8, BLACK)
        pic.rect(133, 74, 4, 4, LGREY)
        pic.rect(147, 74, 4, 4, LGREY)
        # mirror ball
        pic.ellipse(70, 4, 20, 18, LGREY)
        for x, y in ((74, 8), (80, 12), (86, 8), (76, 16), (84, 18)):
            pic.pixel(x, y, WHITE)
        pic.line([(80, 0), (80, 4)], LGREY)
        # Ginger's table
        pic.rect(TABLE_X, TABLE_Y, 30, 6, BROWN)
        pic.rect(TABLE_X + 13, TABLE_Y + 6, 4, 14, BROWN)
        pic.rect(TABLE_X + 12, TABLE_Y - 6, 4, 6, RED)  # candle jar
        pic.pixel(TABLE_X + 14, TABLE_Y - 7, YELLOW)
        pic.rect(TABLE_X, TABLE_Y + 18, 30, 4, None, 0)
        pic.walls(98)

    # -- sprites -------------------------------------------------------------------

    def ginger(self, dancing: bool) -> pygame.Surface:
        if not self._ginger:
            self._ginger = [from_ascii(GINGER_ART, GINGER_LEGEND), from_ascii(GINGER_DANCE, GINGER_LEGEND)]
        return self._ginger[1 if dancing else 0]

    def floor_frames(self) -> list[pygame.Surface]:
        if not self._floor:
            x, y, w, h = FLOOR
            for phase in range(4):
                surf = pygame.Surface((w, h))
                for row in range(h // 8):
                    for col in range(w // 8):
                        colour = FLOOR_COLOURS[(row + col * 3 + phase * 5) % len(FLOOR_COLOURS)]
                        pygame.draw.rect(surf, PALETTE[colour], pygame.Rect(col * 8, row * 8, 8, 8))
                        pygame.draw.rect(surf, PALETTE[BLACK], pygame.Rect(col * 8, row * 8, 8, 8), 1)
                self._floor.append(surf)
        return self._floor

    def underlays(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        x, y, _w, _h = FLOOR
        return [(self.floor_frames()[(game.cycle_count // 5) % 4], x, y)]

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        out: list[tuple[pygame.Surface, int, int]] = []
        if self.dance_timer:
            frame = self.ginger((game.cycle_count // 6) % 2 == 0)
            gx, gy = GINGER_FLOOR
        else:
            frame = self.ginger(False)
            gx, gy = GINGER_TABLE
        out.append((frame, gx, gy))
        return out

    # -- logic ---------------------------------------------------------------------

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.dance_timer = 0
        if not game.flags.get("seen_disco"):
            game.flags["seen_disco"] = True
            game.print(
                "The bass hits you in the sternum. Lights hit you everywhere else. Nobody "
                "looks at you, which in a place like this is a kind of welcome."
            )

    def update(self, game: Game) -> None:
        if self.dance_timer:
            self.dance_timer -= 1
            if game.cycle_count % 8 == 0:
                game.ego.facing = "left" if game.ego.facing == "right" else "right"
            if self.dance_timer == 0:
                self._dance_over(game)

    def _near_ginger(self, game: Game) -> bool:
        return game.ego.centre_x <= 52 and game.ego.y >= 120

    def _on_floor(self, game: Game) -> bool:
        x, y, w, h = FLOOR
        return x <= game.ego.centre_x <= x + w and y <= game.ego.y <= y + h + 4

    def said(self, game: Game, p: Parsed) -> bool:
        if self.dance_timer:
            game.print("You're dancing. Concentrate. Left foot, right foot, the whole arrangement.")
            return True
        if p.said("talk", "hooker") or p.said("talk", "hooker", "rol") or p.said("talk"):
            self._talk(game)
        elif p.said("give", "candy", "rol") or p.said("give", "candy") or p.said("give", "hooker", "candy"):
            self._give(game, "candy")
        elif p.said("give", "wine", "rol") or p.said("give", "wine") or p.said("give", "hooker", "wine"):
            self._give(game, "wine")
        elif p.said("give", "rol") and p.has("hooker"):
            game.print('Ginger looks at it, then at you. "Sweet," she says, meaning no.')
        elif p.said("dance", "rol") or p.said("dance"):
            self._dance(game, with_her=p.has("hooker") or self._near_ginger(game))
        elif p.said("kiss", "hooker"):
            if game.flags.get("ginger_danced"):
                game.print('"Ring first, Romeo." She taps her bare finger. "Then we\'ll talk about the rest."')
            else:
                game.print(
                    'She leans away with the precision of long practice. "Buy a girl a drink first. Or a country."'
                )
        elif p.said("sit", "rol") or p.said("sit"):
            if self._near_ginger(game):
                game.print("You sit. Ginger allows it, the way a cat allows weather.")
            else:
                game.print("There's one table, and someone's at it. Everyone else stands; it's that kind of place.")
        elif p.said("talk", "dj") or p.said("use", "dj") or p.has("song"):
            game.print(
                "You request a song. The DJ nods, and plays the one he was going to play anyway. It has a saxophone."
            )
        elif p.said("buy", "rol") or p.said("buy"):
            game.print("The bartender is a silhouette. Silhouettes don't take orders; you've tried.")
        elif p.has("door") and p.verb in ("open", "enter", "use") or p.said("enter", "bathroom"):
            if LADIES_X[0] - 8 <= game.ego.centre_x <= LADIES_X[1] + 8 and game.ego.y <= 110:
                game.die(
                    "You push through the door marked LADIES. A scream. A handbag, swung "
                    "with real technique. Another. Paul dies of blunt force purse, which "
                    "the coroner spells correctly on the second try."
                )
            else:
                game.print("The LADIES door is at the back right. Think hard about whether you want to.")
        elif p.said("look", "hooker", "rol"):
            game.print(self.looks["hooker"])
        elif p.said("smell"):
            game.print("Dry ice, spilled sweet drinks, and a hundred colognes fighting to the death.")
        elif p.said("listen"):
            game.print("Bass. A saxophone, of course. Ginger, laughing at something that wasn't you.")
        else:
            return False
        return True

    def _talk(self, game: Game) -> None:
        if not self._near_ginger(game):
            game.print("You'd have to go over to her table. Shouting across a disco is how fights start.")
        elif game.flags.get("ginger_danced"):
            game.print(
                '"A girl like me needs a ring, Paul. A real one." She looks at your hand, '
                'then at the door. "The chapel on Fifth does walk-ins. Bring a ring, and '
                "we'll see about the rest of your evening.\""
            )
        elif game.flags.get("ginger_wine"):
            game.print('"You dance?" says Ginger, and it is not rhetorical, and it is not a no.')
        elif game.flags.get("ginger_candy"):
            game.print('"Chocolates are a start," she says. "A girl gets thirsty, though. Just saying."')
        else:
            game.print(
                '"Hi," says Ginger, without moving anything but her eyebrows. "Big night?" '
                'She takes in the suit. "Sure. Sure it is."'
            )

    def _give(self, game: Game, item: str) -> None:
        if not game.has(item):
            game.print(f"You don't have any {item}. You'd have noticed; it would be the best thing you own.")
        elif not self._near_ginger(game):
            game.print("Take it over to her. Gifts thrown across a dance floor are a cry for help.")
        elif game.flags.get(f"ginger_{item}"):
            game.print("She's already had that from you. Variety, Paul. Women like variety, and you've got none.")
        elif item == "wine" and not game.flags.get("ginger_candy"):
            game.print('"Wine? Before dessert?" She smiles, not unkindly. "Try again, sugar. In the right order."')
        else:
            game.take(item)
            game.flags[f"ginger_{item}"] = True
            if item == "candy":
                game.award("ginger_candy", 3)
                game.print(
                    "Ginger opens the heart-shaped box, counts the missing ones, and eats "
                    'a third. "Well," she says, "you\'re trying. I like trying."'
                )
            else:
                game.award("ginger_wine", 2)
                game.print(
                    'She turns the bottle to read the label. "Chateau Kwik." She laughs, '
                    'properly, for the first time. "You\'re a disaster. Dance with me."'
                )

    def _dance(self, game: Game, with_her: bool) -> None:
        if not with_her:
            game.print("You dance alone. The floor pulses. The mirror ball turns. Nobody joins you; nobody would.")
            return
        if game.flags.get("ginger_danced"):
            game.print('"One dance a night, honey. I have a rule and a hip."')
            return
        if not game.flags.get("ginger_wine"):
            game.print('"Dance? With you?" She stirs her drink. "Give me a reason. Two reasons. Bring them here."')
            return
        if not self._near_ginger(game):
            game.print("Go and ask her at the table. Nobody dances with a man who shouts from the floor.")
            return
        self.dance_timer = DANCE_CYCLES
        game.ego.x, game.ego.y = GINGER_FLOOR[0] - 16, GINGER_FLOOR[1]
        game.ego.facing = "right"
        game.ego.frozen = True
        game.print(
            "Ginger takes your hand and pulls you onto the floor. The lights go wild. "
            "You dance like a man who has read about it. She dances like she invented it."
        )

    def _dance_over(self, game: Game) -> None:
        game.ego.frozen = False
        game.ego.stop()
        game.flags["ginger_danced"] = True
        game.award("ginger_dance", 5)
        game.print(
            "The song ends. Ginger is flushed and, for a moment, looking at you like you "
            'are a person. "Here\'s the thing, Paul." She holds up her left hand. "No ring. '
            'A girl like me needs a ring. Get one, and meet me at the chapel on Fifth."'
        )
