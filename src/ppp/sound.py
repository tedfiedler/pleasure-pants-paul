"""PC-speaker style sound: square waves synthesised at runtime, no audio files.

Everything is a sequence of (note, beats) pairs rendered to one mono 16-bit
Sound and cached on first use. `play()` is a no-op when the mixer failed to
start (no audio device, headless tests) or when sound is switched off.
"""

from __future__ import annotations

from array import array

import pygame

RATE = 22050
VOLUME = 0.22
enabled = True
_ready = False
_rate = RATE  # what the mixer actually opened with
_channels = 1
_cache: dict[str, pygame.mixer.Sound] = {}

Note = tuple[str | None, float]  # ("A4", beats); None is a rest

_SEMITONE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def init() -> None:
    """Start the mixer. Call before pygame.init(); failures just leave sound off."""
    global _ready, _rate, _channels
    try:
        pygame.mixer.pre_init(RATE, -16, 1, 512)
        pygame.mixer.init(RATE, -16, 1, 512)
        opened = pygame.mixer.get_init()
        _ready = opened is not None
        if opened is not None:
            _rate, _channels = opened[0], opened[2]
    except pygame.error:
        _ready = False


def freq(name: str) -> float:
    """'A4' -> 440.0, equal temperament."""
    pitch, octave = name[:-1], int(name[-1])
    n = _SEMITONE[pitch] + 12 * (octave + 1)
    return 440.0 * 2 ** ((n - 69) / 12)


def render(seq: list[Note], bpm: float = 150.0, duty: float = 0.5) -> pygame.mixer.Sound:
    """Render a note sequence to a square-wave Sound, with a short decay per note."""
    samples = array("h")
    beat = 60.0 / bpm
    amp = int(32767 * VOLUME)
    for name, beats in seq:
        n = int(_rate * beat * beats)
        if name is None:
            samples.extend([0] * (n * _channels))
            continue
        period = _rate / freq(name)
        gap = max(1, int(_rate * 0.02))  # a breath between notes, like the speaker had
        for i in range(n):
            if i >= n - gap:
                v = 0
            else:
                env = 1.0 if i < n * 0.7 else max(0.0, 1.0 - (i - n * 0.7) / (n * 0.3))
                v = int((amp if (i % period) < period * duty else -amp) * env)
            samples.extend([v] * _channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def noise(ms: int, rising: bool = True) -> pygame.mixer.Sound:
    """A cheap slot-reel whirr: a square wave that sweeps up or down in pitch."""
    samples = array("h")
    n = int(_rate * ms / 1000)
    amp = int(32767 * VOLUME * 0.6)
    phase = 0.0
    for i in range(n):
        t = i / n
        f = 200 + 900 * (t if rising else 1 - t)
        phase += f / _rate
        samples.extend([amp if (phase % 1.0) < 0.5 else -amp] * _channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())


# -- the tunes ------------------------------------------------------------------------

THEME: list[Note] = [  # an original lounge strut for the title card
    ("E4", 1),
    ("G4", 1),
    ("A4", 1),
    ("B4", 2),
    ("A4", 1),
    ("G4", 1),
    ("E4", 2),
    ("D4", 1),
    ("E4", 1),
    ("G4", 1),
    ("E4", 2),
    (None, 1),
    ("D4", 1),
    ("B3", 2),
    ("E4", 1),
    ("G4", 1),
    ("A4", 1),
    ("B4", 2),
    ("D5", 1),
    ("B4", 1),
    ("A4", 2),
    ("G4", 1),
    ("A4", 1),
    ("G4", 1),
    ("E4", 2),
    (None, 1),
    ("D4", 1),
    ("E4", 3),
]
DEATH: list[Note] = [("E4", 1), ("D#4", 1), ("D4", 1), ("C#4", 1), ("C4", 3), (None, 0.5), ("B3", 1), ("C4", 3)]
SCORE: list[Note] = [("C5", 0.25), ("E5", 0.25), ("G5", 0.4)]
DING: list[Note] = [("A5", 0.5), ("E6", 1)]
BUZZ: list[Note] = [("A2", 1.5)]
HORN: list[Note] = [("A3", 0.6), ("F3", 1.2)]
WEDDING: list[Note] = [  # Mendelssohn, the bit everyone knows; long out of copyright
    ("C5", 1),
    ("F4", 1),
    ("A4", 0.5),
    ("F4", 0.5),
    ("C5", 2),
    ("C5", 1),
    ("F4", 1),
    ("A4", 0.5),
    ("F4", 0.5),
    ("C5", 2),
    ("C5", 1),
    ("D5", 1),
    ("E5", 1),
    ("F5", 1),
    ("E5", 1),
    ("D5", 1),
    ("C5", 1),
    ("A4", 1),
    ("F4", 3),
]
_ARPEGGIO: list[Note] = [("C5", 0.3), ("E5", 0.3), ("G5", 0.3), ("C6", 0.3)]
JACKPOT: list[Note] = _ARPEGGIO * 3 + [("C6", 1.5)]
DISCO: list[Note] = [
    ("E2", 0.5),
    ("E2", 0.5),
    ("E3", 0.5),
    ("E2", 0.5),
    ("G2", 0.5),
    ("E2", 0.5),
    ("A2", 0.5),
    ("B2", 0.5),
] * 2
ROBBED: list[Note] = [("G4", 1), ("F#4", 1), ("F4", 1), ("E4", 3)]
ENDING: list[Note] = THEME + [("E4", 1), ("G4", 1), ("B4", 1), ("E5", 4)]

TUNES: dict[str, tuple[list[Note], float]] = {
    "theme": (THEME, 170),
    "ending": (ENDING, 170),
    "death": (DEATH, 120),
    "score": (SCORE, 220),
    "ding": (DING, 200),
    "buzz": (BUZZ, 150),
    "horn": (HORN, 160),
    "wedding": (WEDDING, 110),
    "jackpot": (JACKPOT, 200),
    "disco": (DISCO, 240),
    "robbed": (ROBBED, 100),
}


def _get(name: str) -> pygame.mixer.Sound | None:
    if name in _cache:
        return _cache[name]
    if name == "spin":
        snd = noise(700, rising=True)
    elif name in TUNES:
        seq, bpm = TUNES[name]
        snd = render(seq, bpm)
    else:
        return None
    _cache[name] = snd
    return snd


def play(name: str) -> None:
    """Play a named sound, if the mixer is up and sound is on. Never raises."""
    if not (_ready and enabled):
        return
    try:
        snd = _get(name)
        if snd is not None:
            snd.play()
    except pygame.error:
        pass


def stop() -> None:
    if _ready:
        pygame.mixer.stop()
