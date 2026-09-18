"""Saved games: JSON snapshots in the platform's per-user data directory."""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ppp.game import Game

APP_DIR = "PleasurePantsPaul"
FORMAT = 1
MAX_SAVES = 12


def save_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share")))
    d = Path(os.environ.get("PPP_SAVE_DIR", str(base / APP_DIR / "saves")))
    d.mkdir(parents=True, exist_ok=True)
    return d


@dataclass
class SaveInfo:
    path: Path
    description: str
    when: float


def snapshot(game: Game, description: str) -> dict[str, Any]:
    assert game.room is not None
    return {
        "format": FORMAT,
        "description": description,
        "when": time.time(),
        "room": game.room.number,
        "ego": {"x": game.ego.x, "y": game.ego.y, "facing": game.ego.facing},
        "score": game.score,
        "scored": sorted(game.scored),
        "inventory": list(game.inventory),
        "flags": dict(game.flags),
        "vars": dict(game.vars),
        "sound_on": game.sound_on,
        "speed": game.speed,
        "cycle_count": game.cycle_count,
    }


def apply(game: Game, data: dict[str, Any]) -> None:
    """Load a snapshot into a game whose rooms are already registered."""
    if data.get("format") != FORMAT:
        raise ValueError("unsupported save format")
    game.score = int(data["score"])
    game.scored = set(data["scored"])
    game.inventory = list(data["inventory"])
    game.flags = dict(data["flags"])
    game.vars = dict(data["vars"])
    game.sound_on = bool(data["sound_on"])
    game.speed = str(data.get("speed", "normal"))
    game.cycle_count = int(data.get("cycle_count", 0))
    game.messages.clear()
    game.dead = False
    game.new_room(int(data["room"]))
    game.messages.clear()  # room.enter() may greet; a restore is silent
    ego = data["ego"]
    game.ego.x, game.ego.y = int(ego["x"]), int(ego["y"])
    game.ego.facing = str(ego["facing"])
    game.ego.stop()


def write(game: Game, description: str) -> Path:
    data = snapshot(game, description)
    stamp = int(data["when"] * 1000)
    path = save_dir() / f"{stamp}.json"
    n = 0
    while path.exists():
        n += 1
        path = save_dir() / f"{stamp}-{n}.json"
    data["when"] = stamp / 1000 + n / 1e6  # keep list order stable for same-millisecond saves
    path.write_text(json.dumps(data, indent=1))
    for old in list_saves()[MAX_SAVES:]:
        old.path.unlink(missing_ok=True)
    return path


def read(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def list_saves() -> list[SaveInfo]:
    out: list[SaveInfo] = []
    for path in save_dir().glob("*.json"):
        try:
            data = read(path)
            out.append(SaveInfo(path, str(data.get("description", path.stem)), float(data.get("when", 0))))
        except (OSError, ValueError):
            continue
    out.sort(key=lambda s: s.when, reverse=True)
    return out
