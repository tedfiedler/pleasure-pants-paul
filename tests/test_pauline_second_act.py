"""Pauline's game, second act: the penthouse, the executive floor, the lounge and the roof."""

import re

import pygame
import pytest

from ppp.game import Game
from ppp.rooms import register

ROOMS = (25, 26, 27, 28)
PAUL_ONLY = ("Ginger", "Hope", "Dawn", "Dolores", "Brick", "Paul ", "Paul,", "Paul.", "HOPE")
MARKUP = re.compile(r"\[[^\[\]]*\|[^\[\]]*\]")


def make(tmp_path, monkeypatch, pauline: bool) -> Game:
    monkeypatch.setenv("PPP_SAVE_DIR", str(tmp_path))
    pygame.init()
    g = Game(pauline=pauline)
    register(g)
    return g


@pytest.fixture
def game(tmp_path, monkeypatch) -> Game:
    return make(tmp_path, monkeypatch, pauline=True)


def drain(game: Game) -> list[str]:
    out = list(game.messages)
    game.messages.clear()
    return out


def run(game: Game, cycles: int) -> None:
    for _ in range(cycles):
        game.cycle()


def assert_mirrored(text: str) -> None:
    assert not MARKUP.search(text), f"unrendered markup: {text!r}"
    for name in PAUL_ONLY:
        assert name not in text, f"{name!r} in Pauline's game: {text!r}"


def after_honeymoon(game: Game) -> Game:
    game.flags["honeymoon_done"] = True
    game.flags["freed"] = True
    game.vars["money"] = 10
    return game


@pytest.mark.parametrize("number", ROOMS)
def test_descriptions_and_looks_are_mirrored(game: Game, number: int) -> None:
    game.new_room(number)
    room = game.room
    assert room is not None
    drain(game)
    game.handle_input("look")
    for noun in room.looks:
        game.print(room.looks[noun])
    for text in drain(game):
        assert_mirrored(text)


def test_second_act_cast_by_name(game: Game) -> None:
    game.new_room(25)
    drain(game)
    game.handle_input("look at rusty")
    text = drain(game)[0]
    assert text.startswith("Rusty, on the bed") and "Your husband." in text
    game.new_room(26)
    drain(game)
    game.handle_input("look at the man")
    text = drain(game)[0]
    assert text.startswith("Chance.") and "He knows it" in text
    game.handle_input("look")
    assert "CHANCE" in drain(game)[0]
    game.flags["pool_pass"] = True
    game.new_room(28)
    drain(game)
    game.handle_input("look at him")
    assert "is Dusty" in drain(game)[0]


def test_paul_names_are_not_words_in_paulines_game(game: Game) -> None:
    game.new_room(26)
    drain(game)
    game.handle_input("talk to hope")
    assert "don't know the word" in drain(game)[0]


def test_honeymoon_robbery_and_escape_as_pauline(game: Game) -> None:
    from ppp.rooms.penthouse import MAID_CYCLES, Penthouse

    game.flags["ginger_married"] = True
    game.give("key")
    game.vars["money"] = 120
    game.new_room(25)
    room = game.room
    assert isinstance(room, Penthouse) and len(room.objects(game)) == 1
    entry = drain(game)[0]
    assert entry.startswith("Rusty is on the bed") and '"Wife," he says' in entry
    game.ego.x, game.ego.y = 100, 116
    game.handle_input("kiss rusty")
    msgs = drain(game)
    assert len(msgs) == 3 and "$120" in msgs[2] and "Thanks for the ring, wife" in msgs[2]
    for m in msgs:
        assert_mirrored(m)
    assert game.flags["tied_up"] and game.vars["money"] == 0 and not game.has("key")
    assert room.objects(game)[0][0] is room.tied(True)
    game.handle_input("look at me")
    assert "You are Pauline" in drain(game)[0]
    game.handle_input("untie rope")
    assert "Rusty was clearly a Scout" in drain(game)[0]
    game.handle_input("get up")
    assert "tied to a bed, Pauline" in drain(game)[0]
    game.handle_input("call the houseman")
    assert room.maid_timer == MAID_CYCLES
    drain(game)
    run(game, MAID_CYCLES)
    assert game.flags["freed"] and not game.flags["tied_up"] and game.ego.visible
    freed = drain(game)[0]
    assert "A houseman comes in" in freed and "He takes the rope" in freed
    game.handle_input("read the note")
    note = drain(game)[0]
    assert "A guy isn't a monster" in note and "Don't call. R." in note
    assert_mirrored(note)
    game.handle_input("look at mirror")
    assert "tired woman" in drain(game)[0]


def test_balcony_is_fatal_for_pauline_too(game: Game) -> None:
    game.new_room(25)
    drain(game)
    game.handle_input("open the balcony door")
    assert game.dead and "Pauline checks out early" in drain(game)[0]


