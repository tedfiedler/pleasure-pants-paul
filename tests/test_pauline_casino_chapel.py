"""Pauline's game in the casino and the chapel: the same puzzles, the mirror-image cast."""

import random
import re

import pygame
import pytest

from ppp.game import Game
from ppp.pic import Picture
from ppp.rooms import START_ROOM, register
from ppp.rooms.chapel import Chapel

ROOMS = (21, 22, 23, 24)
LEFTOVER = re.compile(r"\[[^\[\]]*\|[^\[\]]*\]")  # an unrendered [x|y]
PAUL_ONLY = re.compile(r"\b(Paul|Ginger|Dolores|Hope|Dawn|Brick)\b")


def make(tmp_path, monkeypatch, pauline: bool) -> Game:
    monkeypatch.setenv("PPP_SAVE_DIR", str(tmp_path))
    pygame.init()
    g = Game(pauline=pauline)
    register(g)
    g.new_room(START_ROOM)
    return g


@pytest.fixture
def pauline(tmp_path, monkeypatch) -> Game:
    return make(tmp_path, monkeypatch, True)


@pytest.fixture
def paul(tmp_path, monkeypatch) -> Game:
    return make(tmp_path, monkeypatch, False)


def drain(game: Game) -> list[str]:
    out = list(game.messages)
    game.messages.clear()
    return out


@pytest.mark.parametrize("number", ROOMS)
def test_room_text_is_fully_mirrored(pauline: Game, number: int) -> None:
    pauline.new_room(number)
    room = pauline.room
    assert room is not None
    drain(pauline)
    pauline.handle_input("look")
    for noun in room.looks:
        pauline.print(room.looks[noun])
    for text in drain(pauline):
        assert not LEFTOVER.search(text), text
        assert not PAUL_ONLY.search(text), text


@pytest.mark.parametrize("number", ROOMS)
def test_paul_sees_no_markup_either(paul: Game, number: int) -> None:
    paul.new_room(number)
    room = paul.room
    assert room is not None
    drain(paul)
    paul.handle_input("look")
    for noun in room.looks:
        paul.print(room.looks[noun])
    for text in drain(paul):
        assert not LEFTOVER.search(text), text
        assert "Pauline" not in text and "Rusty" not in text


def test_the_doorwoman_calls_her_maam(pauline: Game) -> None:
    pauline.new_room(21)
    assert "ma'am" in drain(pauline)[0]
    pauline.handle_input("talk to doorwoman")
    msg = drain(pauline)[0]
    assert "ma'am" in msg and "She means it" in msg
    pauline.handle_input("look at the doorwoman")
    assert "She is paid by the smile" in drain(pauline)[0]


def test_casino_cast_is_mirrored(pauline: Game) -> None:
    pauline.new_room(22)
    assert "waiter" in drain(pauline)[0]
    pauline.handle_input("look at clerk")
    msg = drain(pauline)[0]
    assert msg.startswith("A man behind the prize counter") and "duchess" in msg and "He sells" in msg
    pauline.handle_input("look at dealer")
    assert "HOPE" in drain(pauline)[0]
    pauline.handle_input("look at ring")
    assert "Rusty would not ask" in drain(pauline)[0]
    pauline.ego.x, pauline.ego.y = 136, 110
    pauline.vars["money"] = 300
    pauline.handle_input("buy ring")
    msg = drain(pauline)[0]
    assert pauline.has("ring") and "prize gent" in msg and '"Congratulations," he says' in msg


def test_high_roller_gets_a_title(pauline: Game) -> None:
    pauline.rng = random.Random(3)
    pauline.new_room(22)
    drain(pauline)
    pauline.ego.x, pauline.ego.y = 30, 110
    pauline.vars["money"] = 600
    pauline.handle_input("pull lever")
    comp, spin = drain(pauline)
    assert "waiter" in comp and "ma'am.\" Ma'am." in comp
    assert re.search(r"\[( % | o | A |BAR| 7 )\]", spin)  # the reels keep their brackets


def test_stealing_chips_kills_pauline(pauline: Game) -> None:
    pauline.new_room(22)
    drain(pauline)
    pauline.handle_input("steal chips")
    assert pauline.dead and "Pauline is later found" in drain(pauline)[0]


def test_no_groom_no_wedding(pauline: Game) -> None:
    pauline.new_room(24)
    assert pauline.room is not None and not pauline.room.objects(pauline)
    msg = drain(pauline)[0]
    assert '"Groom?" She looks past you.' in msg
    pauline.ego.x, pauline.ego.y = 80, 110
    pauline.handle_input("marry rusty")
    assert "Marry whom" in drain(pauline)[0]
    pauline.handle_input("talk to mother")
    assert "No groom, no wedding" in drain(pauline)[0]
    pauline.handle_input("talk to the groom")
    assert "There's no groom here" in drain(pauline)[0]
    pauline.handle_input("pay preacher")
    assert "Bring a groom" in drain(pauline)[0]


