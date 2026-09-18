# Pleasure Pants Paul

A text-parser graphic adventure in the style of Sierra's 1987 AGI games.
Sixteen EGA colours, a 160x200 double-wide-pixel picture, arrow-key walking,
a `>` prompt, and a hero in a white polyester leisure suit who deserves none
of what happens to him.

Working title. All art, text, rooms and puzzles are original.

## Run it

```sh
uv sync
uv run ppp              # title -> age quiz -> game
uv run ppp --skip-quiz  # straight into room 10
uv run ppp --scale 4    # bigger window (integer scale, default 3)
```

Walk with the arrow keys (press the same arrow again to stop, like the
original). Type commands such as `look`, `look bar`, `talk to bartender`,
`buy whiskey`, `give whiskey to drunk`, `inventory`, `score`, `quit`.

Alt-X (or Cmd-X on a Mac) skips the age quiz.

**ESC** opens the Sierra menu bar (File, Action, Special, Speed). Left and
right arrows switch menus, up and down pick an item, ENTER activates, ESC
closes. Shortcuts: F1 help, F2 sound on/off, F3 score, F4 look, F5 save,
F7 restore, F9 restart, Tab inventory, Alt-Z (Cmd-Z) quit. Typing `save`,
`restore`, `restart` or `quit` at the prompt does the same thing.

Saved games are JSON files, twelve most recent kept, in:

| Platform | Directory |
|---|---|
| macOS | `~/Library/Application Support/PleasurePantsPaul/saves` |
| Windows | `%APPDATA%\PleasurePantsPaul\saves` |
| Linux | `$XDG_DATA_HOME/PleasurePantsPaul/saves` |

Set `PPP_SAVE_DIR` to override.

## How faithful is it?

The engine reproduces the AGI model rather than emulating it:

- **Screen**: 320x200, 25 text rows. Row 0 is the status line, rows 1-21 the
  picture, row 23 the parser prompt.
- **Pictures**: not bitmaps. Each room draws its background with vector-style
  commands (rects, lines, polygons, flood fills) into a 160x168 visual screen
  and a matching **priority screen**, exactly like AGI PIC resources. Priority
  bands (4..15, twelve rows each below y=48) decide whether Paul walks in
  front of or behind scenery. Priority 0 is an unwalkable control line.
- **Ego**: 8-unit-wide sprite in picture coordinates, one unit per cycle at
  20 cycles/second. Arrow keys toggle direction, AGI-style.
- **Parser**: words map to synonym groups; noise words are dropped; rooms match
  with `said("give", "whiskey", "drunk")`, `anyword` and `rol` (rest of line).
- **Message boxes**: white, double red border, black text, word-wrapped at 30
  columns, dismissed by any key. Dialogs (save, restore, confirm) use the
  same box with an inverted highlight bar.
- **Menu bar**: ESC replaces the status line with File / Action / Special /
  Speed, with a white dropdown and inverted selection.
- **Speed**: slow, normal, fast, fastest = 10, 20, 40, 80 cycles a second.
- **Font**: public-domain 8x8 IBM PC bitmap font.
- **Score** shown as `Score: N of 222`, awarded once per action.

## Layout

```
src/ppp/
  main.py      window, main loop, title/quiz/play states
  game.py      state, scoring, inventory, command dispatch, global verbs
  room.py      Room base class (draw, enter, update, said, looks)
  rooms/       one file per room; register() lists them
  pic.py       Picture: visual + priority screens and drawing commands
  ego.py       Paul's sprite frames, movement, priority-aware blit
  parser.py    tokeniser and said() matcher
  words.py     vocabulary groups
  ui.py        status line, prompt, message box, text pages
  menu.py      menu bar definition, navigation, drawing, F-key shortcuts
  dialog.py    confirm / text-entry / list-pick modal dialogs
  save.py      JSON save files: snapshot, apply, list, platform save dir
  quiz.py      age-verification quiz
  font.py      8x8 font renderer; fontdata.py holds the glyphs
  const.py     geometry, EGA palette, priority bands
```

## Adding a room

Subclass `Room`, set `number`, `name`, `description`, `horizon`, `edges`,
`spawns` and a `looks` table, implement `draw(pic)`, and add it to
`rooms/__init__.py`. Override `said()` for puzzles and `update()` for
per-cycle triggers. See `rooms/bar.py` for a complete example.

## Building executables

Both platforms use PyInstaller from the same source:

```sh
uv run pyinstaller --onefile --windowed --name "Pleasure Pants Paul" src/ppp/main.py
```

Run that on a Mac for a `.app`, and on Windows for an `.exe`. There is no
port to do: the game is the same Python on both.

## Development

```sh
uv run pytest
uv run ruff check src tests
uv run mypy src
```

## License

MIT. The font (`fontdata.py`) is public domain, from dhepper/font8x8.
