"""Base class for rooms. Each room owns its picture, exits, and parser logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ppp.parser import Parsed
from ppp.pic import Picture

if TYPE_CHECKING:
    from ppp.game import Game


class Room:
    number: int = 0
    name: str = "Nowhere"
    description: str = "There is nothing here. Not even a description."
    horizon: int = 36  # ego cannot walk above this y
    # edge name -> room number Paul walks into
    edges: dict[str, int] = {}
    # noun group -> description for "look <noun>"
    looks: dict[str, str] = {}
    # spawn positions when arriving from a given room (or "default")
    spawns: dict[str | int, tuple[int, int]] = {"default": (76, 150)}

    def draw(self, pic: Picture) -> None:
        raise NotImplementedError

    @staticmethod
    def near(game: Game, x0: int, x1: int, max_y: int = 116) -> bool:
        """Is Paul within an x range and no lower than max_y? The standard 'close enough' test."""
        return x0 <= game.ego.centre_x <= x1 and game.ego.y <= max_y

    def enter(self, game: Game, from_room: int | None) -> None:
        """Called after the picture is drawn. Position Paul here."""
        x, y = self.spawns.get(from_room if from_room is not None else "default", self.spawns["default"])
        game.ego.x, game.ego.y = x, y
        game.ego.stop()

    def update(self, game: Game) -> None:
        """Per-cycle logic (timers, NPC animation, triggers)."""

    def underlays(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        """Animated floor-level surfaces as (surface, x, top_y), drawn under everything."""
        return []

    def objects(self, game: Game) -> list[tuple[pygame.Surface, int, int]]:
        """Animated objects as (surface, x, baseline_y), drawn in baseline order with Paul."""
        return []

    def said(self, game: Game, p: Parsed) -> bool:
        """Handle a parsed command. Return True if handled."""
        return False

    def look(self, game: Game, p: Parsed) -> bool:
        """Default `look <noun>` handling via the `looks` table."""
        if len(p.words) >= 2 and p.words[0] == "look":
            text = self.looks.get(p.words[1])
            if text:
                game.print(text)
                return True
        return False
