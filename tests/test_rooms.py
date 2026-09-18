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
    game.handle_input("take me to the chapel")
    assert game.vars["fare"] == 5 and game.vars["cab_dest"] == 23
    drain(game)
    game.handle_input("get out")
    assert game.room.number == 13 and "lock" in (game.message or "")
    drain(game)
    game.handle_input("pay the driver")
    assert game.vars["money"] == 15 and game.vars["fare"] == 0
    drain(game)
    game.handle_input("exit")
    assert game.room.number == 23 and not game.ego.frozen
    assert street.curb.state != "waiting"  # the cab left Rooster's with Paul in it
    chapel_street = game.room
    assert chapel_street.objects(game)  # and is pulling away from the chapel curb
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


def test_doorman_needs_the_magazine(game: Game) -> None:
    game.new_room(19)
    drain(game)
    game.ego.x, game.ego.y = 76, 120
    game.ego.set_direction(1)
    run(game, 4)
    assert game.room is not None and game.room.number == 19
    game.ego.x, game.ego.y = 100, 126
    game.handle_input("give magazine to doorman")
    assert "don't have" in drain(game)[0]
    game.give("magazine")
    game.handle_input("give magazine to doorman")
    assert game.flags["disco_admitted"] and game.score == 2 and not game.has("magazine")
    drain(game)
    game.ego.x, game.ego.y = 76, 120
    game.ego.set_direction(1)
    run(game, 4)
    assert game.room.number == 20


def test_cab_reaches_the_disco(game: Game) -> None:
    game.vars["money"] = 20
    game.new_room(13)
    drain(game)
    game.handle_input("disco")
    game.handle_input("pay")
    game.handle_input("get out")
    assert game.room is not None and game.room.number == 19


def test_wooing_ginger_in_order(game: Game) -> None:
    game.new_room(20)
    drain(game)
    game.ego.x, game.ego.y = 30, 140
    game.give("wine")
    game.give("candy")
    game.handle_input("give wine to ginger")
    assert "right order" in drain(game)[0] and game.has("wine")
    game.handle_input("dance with ginger")
    assert "reason" in drain(game)[0]
    game.handle_input("give chocolates to her")
    assert game.flags["ginger_candy"] and game.score == 3
    game.handle_input("give her the wine")
    assert game.flags["ginger_wine"] and game.score == 5
    drain(game)
    game.handle_input("dance with ginger")
    room = game.room
    assert room is not None and game.ego.frozen
    from ppp.rooms.disco import DANCE_CYCLES, Disco

    assert isinstance(room, Disco) and room.dance_timer == DANCE_CYCLES
    drain(game)
    run(game, DANCE_CYCLES)
    assert game.flags["ginger_danced"] and game.score == 10 and not game.ego.frozen
    assert "ring" in (game.message or "")
    drain(game)
    game.ego.x, game.ego.y = 30, 140  # back to her table after the song
    game.handle_input("talk to ginger")
    assert "chapel" in drain(game)[0]
    game.handle_input("dance with her")
    assert "rule" in drain(game)[0]


def test_ladies_room_is_fatal(game: Game) -> None:
    game.new_room(20)
    game.ego.x, game.ego.y = 110, 104
    game.handle_input("enter door")
    assert game.dead


def test_parser_numbers() -> None:
    from ppp.parser import parse

    p = parse("bet 20 dollars")
    assert p.words == ["bet", "number", "money"] and p.number == 20 and p.unknown is None


def test_cab_reaches_the_casino(game: Game) -> None:
    game.vars["money"] = 20
    game.new_room(13)
    game.handle_input("casino")
    game.handle_input("pay")
    game.handle_input("get out")
    assert game.room is not None and game.room.number == 21
    drain(game)
    game.ego.x, game.ego.y = 80, 120
    game.ego.set_direction(1)
    run(game, 4)
    assert game.room.number == 22


def test_slots_pay_and_charge(game: Game) -> None:
    import random

    game.rng = random.Random(3)
    game.new_room(22)
    drain(game)
    game.handle_input("pull lever")
    assert "left wall" in drain(game)[0]
    game.ego.x, game.ego.y = 30, 110
    game.vars["money"] = 100
    for _ in range(40):
        game.handle_input("pull the lever")
    assert game.vars["money"] != 100
    assert game.score in (0, 1)
    game.vars["money"] = 2
    game.handle_input("play slots")
    assert "sorry" in drain(game)[-1]


