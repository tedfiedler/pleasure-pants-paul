"""Modal dialogs drawn as Sierra boxes: confirm, text entry, and list pick."""

from __future__ import annotations

from collections.abc import Callable

import pygame


class Dialog:
    def handle(self, ev: pygame.event.Event) -> bool:
        """Consume an event. Return True when the dialog is finished."""
        raise NotImplementedError

    def lines(self) -> tuple[list[str], int | None]:
        """Text lines to show, and the index of a highlighted line if any."""
        raise NotImplementedError


class ConfirmDialog(Dialog):
    def __init__(self, text: str, verb: str, on_yes: Callable[[], None]) -> None:
        self.text = text
        self.verb = verb
        self.on_yes = on_yes

    def handle(self, ev: pygame.event.Event) -> bool:
        if ev.type != pygame.KEYDOWN:
            return False
        if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.on_yes()
            return True
        return bool(ev.key == pygame.K_ESCAPE)

    def lines(self) -> tuple[list[str], int | None]:
        return [self.text, "", f"Press ENTER to {self.verb}.", "Press ESC to keep playing."], None


class TextDialog(Dialog):
    MAX = 28

    def __init__(self, prompt: str, on_submit: Callable[[str], None], initial: str = "") -> None:
        self.prompt = prompt
        self.on_submit = on_submit
        self.text = initial

    def handle(self, ev: pygame.event.Event) -> bool:
        if ev.type == pygame.TEXTINPUT:
            if len(self.text) < self.MAX:
                self.text += ev.text
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                return True
            if ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.text.strip():
                self.on_submit(self.text.strip())
                return True
        return False

    def lines(self) -> tuple[list[str], int | None]:
        return [self.prompt, "", self.text + "_", "", "ENTER to accept, ESC to cancel."], None


class ListDialog(Dialog):
    def __init__(self, title: str, items: list[str], on_pick: Callable[[int], None]) -> None:
        self.title = title
        self.items = items
        self.on_pick = on_pick
        self.index = 0

    def handle(self, ev: pygame.event.Event) -> bool:
        if ev.type != pygame.KEYDOWN:
            return False
        if ev.key == pygame.K_ESCAPE:
            return True
        if ev.key == pygame.K_UP:
            self.index = (self.index - 1) % len(self.items)
        elif ev.key == pygame.K_DOWN:
            self.index = (self.index + 1) % len(self.items)
        elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.on_pick(self.index)
            return True
        return False

    def lines(self) -> tuple[list[str], int | None]:
        rows = [self.title, ""]
        first = len(rows)
        rows.extend(f" {item[:28]} " for item in self.items)
        rows.extend(["", "Arrows to choose, ENTER to pick,", "ESC to cancel."])
        return rows, first + self.index
