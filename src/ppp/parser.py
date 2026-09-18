"""Text parser: tokenise a typed line into word groups and match `said` patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ppp.words import ANY, IGNORE, ROL, lookup

_token_re = re.compile(r"[a-z0-9']+")


@dataclass
class Parsed:
    words: list[str] = field(default_factory=list)  # group names in order
    raw: list[str] = field(default_factory=list)  # original tokens kept
    unknown: str | None = None  # first unrecognised word, if any
    number: int | None = None  # the first numeric token, matched as the word "number"

    def said(self, *pattern: str) -> bool:
        """AGI-style match. `anyword` matches one word, `rol` matches the rest."""
        if self.unknown is not None:
            return False
        w = self.words
        for i, p in enumerate(pattern):
            if p == ROL:
                return True
            if i >= len(w):
                return False
            if p != ANY and p != w[i]:
                return False
        return len(w) == len(pattern)

    def has(self, *names: str) -> bool:
        return any(n in self.words for n in names)

    @property
    def verb(self) -> str:
        """The first word group, or "" for an empty or unknown-only line."""
        return self.words[0] if self.words else ""

    @property
    def empty(self) -> bool:
        return not self.words and self.unknown is None


def parse(text: str, pauline: bool = False) -> Parsed:
    out = Parsed()
    table = lookup(pauline)
    for tok in _token_re.findall(text.lower()):
        tok = tok.removesuffix("'s")  # rooster's -> rooster
        if tok in IGNORE:
            continue
        if tok.isdigit():
            if out.number is None:
                out.number = int(tok)
            out.words.append("number")
            out.raw.append(tok)
            continue
        group = table.get(tok)
        if group is None:
            if out.unknown is None:
                out.unknown = tok
            continue
        out.words.append(group)
        out.raw.append(tok)
    return out
