"""Screen geometry and the 16-colour EGA palette.

The AGI layout: a 320x200 screen made of 25 text rows of 8 pixels.
Row 0 is the status line, the picture occupies rows 1..21 (168 px, drawn
at 160 wide with double-width pixels) and the parser input sits on row 23.
"""

SCREEN_W = 320
SCREEN_H = 200
PIC_W = 160  # picture coordinates are 160 wide; each pixel is 2 screen px
PIC_H = 168
PIC_TOP = 8  # screen y of picture row 0
INPUT_ROW = 23  # text row of the parser prompt
STATUS_ROW = 0

CYCLES_PER_SEC = 20  # AGI "normal" speed

# EGA palette, index 0..15
PALETTE: list[tuple[int, int, int]] = [
    (0x00, 0x00, 0x00),  # 0  black
    (0x00, 0x00, 0xAA),  # 1  blue
    (0x00, 0xAA, 0x00),  # 2  green
    (0x00, 0xAA, 0xAA),  # 3  cyan
    (0xAA, 0x00, 0x00),  # 4  red
    (0xAA, 0x00, 0xAA),  # 5  magenta
    (0xAA, 0x55, 0x00),  # 6  brown
    (0xAA, 0xAA, 0xAA),  # 7  light grey
    (0x55, 0x55, 0x55),  # 8  dark grey
    (0x55, 0x55, 0xFF),  # 9  light blue
    (0x55, 0xFF, 0x55),  # 10 light green
    (0x55, 0xFF, 0xFF),  # 11 light cyan
    (0xFF, 0x55, 0x55),  # 12 light red
    (0xFF, 0x55, 0xFF),  # 13 light magenta
    (0xFF, 0xFF, 0x55),  # 14 yellow
    (0xFF, 0xFF, 0xFF),  # 15 white
]

BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, BROWN, LGREY = range(8)
DGREY, LBLUE, LGREEN, LCYAN, LRED, LMAGENTA, YELLOW, WHITE = range(8, 16)

# Priority screen control values (AGI semantics)
PRI_UNWALKABLE = 0
PRI_BARRIER = 1  # conditional barrier
PRI_SIGNAL = 2  # trigger line
PRI_WATER = 3
PRI_MIN = 4  # lowest drawable priority band
PRI_MAX = 15


def priority_for_y(y: int) -> int:
    """AGI priority band for a baseline y in picture coordinates.

    Bands 5..14 each cover 12 rows starting at y=48; everything above 48 is 4.
    Band 15 begins at y=168, just below the picture, so only scenery uses it.
    """
    if y < 48:
        return PRI_MIN
    return min(PRI_MAX, (y - 48) // 12 + 5)
