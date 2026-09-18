"""Paul, the player character: a procedurally defined AGI-style animated sprite.

Frames are ASCII art in 160-wide picture coordinates. Legend:
  .  transparent   h hair (black)   f face (light red)   w suit (white)
  k  shirt/belt (black)   g gold chain (yellow)   b shoes (brown)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from ppp.const import BLACK, BROWN, LRED, PALETTE, PIC_H, PIC_W, WHITE, YELLOW, priority_for_y
from ppp.pic import Picture

LEGEND = {"h": BLACK, "f": LRED, "w": WHITE, "k": BLACK, "g": YELLOW, "b": BROWN}

_HEAD_FRONT = """
..hhhh..
.hhhhhh.
.hffffh.
.hkffkh.
..ffff..
...ff...
"""
_HEAD_BACK = """
..hhhh..
.hhhhhh.
.hhhhhh.
.hhhhhh.
..hhhh..
...ff...
"""
_HEAD_SIDE = """
..hhhh..
.hhhhhh.
.hhffff.
.hhkfff.
..hfff..
...ff...
"""
_TORSO_FRONT = """
.wwkkww.
wwwkkwww
wwwgkwww
wwwkkwww
wwwwwwww
wwwwwwww
wwwwwwww
fwwwwwwf
.wwwwww.
.kkkkkk.
.wwwwww.
"""
_TORSO_BACK = _TORSO_FRONT.replace("k", "w").replace("g", "w")
_TORSO_SIDE = """
..wwww..
..wwkw..
..wwgw..
..wwww..
..wwww..
..wwww..
..wwwww.
..wwwwf.
..wwww..
..kkkk..
..wwww..
"""
_LEGS_FRONT_A = """
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.bb..bb.
.bb..bb.
"""
_LEGS_FRONT_B = """
.ww..ww.
.ww..ww.
ww....ww
ww....ww
ww....ww
ww....ww
ww....ww
ww....ww
ww....ww
bb....bb
bb....bb
"""
_LEGS_SIDE_A = """
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..bbbb..
..bbbbb.
"""
_LEGS_SIDE_B = """
..wwww..
.www.ww.
.ww..ww.
.ww...ww
.ww...ww
ww....ww
ww....ww
ww....ww
ww....ww
bb....bb
bb....bb
"""


def _rows(block: str) -> list[str]:
    rows = [r for r in block.strip("\n").split("\n")]
    for r in rows:
        assert len(r) == 8, f"sprite row must be 8 wide: {r!r}"
    return rows


def _frame(head: str, torso: str, legs: str) -> list[str]:
    return _rows(head) + _rows(torso) + _rows(legs)


def _surface(rows: list[str], mirror: bool = False) -> pygame.Surface:
    h = len(rows)
    surf = pygame.Surface((8, h))
    key = (1, 2, 3)
    surf.fill(key)
    surf.set_colorkey(key)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                surf.set_at((x, y), PALETTE[LEGEND[ch]])
    return pygame.transform.flip(surf, True, False) if mirror else surf


# AGI directions: 0 stop, 1 N, 2 NE, 3 E, 4 SE, 5 S, 6 SW, 7 W, 8 NW
DIR_DELTA: dict[int, tuple[int, int]] = {
    0: (0, 0),
    1: (0, -1),
    2: (1, -1),
    3: (1, 0),
    4: (1, 1),
    5: (0, 1),
    6: (-1, 1),
    7: (-1, 0),
    8: (-1, -1),
}


def _build_frames() -> dict[str, list[pygame.Surface]]:
    down = [_frame(_HEAD_FRONT, _TORSO_FRONT, _LEGS_FRONT_A), _frame(_HEAD_FRONT, _TORSO_FRONT, _LEGS_FRONT_B)]
    up = [_frame(_HEAD_BACK, _TORSO_BACK, _LEGS_FRONT_A), _frame(_HEAD_BACK, _TORSO_BACK, _LEGS_FRONT_B)]
    right = [_frame(_HEAD_SIDE, _TORSO_SIDE, _LEGS_SIDE_A), _frame(_HEAD_SIDE, _TORSO_SIDE, _LEGS_SIDE_B)]
    return {
        "down": [_surface(f) for f in down],
        "up": [_surface(f) for f in up],
        "right": [_surface(f) for f in right],
        "left": [_surface(f, mirror=True) for f in right],
    }


def _facing(direction: int) -> str:
    if direction in (2, 3, 4):
        return "right"
    if direction in (6, 7, 8):
        return "left"
    if direction == 1:
        return "up"
    return "down"


@dataclass
class Ego:
    x: int = 80  # left edge of the 8-wide sprite, picture coords
    y: int = 140  # baseline (feet), picture coords
    direction: int = 0
    facing: str = "down"
    step: int = 1
    frame: int = 0
    anim_tick: int = 0
    visible: bool = True
    frozen: bool = False  # true while a cutscene or message holds him
    frames: dict[str, list[pygame.Surface]] = field(default_factory=dict, repr=False)

    def ensure_frames(self) -> None:
        if not self.frames:
            self.frames = _build_frames()

    @property
    def width(self) -> int:
        return 8

    @property
    def height(self) -> int:
        self.ensure_frames()
        return self.frames["down"][0].get_height()

    @property
    def priority(self) -> int:
        return priority_for_y(self.y)

    @property
    def centre_x(self) -> int:
        return self.x + 4

    def set_direction(self, d: int) -> None:
        """AGI feel: pressing the current direction again stops walking."""
        self.direction = 0 if d == self.direction else d
        if self.direction:
            self.facing = _facing(self.direction)

    def stop(self) -> None:
        self.direction = 0
        self.frame = 0

    def _blocked(self, pic: Picture, nx: int, ny: int, horizon: int) -> bool:
        if ny < horizon:
            return True
        # feet strip: bottom row of the sprite across the body width
        for px in range(nx + 1, nx + 7):
            if pic.pri_at(px, ny) == 0:
                return True
        return False

    def update(self, pic: Picture, horizon: int) -> str | None:
        """Advance one cycle. Returns an edge name if Paul walked off screen."""
        if self.frozen or not self.direction:
            return None
        dx, dy = DIR_DELTA[self.direction]
        nx, ny = self.x + dx * self.step, self.y + dy * self.step
        if nx < -4:
            return "left"
        if nx + self.width > PIC_W + 4:
            return "right"
        if ny >= PIC_H:
            return "bottom"
        if ny < horizon and dy < 0 and horizon <= 0:
            return "top"
        if self._blocked(pic, nx, ny, horizon):
            # try sliding along one axis
            if dx and not self._blocked(pic, self.x + dx * self.step, self.y, horizon):
                nx, ny = self.x + dx * self.step, self.y
            elif dy and not self._blocked(pic, self.x, self.y + dy * self.step, horizon):
                nx, ny = self.x, self.y + dy * self.step
            else:
                return None
        self.x, self.y = nx, ny
        self.anim_tick += 1
        if self.anim_tick % 4 == 0:
            self.frame ^= 1
        return None

    def draw(self, target: pygame.Surface, pic: Picture) -> None:
        """Blit with priority: background pixels of higher priority cover Paul."""
        if not self.visible:
            return
        self.ensure_frames()
        surf = self.frames[self.facing][self.frame if self.direction else 0]
        top = self.y - surf.get_height() + 1
        raw_key = surf.get_colorkey()
        key = pygame.Color(*raw_key) if raw_key else None
        mine = self.priority
        for sy in range(surf.get_height()):
            py = top + sy
            if not 0 <= py < PIC_H:
                continue
            for sx in range(surf.get_width()):
                px = self.x + sx
                if not 0 <= px < PIC_W:
                    continue
                c = surf.get_at((sx, sy))
                if c == key:
                    continue
                if pic.pri_at(px, py) > mine:
                    continue
                target.set_at((px, py), c)