def test_blackjack_hand(game: Game) -> None:
    from ppp.rooms.casino import Casino, hand_value

    assert hand_value(["As", "Kd"]) == 21
    assert hand_value(["As", "9d", "5c"]) == 15
    assert hand_value(["Ks", "Qd", "2c"]) == 22
    import random

    game.rng = random.Random(1)
    game.new_room(22)
    room = game.room
    assert isinstance(room, Casino)
    game.ego.x, game.ego.y = 88, 110
    game.vars["money"] = 50
    drain(game)
    game.handle_input("bet 10")
    assert "Sit at the blackjack" in drain(game)[0]
    game.handle_input("play blackjack")
    assert room.bj is not None
    drain(game)
    game.handle_input("bet 500")
    assert "Five to a hundred" in drain(game)[0]
    game.handle_input("bet 20")
    assert game.vars["money"] == 50  # the stake only moves when the hand settles
    # rig the hand: player 20, dealer 17, then stand
    room.bj.update({"bet": 20, "player": ["Kd", "Qs"], "dealer": ["7h", "Kc"], "deck": ["2c", "2d"]})
    drain(game)
    game.handle_input("stand")
    assert game.vars["money"] == 70 and game.score == 2
    drain(game)
    game.handle_input("bet 10")
    room.bj.update({"bet": 10, "player": ["Kd", "9s"], "dealer": ["7h", "Kc"], "deck": ["2d", "5c"]})
    game.handle_input("hit")
    assert game.vars["money"] == 60 and "Bust" in drain(game)[-1]
    # a natural against a dealer 21 is a push; against anything else pays 3:2 rounded up
    room.bj.update({"bet": 15, "player": ["As", "Kd"], "dealer": ["Ah", "Qc"], "deck": ["2c"]})
    room._settle(game, natural=True)
    assert game.vars["money"] == 60 and "push" in drain(game)[-1].lower()
    room.bj.update({"bet": 15, "player": ["As", "Kd"], "dealer": ["7h", "6c"], "deck": ["2c"]})
    room._settle(game, natural=True)
    assert game.vars["money"] == 83 and "7h 6c" in drain(game)[-1]  # dealer did not draw
    # walking out mid-hand costs nothing
    game.handle_input("bet 50")
    game.ego.x, game.ego.y = 80, 166
    game.ego.set_direction(5)
    run(game, 4)
    assert game.room is not None and game.room.number == 21 and game.vars["money"] == 83
    game.new_room(22)
    assert room.bj is None
    game.ego.x, game.ego.y = 88, 110
    game.handle_input("play blackjack")
    game.handle_input("bet 10")
    drain(game)
    game.handle_input("leave")
    assert "Finish the hand" in drain(game)[0]
    game.handle_input("stand")
    game.handle_input("leave")
    assert room.bj is None


def test_ring_costs_250(game: Game) -> None:
    game.new_room(22)
    game.ego.x, game.ego.y = 136, 110
    game.vars["money"] = 100
    game.handle_input("buy ring")
    assert not game.has("ring")
    game.vars["money"] = 300
    game.handle_input("buy the ring")
    assert game.has("ring") and game.vars["money"] == 50 and game.score == 5


def test_stealing_chips_is_fatal_only_at_the_table(game: Game) -> None:
    game.new_room(22)
    game.ego.x, game.ego.y = 30, 130
    game.handle_input("take winnings")
    assert not game.dead and "in your pocket" in drain(game)[-1]
    game.handle_input("cash out")
    assert not game.dead and "$" in drain(game)[-1]
    game.ego.x, game.ego.y = 88, 110
    game.handle_input("take chips")
    assert game.dead


def test_hit_and_cash_still_reach_the_rooms(game: Game) -> None:
    game.new_room(15)
    game.handle_input("hit brick")
    assert game.dead
    game.dead = False
    game.messages.clear()
    game.new_room(13)
    drain(game)
    game.handle_input("store")
    drain(game)
    game.handle_input("give cash to driver")
    assert game.vars["fare"] == 0
    game.new_room(18)
    drain(game)
    game.handle_input("look at the chips")
    assert "flavour" in drain(game)[0]


def test_typed_entry_at_open_doors(game: Game) -> None:
    game.new_room(21)
    game.ego.x, game.ego.y = 80, 120
    game.handle_input("enter casino")
    assert game.room is not None and game.room.number == 22
    game.new_room(17)
    game.ego.x, game.ego.y = 80, 120
    game.handle_input("open door")
    assert game.room.number == 18


def test_cab_reaches_the_chapel(game: Game) -> None:
    game.vars["money"] = 20
    game.new_room(13)
    game.handle_input("chapel")
    game.handle_input("pay")
    game.handle_input("get out")
    assert game.room is not None and game.room.number == 23
    game.ego.x, game.ego.y = 80, 120
    game.handle_input("enter chapel")
    assert game.room.number == 24


