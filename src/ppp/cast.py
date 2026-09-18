"""The cast, and the markup that lets one script serve both versions of the game.

Run with --pauline and the whole world is its mirror image: Paul is Pauline,
Dolores is Donny, and so on down the call sheet. Game text marks the places
that differ with square brackets:

  [Ginger]    a name from CAST: "Ginger" for Paul, "Rusty" for Pauline
  [she|he]    a choice: the text before the bar for Paul, after it for Pauline

Anything else in brackets, a slot machine's "[BAR]" say, is left alone.
"""

from __future__ import annotations

import re

# Paul's game -> Pauline's game
CAST: dict[str, str] = {
    "Paul": "Pauline",
    "Dolores": "Donny",
    "Ginger": "Rusty",
    "Hope": "Chance",
    "Dawn": "Dusty",
    "Brick": "Roxy",
}

TITLE = "Pleasure Pants [Paul]"

_markup = re.compile(r"\[([^\[\]|]*)(?:\|([^\[\]]*))?\]")


def render(text: str, pauline: bool) -> str:
    """Resolve the bracket markup in `text` for one version of the game."""

    def pick(m: re.Match[str]) -> str:
        first, second = m.group(1), m.group(2)
        if second is not None:
            return second if pauline else first
        if first in CAST:
            return CAST[first] if pauline else first
        return m.group(0)

    return _markup.sub(pick, text)
