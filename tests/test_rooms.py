import pygame
import pytest

from ppp.cab import CAB_STOP_X
from ppp.game import Game
from ppp.rooms import START_ROOM, register
from ppp.rooms.street import Street


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
    assert street.curb.state == "arriving" and game.score == 1
    drain(game)
    run(game, 60)
    assert street.curb.state == "waiting" and street.curb.x == CAB_STOP_X
    assert street.objects(game)
    run(game, 301)
    assert street.curb.state == "leaving"
    run(game, 80)
    assert street.curb.state == "none" and not street.objects(game)


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
    assert street.curb.state == "leaving"
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


def test_bar_door_leads_to_mens_room_and_back(game: Game) -> None:
    game.new_room(11)
    drain(game)
    game.ego.x, game.ego.y = 144, 104
    game.ego.set_direction(1)
    run(game, 6)
    assert game.room is not None and game.room.number == 14
    game.ego.x, game.ego.y = 76, 166
    game.ego.set_direction(5)
    run(game, 6)
    assert game.room.number == 11
    assert game.ego.x == 145 and game.ego.y >= 104  # spawned at the MEN door, still walking


def test_graffiti_cycles_and_teaches_the_password(game: Game) -> None:
    from ppp.rooms.mensroom import GRAFFITI, PASSWORD_LINE

    game.new_room(14)
    drain(game)
    seen: list[str] = []
    for _ in range(len(GRAFFITI)):
        game.handle_input("read graffiti")
        seen.append(drain(game)[0])
    for line in GRAFFITI:
        assert any(line in s for s in seen)
    assert game.flags["knows_password"] and game.score == 2
    game.handle_input("read the wall")
    assert GRAFFITI[0] in drain(game)[0]  # wraps around
    game.handle_input("read graffiti")
    game.handle_input("read graffiti")
    game.handle_input("read graffiti")
    assert game.score == 2  # the password only scores once
    assert PASSWORD_LINE == 2


def test_password_opens_the_alley_door(game: Game) -> None:
    game.new_room(12)
    game.ego.x, game.ego.y = 104, 112
    game.handle_input("knock on door")
    assert "Password" in drain(game)[0]
    game.handle_input("say rooster sent me")
    assert game.flags.get("backdoor_open") and game.score == 5
    assert "Bolts clank" in drain(game)[0]
    game.handle_input("rooster sent me")
    assert "heard you" in drain(game)[0]
    game.ego.x = 20
    game.new_room(12)
    game.ego.x = 20
    game.handle_input("rooster sent me")
    assert "literal" in drain(game)[0]


def test_drinking_from_the_urinal_is_fatal(game: Game) -> None:
    game.new_room(14)
    game.handle_input("drink water")
    assert game.dead


def test_open_alley_door_leads_to_back_room_and_brick_ejects(game: Game) -> None:
    game.new_room(12)
    game.ego.x, game.ego.y = 104, 108
    game.handle_input("enter door")
    assert game.room is not None and game.room.number == 12  # still locked
    game.handle_input("rooster sent me")
    drain(game)
    game.ego.set_direction(1)
    run(game, 8)
    assert game.room.number == 15
    drain(game)
    game.ego.x, game.ego.y = 140, 100
    game.ego.set_direction(1)
    run(game, 6)
    assert game.room.number == 12  # posted back through the door
    assert (game.ego.x, game.ego.y) == (104, 110)


def test_remote_distracts_brick_and_stairs_score(game: Game) -> None:
    game.flags["backdoor_open"] = True
    game.new_room(15)
    drain(game)
    game.handle_input("use remote")
    assert not game.flags.get("brick_distracted")  # no remote yet
    game.give("remote")
    game.handle_input("change channel")
    assert game.flags["brick_distracted"] and game.score == 4
    game.handle_input("use remote")
    assert game.score == 4
    drain(game)
    game.ego.x, game.ego.y = 140, 100
    frames = game.room.objects(game) if game.room else []
    assert len(frames) == 2
    game.handle_input("climb the stairs")
    assert game.room is not None and game.room.number == 16 and game.score == 9
    assert "thirty dollars" in drain(game)[0]


def test_touching_brick_is_fatal(game: Game) -> None:
    game.new_room(15)
    game.handle_input("kiss brick")
    assert game.dead


def upstairs(game: Game) -> Game:
    game.flags["brick_distracted"] = True
    game.new_room(16)
    drain(game)
    return game


def test_rose_charms_dolores_and_unlocks_the_chocolates(game: Game) -> None:
    upstairs(game)
    game.ego.x, game.ego.y = 72, 110
    game.handle_input("get candy")
    assert "mine" in drain(game)[0] and not game.has("candy")
    game.give("rose")
    game.ego.x = 104
    game.handle_input("give rose to dolores")
    assert game.flags["rose_given"] and not game.has("rose") and game.score == 2
    game.ego.x = 72
    game.handle_input("take the chocolates")
    assert game.has("candy") and game.score == 5


