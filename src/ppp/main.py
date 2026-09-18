"""Entry point: window, main loop, and the title -> quiz -> play state machine."""

from __future__ import annotations

import argparse
import sys
from enum import Enum, auto

import pygame

from ppp import __version__, save
from ppp.const import BLACK, PALETTE, PIC_H, PIC_TOP, PIC_W, SCREEN_H, SCREEN_W, WHITE, YELLOW
from ppp.dialog import ConfirmDialog, Dialog, ListDialog, TextDialog
from ppp.game import MAX_SCORE, Game
from ppp.menu import SHORTCUTS, MenuBar
from ppp.quiz import Quiz
from ppp.rooms import START_ROOM, register
from ppp.ui import draw_box, draw_message, draw_prompt, draw_status, draw_text_screen

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
    WON = auto()


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
        self.menu = MenuBar()
        self.dialog: Dialog | None = None
        self.pending_death = False  # re-show the death dialog after its message clears
        if skip_quiz:
            self.start_game()

    # -- state transitions ------------------------------------------------

    def start_quiz(self) -> None:
        self.quiz.start(self.game.rng)
        self.state = State.QUIZ

    def start_game(self) -> None:
        self.game.new_room(START_ROOM)
        self.state = State.PLAY
        pygame.key.start_text_input()

    def restart(self) -> None:
        self.game = Game()
        register(self.game)
        self.input = ""
        self.start_game()

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
        elif self.state == State.WON:
            if ev.type == pygame.KEYDOWN:
                self.restart()
                self.state = State.TITLE
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
        if self.dialog is not None:
            if self.dialog.handle(ev):
                self.dialog = None
            return
        if self.menu.open:
            if ev.type == pygame.KEYDOWN:
                action = self.menu.handle_key(ev.key)
                if action:
                    self.do_action(action)
            return
        if game.message is not None:
            if ev.type == pygame.KEYDOWN:
                game.dismiss()
                if game.dead and game.message is None:
                    self.pending_death = False
                    self.death_dialog()
                elif game.flags.get("won") and game.message is None:
                    self.state = State.WON
            return
        if game.dead:
            self.death_dialog()
            return
        if ev.type == pygame.TEXTINPUT:
            if len(self.input) < 38:
                self.input += ev.text
        elif ev.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if ev.key == pygame.K_ESCAPE:
                self.menu.show()
            elif ev.key in SHORTCUTS:
                self.do_action(SHORTCUTS[ev.key])
            elif ev.key == pygame.K_z and mods & (pygame.KMOD_ALT | pygame.KMOD_META):
                self.do_action("quit")
            elif ev.key in ARROWS and not self.input:
                game.ego.set_direction(ARROWS[ev.key])
            elif ev.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                text, self.input = self.input, ""
                game.ego.stop()
                game.handle_input(text)
                self.take_request()

    def take_request(self) -> None:
        """Route a menu-level action the parser asked for (SAVE, QUIT...)."""
        if self.game.request:
            action, self.game.request = self.game.request, None
            self.do_action(action)

    # -- menu actions -------------------------------------------------------

    def do_action(self, action: str) -> None:
        game = self.game
        game.ego.stop()
        if action == "save":
            self.dialog = TextDialog("Enter a description for this game:", self.save_game)
        elif action == "restore":
            saves = save.list_saves()
            if not saves:
                game.print("There are no saved games. Yet. Try F5.")
                if game.dead:
                    self.pending_death = True
            else:
                self.dialog = ListDialog(
                    "Select a game to restore:",
                    [s.description for s in saves],
                    lambda i: self.restore_game(saves[i]),
                )
        elif action == "restart":
            self.dialog = ConfirmDialog("Restart the game from the beginning?", "restart", self.restart)
        elif action == "quit":
            if game.dead:
                self.stop()
            else:
                self.dialog = ConfirmDialog("Leave Paul to his fate?", "quit", self.stop)
        elif action in ("look", "inventory", "score", "help"):
            game.handle_input(action)
        elif action == "sound":
            game.toggle_sound()
        elif action.startswith("speed_"):
            game.set_speed(action.removeprefix("speed_"))
            game.print(f"Speed set to {game.speed}.")

    def ending_lines(self) -> list[str]:
        return [
            "",
            "",
            "",
            "              THE END",
            "",
            "   Paul got the girl, the roof, and",
            "   the hot tub, and kept the suit.",
            "",
            f"   Final score: {self.game.score} of {MAX_SCORE}",
            "",
            "   Thanks for playing",
            "        PLEASURE PANTS PAUL",
            "",
            "",
            "      press any key for the title",
        ]

    def death_dialog(self) -> None:
        choices = ["Restore a saved game", "Restart from the beginning", "Quit"]
        actions = ["restore", "restart", "quit"]
        self.dialog = ListDialog(
            f"Paul is dead. Score: {self.game.score} of {MAX_SCORE}.",
            choices,
            lambda i: self.do_action(actions[i]),
            cancellable=False,
        )

    def save_game(self, description: str) -> None:
        try:
            save.write(self.game, description)
        except OSError as exc:
            self.game.print(f"Couldn't save: {exc}")
        else:
            self.game.print("Game saved. Nothing can hurt you now, except everything.")

    def restore_game(self, info: save.SaveInfo) -> None:
        try:
            save.apply(self.game, save.read(info.path))
        except (OSError, ValueError, KeyError) as exc:
            self.game.print(f"Couldn't restore that game: {exc}")
        else:
            self.game.print(f'Restored "{info.description}". Welcome back, Paul.')

    def stop(self) -> None:
        self.running = False

    # -- drawing ------------------------------------------------------------

    def draw(self) -> None:
        if self.state == State.TITLE:
            draw_text_screen(self.screen, TITLE_LINES, fg=YELLOW, bg=BLACK, top=0)
        elif self.state == State.QUIZ:
            draw_text_screen(self.screen, self.quiz.lines(), fg=WHITE, bg=BLACK)
        elif self.state == State.WON:
            draw_text_screen(self.screen, self.ending_lines(), fg=YELLOW, bg=BLACK, top=0)
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
        assert game.room is not None
        for surf, x, top in game.room.underlays(game):
            frame.blit(surf, (x, top))
        ego_drawn = False
        for surf, x, baseline in sorted(game.room.objects(game), key=lambda o: o[2]):
            if not ego_drawn and baseline > game.ego.y:
                game.ego.draw(frame, game.pic)
                ego_drawn = True
            frame.blit(surf, (x, baseline - surf.get_height() + 1))
        if not ego_drawn:
            game.ego.draw(frame, game.pic)
        pygame.transform.scale(
            frame, (PIC_W * 2, PIC_H), self.screen.subsurface(pygame.Rect(0, PIC_TOP, PIC_W * 2, PIC_H))
        )
        draw_status(self.screen, game)
        draw_prompt(self.screen, self.input, blink=(self.ticks // 15) % 2 == 0)
        if self.dialog is not None:
            lines, highlight = self.dialog.lines()
            draw_box(self.screen, lines, highlight)
        elif game.message is not None:
            draw_message(self.screen, game.message)
        if self.menu.open:
            self.menu.draw(self.screen)

    # -- loop ---------------------------------------------------------------

    def run(self) -> None:
        acc = 0.0
        while self.running:
            dt = self.clock.tick(60)
            self.ticks += 1
            for ev in pygame.event.get():
                self.handle_event(ev)
            if self.state == State.PLAY and self.dialog is None and not self.menu.open:
                cycle_ms = 1000 / self.game.cycles_per_sec
                acc += dt
                while acc >= cycle_ms:
                    acc -= cycle_ms
                    self.game.cycle()
            else:
                acc = 0.0
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
