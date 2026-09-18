"""AGI-style picture: a 160x168 visual screen plus a priority screen.

Backgrounds are not bitmaps but a list of drawing commands, as in the
original PIC resources. Rooms call the drawing methods in `draw()`.
Every command can draw to the visual screen, the priority screen, or both.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence

import pygame

from ppp.const import PALETTE, PIC_H, PIC_W, PRI_MIN, WHITE, priority_for_y

Point = tuple[int, int]


class Picture:
    def __init__(self) -> None:
        self.visual = pygame.Surface((PIC_W, PIC_H))
        self.visual.fill(PALETTE[WHITE])
        # priority stored as a greyscale index in the red channel
        self.priority = pygame.Surface((PIC_W, PIC_H))
        for y in range(PIC_H):
            p = priority_for_y(y)
            pygame.draw.line(self.priority, (p, p, p), (0, y), (PIC_W - 1, y))

    # -- queries -------------------------------------------------------

    def pri_at(self, x: int, y: int) -> int:
        if 0 <= x < PIC_W and 0 <= y < PIC_H:
            return self.priority.get_at((x, y))[0]
        return 0

    def colour_at(self, x: int, y: int) -> int:
        rgb = self.visual.get_at((x, y))[:3]
        return PALETTE.index(rgb) if rgb in PALETTE else 0

    # -- drawing -------------------------------------------------------

    def _targets(self, vis: int | None, pri: int | None) -> list[tuple[pygame.Surface, tuple[int, int, int]]]:
        out: list[tuple[pygame.Surface, tuple[int, int, int]]] = []
        if vis is not None:
            out.append((self.visual, PALETTE[vis]))
        if pri is not None:
            out.append((self.priority, (pri, pri, pri)))
        return out

    def rect(self, x: int, y: int, w: int, h: int, vis: int | None, pri: int | None = None) -> None:
        for surf, col in self._targets(vis, pri):
            pygame.draw.rect(surf, col, pygame.Rect(x, y, w, h))

    def line(self, points: Sequence[Point], vis: int | None, pri: int | None = None) -> None:
        for surf, col in self._targets(vis, pri):
            if len(points) == 1:
                surf.set_at(points[0], col)
            else:
                pygame.draw.lines(surf, col, False, list(points))

    def poly(self, points: Sequence[Point], vis: int | None, pri: int | None = None) -> None:
        for surf, col in self._targets(vis, pri):
            pygame.draw.polygon(surf, col, list(points))

    def fill(self, x: int, y: int, vis: int | None, pri: int | None = None) -> None:
        """Flood fill from (x, y), bounded by any colour other than the start colour."""
        for surf, col in self._targets(vis, pri):
            _flood(surf, x, y, col)

    def pixel(self, x: int, y: int, vis: int | None, pri: int | None = None) -> None:
        for surf, col in self._targets(vis, pri):
            surf.set_at((x, y), col)

    def text_pri_band(self, y_top: int, y_bottom: int, pri: int) -> None:
        """Override the priority band for a horizontal strip (e.g. a raised floor)."""
        self.rect(0, y_top, PIC_W, y_bottom - y_top, None, pri)

    def walls(self, y_floor: int) -> None:
        """Mark everything above `y_floor` unwalkable (a back wall)."""
        self.rect(0, 0, PIC_W, y_floor, None, 0)

    def barrier(self, points: Sequence[Point]) -> None:
        self.line(points, None, 0)


def _flood(surf: pygame.Surface, x: int, y: int, colour: tuple[int, int, int]) -> None:
    w, h = surf.get_size()
    if not (0 <= x < w and 0 <= y < h):
        return
    target = surf.get_at((x, y))[:3]
    if target == colour:
        return
    surf.lock()
    q: deque[Point] = deque([(x, y)])
    while q:
        cx, cy = q.popleft()
        if surf.get_at((cx, cy))[:3] != target:
            continue
        # scan left/right
        lx = cx
        while lx - 1 >= 0 and surf.get_at((lx - 1, cy))[:3] == target:
            lx -= 1
        rx = cx
        while rx + 1 < w and surf.get_at((rx + 1, cy))[:3] == target:
            rx += 1
        for px in range(lx, rx + 1):
            surf.set_at((px, cy), colour)
            if cy > 0 and surf.get_at((px, cy - 1))[:3] == target:
                q.append((px, cy - 1))
            if cy + 1 < h and surf.get_at((px, cy + 1))[:3] == target:
                q.append((px, cy + 1))
    surf.unlock()


__all__ = ["Picture", "Point", "PRI_MIN"]
