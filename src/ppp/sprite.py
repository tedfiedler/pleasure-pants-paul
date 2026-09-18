"""ASCII-art sprites: one character per picture pixel, a legend of palette indexes."""

from __future__ import annotations

import pygame

from ppp.const import PALETTE

KEY = (1, 2, 3)  # colour-key for transparency


def rows_of(block: str, width: int | None = None) -> list[str]:
    rows = block.strip("\n").split("\n")
    w = width or len(rows[0])
    for r in rows:
        assert len(r) == w, f"sprite row must be {w} wide: {r!r}"
    return rows


def from_rows(rows: list[str], legend: dict[str, int], mirror: bool = False) -> pygame.Surface:
    h, w = len(rows), len(rows[0])
    surf = pygame.Surface((w, h))
    surf.fill(KEY)
    surf.set_colorkey(KEY)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                surf.set_at((x, y), PALETTE[legend[ch]])
    return pygame.transform.flip(surf, True, False) if mirror else surf


def from_ascii(block: str, legend: dict[str, int], mirror: bool = False) -> pygame.Surface:
    return from_rows(rows_of(block), legend, mirror)
