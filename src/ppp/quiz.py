"""The age-verification quiz: five questions only a grown-up could answer.

Faithful to the spirit of the 1987 original, with our own questions.
A secret key combo skips it, because it always did.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ppp.font import wrap

# (question, [choices], index of correct answer)
QUESTIONS: list[tuple[str, list[str], int]] = [
    ("A mortgage is:", ["A dance craze", "A loan on a house", "A kind of cheese", "A Volvo model"], 1),
    (
        "What does IRS stand for?",
        ["Internal Revenue Service", "I Really Sweat", "Instant Rice Supply", "Iron Rock Stadium"],
        0,
    ),
    ("The legal drinking age in most of the U.S. is:", ["16", "18", "21", "Whenever"], 2),
    ("Which of these is a real tax form?", ["1040", "R2D2", "3.14", "Form 86"], 0),
    ("A '401(k)' is:", ["A highway", "A retirement plan", "A pizza size", "A running shoe"], 1),
    ("Cholesterol is found in:", ["Eggs", "Sunlight", "Cassette tapes", "Elevators"], 0),
    ("A 'happy hour' is:", ["A cartoon", "A yoga pose", "Cheap drinks after work", "A prayer"], 2),
    ("Which one goes on a car?", ["Diapers", "Snow tires", "Bunk beds", "Legos"], 1),
    ("Escrow is:", ["A crow with a hat", "A held deposit", "A breakfast cereal", "An exit ramp"], 1),
    ("You get a W-2 from your:", ["Dentist", "Employer", "Bowling league", "Mother"], 1),
    ("What is a 'deductible'?", ["A vegetable", "What you pay before insurance does", "A detective", "A hairstyle"], 1),
    ("Who fixes a leaky faucet?", ["A plumber", "A pediatrician", "A pilot", "A poodle"], 0),
    ("A 'bar tab' is:", ["A keyboard key", "Money you owe the bartender", "A soap brand", "A wrestling move"], 1),
    ("The 'prime rate' is:", ["Beef quality", "A bank interest rate", "A TV time slot", "A steak sauce"], 1),
]

NEEDED = 5
MAX_WRONG = 2


@dataclass
class Quiz:
    questions: list[tuple[str, list[str], int]] = field(default_factory=list)
    index: int = 0
    wrong: int = 0
    done: bool = False
    passed: bool = False
    skipped: bool = False
    feedback: str | None = None

    def start(self, rng: random.Random | None = None) -> None:
        rng = rng or random.Random()
        self.questions = rng.sample(QUESTIONS, NEEDED)
        self.index = 0
        self.wrong = 0
        self.done = False
        self.passed = False
        self.skipped = False
        self.feedback = None

    @property
    def current(self) -> tuple[str, list[str], int]:
        return self.questions[self.index]

    def answer(self, letter: str) -> None:
        """Answer with 'a'..'d'. Advances, and ends the quiz when settled."""
        if self.done or self.feedback is not None:
            return
        choice = "abcd".find(letter.lower())
        if choice < 0:
            return
        q, choices, correct = self.current
        if choice == correct:
            self.feedback = "Correct. Carry on."
        else:
            self.wrong += 1
            self.feedback = f"Wrong. It's {'ABCD'[correct]}: {choices[correct]}."
        if self.wrong > MAX_WRONG:
            self.done = True
            self.passed = False

    def next(self) -> None:
        """Dismiss feedback and move to the next question."""
        self.feedback = None
        if self.done:
            return
        self.index += 1
        if self.index >= len(self.questions):
            self.done = True
            self.passed = True

    def skip(self) -> None:
        self.done = True
        self.passed = True
        self.skipped = True

    def lines(self) -> list[str]:
        """Render the current state as 40-column text lines."""
        out = [
            "   PLEASURE PANTS PAUL - AGE CHECK",
            "",
            "This game is for grown-ups. Prove it.",
            f"Question {self.index + 1} of {len(self.questions)}    Wrong: {self.wrong}/{MAX_WRONG}",
            "",
        ]
        q, choices, _ = self.current
        out.extend(wrap(q, 40))
        out.append("")
        for i, c in enumerate(choices):
            out.extend(wrap(f"  {'ABCD'[i]}. {c}", 40))
        out.append("")
        if self.feedback:
            out.extend(wrap(self.feedback, 40))
            out.append("")
            out.append("Press any key.")
        else:
            out.append("Press A, B, C or D.")
        return out
