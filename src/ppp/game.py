"""Game state and the command dispatcher."""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

from ppp.const import PIC_H, PIC_W
from ppp.ego import Ego
from ppp.parser import Parsed, parse
from ppp.pic import Picture
from ppp.room import Room

MAX_SCORE = 222

DUMB_REPLIES = [
    "That wouldn't accomplish anything, Paul.",
    "You can't do that. Not in those pants.",
    "Nice idea. Doesn't work.",
    "Paul thinks about it, then thinks better of it.",
    "Nothing happens. Story of your life.",
]

DIRECTION_REPLY = "Use the arrow keys to walk. The keyboard was invented for a reason, Paul."


@dataclass
class Game:
    rooms: dict[int, Room] = field(default_factory=dict)
    room: Room | None = None
    ego: Ego = field(default_factory=Ego)
    pic: Picture | None = None
    score: int = 0
    inventory: list[str] = field(default_factory=list)
    flags: dict[str, bool] = field(default_factory=dict)
    vars: dict[str, int] = field(default_factory=dict)
    messages: deque[str] = field(default_factory=deque)
    sound_on: bool = True
    quit_requested: bool = False
    dead: bool = False
    cycle_count: int = 0
    scored: set[str] = field(default_factory=set)

    # -- output ----------------------------------------------------------

    def print(self, text: str) -> None:
        self.messages.append(text)

    @property
    def message(self) -> str | None:
        return self.messages[0] if self.messages else None

    def dismiss(self) -> None:
        if self.messages:
            self.messages.popleft()

    # -- scoring & inventory --------------------------------------------

    def award(self, key: str, points: int) -> None:
        """Award points once per key, so repeating an action never re-scores."""
        if key not in self.scored:
            self.scored.add(key)
            self.score += points

    def has(self, item: str) -> bool:
        return item in self.inventory

    def give(self, item: str) -> None:
        if item not in self.inventory:
            self.inventory.append(item)

    def take(self, item: str) -> None:
        if item in self.inventory:
            self.inventory.remove(item)

    # -- rooms ------------------------------------------------------------

    def add_room(self, room: Room) -> None:
        self.rooms[room.number] = room

    def new_room(self, number: int) -> None:
        prev = self.room.number if self.room else None
        room = self.rooms[number]
        self.pic = Picture()
        room.draw(self.pic)
        self.room = room
        room.enter(self, prev)

    def _edge_spawn(self, edge: str) -> None:
        """Keep Paul's position but wrap him to the opposite edge."""
        if edge == "left":
            self.ego.x = PIC_W - self.ego.width - 1
        elif edge == "right":
            self.ego.x = 1
        elif edge == "bottom":
            self.ego.y = max(self.room.horizon, 40) if self.room else 40
        elif edge == "top":
            self.ego.y = PIC_H - 2

    # -- per-cycle --------------------------------------------------------

    def cycle(self) -> None:
        if self.room is None or self.pic is None or self.message is not None:
            return
        self.cycle_count += 1
        edge = self.ego.update(self.pic, self.room.horizon)
        if edge:
            target = self.room.edges.get(edge)
            if target is not None:
                keep = self.ego.direction
                prev = self.room.number
                prev_x, prev_y = self.ego.x, self.ego.y
                self.new_room(target)
                if prev not in self.rooms[target].spawns:
                    # plain edge travel: keep Paul's line of motion, wrap to the far edge
                    if edge in ("left", "right"):
                        self.ego.y = prev_y
                    else:
                        self.ego.x = prev_x
                    self._edge_spawn(edge)
                self.ego.direction = keep
                return
            self.ego.stop()
        self.room.update(self)

    # -- parser dispatch --------------------------------------------------

    def handle_input(self, text: str) -> None:
        if self.room is None:
            return
        p = parse(text)
        if p.empty:
            return
        if self.room.said(self, p):
            return
        if self.room.look(self, p):
            return
        if self._global(p):
            return
        if p.unknown is not None:
            self.print(f'I don\'t know the word "{p.unknown}".')
            return
        self.print(random.choice(DUMB_REPLIES))

    def _global(self, p: Parsed) -> bool:
        assert self.room is not None
        if p.said("look") or p.said("look", "room") or p.said("look", "around"):
            self.print(self.room.description)
        elif p.said("look", "self"):
            self.print(
                "You are Paul. Forty-something, balding, and wearing a white polyester "
                "leisure suit that was fashionable once, briefly, somewhere else. "
                "The pants are the pleasure part. Allegedly."
            )
        elif p.said("inventory"):
            self._show_inventory()
        elif p.said("score"):
            self.print(f"You have scored {self.score} out of a possible {MAX_SCORE} points.")
        elif p.said("help"):
            self.print(
                "Type what you want Paul to do, like LOOK AT BAR or TALK TO BARTENDER. "
                "Walk with the arrow keys. Press ESC for the menu. Try everything. Twice."
            )
        elif p.said("quit"):
            self.quit_requested = True
        elif p.said("save") or p.said("restore"):
            self.print("Saving and restoring aren't wired up yet. Live dangerously.")
        elif p.has("north", "south", "east", "west"):
            self.print(DIRECTION_REPLY)
        elif p.said("wait"):
            self.print("Time passes. Paul does not get any younger, or any cooler.")
        elif p.said("look", "floor"):
            self.print("It's a floor. It does the thing floors do.")
        elif p.said("look", "wall"):
            self.print("Walls. Load-bearing, probably.")
        elif p.words and p.words[0] == "look" and p.unknown is None and len(p.words) > 1:
            self.print(f"You see no {p.raw[1]} here worth looking at.")
        elif p.said("get", "rol") and p.unknown is None:
            self.print("You can't take that. Believe me, you'd regret it anyway.")
        elif p.said("talk", "self") or p.said("talk"):
            self.print("Paul mutters something encouraging to himself. It doesn't help.")
        elif p.said("kiss", "self"):
            self.print("Paul puckers up. There's nobody there. Just like high school.")
        elif p.said("dance"):
            self.print("Paul does a little shuffle. Somewhere, a disco ball weeps.")
        else:
            return False
        return True

    def _show_inventory(self) -> None:
        if not self.inventory:
            self.print("You are carrying nothing but your dignity, and that's on a short leash.")
        else:
            items = "\n".join(f"  {name}" for name in self.inventory)
            self.print(f"You are carrying:\n{items}")
