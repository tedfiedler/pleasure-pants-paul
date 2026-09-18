"""Vocabulary: each tuple is a word group; the first entry is the group name.

Room logic matches on group names, so "l", "look" and "examine" are all
the word "look". Words in IGNORE are dropped before matching, as AGI did.
"""

IGNORE = frozenset("the a an at to in into on onto of with for up my some this that please and then".split())

GROUPS: list[tuple[str, ...]] = [
    # verbs
    ("look", "l", "examine", "see", "view", "inspect", "read", "x"),
    ("get", "take", "pick", "grab", "acquire"),
    ("drop", "leave", "discard", "throw"),
    ("open", "unlock"),
    ("close", "shut"),
    ("talk", "speak", "chat", "converse", "ask", "say", "tell", "hello", "hi"),
    ("buy", "purchase", "order"),
    ("give", "offer", "hand"),
    ("use",),
    ("drink", "sip", "swig", "chug"),
    ("eat", "chew"),
    ("push", "press", "hit", "punch"),
    ("pull", "tug"),
    ("sit", "rest"),
    ("stand",),
    ("wait", "z"),
    ("kiss", "hug", "smooch"),
    ("dance", "boogie"),
    ("enter", "go", "walk", "climb", "exit"),
    ("inventory", "i", "inv"),
    ("help", "hint"),
    ("quit", "q", "bye"),
    ("save",),
    ("restore", "load"),
    ("score",),
    ("smell", "sniff"),
    ("listen", "hear"),
    ("kick",),
    ("knock", "ring"),
    ("play", "flip"),
    ("pay", "tip"),
    ("call", "phone", "dial"),
    # directions
    ("north", "n", "forward"),
    ("south", "s", "back", "backward"),
    ("east", "e", "right"),
    ("west", "w", "left"),
    # nouns: the world
    ("self", "me", "myself", "paul", "suit", "pants", "clothes"),
    ("room", "around", "here", "place"),
    ("door", "doorway", "entrance"),
    ("wall", "walls"),
    ("floor", "ground", "sidewalk", "pavement", "street"),
    ("sign", "neon", "lights", "light"),
    ("window", "windows"),
    ("bar", "counter"),
    ("bartender", "barkeep", "barman", "keeper"),
    ("drunk", "bum", "man", "guy", "lush", "wino", "customer"),
    ("dog", "mutt", "hound"),
    ("stool", "stools", "chair", "seat", "booth", "table"),
    ("whiskey", "whisky", "booze", "liquor", "shot", "beer", "scotch", "bourbon"),
    ("remote", "control", "clicker"),
    ("money", "cash", "dollars", "dollar", "bucks", "wallet"),
    ("jukebox", "music", "juke"),
    ("bathroom", "restroom", "toilet", "john", "men", "mens"),
    ("trash", "garbage", "can", "bin", "dumpster"),
    ("hydrant",),
    ("building", "buildings", "bar_building", "dive"),
    ("cab", "taxi"),
    ("hooker", "prostitute", "woman", "lady", "girl"),
    ("pimp", "bouncer", "thug"),
    ("tv", "television", "set"),
]

ANY = "anyword"
ROL = "rol"  # rest of line


def _build() -> dict[str, str]:
    table: dict[str, str] = {}
    for group in GROUPS:
        name = group[0]
        for word in group:
            assert word not in table, f"duplicate vocabulary word: {word}"
            table[word] = name
    return table


LOOKUP: dict[str, str] = _build()