def test_no_bride_no_wedding(game: Game) -> None:
    game.new_room(24)
    assert not game.room.objects(game) if game.room else False
    drain(game)
    game.ego.x, game.ego.y = 80, 110
    game.handle_input("marry ginger")
    assert "Marry whom" in drain(game)[0]
    game.handle_input("pay preacher")
    assert "wishing well" in drain(game)[0]


def test_wedding_needs_fee_and_ring_then_gives_the_key(game: Game) -> None:
    game.flags["ginger_danced"] = True
    game.new_room(24)
    room = game.room
    assert room is not None and room.objects(game)  # Ginger at the altar
    drain(game)
    game.ego.x, game.ego.y = 80, 110
    game.vars["money"] = 100
    game.handle_input("marry ginger")
    assert "Fifty dollars first" in drain(game)[0]
    game.handle_input("pay the preacher")
    assert game.flags["chapel_paid"] and game.vars["money"] == 50
    drain(game)
    game.handle_input("give ring to ginger")
    assert "nothing to put on it" in drain(game)[0]
    game.give("ring")
    game.handle_input("marry her")
    msgs = drain(game)
    assert len(msgs) == 3 and "pronounce" in msgs[2]
    assert game.flags["ginger_married"] and game.has("key") and not game.has("ring")
    assert game.score == 15
    assert not room.objects(game)  # she has gone ahead
    game.ego.x, game.ego.y = 20, 110
    game.handle_input("pull the rope")
    assert game.score == 16
    game.handle_input("pull rope")
    assert game.score == 16
    # she has left the disco too, and the casino elevator knows the key
    game.new_room(20)
    assert game.room is not None and not game.room.objects(game)
    game.new_room(22)
    drain(game)
    game.ego.x, game.ego.y = 46, 110
    game.handle_input("use key")
    assert game.room is not None and game.room.number == 25


def test_collection_box_is_fatal(game: Game) -> None:
    game.new_room(24)
    game.handle_input("take the collection box")
    assert game.dead


def test_elevator_needs_the_key(game: Game) -> None:
    game.new_room(22)
    game.ego.x, game.ego.y = 46, 110
    drain(game)
    game.handle_input("use elevator")
    assert game.room is not None and game.room.number == 22 and "keyhole" in drain(game)[0]
    game.give("key")
    game.handle_input("enter elevator")
    assert game.room.number == 25


def test_honeymoon_robbery_and_escape(game: Game) -> None:
    from ppp.rooms.penthouse import MAID_CYCLES, Penthouse

    game.flags["ginger_married"] = True
    game.give("key")
    game.vars["money"] = 120
    game.new_room(25)
    room = game.room
    assert isinstance(room, Penthouse) and len(room.objects(game)) == 1
    drain(game)
    game.ego.x, game.ego.y = 100, 116
    game.handle_input("kiss ginger")
    msgs = drain(game)
    assert len(msgs) == 3 and "$120" in msgs[2]
    assert game.flags["tied_up"] and game.vars["money"] == 0 and not game.has("key")
    assert game.score == 10 and not game.ego.visible and game.ego.frozen
    game.handle_input("untie rope")
    assert "Scout" in drain(game)[0]
    game.handle_input("get up")
    assert "tied to a bed" in drain(game)[0]
    game.handle_input("read note")
    assert "hands are free" in drain(game)[0]
    game.handle_input("kick the phone")
    assert room.maid_timer == MAID_CYCLES and "Desk" in drain(game)[0]
    game.handle_input("scream")
    assert "on its way" in drain(game)[0]
    run(game, MAID_CYCLES)
    assert game.flags["freed"] and not game.flags["tied_up"] and game.score == 15
    assert game.ego.visible and not game.ego.frozen
    assert "maid" in (game.message or "")
    drain(game)
    game.handle_input("read the note")
    assert game.score == 16 and "stairs" in drain(game)[0]
    assert not room.objects(game)
    # back down, and the elevator is closed to him now
    game.ego.x, game.ego.y = 76, 166
    game.ego.set_direction(5)
    run(game, 4)
    assert game.room is not None and game.room.number == 22
    game.ego.x, game.ego.y = 46, 110
    game.handle_input("use elevator")
    assert "pity" in drain(game)[0]


def test_balcony_is_fatal(game: Game) -> None:
    game.new_room(25)
    game.handle_input("open the balcony door")
    assert game.dead
