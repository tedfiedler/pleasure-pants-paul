"""Room 18: inside the Kwik-Snak. A clerk, a cooler, a rack, and one famous purchase."""

from __future__ import annotations

from ppp.const import (
    BLUE,
    BROWN,
    CYAN,
    DGREY,
    GREEN,
    LBLUE,
    LCYAN,
    LGREY,
    LRED,
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

PRICES = {"protection": 5, "wine": 8, "magazine": 3}


class Store(Room):
    number = 18
    name = "The Kwik-Snak"
    description = (
        "Fluorescent light on everything, forgiving nothing. A counter at the back "
        "with a bored clerk behind it. Shelves of snacks that will outlive you. A "
        "cooler of wine along the right wall and a magazine rack on the left, the "
        "top row in brown paper. The doors are at the bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 17}
    spawns = {"default": (76, 150), 17: (76, 156)}
    looks = {
        "clerk": "A kid in a red vest with a name tag that says ASK ME. Nothing about him suggests that you should.",
        "bar": "A counter with a register, a jar of pickled something, a rack of lighters, "
        "and, behind the clerk, the discreet little boxes that people cross town for.",
        "shelf": "Chips, jerky, a pyramid of canned meat, and a cake that has been on sale since the moon landing.",
        "chip": "Chips in every flavour the state allows and two it doesn't. Not for sale to you; you have a list.",
        "cooler": "A humming cooler with soda on the top shelf and, on the bottom, "
        "bottles of wine with screw tops and ambitions.",
        "wine": "A bottle of Chateau Kwik, red, screw top, eight dollars. It has notes of "
        "cherry, regret and the parking lot.",
        "magazine": "The top row is wrapped in brown paper, which is how you know which "
        "row it is. Three dollars. The clerk is already judging you.",
        "protection": "The little boxes behind the counter. You'll have to ask. Out loud. To him.",
        "floor": "Black and white tiles, mopped recently by someone who hates them.",
        "window": "Through the glass: the street, the phone, and a cab that isn't yours.",
        "door": "The glass doors, and the bell above them. The way out is at the bottom of the screen.",
        "sign": "A sign by the register: SHOPLIFTERS WILL BE SHOT. SURVIVORS WILL BE SHOT AGAIN.",
        "money": "You count your money at the counter, which is a mistake in any store.",
    }

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 100, WHITE)
        pic.rect(0, 0, PIC_W, 6, LGREY)  # ceiling strip
        for x in range(10, PIC_W, 30):
            pic.rect(x, 1, 20, 3, LCYAN)  # tubes
        pic.rect(0, 100, PIC_W, 68, LGREY)  # tiled floor
        for y in range(100, 168, 8):
            for x in range(0, PIC_W, 8):
                if (x // 8 + y // 8) % 2 == 0:
                    pic.rect(x, y, 8, 8, DGREY)
        # back shelves with the little boxes
        pic.rect(52, 20, 60, 36, LGREY)
        for y in (28, 40, 52):
            pic.line([(52, y), (111, y)], DGREY)
        for i in range(6):
            pic.rect(56 + i * 9, 22, 6, 5, (BLUE, RED, GREEN, LBLUE, YELLOW, LRED)[i])
            pic.rect(56 + i * 9, 34, 6, 5, (LRED, YELLOW, BLUE, RED, GREEN, LBLUE)[i])
            pic.rect(56 + i * 9, 45, 6, 5, (CYAN, CYAN, CYAN, CYAN, CYAN, CYAN)[i])  # the boxes
        # the clerk, then the counter that hides his legs
        draw_person(pic, 78, 44, suit=RED, skin=LRED, hair=BROWN)
        pic.rect(44, 66, 76, 16, BROWN)
        pic.rect(44, 64, 76, 3, LGREY)
        pic.rect(100, 56, 12, 10, DGREY)  # register
        pic.rect(102, 58, 8, 4, LCYAN)
        pic.rect(48, 58, 6, 8, GREEN)  # the pickle jar
        pic.rect(44, 64, 76, 18, None, 0)
        # magazine rack, left wall
        pic.rect(6, 24, 26, 76, DGREY, 0)
        for y in (30, 50, 70):
            pic.rect(8, y, 22, 16, WHITE)
        pic.rect(8, 30, 22, 16, BROWN)  # the brown-paper row
        for x in (10, 18, 26):
            pic.rect(x, 52, 4, 12, (RED, BLUE, YELLOW)[(x // 8) % 3])
            pic.rect(x, 72, 4, 12, (GREEN, LRED, LBLUE)[(x // 8) % 3])
        # cooler, right wall
        pic.rect(128, 16, 28, 84, DGREY, 0)
        pic.rect(130, 18, 24, 80, LCYAN)
        for y in (38, 58, 78):
            pic.line([(130, y), (153, y)], DGREY)
        for x in (132, 138, 144, 150):
            pic.rect(x, 24, 3, 12, RED)
            pic.rect(x, 44, 3, 12, LBLUE)
            pic.rect(x, 64, 3, 12, RED)  # wine
            pic.rect(x, 84, 3, 12, RED)
        # snack shelf, left of the counter
        pic.rect(34, 40, 12, 60, LGREY)
        pic.rect(34, 100, 12, 4, None, 0)
        pic.walls(100)
        pic.rect(6, 100, 26, 4, None, 0)
        pic.rect(128, 100, 28, 4, None, 0)

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if not game.flags.get("seen_store"):
            game.flags["seen_store"] = True
            game.print('A bell jingles. "Help you?" says the clerk, in the tone of a man hoping not to.')

    def _near_counter(self, game: Game) -> bool:
        return self.near(game, 36, 128)

    def said(self, game: Game, p: Parsed) -> bool:
        item = next((n for n in PRICES if p.has(n)), None)
        if p.said("buy", "rol") or p.said("buy"):
            self._buy(game, item)
        elif p.has("steal") or (p.verb == "get" and item is not None):
            game.die(
                "You palm it and turn for the door. The clerk produces a shotgun from under "
                "the counter with the ease of long practice. The sign by the register was "
                "not a joke. Paul is now a cautionary poster in the break room."
            )
        elif p.said("talk", "clerk") or p.said("talk", "clerk", "rol") or p.said("talk"):
            game.print(
                '"Help you?" He does not look up from a magazine. It is not one of the brown-paper ones. It is worse.'
            )
        elif p.said("look", "protection", "rol") or p.said("look", "bar", "rol"):
            game.print(self.looks["protection"])
        elif p.said("read", "magazine") or p.said("look", "magazine", "rol"):
            if game.has("magazine"):
                game.print(
                    "You read it for the articles. The articles are also pictures. "
                    "You learn a great deal, none of it useful."
                )
            else:
                game.print("It's wrapped. The paper is the point. Buy it or stop fondling it; the clerk has counted.")
        elif p.said("drink", "wine"):
            if game.has("wine"):
                game.print(
                    "You take a swig. It tastes like a headache with grapes in it. "
                    "You keep the rest; you have plans, vaguely."
                )
            else:
                game.print("Buy it first. This isn't a tasting room; it barely qualifies as a room.")
        elif p.said("eat", "rol"):
            game.print("You are not that hungry. Nobody is that hungry. That's why it's still on the shelf.")
        elif p.said("smell"):
            game.print("Hot dogs rolling since dawn, floor cleaner, and the sweet plastic breath of the cooler.")
        elif p.said("listen"):
            game.print("The cooler hums. The tubes buzz. The clerk turns a page with wet fingers.")
        elif p.said("pay", "rol") or p.said("pay"):
            game.print("Say what you're buying. He's not a mind reader, and if he were he'd have quit.")
        else:
            return False
        return True

    def _buy(self, game: Game, item: str | None) -> None:
        if item is None:
            game.print(
                '"We got three things worth buying," says the clerk. "Wine, magazines, and, uh, you know. Which?"'
            )
            return
        if not self._near_counter(game):
            game.print("Walk up to the counter. He's not coming to you; nobody in this city comes to you.")
            return
        if game.has(item):
            game.print("You've already got one. Pace yourself; the night is long and so is your list.")
            return
        price = PRICES[item]
        money = game.vars.get("money", 0)
        if money < price:
            game.print(
                f'"That\'s ${price}." You have ${money}. He looks at you the way the cooler looks at a warm soda.'
            )
            return
        game.vars["money"] = money - price
        game.give(item)
        if item == "protection":
            game.award("buy_protection", 3)
            game.print(
                'You lean in and ask, very quietly, for protection. "WHAT?" says the clerk. '
                "You ask again, less quietly."
            )
            game.print(
                '"Sure. What kind? Ribbed? Lubricated? Coloured? Flavoured? Extra-large? '
                'Extra-small?" He is not lowering his voice. He is, if anything, raising it.'
            )
            game.print(
                'He leans into the microphone by the register. "PRICE CHECK. ONE PROTECTION, '
                'PLAIN, SMALL, FOR THE GENTLEMAN IN THE WHITE SUIT." The whole store looks. '
                f"The whole store is you and him. You pay ${price} and have ${game.vars['money']} left."
            )
        elif item == "wine":
            game.award("buy_wine", 1)
            game.print(
                f'"Chateau Kwik. Good year, this year." He bags it. ${price}. You have ${game.vars["money"]} left.'
            )
        else:
            game.award("buy_magazine", 1)
            game.print(
                f"He slides the brown-paper magazine across without meeting your eye. ${price}. "
                f"You have ${game.vars['money']} left, and the beginnings of a reputation."
            )
