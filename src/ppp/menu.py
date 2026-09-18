"""The Sierra menu bar: ESC opens it on the status line, arrows navigate."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from ppp.const import BLACK, PALETTE, SCREEN_W, WHITE
from ppp.font import CHAR_H, CHAR_W, draw_row, draw_text


@dataclass(frozen=True)
class Item:
    label: str
    action: str
    key: str = ""  # shortcut hint shown on the right


@dataclass(frozen=True)
class Menu:
    title: str
    items: tuple[Item, ...]


MENUS: tuple[Menu, ...] = (
    Menu(
        "File",
        (
            Item("Save Game", "save", "F5"),
            Item("Restore Game", "restore", "F7"),
            Item("Restart Game", "restart", "F9"),
            Item("Quit", "quit", "Alt-Z"),
        ),
    ),
    Menu(
        "Action",
        (
            Item("Look", "look", "F4"),
            Item("Inventory", "inventory", "Tab"),
            Item("Score", "score", "F3"),
        ),
    ),
    Menu(
        "Special",
        (
            Item("Help", "help", "F1"),
            Item("Sound on/off", "sound", "F2"),
        ),
    ),
    Menu(
        "Speed",
        (
            Item("Slow", "speed_slow"),
            Item("Normal", "speed_normal"),
            Item("Fast", "speed_fast"),
            Item("Fastest", "speed_fastest"),
        ),
    ),
)

SHORTCUTS: dict[int, str] = {
    pygame.K_F1: "help",
    pygame.K_F2: "sound",
    pygame.K_F3: "score",
    pygame.K_F4: "look",
    pygame.K_F5: "save",
    pygame.K_F7: "restore",
    pygame.K_F9: "restart",
    pygame.K_TAB: "inventory",
}


class MenuBar:
    def __init__(self, menus: tuple[Menu, ...] = MENUS) -> None:
        self.menus = menus
        self.open = False
        self.menu = 0
        self.item = 0
        # column of each title on the 40-column status line
        self.columns: list[int] = []
        col = 1
        for m in menus:
            self.columns.append(col)
            col += len(m.title) + 2

    def show(self) -> None:
        self.open = True
        self.menu = 0
        self.item = 0

    def hide(self) -> None:
        self.open = False

    def handle_key(self, key: int) -> str | None:
        """Navigate; return an action name when an item is chosen."""
        n = len(self.menus)
        items = self.menus[self.menu].items
        if key == pygame.K_ESCAPE:
            self.hide()
        elif key == pygame.K_LEFT:
            self.menu = (self.menu - 1) % n
            self.item = 0
        elif key == pygame.K_RIGHT:
            self.menu = (self.menu + 1) % n
            self.item = 0
        elif key == pygame.K_UP:
            self.item = (self.item - 1) % len(items)
        elif key == pygame.K_DOWN:
            self.item = (self.item + 1) % len(items)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.hide()
            return items[self.item].action
        return None

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, PALETTE[WHITE], pygame.Rect(0, 0, SCREEN_W, CHAR_H))
        for i, m in enumerate(self.menus):
            fg, bg = (WHITE, BLACK) if i == self.menu else (BLACK, WHITE)
            draw_row(screen, 0, self.columns[i], m.title, fg, bg)
        menu = self.menus[self.menu]
        width = max(len(it.label) + (len(it.key) + 2 if it.key else 0) for it in menu.items) + 2
        x = min(self.columns[self.menu], 40 - width - 1) * CHAR_W
        y = CHAR_H
        box = pygame.Rect(x, y, width * CHAR_W, (len(menu.items) + 2) * CHAR_H)
        pygame.draw.rect(screen, PALETTE[WHITE], box)
        pygame.draw.rect(screen, PALETTE[BLACK], box.inflate(-4, -4), 1)
        for j, it in enumerate(menu.items):
            fg, bg = (WHITE, BLACK) if j == self.item else (BLACK, WHITE)
            text = it.label.ljust(width - 2 - len(it.key)) + it.key
            draw_text(screen, x + CHAR_W, y + (j + 1) * CHAR_H, text, fg, bg)
