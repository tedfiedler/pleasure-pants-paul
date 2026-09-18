"""Room 11: inside Rooster's. A bartender, a drunk, and your first puzzle."""

from __future__ import annotations

from ppp.const import (
    BLACK,
    BROWN,
    CYAN,
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
from ppp.game import START_MONEY, Game
from ppp.npc import draw_person
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

WHISKEY_PRICE = 10
DOOR_X = (138, 160)  # walk up into this range to enter the men's room


class Bar(Room):
    number = 11
    name = "Rooster's"
    description = (
        "Rooster's, in all its glory. A long bar runs along the back wall with a "
        "bartender behind it polishing a glass that will never be clean. A drunk "
        "slumps in the booth on the right. A jukebox glows in the corner. A door at "
        "the back is marked MEN. The exit is at the bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 10}
    spawns = {"default": (76, 150), 10: (76, 156), 14: (145, 104)}
    looks = {
        "bar": "A scarred wooden bar, sticky in places you don't want to think about. "
        "Behind it: bottles, a mirror, and the bartender.",
        "bartender": "A big man with forearms like hams and a towel over one shoulder. He "
        "looks like he has heard every line you're about to try.",
        "drunk": "A gentleman of the old school, if the old school was a bus station. He is "
        "nursing an empty glass and mumbling about his 'shows'. His coat pocket bulges.",
        "jukebox": "A jukebox with a cracked chrome front. Every song on it is by someone's cousin.",
        "door": "A door on the right marked MEN. It stands ajar, breathing. Walk up to it to go in.",
        "stool": "Bar stools, bolted to the floor, which tells you about the clientele.",
        "whiskey": "A shot of house whiskey. It's the colour of old pennies and smells like a campfire in a tyre yard.",
        "money": "You have some cash in your wallet. Less than you'd like.",
        "mirror": "You avoid your reflection. It avoids you back.",
        "window": "There are no windows. Rooster's keeps its own hours, none of them daylight.",
    }

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 100, MAGENTA)  # wallpaper
        pic.rect(0, 100, PIC_W, 68, BROWN)  # floor
        for y in range(104, 168, 8):
            pic.line([(0, y), (PIC_W - 1, y)], BLACK)
        # back bar shelf and bottles
        pic.rect(20, 30, 100, 30, DGREY)
        pic.rect(22, 32, 96, 26, BLACK)
        for i, c in enumerate((YELLOW, LRED, CYAN, WHITE, LBLUE, YELLOW, LRED, CYAN)):
            pic.rect(28 + i * 11, 40, 4, 16, c)
        # bartender first, so the counter drawn after him hides his legs
        draw_person(pic, 62, 46, suit=WHITE, skin=LRED, hair=BLACK, apron=True)
        # the bar counter keeps its default band priority, so Paul (always
        # below it, in a higher band) is drawn in front of it
        pic.rect(16, 68, 84, 14, BROWN)
        pic.rect(16, 66, 84, 3, LGREY)
        pic.rect(16, 66, 84, 16, None, 0)  # cannot walk through the bar
        # jukebox left, booth right
        pic.rect(2, 44, 16, 56, DGREY, 0)
        pic.rect(4, 46, 12, 24, CYAN)
        pic.rect(4, 72, 12, 26, LGREY)
        pic.rect(104, 70, 30, 24, RED, 0)  # booth seat
        pic.rect(100, 92, 34, 6, BROWN, 0)  # booth table
        draw_person(pic, 114, 74, suit=DGREY, skin=LRED, hair=LGREY)
        # men's room door, at floor level so Paul can walk in
        pic.rect(138, 44, 22, 56, BROWN)
        pic.rect(140, 46, 18, 54, DGREY)
        pic.rect(142, 54, 14, 6, WHITE)  # the MEN sign
        pic.pixel(155, 78, YELLOW)
        pic.rect(DOOR_X[0], 100, DOOR_X[1] - DOOR_X[0], 2, None, 2)  # threshold signal
        # walls: nothing above the bar line is walkable
        pic.walls(100)
        pic.line([(0, 100), (PIC_W - 1, 100)], BLACK)

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        if not game.flags.get("seen_bar"):
            game.flags["seen_bar"] = True
            game.print(
                "The door swings shut behind you. Heads do not turn. Nobody here has turned their head since 1979."
            )

    def _near(self, game: Game, x0: int, x1: int) -> bool:
        return x0 <= game.ego.centre_x <= x1 and game.ego.y <= 112

    def update(self, game: Game) -> None:
        ego = game.ego
        if ego.direction == 1 and DOOR_X[0] <= ego.centre_x <= DOOR_X[1] and ego.y <= self.horizon + 1:
            game.new_room(14)

    def said(self, game: Game, p: Parsed) -> bool:
        near_bar = self._near(game, 16, 124)
        near_drunk = self._near(game, 92, 140)

        if p.said("talk", "bartender") or p.said("talk", "bartender", "rol"):
            if not near_bar:
                game.print("He can't hear you from there. Walk up to the bar.")
            else:
                game.print('"You want something, or you just here to shine?"')
        elif p.said("buy", "whiskey") or p.said("order", "whiskey") or p.said("buy", "drink"):
            self._buy_whiskey(game, near_bar)
        elif p.said("drink", "whiskey"):
            if game.has("whiskey"):
                game.take("whiskey")
                game.print(
                    "You knock it back. It goes down like a lit road flare. Your eyes water, "
                    "your future dims, and ten dollars is gone forever."
                )
            else:
                game.print("You have no whiskey. The bartender does. See where this is going?")
        elif p.said("give", "whiskey", "drunk") or p.said("give", "drunk", "whiskey") or p.said("give", "whiskey"):
            self._give_whiskey(game, near_drunk)
        elif p.said("talk", "drunk") or p.said("talk", "drunk", "rol"):
            if not near_drunk:
                game.print("He's too far away, and he isn't coming to you.")
            elif game.flags.get("drunk_paid"):
                game.print('"Wonderful fella. Wonderful. Nother round when you get a minute."')
            else:
                game.print('"Hey. Hey pal. Pal. My glass has a hole in the top." He waggles it. It is very empty.')
        elif p.said("get", "remote") or p.said("get", "remote", "rol"):
            if game.has("remote"):
                game.print("You already have it. Don't get greedy.")
            elif not near_drunk:
                game.print("What remote? Get closer to the gentleman in the booth and think again.")
            else:
                game.print("He's sitting on the pocket. You'd need a distraction, or a bribe.")
        elif p.said("look", "drunk", "rol") or p.said("look", "pocket"):
            game.print(self.looks["drunk"])
        elif p.said("play", "jukebox") or p.said("push", "jukebox") or p.said("use", "jukebox"):
            game.print("You feed it a quarter. It plays a song about a truck. The drunk weeps.")
        elif (
            p.said("open", "door")
            or p.said("enter", "door")
            or p.said("enter", "bathroom")
            or p.said("use", "bathroom")
        ):
            game.print("Walk up to the door marked MEN. It's on the right, past the booth. Follow the smell.")
        elif p.said("sit", "rol") or p.said("sit"):
            game.print("You perch on a stool. It wobbles. So do you.")
        elif p.said("look", "money") or p.said("look", "wallet") or p.said("money"):
            game.print(f"You have ${game.vars.get('money', START_MONEY)}.")
        elif p.said("pay", "rol") or p.said("pay"):
            game.print("Pay for what? Buy something first, big spender.")
        elif p.said("dance"):
            game.print("You dance. The bartender stops polishing. Everyone stops. You stop.")
        elif p.said("smell"):
            game.print("Beer, bleach, and the ghost of a thousand cigarettes.")
        elif p.said("listen"):
            game.print("The jukebox plays something with a saxophone. The drunk hums the wrong tune.")
        else:
            return False
        return True

    def _buy_whiskey(self, game: Game, near_bar: bool) -> None:
        if not near_bar:
            game.print("Get up to the bar first. He doesn't deliver.")
            return
        if game.has("whiskey"):
            game.print("You've already got one. Pace yourself; it's a long game.")
            return
        money = game.vars.get("money", START_MONEY)
        if money < WHISKEY_PRICE:
            game.print('"No money, no whiskey." He goes back to the glass.')
            return
        game.vars["money"] = money - WHISKEY_PRICE
        game.give("whiskey")
        game.award("buy_whiskey", 2)
        game.print(
            f'He slides a shot across the bar. "Ten bucks." You pay. You now have ${game.vars["money"]} and a whiskey.'
        )

    def _give_whiskey(self, game: Game, near_drunk: bool) -> None:
        if not game.has("whiskey"):
            game.print("You'd need a whiskey to give. Funny how that works.")
            return
        if not near_drunk:
            game.print("You'll have to bring it over to him. He's not a self-serve kind of guy.")
            return
        game.take("whiskey")
        game.flags["drunk_paid"] = True
        game.give("remote")
        game.award("remote", 4)
        game.print(
            'His eyes go wide. "Pal!" He drains it in one go, fishes in his coat, and '
            "presses something into your hand. It's a TV remote control. \"Never lose "
            'your shows," he says, and slides under the table.'
        )
