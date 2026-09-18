"""Paul, the player character: a procedurally defined AGI-style animated sprite.

Frames are ASCII art in 160-wide picture coordinates. Legend:
  .  transparent   h hair (black)   f face (light red)   w suit (white)
  k  shirt/belt (black)   g gold chain (yellow)   b shoes (brown)

Pauline, his mirror image, has her own frames in the same layout: big hair,
a pink blouse (p) under the white pantsuit, bell-bottoms, and red heels (b).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from ppp.const import BLACK, BROWN, LMAGENTA, LRED, PIC_H, PIC_W, RED, WHITE, YELLOW, priority_for_y
from ppp.pic import Picture
from ppp.sprite import from_rows, rows_of

LEGEND = {"h": BLACK, "f": LRED, "w": WHITE, "k": BLACK, "g": YELLOW, "b": BROWN}
PAULINE_LEGEND = {**LEGEND, "p": LMAGENTA, "b": RED}

# Paul is balding: flesh on top, hair at the sides and back.
_HEAD_FRONT = """
..ffff..
.hffffh.
.hffffh.
.hkffkh.
..ffff..
...ff...
"""
_HEAD_BACK = """
..ffff..
.hhffhh.
.hhhhhh.
.hhhhhh.
..hhhh..
...ff...
"""
# Profile: hair at the back (left), a three-unit face with one eye in front.
_HEAD_SIDE = """
..ffff..
.hhfff..
.hhkff..
.hhfff..
..hff...
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
_TORSO_BACK = """
.wwwwww.
wwwwwwww
wwwwwwww
wwwwwwww
wwwwwwww
wwwwwwww
wwwwwwww
fwwwwwwf
.wwwwww.
.kkkkkk.
.wwwwww.
"""
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
# one leg lifted mid-stride; C is B's mirror so the cycle goes A B A C
_LEGS_FRONT_B = """
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..bb.
.ww..bb.
.ww.....
.bb.....
.bb.....
"""
_LEGS_FRONT_C = "\n".join(r[::-1] for r in _LEGS_FRONT_B.split("\n"))
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

_PAULINE_HEAD_FRONT = """
.hhhhhh.
hhffffhh
hhffffhh
hhkffkhh
hhffffhh
.h.ff.h.
"""
_PAULINE_HEAD_BACK = """
.hhhhhh.
hhhhhhhh
hhhhhhhh
hhhhhhhh
hhhhhhhh
.hhhhhh.
"""
_PAULINE_HEAD_SIDE = """
.hhhhh..
hhhfff..
hhhkff..
hhhfff..
hhhff...
.hhff...
"""
# arms hang clear of a narrower waist
_PAULINE_TORSO_FRONT = """
.wwppww.
wwwppwww
wwwgpwww
wwwwwwww
w.wwww.w
w.wwww.w
w.wwww.w
f.wwww.f
..wwww..
.kkkkkk.
.wwwwww.
"""
_PAULINE_TORSO_BACK = """
.whhhhw.
wwwhhwww
wwwwwwww
wwwwwwww
w.wwww.w
w.wwww.w
w.wwww.w
f.wwww.f
..wwww..
.kkkkkk.
.wwwwww.
"""
_PAULINE_TORSO_SIDE = """
.hwwww..
..wwpw..
..wwgww.
..wwwww.
..wwww..
..wwww..
..wwwww.
..wwwwf.
..wwww..
..kkkk..
..wwwww.
"""
# bell-bottoms: the flare sits on top of the heels
_PAULINE_LEGS_FRONT_A = """
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
www..www
www..www
.bb..bb.
"""
_PAULINE_LEGS_FRONT_B = """
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..ww.
.ww..www
.ww..www
.ww..bb.
www.....
www.....
.bb.....
"""
_PAULINE_LEGS_FRONT_C = "\n".join(r[::-1] for r in _PAULINE_LEGS_FRONT_B.split("\n"))
_PAULINE_LEGS_SIDE_A = """
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
..wwww..
.wwwwww.
.wwwwww.
..bbbbb.
"""
_PAULINE_LEGS_SIDE_B = """
..wwww..
.www.ww.
.ww..ww.
.ww...ww
.ww...ww
ww....ww
ww....ww
ww....ww
www..www
www..www
bb....bb
"""


