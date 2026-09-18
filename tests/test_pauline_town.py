"""Pauline's game around town: the cab, the Kwik-Snak and the Boogie Palace, with the cast mirrored."""

import ast
import inspect

import pygame
import pytest

from ppp.cast import render
from ppp.game import Game
from ppp.pic import Picture
from ppp.rooms import START_ROOM, disco, discostreet, register, store, storestreet, taxi
from ppp.rooms.disco import DANCE_CYCLES, Disco

TOWN = (13, 17, 18, 19, 20)
MODULES = (taxi, storestreet, store, discostreet, disco)
PAUL_ONLY = ("Ginger", "Paul ", "Paul.", "Paul,", "Paul'", "doorman", "LADIES", "leisure suit")


@pytest.fixture
def game(tmp_path, monkeypatch) -> Game:
    monkeypatch.setenv("PPP_SAVE_DIR", str(tmp_path))
    pygame.init()
    g = Game(pauline=True)
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


def assert_clean(text: str) -> None:
    assert not any(c in text for c in "[]|"), f"leftover markup: {text!r}"


def test_every_marked_string_renders_clean_in_both_versions() -> None:
    seen = 0
    for module in MODULES:
        for node in ast.walk(ast.parse(inspect.getsource(module))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and "[" in node.value:
                seen += 1
                for pauline in (False, True):
                    assert_clean(render(node.value, pauline))
    assert seen > 50


def test_descriptions_and_looks_are_mirrored(game: Game) -> None:
    for number in TOWN:
        room = game.rooms[number]
        for text in (room.description, *room.looks.values()):
            out = game.tr(text)
            assert_clean(out)
            # pronouns go both ways in a mirror, so check the words that only belong to Paul's side
            assert not any(word in out for word in PAUL_ONLY), out
    assert "Rusty" in game.tr(game.rooms[20].looks["hooker"])
    assert "MEN" in game.tr(game.rooms[20].description) and "LADIES" not in game.tr(game.rooms[20].description)
    assert "doorwoman" in game.tr(game.rooms[19].description)
    assert "She's bored" in game.tr(game.rooms[19].looks["bouncer"])
    assert "about her suggests" in game.tr(game.rooms[18].looks["clerk"])
    assert "around her neck" in game.tr(game.rooms[20].looks["dj"])


def test_rooms_draw_and_sprites_build_in_both_versions(game: Game) -> None:
    for pauline in (False, True):
        for number in TOWN:
            pic = Picture(pauline)
            game.rooms[number].draw(pic)
    room = game.rooms[20]
    assert isinstance(room, Disco)
    ginger, rusty = room.ginger(False, False), room.ginger(False, True)
    assert ginger.get_size() == rusty.get_size()
    assert pygame.image.tobytes(ginger, "RGB") != pygame.image.tobytes(rusty, "RGB")
    assert room.ginger(True, True).get_size() == room.ginger(True, False).get_size()
    assert room.ginger(False, True) is rusty  # cached per version, so a restored game can switch


def test_the_cabbie_is_a_woman(game: Game) -> None:
    game.vars["money"] = 20
    game.new_room(13)
    greeting = drain(game)[0]
    assert "her racing form" in greeting and "hon" in greeting
    game.handle_input("look at driver")
    assert "She's right" in drain(game)[0]
    game.handle_input("disco")
    assert "She floors it" in drain(game)[0]
    game.handle_input("pay")
    assert '"Pleasure," she says' in drain(game)[0]
    game.handle_input("get out")
    assert game.room is not None and game.room.number == 19


def test_price_check_for_the_lady(game: Game) -> None:
    game.vars["money"] = 20
    game.new_room(18)
    assert "woman hoping not to" in drain(game)[0]
    game.ego.x, game.ego.y = 80, 110
    game.handle_input("buy protection")
    msgs = drain(game)
    assert game.has("protection") and len(msgs) == 3
    assert "FOR THE LADY IN THE WHITE SUIT" in msgs[2] and "you and her" in msgs[2]
    for m in msgs:
        assert_clean(m)
    game.handle_input("steal wine")
    assert game.dead and "Pauline is now" in drain(game)[0]


def test_doorwoman_takes_the_magazine(game: Game) -> None:
    game.new_room(19)
    assert "doorwoman looks at your suit, then at her clipboard" in drain(game)[0]
    game.ego.x, game.ego.y = 100, 126
    game.handle_input("talk to doorwoman")
    assert "She taps the clipboard" in drain(game)[0]
    game.give("magazine")
    game.handle_input("give magazine to doorwoman")
    assert game.flags["disco_admitted"] and not game.has("magazine")
    assert "ma'am" in drain(game)[0]
    game.handle_input("talk to miss")
    assert "ma'am" in drain(game)[0]
    game.ego.x, game.ego.y = 76, 120
    game.ego.set_direction(1)
    run(game, 4)
    assert game.room is not None and game.room.number == 20


def test_wooing_rusty_in_order(game: Game) -> None:
    game.new_room(20)
    drain(game)
    game.ego.x, game.ego.y = 30, 140
    game.handle_input("look at rusty")
    assert "His name, the napkin says, is Rusty" in drain(game)[0]
    game.handle_input("talk to man")
    assert '"Hi," says Rusty' in drain(game)[0]
    game.give("wine")
    game.give("candy")
    game.handle_input("give wine to rusty")
    assert "He smiles" in drain(game)[0] and game.has("wine")
    game.handle_input("give chocolates to him")
    assert game.flags["ginger_candy"]
    game.handle_input("give him the wine")
    assert game.flags["ginger_wine"]
    assert "He laughs" in drain(game)[-1]
    game.handle_input("kiss the redhead")
    assert "Buy a guy a drink first" in drain(game)[0]
    game.handle_input("dance with rusty")
    assert game.ego.frozen and "He dances like he invented it" in drain(game)[0]
    run(game, DANCE_CYCLES)
    assert game.flags["ginger_danced"] and not game.ego.frozen
    message = game.message or ""
    assert "Here's the thing, Pauline." in message and "A guy like me needs a ring" in message
    # Paul's words for her don't reach him: they belong to other people now
    drain(game)
    game.handle_input("talk to ginger")
    assert "don't know the word" in drain(game)[0]


def test_mens_room_is_fatal_for_pauline(game: Game) -> None:
    game.new_room(20)
    drain(game)
    game.ego.x, game.ego.y = 110, 104
    game.handle_input("enter mens")
    text = drain(game)[0]
    assert game.dead and "marked MEN" in text and "Pauline dies of blunt force duffel" in text
