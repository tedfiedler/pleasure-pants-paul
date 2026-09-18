import pygame
import pytest

from ppp.const import PIC_H, PIC_W, priority_for_y
from ppp.font import wrap
from ppp.fontdata import GLYPHS
from ppp.game import MAX_SCORE, Game
from ppp.rooms import START_ROOM, register


@pytest.fixture
def game() -> Game:
    pygame.init()
    g = Game()
    register(g)
    g.new_room(START_ROOM)
    return g


def test_font_has_full_ascii() -> None:
    assert len(GLYPHS) == 128
    assert all(len(g) == 8 for g in GLYPHS)


def test_priority_bands() -> None:
    assert priority_for_y(0) == 4
    assert priority_for_y(47) == 4
    assert priority_for_y(48) == 5
    assert priority_for_y(59) == 5
    assert priority_for_y(60) == 6
    assert priority_for_y(PIC_H - 1) == 14  # band 15 lies below the picture


def test_wrap() -> None:
    assert wrap("one two three four", 9) == ["one two", "three", "four"]
    assert wrap("a\nb", 10) == ["a", "b"]


def test_every_edge_and_spawn_points_at_a_real_room(game: Game) -> None:
    for room in game.rooms.values():
        for target in room.edges.values():
            assert target in game.rooms, f"room {room.number} edge -> {target}"
        for key in room.spawns:
            if key != "default":
                assert key in game.rooms, f"room {room.number} spawn from {key}"
        for x, y in room.spawns.values():
            assert 0 <= x < PIC_W and room.horizon <= y < PIC_H


def test_every_room_draws(game: Game) -> None:
    for number in game.rooms:
        game.new_room(number)
        assert game.pic is not None
        # the spawn point must be walkable
        assert game.pic.pri_at(game.ego.centre_x, game.ego.y) != 0


def test_unknown_word_reply(game: Game) -> None:
    game.handle_input("frobnicate the bar")
    assert game.message == 'I don\'t know the word "frobnicate".'


def test_bar_puzzle_awards_points_once(game: Game) -> None:
    game.new_room(11)
    game.dismiss()
    game.ego.x, game.ego.y = 60, 108
    game.handle_input("buy whiskey")
    assert game.has("whiskey")
    assert game.score == 2
    game.ego.x, game.ego.y = 130, 108
    game.handle_input("give whiskey to drunk")
    assert game.has("remote") and not game.has("whiskey")
    assert game.score == 6
    game.handle_input("buy whiskey")
    game.handle_input("give whiskey to drunk")
    assert game.score == 6
    assert game.score <= MAX_SCORE


def test_walking_off_bar_exit_returns_to_street(game: Game) -> None:
    game.new_room(11)
    game.dismiss()
    game.ego.x, game.ego.y = 76, 160
    game.ego.set_direction(5)
    for _ in range(30):
        game.cycle()
        if game.room and game.room.number == 10:
            break
    assert game.room is not None and game.room.number == 10


def test_ego_cannot_walk_through_walls(game: Game) -> None:
    game.new_room(11)
    game.dismiss()
    game.ego.x, game.ego.y = 60, 104
    game.ego.set_direction(1)
    for _ in range(20):
        game.cycle()
    assert game.ego.y >= game.room.horizon if game.room else True