def _frame(head: str, torso: str, legs: str) -> list[str]:
    return rows_of(head, 8) + rows_of(torso, 8) + rows_of(legs, 8)


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


def _build_frames(pauline: bool = False) -> dict[str, list[pygame.Surface]]:
    if pauline:
        legend = PAULINE_LEGEND
        heads = (_PAULINE_HEAD_FRONT, _PAULINE_HEAD_BACK, _PAULINE_HEAD_SIDE)
        torsos = (_PAULINE_TORSO_FRONT, _PAULINE_TORSO_BACK, _PAULINE_TORSO_SIDE)
        front_a, front_b, front_c = _PAULINE_LEGS_FRONT_A, _PAULINE_LEGS_FRONT_B, _PAULINE_LEGS_FRONT_C
        side_a, side_b = _PAULINE_LEGS_SIDE_A, _PAULINE_LEGS_SIDE_B
    else:
        legend = LEGEND
        heads = (_HEAD_FRONT, _HEAD_BACK, _HEAD_SIDE)
        torsos = (_TORSO_FRONT, _TORSO_BACK, _TORSO_SIDE)
        front_a, front_b, front_c = _LEGS_FRONT_A, _LEGS_FRONT_B, _LEGS_FRONT_C
        side_a, side_b = _LEGS_SIDE_A, _LEGS_SIDE_B
    front_cycle = (front_a, front_b, front_a, front_c)
    down = [_frame(heads[0], torsos[0], legs) for legs in front_cycle]
    up = [_frame(heads[1], torsos[1], legs) for legs in front_cycle]
    right = [_frame(heads[2], torsos[2], side_a), _frame(heads[2], torsos[2], side_b)]
    return {
        "down": [from_rows(f, legend) for f in down],
        "up": [from_rows(f, legend) for f in up],
        "right": [from_rows(f, legend) for f in right],
        "left": [from_rows(f, legend, mirror=True) for f in right],
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
    pauline: bool = False  # which set of frames to wear
    frames: dict[str, list[pygame.Surface]] = field(default_factory=dict, repr=False)

    def ensure_frames(self) -> None:
        if not self.frames:
            self.frames = _build_frames(self.pauline)

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

    def blocked(self, pic: Picture, nx: int, ny: int, horizon: int) -> bool:
        if ny < horizon:
            return True
        # feet strip: bottom row of the sprite across the body width;
        # pixels beyond the picture edge are open so Paul can walk off screen
        for px in range(nx + 1, nx + 7):
            if 0 <= px < PIC_W and pic.pri_at(px, ny) == 0:
                return True
        return False

    def update(self, pic: Picture, horizon: int) -> str | None:
        """Advance one cycle. Returns an edge name if Paul walked off screen."""
        if self.frozen or not self.direction:
            return None
        dx, dy = DIR_DELTA[self.direction]
        nx, ny = self.x + dx * self.step, self.y + dy * self.step
        if nx < 0:
            return "left"
        if nx + self.width > PIC_W:
            return "right"
        if ny >= PIC_H:
            return "bottom"
        if ny < horizon and dy < 0 and horizon <= 0:
            return "top"
        if self.blocked(pic, nx, ny, horizon):
            # try sliding along one axis
            if dx and not self.blocked(pic, self.x + dx * self.step, self.y, horizon):
                nx, ny = self.x + dx * self.step, self.y
            elif dy and not self.blocked(pic, self.x, self.y + dy * self.step, horizon):
                nx, ny = self.x, self.y + dy * self.step
            else:
                return None
        self.x, self.y = nx, ny
        self.anim_tick += 1
        if self.anim_tick % 4 == 0:
            self.ensure_frames()
            self.frame = (self.frame + 1) % len(self.frames[self.facing])
        return None

    def draw(self, target: pygame.Surface, pic: Picture) -> None:
        """Blit with priority: background pixels of higher priority cover Paul."""
        if not self.visible:
            return
        self.ensure_frames()
        cycle = self.frames[self.facing]
        surf = cycle[self.frame % len(cycle) if self.direction else 0]
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