def test_chance_trades_the_pass_for_coffee(game: Game) -> None:
    game.new_room(26)
    assert drain(game)[0].startswith("Chance looks up")
    game.ego.x, game.ego.y = 80, 112
    game.handle_input("kiss chance")
    text = drain(game)[0]
    assert "his left hand" in text and "To a woman who bench-presses receptionists" in text
    game.handle_input("look at photo")
    assert "Chance and a woman the size of a vending machine" in drain(game)[0]
    game.handle_input("get apple")
    assert "says Chance" in drain(game)[0] and not game.has("apple")
    after_honeymoon(game)
    game.handle_input("talk to the receptionist")
    assert "He looks at you" in drain(game)[0]
    game.ego.x = 144
    game.handle_input("get coffee")
    game.ego.x = 80
    drain(game)
    game.handle_input("give coffee to chance")
    text = drain(game)[0]
    assert game.has("pass") and "don't tell my wife, she'll want one" in text
    assert_mirrored(text)
    game.handle_input("take an apple")
    assert game.has("apple")
    game.ego.x = 16
    game.handle_input("open door")
    assert game.room is not None and game.room.number == 28


def test_lounge_act_as_pauline(game: Game) -> None:
    from ppp.rooms.lounge import JOKES

    after_honeymoon(game)
    game.new_room(27)
    assert "Ma'am, is that suit white" in drain(game)[0]
    seen: list[str] = []
    for _ in range(len(JOKES)):
        game.handle_input("sit")
        seen.extend(drain(game))
    act = "\n".join(seen)
    assert_mirrored(act)
    assert "My husband tied me to a bed" in act and "white pantsuit" in act and "Look at her" in act
    assert "Tip your waiter, he's the only one" in act and "She bows to nobody" in act
    assert game.score == 3
    game.handle_input("talk to comedian")
    assert "shades her eyes" in drain(game)[0]
    game.handle_input("look at comedian")
    assert "Her act has three jokes" in drain(game)[0]


def test_roof_ending_as_pauline(game: Game) -> None:
    from ppp.rooms.roof import Roof

    game.flags["pool_pass"] = True
    game.new_room(28)
    room = game.room
    assert isinstance(room, Roof) and room.objects(game)[0][0] is room.dawn(True)
    assert "You're not the waitress" in drain(game)[0]
    game.ego.x, game.ego.y = 110, 136
    game.handle_input("get in the tub")
    assert "says Dusty" in drain(game)[0]
    game.handle_input("talk to dusty")
    text = drain(game)[0]
    assert text.startswith('"Dusty," he says') and "the houseman" in text
    game.give("apple")
    game.handle_input("give the apple to dusty")
    text = drain(game)[0]
    assert game.flags["dawn_apple"] and "Get in, Pauline" in text
    assert_mirrored(text)
    game.handle_input("kiss the man")
    ending = drain(game)
    assert game.flags["won"] and game.score == 35 and not game.ego.visible
    assert len(ending) == 2 and "white pantsuit" in ending[0] and "Dusty puts his head on your shoulder" in ending[1]
    assert not room.objects(game)


def test_parapet_is_fatal_for_pauline_too(game: Game) -> None:
    game.flags["pool_pass"] = True
    game.new_room(28)
    drain(game)
    game.handle_input("climb the rail")
    assert game.dead and "Pauline goes down in style" in drain(game)[-1]


def test_sprites_build_in_both_versions_and_match_in_size() -> None:
    from ppp.rooms.execfloor import ExecFloor
    from ppp.rooms.penthouse import Penthouse
    from ppp.rooms.roof import Roof

    pygame.init()
    pent, floor, roof = Penthouse(), ExecFloor(), Roof()
    for a, b in (
        (pent.tied(False), pent.tied(True)),
        (pent.ginger(False), pent.ginger(True)),
        (floor.hope(False), floor.hope(True)),
        (roof.dawn(False), roof.dawn(True)),
    ):
        assert a is not b and a.get_size() == b.get_size()
    assert pent.tied(True) is pent.tied(True)  # cached per version


def test_a_live_game_can_switch_versions(tmp_path, monkeypatch) -> None:
    """A restored save may flip the version on a Game whose rooms have already cached sprites."""
    game = make(tmp_path, monkeypatch, pauline=False)
    game.flags["pool_pass"] = True
    game.new_room(28)
    room = game.room
    assert room is not None
    paul_side = room.objects(game)[0][0]
    game.set_pauline(True)
    game.new_room(28)
    assert room.objects(game)[0][0] is not paul_side
    game.new_room(26)
    assert game.pic is not None and game.pic.pauline
    drain(game)
    game.handle_input("look")
    assert "CHANCE" in drain(game)[0]


def test_execfloor_picture_differs_between_versions(tmp_path, monkeypatch) -> None:
    from ppp.rooms.execfloor import HOPE_POS

    pics = []
    for pauline in (False, True):
        g = make(tmp_path, monkeypatch, pauline)
        g.new_room(26)
        assert g.pic is not None
        pics.append(pygame.image.tobytes(g.pic.visual.subsurface(pygame.Rect(*HOPE_POS, 14, 17)), "RGB"))
    assert pics[0] != pics[1]
