import pygame
import pytest

from ppp.game import Game
from ppp.rooms import START_ROOM, register
from ppp.rooms.street import CAB_STOP_X, Street


@pytest.fixture
def game(tmp_path, monkeypatch) -> Game:
    monkeypatch.setenv("PPP_SAVE_DIR", str(tmp_path))
    pygame.init()
    g = Game()
    register(g)
    g.new_room(START_ROOM)
    return g


def drain(game: Game) -> list[str]:
    out = list(game.messages)
    game.messages.clear()
    return out


def run(game: Game, cycles: int) -> None:
    for _ in range(cycles):
        game.messages.clear()
        game.cycle()


def test_street_to_alley_and_back(game: Game) -> None:
    game.ego.x, game.ego.y = 4, 150
    game.ego.set_direction(7)
    run(game, 12)
    assert game.room is not None and game.room.number == 12
    assert game.ego.y == 150
    game.ego.set_direction(3)
    run(game, 40)
    assert game.room.number == 10


def test_alley_rose(game: Game) -> None:
    game.new_room(12)
    game.handle_input("get rose")
    assert "What rose" in (game.message or "")
    drain(game)
    game.handle_input("search dumpster")
    assert "rose" in (game.message or "")
    drain(game)
    game.ego.x, game.ego.y = 40, 112
    game.handle_input("take the rose")
    assert game.has("rose") and game.score == 2
    game.handle_input("get rose")
    assert game.score == 2


def test_alley_mugger_kills_after_lingering(game: Game) -> None:
    game.new_room(12)
    run(game, 499)
    assert not game.dead
    game.cycle()
    assert game.dead
    game.handle_input("look")  # dead men type nothing
    assert game.message and "alley" in game.message


def test_kick_dog_is_fatal(game: Game) -> None:
    game.new_room(12)
    game.handle_input("kick dog")
    assert game.dead


def test_cab_arrives_and_leaves_if_ignored(game: Game) -> None:
    street = game.room
    assert isinstance(street, Street)
    game.handle_input("call a cab")
    assert street.cab_state == "arriving" and game.score == 1
    drain(game)
    run(game, 60)
    assert street.cab_state == "waiting" and street.cab_x == CAB_STOP_X
    assert street.objects(game)
    run(game, 301)
    assert street.cab_state == "leaving"
    run(game, 80)
    assert street.cab_state == "none" and not street.objects(game)


def test_cab_ride_pay_and_exit(game: Game) -> None:
    street = game.room
    assert isinstance(street, Street)
    game.vars["money"] = 20
    game.handle_input("hail taxi")
    run(game, 60)
    game.ego.x, game.ego.y = CAB_STOP_X + 10, 140
    game.handle_input("get in the cab")
    assert game.room is not None and game.room.number == 13
    assert game.ego.frozen
    drain(game)
    game.handle_input("get out")
    assert game.room.number == 10  # no ride yet: he lets you go
    game.new_room(13)
    drain(game)
    game.handle_input("take me to the casino")
    assert game.vars["fare"] == 5
    drain(game)
    game.handle_input("get out")
    assert game.room.number == 13 and "lock" in (game.message or "")
    drain(game)
    game.handle_input("pay the driver")
    assert game.vars["money"] == 15 and game.vars["fare"] == 0
    drain(game)
    game.handle_input("exit")
    assert game.room.number == 10 and not game.ego.frozen
    assert street.cab_state == "leaving"
    assert (game.ego.x, game.ego.y) == (100, 136)


def test_cab_throws_you_out_when_broke(game: Game) -> None:
    game.vars["money"] = 2
    game.new_room(13)
    drain(game)
    game.handle_input("disco")
    game.handle_input("pay")
    assert game.room is not None and game.room.number == 10
    assert game.vars["money"] == 2


def test_traffic_is_fatal(game: Game) -> None:
    game.ego.x, game.ego.y = 60, 160
    run(game, 45)
    assert game.dead


def test_restore_revives(game: Game) -> None:
    from ppp import save

    path = save.write(game, "alive")
    game.die("test")
    assert game.dead
    save.apply(game, save.read(path))
    assert not game.dead and game.message is None