def test_pauline_marries_rusty(pauline: Game) -> None:
    game = pauline
    game.flags["ginger_danced"] = True
    game.new_room(24)
    room = game.room
    assert room is not None and room.objects(game)  # Rusty at the altar
    msg = drain(game)[0]
    assert msg.startswith("Rusty is at the altar in a top hat he must have brought with him. He turns.")
    game.ego.x, game.ego.y = 80, 110
    game.vars["money"] = 100
    game.handle_input("talk to man")
    assert "Pay the lady" in (msg := drain(game)[0]) and "on his fingers" in msg
    game.handle_input("kiss him")
    assert drain(game)[0] == '"After," says Rusty. "Pay the lady first."'
    game.handle_input("marry rusty")
    assert "Fifty dollars first" in drain(game)[0]
    game.handle_input("talk to priestess")
    assert "ceremony, child" in drain(game)[0]
    game.handle_input("pay the preacher")
    assert game.flags["chapel_paid"] and game.vars["money"] == 50
    drain(game)
    game.handle_input("give ring to rusty")
    assert drain(game)[0] == (
        'Rusty holds out his hand. You have nothing to put on it. "Pauline," he says. That\'s all. "Pauline."'
    )
    game.give("ring")
    game.handle_input("talk to preacher")
    assert "a groom who's stopped checking his watch" in drain(game)[0]
    game.handle_input("marry him")
    msgs = drain(game)
    assert len(msgs) == 3
    assert "Dearly beloved, and Pauline." in msgs[0] and "Rusty takes your hand" in msgs[0]
    assert "onto his finger" in msgs[1]
    assert "Don't keep a guy waiting.\" He goes. The organ plays him out." in msgs[2]
    assert game.flags["ginger_married"] and game.has("key") and not game.has("ring")
    assert game.score == 15
    assert not room.objects(game)  # he has gone ahead
    game.handle_input("talk to husband")
    assert "you have a husband. Go." in drain(game)[0]
    game.ego.x, game.ego.y = 20, 110
    game.handle_input("pull the rope")
    assert game.score == 16
    drain(game)
    game.new_room(24)
    assert "Your husband has gone ahead" in drain(game)[0]
    # the casino elevator knows the key, and who took it afterwards
    game.new_room(22)
    drain(game)
    game.ego.x, game.ego.y = 46, 110
    game.take("key")
    game.flags["honeymoon_done"] = True
    game.handle_input("use elevator")
    assert "He took the key" in drain(game)[0]


def test_kiss_with_nobody_at_the_altar(paul: Game) -> None:
    paul.new_room(24)
    drain(paul)
    paul.handle_input("kiss ginger")
    assert drain(paul)[0] == "Nobody to kiss. The preacher has a policy."


def test_collection_box_is_fatal_in_a_pantsuit(pauline: Game) -> None:
    pauline.new_room(24)
    drain(pauline)
    pauline.handle_input("take the collection box")
    assert pauline.dead and "Pauline is a small pile of ash in a pantsuit" in drain(pauline)[0]


def test_wedding_sprites_build_in_both_versions() -> None:
    pygame.init()
    room = Chapel()
    bride, groom = room.ginger(False), room.ginger(True)
    assert bride.get_size() == (12, 24)
    assert groom.get_size() == (12, 27)  # the top hat adds three rows
    assert room.ginger(True) is groom and room.ginger(False) is bride  # cached per version
    white, black = (255, 255, 255), (0, 0, 0)
    assert bride.get_at((5, 0))[:3] == white  # the veil
    assert groom.get_at((5, 0))[:3] == black  # the hat


@pytest.mark.parametrize("number", ROOMS)
def test_rooms_draw_in_both_versions(pauline: Game, number: int) -> None:
    room = pauline.rooms[number]
    for mode in (False, True):
        room.draw(Picture(mode))


def test_a_live_game_can_switch_versions(pauline: Game) -> None:
    pauline.flags["ginger_danced"] = True
    pauline.new_room(24)
    room = pauline.room
    assert room is not None
    groom = room.objects(pauline)[0][0]
    pauline.set_pauline(False)
    pauline.new_room(24)
    bride = room.objects(pauline)[0][0]
    assert bride is not groom and bride.get_height() == 24
    assert drain(pauline)[-1].startswith("Ginger is at the altar in a veil")