def test_unprotected_business_is_fatal(game: Game) -> None:
    upstairs(game)
    game.ego.x, game.ego.y = 104, 110
    game.handle_input("kiss dolores")
    assert "Business first" in drain(game)[0]
    game.vars["money"] = 20
    game.handle_input("pay dolores")
    assert "adorable" in drain(game)[0]
    game.vars["money"] = 40
    game.handle_input("pay her")
    assert game.flags["dolores_paid"] and game.vars["money"] == 10
    drain(game)
    game.handle_input("kiss dolores")
    assert game.dead
    assert game.room is not None and not game.room.objects(game)  # she has gone


def test_protected_business_scores(game: Game) -> None:
    upstairs(game)
    game.ego.x, game.ego.y = 104, 110
    game.vars["money"] = 40
    game.give("protection")
    game.handle_input("pay")
    game.handle_input("make love to dolores")
    assert not game.dead and game.score == 15 and not game.has("protection")
    assert game.ego.visible


def test_window_drops_into_the_alley(game: Game) -> None:
    upstairs(game)
    game.handle_input("climb out the window")
    assert game.room is not None and game.room.number == 12
    assert (game.ego.x, game.ego.y) == (136, 112)


def test_stairs_down_return_to_the_back_room(game: Game) -> None:
    upstairs(game)
    game.ego.x, game.ego.y = 60, 166
    game.ego.set_direction(5)
    run(game, 4)
    assert game.room is not None and game.room.number == 15
    assert game.ego.x == 134


def test_cab_drives_to_the_store_and_back(game: Game) -> None:
    game.vars["money"] = 40
    game.new_room(13)
    drain(game)
    game.handle_input("take me to the store")
    assert game.vars["fare"] == 5 and game.vars["cab_dest"] == 17
    game.handle_input("pay")
    game.handle_input("get out")
    assert game.room is not None and game.room.number == 17
    street = game.room
    assert street.objects(game)  # the cab is pulling away from this curb
    drain(game)
    game.handle_input("call a cab")
    run(game, 60)
    game.ego.x, game.ego.y = CAB_STOP_X + 10, 140
    game.handle_input("get in the cab")
    assert game.room.number == 13
    drain(game)
    game.handle_input("store")
    assert game.vars["fare"] == 3  # around the block
    game.handle_input("pay")
    drain(game)
    game.handle_input("rooster's")
    assert game.vars["fare"] == 5 and game.vars["cab_dest"] == 10
    game.handle_input("pay")
    game.handle_input("get out")
    assert game.room.number == 10


def test_store_purchases(game: Game) -> None:
    game.vars["money"] = 20
    game.new_room(18)
    drain(game)
    game.handle_input("buy protection")
    assert "counter" in drain(game)[0]
    game.ego.x, game.ego.y = 80, 110
    game.handle_input("buy protection")
    msgs = drain(game)
    assert game.has("protection") and game.score == 3 and game.vars["money"] == 15
    assert len(msgs) == 3 and "PRICE CHECK" in msgs[2]
    game.handle_input("buy wine")
    assert game.has("wine") and game.vars["money"] == 7
    game.handle_input("buy a magazine")
    assert game.has("magazine") and game.vars["money"] == 4 and game.score == 5
    drain(game)
    game.handle_input("buy wine")
    assert "already" in drain(game)[0]
    game.vars["money"] = 0
    game.take("wine")
    game.handle_input("buy wine")
    assert "$8" in drain(game)[0] and not game.has("wine")


def test_shoplifting_is_fatal(game: Game) -> None:
    game.new_room(18)
    game.handle_input("get wine")
    assert game.dead


def test_store_street_door_and_phone(game: Game) -> None:
    game.new_room(17)
    drain(game)
    game.ego.x, game.ego.y = 76, 120
    game.ego.set_direction(1)
    run(game, 4)
    assert game.room is not None and game.room.number == 18
    game.ego.x, game.ego.y = 76, 166
    game.ego.set_direction(5)
    run(game, 4)
    assert game.room.number == 17
    game.ego.x, game.ego.y = 16, 126
    game.ego.stop()
    game.handle_input("use phone")
    assert "sticky" in drain(game)[0]


def test_protection_from_the_store_survives_dolores(game: Game) -> None:
    game.vars["money"] = 60
    game.new_room(18)
    game.ego.x, game.ego.y = 80, 110
    game.handle_input("buy protection")
    upstairs(game)
    game.ego.x, game.ego.y = 104, 110
    game.handle_input("pay")
    game.handle_input("kiss dolores")
    assert not game.dead and game.score == 18
