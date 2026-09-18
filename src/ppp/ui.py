"""Status line, parser prompt, and Sierra-style message boxes."""

from __future__ import annotations

import pygame

from ppp.const import (
    BLACK,
    INPUT_ROW,
    PALETTE,
    PIC_TOP,
    RED,
    SCREEN_H,
    SCREEN_W,
    STATUS_ROW,
    WHITE,
)
from ppp.font import CHAR_H, CHAR_W, draw_row, draw_text, wrap
from ppp.game import MAX_SCORE, Game

BOX_COLS = 30  # max text width of a message box in characters


def draw_status(screen: pygame.Surface, game: Game) -> None:
    pygame.draw.rect(screen, PALETTE[WHITE], pygame.Rect(0, STATUS_ROW * CHAR_H, SCREEN_W, CHAR_H))
    draw_row(screen, STATUS_ROW, 1, f"Score: {game.score} of {MAX_SCORE}", BLACK, WHITE)
    sound = "on " if game.sound_on else "off"
    draw_row(screen, STATUS_ROW, 30, f"Sound:{sound}", BLACK, WHITE)


def draw_prompt(screen: pygame.Surface, text: str, blink: bool) -> None:
    y = INPUT_ROW * CHAR_H
    pygame.draw.rect(screen, PALETTE[BLACK], pygame.Rect(0, y, SCREEN_W, CHAR_H * 2))
    line = ">" + text
    draw_text(screen, 0, y, line[-39:], WHITE)
    if blink:
        cx = min(len(line), 39) * CHAR_W
        pygame.draw.rect(screen, PALETTE[WHITE], pygame.Rect(cx, y + CHAR_H - 2, CHAR_W, 2))


def draw_message(screen: pygame.Surface, text: str) -> None:
    lines = wrap(text, BOX_COLS)
    cols = max(len(line) for line in lines)
    w = (cols + 2) * CHAR_W
    h = (len(lines) + 2) * CHAR_H
    x = (SCREEN_W - w) // 2
    pic_mid = PIC_TOP + (INPUT_ROW * CHAR_H - PIC_TOP) // 2
    y = max(PIC_TOP, pic_mid - h // 2)
    y = min(y, SCREEN_H - h - CHAR_H)
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, PALETTE[WHITE], rect)
    pygame.draw.rect(screen, PALETTE[RED], rect.inflate(-4, -4), 1)
    pygame.draw.rect(screen, PALETTE[RED], rect.inflate(-6, -6), 1)
    for i, line in enumerate(lines):
        draw_text(screen, x + CHAR_W, y + CHAR_H + i * CHAR_H, line, BLACK, WHITE)


def draw_text_screen(screen: pygame.Surface, lines: list[str], fg: int = WHITE, bg: int = BLACK, top: int = 2) -> None:
    """A whole-screen text page (title card, age quiz, death screens)."""
    screen.fill(PALETTE[bg])
    for i, line in enumerate(lines):
        draw_row(screen, top + i, 0, line[:40], fg, bg)
