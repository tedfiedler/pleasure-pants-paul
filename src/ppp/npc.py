"""Static people drawn into a room's background."""

from __future__ import annotations

from ppp.const import BLACK, DGREY, WHITE
from ppp.pic import Picture


def draw_person(
    pic: Picture, x: int, y: int, *, suit: int, skin: int, hair: int, apron: bool = False, pri: int | None = None
) -> None:
    """An 8-wide standing figure with its head top at (x, y), in the default priority band."""
    pic.rect(x + 2, y, 4, 4, hair, pri)
    pic.rect(x + 2, y + 3, 4, 4, skin, pri)
    pic.rect(x, y + 7, 8, 12, suit, pri)
    if apron:
        pic.rect(x + 2, y + 10, 4, 9, WHITE, pri)
    pic.rect(x, y + 19, 8, 8, BLACK if not apron else DGREY, pri)
