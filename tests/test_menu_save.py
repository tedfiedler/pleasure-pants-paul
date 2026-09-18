import pygame
import pytest

from ppp import save
from ppp.dialog import ConfirmDialog, ListDialog, TextDialog
from ppp.game import Game
from ppp.menu import MENUS, MenuBar
from ppp.rooms import START_ROOM, register


def key(k: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="")


def text(t: str) -> pygame.event.Event:
    return pygame.event.Event(pygame.TEXTINPUT, text=t)


@pytest.fixture
def game(tmp_path, monkeypatch) -> Game:
    monkeypatch.setenv("PPP_SAVE_DIR", str(tmp_path))
    pygame.init()
    g = Game()
    register(g)
    g.new_room(START_ROOM)
    return g


def test_menu_navigation_returns_actions() -> None:
    bar = MenuBar()
    bar.show()
    assert bar.open
    assert bar.handle_key(pygame.K_RIGHT) is None
    assert bar.menu == 1
    bar.handle_key(pygame.K_DOWN)
    assert bar.handle_key(pygame.K_RETURN) == MENUS[1].items[1].action
    assert not bar.open
    bar.show()
    bar.handle_key(pygame.K_LEFT)
    assert bar.menu == len(MENUS) - 1
    bar.handle_key(pygame.K_ESCAPE)
    assert not bar.open


def test_menu_actions_are_unique_and_known() -> None:
    actions = [it.action for m in MENUS for it in m.items]
    assert len(actions) == len(set(actions))
    assert {"save", "restore", "restart", "quit", "sound"} <= set(actions)


def test_save_and_restore_roundtrip(game: Game) -> None:
    game.new_room(11)
    game.dismiss()
    game.ego.x, game.ego.y = 60, 108
    game.handle_input("buy whiskey")
    game.ego.x, game.ego.y = 130, 108
    game.handle_input("give whiskey to drunk")
    game.set_speed("fast")
    game.ego.x, game.ego.y = 100, 140
    path = save.write(game, "at the bar")
    assert path.exists()

    fresh = Game()
    register(fresh)
    fresh.new_room(START_ROOM)
    saves = save.list_saves()
    assert [s.description for s in saves] == ["at the bar"]
    save.apply(fresh, save.read(saves[0].path))
    assert fresh.room is not None and fresh.room.number == 11
    assert (fresh.ego.x, fresh.ego.y) == (100, 140)
    assert fresh.score == 6 and fresh.has("remote")
    assert fresh.vars["money"] == 84
    assert fresh.speed == "fast"
    assert fresh.message is None  # restoring is silent
    # the puzzle stays solved after restore: no double scoring
    fresh.handle_input("buy whiskey")
    fresh.handle_input("give whiskey to drunk")
    assert fresh.score == 6


def test_save_list_is_newest_first_and_capped(game: Game) -> None:
    for i in range(save.MAX_SAVES + 3):
        save.write(game, f"save {i}")
    saves = save.list_saves()
    assert len(saves) == save.MAX_SAVES
    assert saves[0].description == f"save {save.MAX_SAVES + 2}"


def test_parser_requests_menu_actions(game: Game) -> None:
    game.handle_input("save game")
    assert game.request == "save"
    game.handle_input("quit")
    assert game.request == "quit"


def test_dialogs() -> None:
    picked: list[int] = []
    d = ListDialog("pick", ["a", "b", "c"], picked.append)
    d.handle(key(pygame.K_UP))
    assert d.lines()[1] == 2 + 2
    assert d.handle(key(pygame.K_RETURN)) and picked == [2]

    got: list[str] = []
    t = TextDialog("name?", got.append)
    assert not t.handle(key(pygame.K_RETURN))  # empty text is not accepted
    t.handle(text("hi"))
    t.handle(text("!"))
    t.handle(key(pygame.K_BACKSPACE))
    assert t.handle(key(pygame.K_RETURN)) and got == ["hi"]

    fired: list[bool] = []
    c = ConfirmDialog("sure?", "quit", lambda: fired.append(True))
    assert c.handle(key(pygame.K_ESCAPE)) and not fired
    assert c.handle(key(pygame.K_RETURN)) and fired == [True]
