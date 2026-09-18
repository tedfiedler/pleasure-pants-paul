"""Room 16: the room at the top of the stairs. Dolores, a bed, chocolates, a window."""

from __future__ import annotations

import pygame

from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    DGREY,
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
from ppp.sprite import from_ascii

PRICE = 30
BED_X = (92, 156)
DOLORES_X, DOLORES_BASE = 100, 108  # perched on the edge of the bed, feet on the floor

DOLORES_LEGEND = {"y": YELLOW, "f": LRED, "r": RED, "k": BLACK, "w": WHITE}
DOLORES_ART = """
...yyyyyy...
..yyyyyyyy..
..yyffffyy..
..yyfkfkyy..
..yyffffyy..
..yyyffyyy..
..yy.ff.yy..
....rrrr....
...rrrrrr...
..rrrrrrrr..
..rrrrrrrr..
.frrrrrrrrf.
..rrrrrrrr..
..rrrrrrrr..
..rrrrrrrrr.
...rrrrrrrr.
...ffff.....
...ffff.....
...ffff.....
...ffff.....
...ffff.....
...ffff.....
..kkkk......
..kkkk......
"""


class Upstairs(Room):
    number = 16
    name = "Upstairs"
    description = (
        "A small room with a big bed and a lamp with a red scarf over it. Dolores "
        "sits on the edge of the bed, filing a nail, entirely unsurprised by you. "
        "A nightstand holds the lamp and a heart-shaped box. A window looks out on "
        "the fire escape. The stairs back down are at the bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 15}
    spawns = {"default": (60, 150), 15: (60, 156)}
    looks = {
        "hooker": "Dolores. Blonde by decision, in a red dress that has heard every line "
        "you own. She has kind eyes and a businesslike jaw, and she is looking at your "
        "suit the way a vet looks at a limp.",
        "bed": "A brass bed with a chenille spread and a great deal of history. It sags "
        "in the middle, philosophically.",
        "nightstand": "A nightstand with a lamp under a red scarf, a heart-shaped box of "
        "chocolates, and an ashtray shaped like a smaller ashtray.",
        "candy": "A heart-shaped box of chocolates, lid off, two missing. The kind you give "
        "someone when you mean it, or want them to think so.",
        "window": "A sash window over the fire escape. Below it, the alley; beyond it, the "
        "whole regrettable city. It opens, if you're the climbing type.",
        "door": "You came in that way. The stairs are at the bottom of the screen.",
        "rug": "A heart-shaped rug, pink, worn through in a heart-shaped patch.",
        "floor": "Boards, the rug, and one slipper. Only one.",
        "wall": "Wallpaper with roses on it. The roses are winning.",
        "heart": "There are hearts on everything in here. It's a theme, or a warning.",
        "money": "You count your cash. Dolores counts it too, faster.",
        "rose": "A wilted rose. In this room it is practically a bouquet.",
    }

    def __init__(self) -> None:
        self._dolores: pygame.Surface | None = None

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 100, LMAGENTA)  # rosy wallpaper
        for y in range(6, 100, 14):
            for x in range(4, PIC_W, 16):
                pic.rect(x, y, 3, 3, RED)
                pic.pixel(x + 1, y + 3, MAGENTA)
        pic.rect(0, 100, PIC_W, 68, BROWN)  # boards
        for y in range(106, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        # rug, heart-shaped, more or less
        pic.ellipse(18, 118, 28, 16, LRED)
        pic.ellipse(42, 118, 28, 16, LRED)
        pic.poly([(20, 130), (68, 130), (44, 156)], LRED)
        # window on the fire escape
        pic.rect(18, 14, 36, 40, DGREY)
        pic.rect(20, 16, 32, 36, BLUE)
        pic.line([(36, 16), (36, 51)], DGREY)
        pic.line([(20, 34), (51, 34)], DGREY)
        pic.rect(22, 40, 28, 2, LGREY)  # a fire-escape rail
        pic.pixel(26, 22, YELLOW)
        pic.pixel(44, 26, YELLOW)
        # nightstand, lamp with red scarf, chocolates
        pic.rect(64, 76, 22, 24, BROWN, 0)
        pic.rect(66, 78, 18, 2, DGREY)
        pic.rect(70, 60, 10, 16, RED)  # lamp shade
        pic.rect(74, 66, 2, 10, YELLOW)  # glow
        pic.rect(74, 76, 2, 4, DGREY)
        pic.rect(66, 70, 8, 6, RED)  # the heart-shaped box
        pic.pixel(66, 70, LMAGENTA)
        pic.pixel(73, 70, LMAGENTA)
        # brass bed
        pic.rect(BED_X[0], 60, 4, 40, YELLOW, 0)  # headboard posts
        pic.rect(BED_X[1] - 4, 70, 4, 30, YELLOW, 0)
        pic.rect(BED_X[0], 60, BED_X[1] - BED_X[0], 4, YELLOW)
        pic.rect(BED_X[0] + 4, 74, BED_X[1] - BED_X[0] - 8, 24, WHITE)  # spread
        pic.rect(BED_X[0] + 6, 68, 20, 8, LGREY)  # pillow
        pic.rect(BED_X[0] + 4, 94, BED_X[1] - BED_X[0] - 8, 6, LGREY)
        pic.rect(BED_X[0], 98, BED_X[1] - BED_X[0], 4, None, 0)  # bed footprint
        pic.rect(64, 100, 22, 4, None, 0)  # nightstand footprint
        pic.walls(100)

    def dolores(self) -> pygame.Surface:
        if self._dolores is None:
            self._dolores = from_ascii(DOLORES_ART, DOLORES_LEGEND)
        return self._dolores

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        if game.flags.get("dolores_done"):
            return []
        return [(self.dolores(), DOLORES_X, DOLORES_BASE)]

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if not game.flags.get("seen_upstairs"):
            game.flags["seen_upstairs"] = True
            game.print(
                'Dolores looks up from her nail file. "Well," she says, taking in the suit, '
                "\"somebody's dressed for it.\" She pats the bed. She does not smile. It's "
                "thirty dollars, the pat says."
            )

    def _near_dolores(self, game: Game) -> bool:
        return 84 <= game.ego.centre_x <= 132 and game.ego.y <= 116

    def _near_stand(self, game: Game) -> bool:
        return 56 <= game.ego.centre_x <= 96 and game.ego.y <= 116

    def said(self, game: Game, p: Parsed) -> bool:
        done = bool(game.flags.get("dolores_done"))
        if p.said("talk", "hooker") or p.said("talk", "hooker", "rol") or p.said("talk"):
            self._talk(game)
        elif p.said("give", "rose", "rol") or p.said("give", "rose") or p.said("give", "hooker", "rose"):
            self._give_rose(game)
        elif (
            p.said("pay", "rol") or p.said("pay") or p.said("give", "money", "rol") or p.said("give", "money")
        ) and not done:
            self._pay(game)
        elif p.said("get", "candy") or p.said("get", "candy", "rol"):
            self._get_candy(game)
        elif p.said("eat", "candy"):
            if game.has("candy"):
                game.print(
                    "You eat one. Cherry. You put the lid back on. Somebody else might like these more than you do."
                )
            else:
                game.print("They're not yours to eat. Yet.")
        elif (
            p.has("hooker")
            and p.verb in ("kiss", "love", "use", "undress")
            or p.said("love")
            or p.said("use", "bed")
            or p.said("sit", "bed")
        ):
            self._business(game)
        elif p.has("window") and p.verb in ("open", "enter", "use", "push"):
            game.print(
                "You shove the window up and climb out onto the fire escape, which sways, "
                "and down its ladder, which ends eight feet early. You drop into the alley "
                "with a sound like a suit full of soup."
            )
            game.new_room(12)
        elif p.said("look", "hooker", "rol"):
            game.print(self.looks["hooker"])
        elif p.said("kiss", "self"):
            game.print(
                'Dolores watches you try. "Honey," she says, "that\'s the saddest thing '
                "I've seen today, and I've seen the suit.\""
            )
        elif p.said("smell"):
            game.print("Perfume, cigarettes, and something floral that turns out to be the wallpaper.")
        elif p.said("listen"):
            game.print("Downstairs, a crowd roars at a boxing match. Up here, a nail file, patient as the sea.")
        else:
            return False
        return True

    def _talk(self, game: Game) -> None:
        if game.flags.get("dolores_done"):
            game.print("Dolores has gone to freshen up. You are alone with the wallpaper.")
        elif game.flags.get("dolores_paid"):
            game.print("\"Paid is paid, honey. The clock's running. The bed's right here.\"")
        elif game.flags.get("rose_given"):
            game.print(
                '"You\'re sweet," says Dolores, tucking the rose behind her ear. "Sweet\'s '
                "still thirty dollars, but I'll think fondly of you. Have a chocolate.\""
            )
        else:
            game.print('"It\'s thirty dollars, sugar. Up front. Then we can talk about whatever you like."')

    def _give_rose(self, game: Game) -> None:
        if not game.has("rose"):
            game.print("You'd need a rose. Or anything. Anything at all would be a start.")
        elif not self._near_dolores(game):
            game.print("Walk over to her. Flowers thrown from across a room count as littering.")
        elif game.flags.get("dolores_done"):
            game.print("She's gone. You lay the rose on the pillow, which is the most romantic thing you will ever do.")
        else:
            game.take("rose")
            game.flags["rose_given"] = True
            game.award("give_rose", 2)
            game.print(
                "Dolores takes the wilted rose and looks at it for a long moment. \"Nobody's "
                'given me a flower since the Carter administration." She tucks it behind '
                'her ear. "Have a chocolate, honey. Just the one."'
            )

    def _get_candy(self, game: Game) -> None:
        if game.has("candy"):
            game.print(
                "You have the chocolates. Don't be greedy; it's unattractive, and you can't afford unattractive."
            )
        elif not self._near_stand(game):
            game.print("They're on the nightstand. Walk over there.")
        elif not (game.flags.get("rose_given") or game.flags.get("dolores_done")):
            game.print('"Those are mine." Dolores doesn\'t look up from her nail. "Hands, sugar."')
        else:
            game.give("candy")
            game.award("candy", 3)
            game.print(
                "You take the heart-shaped box, lid and all. Somewhere out there is a woman "
                "who will be impressed by chocolates from a stranger. Statistically."
            )

    def _pay(self, game: Game) -> None:
        money = game.vars.get("money", 0)
        if not self._near_dolores(game):
            game.print("Walk over to her. She doesn't do curbside.")
        elif game.flags.get("dolores_paid"):
            game.print('"You paid, honey. I remember. I remember everything, it\'s a curse."')
        elif money < PRICE:
            game.print(f'You have ${money}. "That\'s adorable," says Dolores. "Come back with thirty."')
        else:
            game.vars["money"] = money - PRICE
            game.flags["dolores_paid"] = True
            game.print(
                f"You hand over ${PRICE}. Dolores counts it twice, folds it into somewhere, "
                f'and stands. "All right, tiger." You have ${game.vars["money"]} left, and '
                "about four minutes."
            )

    def _business(self, game: Game) -> None:
        if game.flags.get("dolores_done"):
            game.print("The moment has passed. Several moments have passed. Go downstairs.")
        elif not self._near_dolores(game):
            game.print("From over there? Ambitious. Walk closer.")
        elif not game.flags.get("dolores_paid"):
            game.print('Dolores holds up one hand. "Business first, sugar. Thirty dollars."')
        else:
            game.flags["dolores_done"] = True
            game.ego.visible = False
            game.print("Dolores turns off the lamp. The screen goes discreetly, mercifully dark.")
            game.print("Some time passes. Not much, if we're honest. Dolores is very professional about it.")
            game.print('The lamp comes back on. Dolores is already filing a nail. "Thanks, tiger. Mind the stairs."')
            if game.has("protection"):
                game.take("protection")
                game.award("dolores", 15)
                game.print(
                    "You get dressed, mostly in the right order. You feel like a new man, "
                    "which is a low bar you have nonetheless cleared."
                )
                game.ego.visible = True
            else:
                game.die(
                    "A day later, a rash. A week later, a doctor with a pamphlet. Paul dies of "
                    "something with a Latin name, unprotected and unrepentant. Next time, "
                    "shop first."
                )
