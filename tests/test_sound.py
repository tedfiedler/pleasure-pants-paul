import pygame

from ppp import sound


def test_freq() -> None:
    assert round(sound.freq("A4")) == 440
    assert round(sound.freq("A5")) == 880
    assert round(sound.freq("C4")) == 262


def test_render_and_play_never_raise_headless() -> None:
    sound.init()  # dummy audio driver, may or may not come up
    pygame.init()
    snd = sound.render([("C4", 1), (None, 0.5), ("E4", 0.5)], bpm=240)
    assert snd.get_length() > 0.3
    assert sound.noise(100).get_length() > 0.05
    for name in list(sound.TUNES) + ["spin", "nonsense"]:
        sound.play(name)
    sound.enabled = False
    sound.play("theme")
    sound.enabled = True
    sound.stop()


def test_every_tune_renders() -> None:
    pygame.init()
    sound.init()
    for name, (seq, bpm) in sound.TUNES.items():
        assert sound.render(seq, bpm).get_length() > 0, name
