"""--pauline: the mirror-image game. Markup, vocabulary, saves, and the block around Rooster's."""

import ast
import re
from pathlib import Path

import pygame
import pytest

import ppp
from ppp import save
from ppp.cast import CAST, TITLE, render
from ppp.ego import Ego
from ppp.game import Game
from ppp.main import App
from ppp.parser import parse
from ppp.rooms import START_ROOM, register

SRC = Path(ppp.__file__).resolve().parent
LEFTOVER = re.compile(r"\[[^\[\]]*\|[^\[\]]*\]")
ORDINARY = ["Brick, wet"]  # the alley wall is made of it, in both games


def _plain(text: str) -> str:
    for words in ORDINARY:
        text = text.replace(words, "")
    return text


@pytest.fixture
def pauline(tmp_path, monkeypatch) -> Game:
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


def say(game: Game, text: str) -> str:
    game.messages.clear()
    game.handle_input(text)
    return " ".join(drain(game))


# -- markup ---------------------------------------------------------------------


def test_render_picks_a_side() -> None:
    text = '[Ginger] looks at [Paul]. "Sweet," [she|he] says. [Ginger]\'s drink is empty.'
    assert render(text, False) == 'Ginger looks at Paul. "Sweet," she says. Ginger\'s drink is empty.'
    assert render(text, True) == 'Rusty looks at Pauline. "Sweet," he says. Rusty\'s drink is empty.'
    assert render("[a whole clause, with commas|]", True) == ""


def test_render_leaves_other_brackets_alone() -> None:
    reels = "[ % ] [BAR] [ 7 ]"
    assert render(reels, False) == reels and render(reels, True) == reels


def test_title() -> None:
    assert render(TITLE, False) == "Pleasure Pants Paul"
    assert render(TITLE, True) == "Pleasure Pants Pauline"


