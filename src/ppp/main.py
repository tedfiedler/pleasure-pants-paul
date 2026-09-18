"""Entry point: window, main loop, and the title -> quiz -> play state machine."""

from __future__ import annotations

import argparse
import sys
from enum import Enum, auto

import pygame

from ppp import __version__
from ppp.const import BLACK, CYCLES_PER_SEC, PALETTE, PIC_H, PIC_TOP, PIC_W, SCREEN_H, SCREEN_W, WHITE, YELLOW
from ppp.game import Game
from ppp.quiz import Quiz
from ppp.rooms import START_ROOM, register
from ppp.ui import draw_message, draw_prompt, draw_status, draw_text_screen

TITLE_LINES = [
    "",
    "",
    "",
    "        PLEASURE PANTS PAUL",
    "",
    "     a text-parser adventure in",
    "      sixteen glorious colours",
    "",
    "",
    f"           version {__version__}",
    "",
    "",
    "",
    "        press any key to begin",
]

ARROWS = {
    pygame.K_UP: 1,
    pygame.K_RIGHT: 3,
    pygame.K_DOWN: 5,
    pygame.K_LEFT: 7,
    pygame.K_KP8: 1,
    pygame.K_KP9: 2,
    pygame.K_KP6: 3,
    pygame.K_KP3: 4,
    pygame.K_KP2: 5,
    pygame.K_KP1: 6,
    pygame.K_KP4: 7,
    pygame.K_KP7: 8,
    pygame.K_PAGEUP: 2,
    pygame.K_PAGEDOWN: 4,
    pygame.K_END: 6,
    pygame.K_HOME: 8,
}


class State(Enum):
    TITLE = auto()
    QUIZ = auto()
    PLAY = auto()
    REJECTED = auto()


class App:
    def __init__(self, scale: int, skip_quiz: bool) -> None:
        pygame.init()
        pygame.display.set_caption("Pleasure Pants Paul")
        self.scale = scale
        self.window = pygame.display.set_mode((SCREEN_W * scale, SCREEN_H * scale))
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.state = State.QUIZ if skip_quiz else State.TITLE
        self.quiz = Quiz()
        self.game = Game()
        register(self.game)
        self.input = ""
        self.ticks = 0
        self.running = True
        if skip_quiz:
            self.start_game()

    # -- state transitions ------------------------------------------------

    def start_quiz(self) -> None:
        self.quiz.start()
        self.state = State.QUIZ

    def start_game(self) -> None:
        self.game.new_room(START_ROOM)
        self.state = State.PLAY
        pygame.key.start_text_input()

    # -- events -------------------------------------------------------------

    def handle_event(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.QUIT:
            self.running = False
            return
        if self.state == State.TITLE:
            if ev.type == pygame.KEYDOWN:
                self.start_quiz()
        elif self.state == State.QUIZ:
            self.handle_quiz_key(ev)
        elif self.state == State.REJECTED:
            if ev.type == pygame.KEYDOWN:
                self.running = False
        elif self.state == State.PLAY:
            self.handle_play_event(ev)

    def handle_quiz_key(self, ev: pygame.event.Event) -> None:
        if ev.type != pygame.KEYDOWN:
            return
        mods = pygame.key.get_mods()
        if ev.key == pygame.K_x and mods & (pygame.KMOD_ALT | pygame.KMOD_META):
            self.quiz.skip()
        elif self.quiz.feedback is not None:
            self.quiz.next()
        elif ev.unicode and ev.unicode.lower() in "abcd":
            self.quiz.answer(ev.unicode)
        if self.quiz.done:
            if self.quiz.passed:
                self.start_game()
            else:
                self.state = State.REJECTED

    def handle_play_event(self, ev: pygame.event.Event) -> None:
        game = self.game
        if game.message is not None:
            if ev.type == pygame.KEYDOWN:
                game.dismiss()
            return
        if ev.type == pygame.TEXTINPUT:
            if len(self.input) < 38:
                self.input += ev.text
        elif ev.type == pygame.KEYDOWN:
            if ev.key in ARROWS and not self.input:
                game.ego.set_direction(ARROWS[ev.key])
            elif ev.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                text, self.input = self.input, ""
                game.ego.stop()
                game.handle_input(text)
            elif ev.key == pygame.K_ESCAPE:
                self.input = ""

    # -- drawing ------------------------------------------------------------

    def draw(self) -> None:
        if self.state == State.TITLE:
            draw_text_screen(self.screen, TITLE_LINES, fg=YELLOW, bg=BLACK, top=0)
        elif self.state == State.QUIZ:
            draw_text_screen(self.screen, self.quiz.lines(), fg=WHITE, bg=BLACK)
        elif self.state == State.REJECTED:
            draw_text_screen(
                self.screen,
                [
                    "",
                    "",
                    "  Sorry, kid. Come back when you can",
                    "  fill out a tax return.",
                    "",
                    "",
                    "  Press any key to leave.",
                ],
            )
        else:
            self.draw_play()
        pygame.transform.scale(self.screen, self.window.get_size(), self.window)
        pygame.display.flip()

    def draw_play(self) -> None:
        game = self.game
        assert game.pic is not None
        self.screen.fill(PALETTE[BLACK])
        frame = game.pic.visual.copy()
        game.ego.draw(frame, game.pic)
        pygame.transform.scale(
            frame, (PIC_W * 2, PIC_H), self.screen.subsurface(pygame.Rect(0, PIC_TOP, PIC_W * 2, PIC_H))
        )
        draw_status(self.screen, game)
        draw_prompt(self.screen, self.input, blink=(self.ticks // 15) % 2 == 0)
        if game.message is not None:
            draw_message(self.screen, game.message)

    # -- loop ---------------------------------------------------------------

    def run(self) -> None:
        cycle_ms = 1000 / CYCLES_PER_SEC
        acc = 0.0
        while self.running and not self.game.quit_requested:
            dt = self.clock.tick(60)
            self.ticks += 1
            for ev in pygame.event.get():
                self.handle_event(ev)
            if self.state == State.PLAY:
                acc += dt
                while acc >= cycle_ms:
                    acc -= cycle_ms
                    self.game.cycle()
            self.draw()
        pygame.quit()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ppp", description="Pleasure Pants Paul")
    ap.add_argument("--scale", type=int, default=3, help="integer window scale (default 3)")
    ap.add_argument("--skip-quiz", action="store_true", help="skip the title and age quiz")
    args = ap.parse_args(argv)
    App(scale=max(1, args.scale), skip_quiz=args.skip_quiz).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
