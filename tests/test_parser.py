from ppp.parser import parse
from ppp.words import GROUPS, LOOKUP


def test_synonyms_collapse_to_group_name() -> None:
    assert parse("examine the barkeep").words == ["look", "bartender"]
    assert parse("l").words == ["look"]


def test_noise_words_dropped() -> None:
    assert parse("give the whiskey to the drunk").words == ["give", "whiskey", "drunk"]


def test_unknown_word_recorded_and_blocks_said() -> None:
    p = parse("look at the flibbertigibbet")
    assert p.unknown == "flibbertigibbet"
    assert not p.said("look")


def test_said_patterns() -> None:
    p = parse("give whiskey to drunk")
    assert p.said("give", "whiskey", "drunk")
    assert p.said("give", "anyword", "drunk")
    assert p.said("give", "rol")
    assert not p.said("give", "whiskey")
    assert not p.said("give", "drunk", "whiskey")


def test_empty_input() -> None:
    assert parse("   ").empty
    assert parse("the a an").empty


def test_vocabulary_has_no_duplicates() -> None:
    seen: set[str] = set()
    for group in GROUPS:
        for word in group:
            assert word not in seen, word
            seen.add(word)
    assert len(LOOKUP) == len(seen)