def _visible_strings() -> list[tuple[str, int, str]]:
    """Every string literal in the package that isn't a docstring: (file, line, text)."""
    out: list[tuple[str, int, str]] = []
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text())
        docstrings = {
            id(node.body[0].value)
            for node in ast.walk(tree)
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
                out.append((path.name, node.lineno, node.value))
    return out


def test_no_cast_name_escapes_the_markup() -> None:
    """A bare "Ginger" in game text would follow Pauline into her game."""
    names = "|".join(CAST)
    bare = re.compile(rf"(?<![\[\w])({names})(?![\w|\]])")
    skip = {"cast.py"}  # the table itself
    found = [
        f"{name}:{line}: {text!r}"
        for name, line, text in _visible_strings()
        if name not in skip and bare.search(_plain(text)) and not text.isupper() and " " in text
    ]
    assert not found, "\n".join(found)


def test_all_markup_resolves_in_both_games() -> None:
    for name, line, text in _visible_strings():
        if name == "cast.py":
            continue
        for mode in (False, True):
            assert not LEFTOVER.search(render(text, mode)), f"{name}:{line}"


def test_every_room_describes_itself_as_pauline(pauline: Game) -> None:
    for number, room in pauline.rooms.items():
        for text in [room.description, *room.looks.values()]:
            shown = _plain(pauline.tr(text))
            assert not LEFTOVER.search(shown), (number, shown)
            for theirs in CAST:
                assert not re.search(rf"\b{theirs}\b", shown), (number, shown)


# -- vocabulary -----------------------------------------------------------------


def test_the_gendered_words_change_sides() -> None:
    assert parse("look at the man").words == ["look", "drunk"]
    assert parse("look at the man", pauline=True).words == ["look", "hooker"]
    assert parse("look at the lady").words == ["look", "hooker"]
    assert parse("look at the lady", pauline=True).words == ["look", "drunk"]
    assert parse("talk to donny", pauline=True).words == ["talk", "hooker"]
    assert parse("talk to donny").unknown == "donny"
    assert parse("talk to dolores", pauline=True).unknown == "dolores"
    assert parse("kick roxy", pauline=True).words == ["kick", "bouncer"]
    assert parse("look at pauline", pauline=True).words == ["look", "self"]


# -- the game itself --------------------------------------------------------------


def test_pauline_looks_at_herself(pauline: Game) -> None:
    text = say(pauline, "look at me")
    assert "You are Pauline" in text and "pantsuit" in text and "balding" not in text
    assert "herself" in say(pauline, "talk to myself")


def test_pauline_has_her_own_sprite() -> None:
    pygame.init()
    him, her = Ego(), Ego(pauline=True)
    assert set(him.frames or (him.ensure_frames() or him.frames)) == {"down", "up", "left", "right"}
    her.ensure_frames()
    assert him.height == her.height and him.width == her.width
    for facing, frames in him.frames.items():
        assert len(frames) == len(her.frames[facing])
    a, b = him.frames["down"][0], her.frames["down"][0]
    assert any(a.get_at((x, y)) != b.get_at((x, y)) for x in range(a.get_width()) for y in range(a.get_height()))


def test_rooms_draw_in_both_games(pauline: Game) -> None:
    for number in pauline.rooms:
        pauline.new_room(number)
        assert pauline.pic is not None and pauline.pic.pauline
        pauline.room.objects(pauline)
        drain(pauline)


def test_the_ladies_room(pauline: Game) -> None:
    assert "marked LADIES" in pauline.tr(pauline.rooms[11].description)
    pauline.new_room(14)
    drain(pauline)
    assert "ladies' room" in say(pauline, "look")
    assert "dispenser" in say(pauline, "look at dispenser")
    assert "quarter" in say(pauline, "use dispenser") and pauline.score == 0
    say(pauline, "use toilet")
    assert pauline.score == 1
    assert "a woman in a white suit" in say(pauline, "look in mirror")
    wall = " ".join(say(pauline, "read graffiti") for _ in range(6))
    assert "Pauline was here" in wall and "ROOSTER SENT ME" in wall


def test_the_block_around_roosters_as_pauline(pauline: Game) -> None:
    g = pauline
    g.new_room(11)
    drain(g)
    assert "A big woman" in say(g, "look at barmaid")
    assert "A lady of the old school" in say(g, "look at the lady")
    g.ego.x, g.ego.y = 60, 108
    assert "She slides a shot" in say(g, "buy whiskey")
    g.ego.x, g.ego.y = 112, 108
    assert "Her eyes go wide" in say(g, "give whiskey to the lady")
    assert g.has("remote")

    g.flags["backdoor_open"] = True
    g.new_room(15)
    assert "Roxy doesn't look up" in " ".join(drain(g))
    assert "sits a woman called Roxy" in say(g, "look")
    assert "pink blouse" in say(g, "look at roxy")
    assert "Roxy leans forward" in say(g, "use remote")
    assert g.room is not None and len(g.room.objects(g)) == 2

    g.new_room(16)
    assert "Donny looks up from his cufflink" in " ".join(drain(g))
    assert "red silk shirt" in say(g, "look at the man")
    g.give("rose")
    g.give("protection")
    g.ego.x, g.ego.y = 104, 110
    assert "behind his ear" in say(g, "give rose to donny")
    assert "says Donny" not in say(g, "pay him") and g.flags["dolores_paid"]
    done = say(g, "kiss donny")
    assert "a new woman" in done and not g.dead
    assert "dolores" in g.scored


def test_pauline_dies_as_pauline(pauline: Game) -> None:
    pauline.new_room(12)
    drain(pauline)
    assert "Pauline is dog food" in say(pauline, "kick the dog")
    assert pauline.dead


# -- saves, and the app -------------------------------------------------------------


def test_a_save_remembers_whose_game_it_is(pauline: Game) -> None:
    save.write(pauline, "her night out")
    info = save.list_saves()[0]

    other = Game()
    register(other)
    other.new_room(16)
    assert "Dolores" in other.tr(other.rooms[16].description)
    other.room.objects(other)  # builds and caches Dolores

    save.apply(other, save.read(info.path))
    assert other.pauline and other.ego.pauline and other.pic is not None and other.pic.pauline
    other.ego.ensure_frames()
    fresh = Ego(pauline=True)
    fresh.ensure_frames()
    assert other.ego.frames["down"][0].get_at((0, 1)) == fresh.frames["down"][0].get_at((0, 1))
    other.new_room(16)
    donny = other.room.objects(other)[0][0]
    other.set_pauline(False)
    assert other.room.objects(other)[0][0] is not donny  # sprite caches are per game


def test_old_saves_are_pauls(pauline: Game, tmp_path) -> None:
    data = save.snapshot(pauline, "from before")
    del data["pauline"]
    save.apply(pauline, data)
    assert not pauline.pauline


def test_the_app_as_pauline(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPP_SAVE_DIR", str(tmp_path))
    app = App(scale=1, skip_quiz=True, pauline=True)
    assert pygame.display.get_caption()[0] == "Pleasure Pants Pauline"
    assert app.game.pauline
    app.game.die("Oops.")
    app.restart()
    assert app.game.pauline and not app.game.dead
    assert any("PAULINE" in line for line in app.ending_lines())
    assert any("Pauline got the guy" in line for line in app.ending_lines())
    app.draw()


def test_the_app_is_pauls_by_default(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPP_SAVE_DIR", str(tmp_path))
    app = App(scale=1, skip_quiz=True)
    assert pygame.display.get_caption()[0] == "Pleasure Pants Paul"
    assert not app.game.pauline
    assert any("Paul got the girl" in line for line in app.ending_lines())
