"""Room 13: inside the cab. Name a destination, pay the man, get out."""

from __future__ import annotations

from ppp.const import (
    BLACK,
    BLUE,
    BROWN,
    DGREY,
    LCYAN,
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

# word group -> (display name, fare, built room number or None)
DESTINATIONS: dict[str, tuple[str, int, int | None]] = {
    "bar": ("Rooster's", 5, 10),
    "casino": ("the Golden Sock Casino", 5, None),
    "disco": ("the Boogie Palace", 5, 19),
    "store": ("the Kwik-Snak convenience store", 5, 17),
    "chapel": ("the Chapel of Eternal Regret", 5, None),
}
AROUND_THE_BLOCK = 3


class Taxi(Room):
    number = 13
    name = "Inside the cab"
    description = (
        "The back seat of a cab that smells of pine air-freshener losing a war. "
        "The driver watches you in the mirror. The meter glows red on the dash. "
        "Through the windshield, the city waits to be named."
    )
    horizon = 160
    spawns = {"default": (96, 164)}
    looks = {
        "driver": "A thick neck, a flat cap, and a pair of eyes in the mirror that have "
        "already decided what you are. He's right.",
        "meter": "A red LED meter. It is either your fare or a countdown.",
        "dashboard": "A dashboard furred with dust, a dangling air-freshener shaped like a "
        "tree, and a radio playing static with a beat.",
        "window": "Through the windshield: brick, neon, and the general suggestion of a city.",
        "cab": "You're in it. The seat is vinyl and it has opinions about your suit.",
        "stool": "Cracked vinyl, patched with tape. You're sticking to it.",
        "money": "You count your cash discreetly. The driver counts it less discreetly.",
    }

    def draw(self, pic: Picture) -> None:
        # windshield with a night street beyond
        pic.rect(0, 0, PIC_W, 70, BLUE)
        pic.rect(0, 40, PIC_W, 30, DGREY)  # far buildings
        for x in range(0, PIC_W, 16):
            pic.rect(x + 4, 44 + (x // 16 % 3) * 4, 8, 26 - (x // 16 % 3) * 4, BLACK)
            pic.pixel(x + 6, 50, YELLOW)
            pic.pixel(x + 9, 56, YELLOW)
        pic.rect(0, 70, PIC_W, 16, LGREY)  # road ahead
        pic.line([(80, 70), (0, 86)], YELLOW)
        pic.line([(80, 70), (PIC_W - 1, 86)], YELLOW)
        # windshield frame and pillars
        pic.rect(0, 0, PIC_W, 4, BLACK)
        pic.rect(0, 0, 10, 90, BLACK)
        pic.rect(PIC_W - 10, 0, 10, 90, BLACK)
        # dashboard
        pic.rect(0, 86, PIC_W, 22, DGREY)
        pic.rect(0, 86, PIC_W, 2, LGREY)
        pic.rect(112, 90, 30, 12, BLACK)  # meter
        pic.rect(114, 92, 26, 8, RED)
        pic.rect(118, 94, 18, 4, BLACK)
        pic.rect(24, 92, 36, 10, BLACK)  # radio
        pic.rect(26, 94, 32, 6, LCYAN)
        # driver's seat, then shoulders, neck, head and flat cap, back to front
        pic.rect(40, 30, 32, 40, BROWN)
        pic.rect(30, 28, 52, 14, BLACK)  # shoulders, a dark jacket
        pic.rect(50, 20, 12, 10, LRED)  # neck
        pic.ellipse(44, 2, 24, 24, LRED)  # head
        pic.ellipse(42, 0, 28, 10, BLACK)  # flat cap
        pic.rect(40, 8, 32, 3, BLACK)  # brim
        # steering wheel, seen edge-on past his shoulder
        pic.ellipse(34, 84, 44, 8, BLACK, None, 2)
        # front seat back across the cab, and the rear bench in front of the camera
        pic.rect(10, 108, PIC_W - 20, 32, BROWN)
        pic.rect(10, 108, PIC_W - 20, 3, DGREY)
        pic.rect(0, 150, PIC_W, 18, BROWN, 15)  # bench hides Paul's legs
        pic.rect(0, 150, PIC_W, 2, LGREY, 15)
        pic.rect(0, 0, PIC_W, 160, None, 0)  # nowhere to walk in a cab
        pic.rect(0, 108, 4, 60, WHITE)  # door edges
        pic.rect(PIC_W - 4, 108, 4, 60, WHITE)

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        game.ego.facing = "down"
        game.ego.frozen = True
        game.vars["fare"] = 0
        game.flags["cab_ride_done"] = False
        if from_room is not None:
            game.vars["cab_origin"] = from_room
        game.vars["cab_dest"] = game.vars.get("cab_origin", 10)
        game.print('You slide into the back seat. The driver folds his racing form. "Where to, pal? Meter\'s running."')

    def _destination(self, p: Parsed) -> str | None:
        if p.has("look"):
            return None
        if p.has("rooster"):
            return "bar"
        for name in DESTINATIONS:
            if p.has(name):
                return name
        return None

    def said(self, game: Game, p: Parsed) -> bool:
        dest = self._destination(p)
        money = game.vars.get("money", 0)
        fare = game.vars.get("fare", 0)

        if dest is not None:
            self._ride(game, dest)
        elif p.said("talk", "driver") or p.said("talk", "driver", "rol") or p.said("talk"):
            if fare:
                game.print(f'"That\'s ${fare}, pal. Then we can be friends."')
            else:
                game.print(
                    '"Where to? Rooster\'s, the casino, the disco, the store, the chapel. Pick one, I got a life."'
                )
        elif p.said("pay", "rol") or p.said("pay") or p.said("give", "money", "rol") or p.said("give", "money"):
            self._pay(game, fare, money)
        elif p.said("look", "meter"):
            game.print(f"The meter reads ${fare}." if fare else "The meter reads $0. For now.")
        elif p.verb in ("enter", "open", "stand", "get", "drop") and (len(p.words) == 1 or p.has("out", "door")):
            self._leave(game, fare)
        elif p.said("enter", "cab") or p.said("enter", "cab", "rol"):
            game.print("You're in it. This is the in part.")
        elif p.said("look", "money"):
            game.print(f"You have ${money}. The driver, judging by his face, has more.")
        elif p.said("use", "radio") or p.said("push", "radio"):
            game.print('You reach for the radio. "Touch it and walk," says the driver, not turning around.')
        elif p.said("kiss", "driver"):
            game.print("The driver's eyes in the mirror say no. His whole neck says no.")
        elif p.said("smell"):
            game.print("Pine. Then, under the pine, everything the pine was hired to hide.")
        elif p.said("listen"):
            game.print("Static, a dispatcher, and the driver breathing through his nose.")
        else:
            return False
        return True

    def _ride(self, game: Game, dest: str) -> None:
        name, price, room = DESTINATIONS[dest]
        if game.vars.get("fare", 0):
            game.print('"One ride at a time. Pay for this one first."')
            return
        game.flags["cab_ride_done"] = True
        if room is not None and room == game.vars.get("cab_origin"):
            game.vars["fare"] = AROUND_THE_BLOCK
            game.print(
                f'"{name}? Pal, you\'re parked outside it." He drives around the block '
                f'anyway, slowly, with the meter on. "Three bucks."'
            )
        elif room is not None:
            game.vars["fare"] = price
            game.vars["cab_dest"] = room
            game.award(f"ride_{dest}", 1)
            game.print(
                f"He floors it toward {name}. The city smears past: neon, brick, a man "
                f"arguing with a lamp post. He stops at the curb outside {name}. "
                f'"Five bucks."'
            )
        else:
            game.vars["fare"] = price
            game.award(f"ride_{dest}", 1)
            game.print(
                f"He floors it toward {name}. The city smears past. Then he brakes hard: "
                f"{name} is behind a plywood fence and a sign that says COMING SOON. "
                f'He drives you back to Rooster\'s. "Five bucks. Not my fault."'
            )

    def _pay(self, game: Game, fare: int, money: int) -> None:
        if not fare:
            game.print('"Pay for what? Tell me where you\'re going first."')
        elif money >= fare:
            game.vars["money"] = money - fare
            game.vars["fare"] = 0
            game.award("pay_cab", 1)
            game.print(
                f'You hand over ${fare}. "Pleasure," he says, meaning the money. You have ${game.vars["money"]} left.'
            )
        else:
            game.vars["fare"] = 0
            game.print(
                f"You have ${money}. The fare is ${fare}. The driver does the arithmetic, "
                "reaches back, opens your door, and helps you out with his foot. "
                "You land on the sidewalk outside Rooster's."
            )
            game.new_room(10)

    def _leave(self, game: Game, fare: int) -> None:
        if fare:
            game.print(f'The doors lock with a clunk. "Meter says ${fare}, pal." He waits.')
        elif not game.flags.get("cab_ride_done"):
            game.print('"Nice. Real nice. Waste a man\'s time." You climb out onto the sidewalk.')
            game.new_room(int(game.vars.get("cab_origin", 10)))
        else:
            game.print("You slide out onto the sidewalk. The cab idles, hopeful.")
            game.new_room(int(game.vars.get("cab_dest", 10)))
