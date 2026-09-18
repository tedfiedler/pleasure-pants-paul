"""Render the 8x8 bitmap font onto pygame surfaces."""

from __future__ import annotations

import pygame

from ppp.const import PALETTE
from ppp.fontdata import GLYPHS

CHAR_W = 8
CHAR_H = 8

_cache: dict[tuple[str, int, int | None], pygame.Surface] = {}


def glyph(ch: str, fg: int, bg: int | None = None) -> pygame.Surface:
    """Return an 8x8 surface for one character, cached by colour."""
    key = (ch, fg, bg)
    surf = _cache.get(key)
    if surf is not None:
        return surf
    code = ord(ch)
    rows = GLYPHS[code] if code < len(GLYPHS) else GLYPHS[ord("?")]
    surf = pygame.Surface((CHAR_W, CHAR_H))
    if bg is None:
        surf.set_colorkey((1, 2, 3))
        surf.fill((1, 2, 3))
    else:
        surf.fill(PALETTE[bg])
    colour = PALETTE[fg]
    for y, row in enumerate(rows):
        for x in range(CHAR_W):
            if row >> x & 1:
                surf.set_at((x, y), colour)
    _cache[key] = surf
    return surf


def draw_text(target: pygame.Surface, x: int, y: int, text: str, fg: int, bg: int | None = None) -> None:
    """Draw text with its top-left corner at pixel (x, y)."""
    for i, ch in enumerate(text):
        target.blit(glyph(ch, fg, bg), (x + i * CHAR_W, y))


def draw_row(target: pygame.Surface, row: int, col: int, text: str, fg: int, bg: int | None = None) -> None:
    """Draw text at a text-cell position (row, col) on a 40x25 grid."""
    draw_text(target, col * CHAR_W, row * CHAR_H, text, fg, bg)


def wrap(text: str, width: int) -> list[str]:
    """Greedy word-wrap to `width` columns, honouring explicit newlines."""
    lines: list[str] = []
    for para in text.split("\n"):
        line = ""
        for word in para.split(" "):
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= width:
                line += " " + word
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines
