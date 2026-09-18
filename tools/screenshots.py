"""Regenerate the README screenshots headlessly: uv run python tools/screenshots.py"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from ppp.cab import CAB_STOP_X  # noqa: E402
from ppp.main import App, State  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "images"
SCALE = 2


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ["PPP_SAVE_DIR"] = str(OUT.parent / ".saves-tmp")
    app = App(scale=1, skip_quiz=False)
    game = app.game

    def shot(name: str) -> None:
        app.draw()
        w, h = app.screen.get_size()
        pygame.image.save(pygame.transform.scale(app.screen, (w * SCALE, h * SCALE)), str(OUT / f"{name}.png"))
        print("wrote", name)

    def key(k: int) -> None:
        app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode=""))

    def cmd(text: str, dismiss: bool = True) -> None:
        for ch in text:
            app.handle_event(pygame.event.Event(pygame.TEXTINPUT, text=ch))
        key(pygame.K_RETURN)
        if dismiss:
            key(pygame.K_SPACE)

    def cycles(n: int) -> None:
        for _ in range(n):
            game.messages.clear()
            game.cycle()

    shot("title")
    app.quiz.start(random.Random(4))
    app.state = State.QUIZ
    shot("quiz")
    app.start_game()
    game.messages.clear()
    shot("street")
    cmd("look at sign", dismiss=False)
    shot("message")
    key(pygame.K_SPACE)
    key(pygame.K_ESCAPE)
    shot("menu")
    key(pygame.K_ESCAPE)
    cmd("call a cab")
    cycles(60)
    game.ego.x, game.ego.y = 60, 134
    shot("street-cab")
    game.ego.x = CAB_STOP_X + 12
    cmd("get in cab")
    shot("taxi")
    cmd("store")
    cmd("pay driver")
    cmd("get out")
    game.messages.clear()
    game.ego.x, game.ego.y = 40, 130
    cycles(12)
    shot("store-street")
    game.ego.x, game.ego.y = 76, 120
    game.ego.set_direction(1)
    cycles(4)
    game.messages.clear()
    game.ego.x, game.ego.y = 80, 112
    shot("store")
    cmd("buy protection")
    key(pygame.K_SPACE)
    shot("store-pricecheck")
    key(pygame.K_SPACE)
    cmd("buy wine")
    cmd("buy magazine")
    game.new_room(19)
    game.messages.clear()
    game.ego.x, game.ego.y = 40, 130
    shot("disco-street")
    game.ego.x, game.ego.y = 100, 126
    cmd("give magazine to doorman")
    game.ego.x, game.ego.y = 76, 120
    game.ego.set_direction(1)
    cycles(4)
    game.messages.clear()
    game.give("candy")
    game.ego.x, game.ego.y = 30, 140
    cmd("give chocolates to ginger")
    cmd("give wine to ginger")
    cmd("dance with ginger")
    cycles(20)
    shot("disco")
    game.new_room(10)
    game.messages.clear()
    game.ego.x, game.ego.y = 76, 128
    game.ego.set_direction(1)
    cycles(14)
    game.messages.clear()
    game.ego.x, game.ego.y = 60, 108
    shot("bar")
    cmd("buy whiskey")
    game.ego.x, game.ego.y = 116, 108
    cmd("give whiskey to drunk")
    game.ego.x, game.ego.y = 144, 104
    game.ego.set_direction(1)
    cycles(6)
    game.messages.clear()
    game.ego.x, game.ego.y = 90, 130
    shot("mensroom")
    cmd("read graffiti")
    cmd("read graffiti")
    cmd("read graffiti", dismiss=False)
    shot("mensroom-graffiti")
    key(pygame.K_SPACE)
    game.new_room(12)
    game.ego.x, game.ego.y = 40, 112
    cmd("search dumpster")
    cmd("get rose")
    shot("alley")
    game.ego.x, game.ego.y = 104, 108
    cmd("rooster sent me")
    game.ego.set_direction(1)
    cycles(8)
    game.messages.clear()
    game.ego.x, game.ego.y = 100, 140
    shot("backroom")
    cmd("use remote", dismiss=False)
    shot("backroom-remote")
    key(pygame.K_SPACE)
    game.ego.x, game.ego.y = 140, 100
    cmd("climb stairs")
    game.messages.clear()
    game.ego.x, game.ego.y = 60, 130
    shot("upstairs")
    game.ego.x, game.ego.y = 116, 112
    cmd("give rose to dolores", dismiss=False)
    shot("upstairs-rose")
    key(pygame.K_SPACE)
    game.new_room(12)
    game.messages.clear()
    game.ego.x, game.ego.y = 40, 112
    cmd("kick the dog")
    shot("death")
    game.messages.clear()
    game.ego.x, game.ego.y = 8, 150
    cycles(0)
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
