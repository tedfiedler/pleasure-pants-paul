"""Room 22: the casino floor. Slots, blackjack, and a prize counter with one ring."""

from __future__ import annotations

from ppp.const import (
    BLACK,
    BLUE,
    DGREY,
    GREEN,
    LBLUE,
    LCYAN,
    LGREEN,
    LGREY,
    LMAGENTA,
    LRED,
    PIC_W,
    RED,
    WHITE,
    YELLOW,
)
from ppp.game import Game
from ppp.npc import draw_person
from ppp.parser import Parsed
from ppp.pic import Picture
from ppp.room import Room

RING_PRICE = 250
SLOT_COST = 5
MIN_BET, MAX_BET = 5, 100

SLOT_SYMBOLS = ("cherry", "lemon", "bell", "bar", "seven")
SLOT_WEIGHTS = (30, 30, 20, 14, 6)
SLOT_PAYS = {"cherry": 25, "lemon": 15, "bell": 50, "bar": 125, "seven": 500}  # three of a kind
SLOT_LOOK = {"cherry": "[ % ]", "lemon": "[ o ]", "bell": "[ A ]", "bar": "[BAR]", "seven": "[ 7 ]"}

RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SUITS = ("s", "h", "d", "c")


def hand_value(hand: list[str]) -> int:
    total, aces = 0, 0
    for card in hand:
        rank = card[:-1]
        if rank == "A":
            aces += 1
            total += 11
        elif rank in ("J", "Q", "K"):
            total += 10
        else:
            total += int(rank)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def show(hand: list[str]) -> str:
    return " ".join(hand) + f" ({hand_value(hand)})"


class Casino(Room):
    number = 22
    name = "The Golden Sock"
    description = (
        "The casino floor: red carpet, gold trim, and a noise like a thousand tiny "
        "bells having an argument. Slot machines line the left wall. A blackjack "
        "table sits in the middle with a dealer who never blinks. On the right, a "
        "prize counter under glass. A door at the back says LOUNGE and an elevator "
        "beside it says nothing. The doors out are at the bottom of the screen."
    )
    horizon = 100
    edges = {"bottom": 21}
    spawns = {"default": (80, 150), 21: (80, 156)}
    looks = {
        "slot": "Three slot machines, chrome and neon, each with a lever like a "
        "question. A pull costs five dollars. Try PULL LEVER.",
        "blackjack": "A kidney-shaped table in green felt with a dealer behind it and "
        "chips in a rack. Bets from $5 to $100. Try PLAY BLACKJACK.",
        "dealer": "The dealer has a bow tie, a name tag that says CHANCE, and hands that "
        "move like they're being paid by the card. They are.",
        "prize": "A glass case with a pen set, a clock radio, a bottle of aftershave, and "
        "one diamond ring on a velvet finger. The ring is $250. The rest is free "
        "with the ring.",
        "ring": "A diamond ring, diamond in the sense of shiny, in a glass case. $250. "
        "Ginger would not ask where it came from.",
        "clerk": "A woman behind the prize counter in a gold vest, reading a paperback "
        "with a duke on the cover. She sells one ring a year and it's not October.",
        "lounge": "A padded door marked LOUNGE. A sign: TONIGHT! COMEDY! (SOLD OUT). Someone has added: THANK GOD.",
        "elevator": "Brass elevator doors. A sign says PENTHOUSE, and, below it, a keyhole where the button should be.",
        "floor": "Red carpet with a gold pattern that hides everything except your losses.",
        "chip": "You don't have chips. This casino deals in cash and disappointment.",
        "money": "You count your money at a blackjack table. Everyone looks. Everyone.",
    }

    def __init__(self) -> None:
        self.bj: dict[str, object] | None = None  # active blackjack hand

    def draw(self, pic: Picture) -> None:
        pic.rect(0, 0, PIC_W, 100, RED)
        for y in range(6, 100, 10):
            pic.line([(0, y), (PIC_W - 1, y)], YELLOW)
        pic.rect(0, 100, PIC_W, 68, RED)
        for y in range(104, 168, 8):
            for x in range(0, PIC_W, 8):
                if (x // 8 + y // 8) % 2 == 0:
                    pic.pixel(x + 4, y + 4, YELLOW)
        # slot machines, left wall
        for i in range(3):
            x = 6 + i * 20
            pic.rect(x, 50, 16, 50, DGREY, 0)
            pic.rect(x + 2, 52, 12, 10, (LMAGENTA, LCYAN, YELLOW)[i])
            pic.rect(x + 2, 66, 12, 8, WHITE)
            for j in range(3):
                pic.rect(x + 3 + j * 4, 68, 2, 4, (RED, YELLOW, BLACK)[(i + j) % 3])
            pic.rect(x + 16, 56, 2, 14, LGREY)  # lever
            pic.pixel(x + 16, 55, RED)
        pic.rect(6, 100, 56, 4, None, 0)
        # blackjack table, centre: the dealer first, then a half-moon of felt in front of him
        draw_person(pic, 84, 60, suit=BLACK, skin=LRED, hair=DGREY)
        pic.rect(86, 67, 4, 2, RED)  # bow tie
        pic.ellipse(60, 66, 56, 40, GREEN)
        pic.rect(60, 66, 56, 20, RED)  # restore the wall behind the dealer's half
        pic.rect(84, 66, 8, 20, BLACK)  # his jacket, over the red
        pic.rect(60, 84, 56, 3, YELLOW)  # padded rail
        pic.rect(80, 92, 16, 4, WHITE)  # a card or two
        pic.rect(64, 94, 6, 4, LBLUE)  # chips
        pic.rect(106, 94, 6, 4, LRED)
        pic.rect(60, 100, 56, 8, None, 0)  # nobody stands on the felt
        # prize counter, right
        pic.rect(120, 60, 36, 40, DGREY, 0)
        pic.rect(122, 62, 32, 20, LCYAN)  # glass
        pic.rect(126, 70, 6, 6, LGREY)
        pic.rect(136, 70, 6, 6, LGREEN)
        pic.pixel(147, 72, WHITE)  # the ring
        pic.pixel(148, 71, YELLOW)
        pic.rect(122, 82, 32, 16, BLACK)
        draw_person(pic, 134, 34, suit=YELLOW, skin=LRED, hair=BLACK)
        # lounge door and elevator, back wall
        pic.rect(6, 10, 22, 38, BLUE)
        pic.rect(8, 16, 18, 6, WHITE)
        pic.rect(36, 10, 20, 38, YELLOW)
        pic.line([(46, 10), (46, 47)], BLACK)
        pic.walls(100)
        pic.rect(120, 100, 36, 4, None, 0)

    def enter(self, game: Game, from_room: int | None) -> None:
        super().enter(game, from_room)
        self.bj = None
        if not game.flags.get("seen_casino"):
            game.flags["seen_casino"] = True
            game.print(
                "Bells, lights, carpet. A cocktail waitress passes without seeing you, "
                "which is a skill. Somewhere a slot machine pays out for someone else."
            )

    def _near(self, game: Game, x0: int, x1: int) -> bool:
        return x0 <= game.ego.centre_x <= x1 and game.ego.y <= 116

    # -- dispatch ------------------------------------------------------------------

    def said(self, game: Game, p: Parsed) -> bool:
        if self.bj is not None and self._blackjack_said(game, p):
            return True
        if p.has("slot") and p.verb in ("play", "use", "pull", "push", "enter") or p.said("pull"):
            self._slots(game)
        elif (
            p.has("blackjack")
            and p.verb in ("play", "use", "sit", "enter")
            or p.said("play", "rol")
            and p.has("dealer")
        ):
            self._blackjack_start(game)
        elif p.said("bet", "number") or p.said("bet", "number", "rol") or p.said("bet"):
            self._blackjack_bet(game, p.number)
        elif p.said("buy", "ring") or p.said("buy", "ring", "rol") or p.said("buy", "prize"):
            self._buy_ring(game)
        elif p.said("buy", "rol") or p.said("buy"):
            game.print('"The ring, or nothing," says the prize lady. "The clock radio\'s a display model. So am I."')
        elif p.has("chip") and p.verb in ("get", "steal") or p.said("get", "money") or p.said("steal", "rol"):
            game.die(
                "You reach for the chips. A hand the size of a dinner plate lands on your "
                "shoulder. The pit boss walks you to a small room with no windows. Paul "
                "is later found to have left town, in the sense that matters."
            )
        elif p.said("talk", "dealer") or p.said("talk", "dealer", "rol"):
            game.print('"Place your bets," says the dealer, to no one, to you, to the room.')
        elif p.said("talk", "clerk") or p.said("talk", "clerk", "rol") or p.said("talk"):
            game.print('"Ring\'s two-fifty," says the prize lady, not looking up. "Duke\'s about to propose. Hush."')
        elif p.has("lounge") and p.verb in ("open", "enter", "use"):
            game.print(
                "The lounge is sold out. You hear a drum roll and a groan. You're not missing anything, "
                "and it's still sold out."
            )
        elif p.has("elevator") and p.verb in ("open", "enter", "use", "push", "call"):
            game.print("No button, only a keyhole. Whoever lives up there doesn't want visitors. Yet.")
        elif p.said("look", "slot", "rol") or p.said("look", "blackjack", "rol"):
            game.print(self.looks["slot"] if p.has("slot") else self.looks["blackjack"])
        elif p.said("smell"):
            game.print("Cigars, carpet shampoo, and the sweet cologne of a man who just won and won't again.")
        elif p.said("listen"):
            game.print("Bells, chips, the shuffle of cards, and under it a saxophone. There's always a saxophone.")
        else:
            return False
        return True

    # -- slots ---------------------------------------------------------------------

    def _slots(self, game: Game) -> None:
        if not self._near(game, 4, 66):
            game.print("The slots are along the left wall. Walk over; they don't come to you, though they'd like to.")
            return
        money = game.vars.get("money", 0)
        if money < SLOT_COST:
            game.print(f"A pull is ${SLOT_COST}. You have ${money}. The machine, for once, is the one that's sorry.")
            return
        game.vars["money"] = money - SLOT_COST
        reels = game.rng.choices(SLOT_SYMBOLS, weights=SLOT_WEIGHTS, k=3)
        line = " ".join(SLOT_LOOK[r] for r in reels)
        win = 0
        if reels[0] == reels[1] == reels[2]:
            win = SLOT_PAYS[reels[0]]
        elif reels.count("cherry") == 2:
            win = 10
        elif "cherry" in reels:
            win = SLOT_COST
        if win:
            game.vars["money"] += win
            game.award("slots_win", 1)
            verdict = f"Bells! Lights! ${win}!"
            if win <= SLOT_COST:
                verdict = "A cherry. Your five dollars back. Thrilling."
        else:
            verdict = "Nothing. The machine sighs. So do you."
        game.print(
            f"You pull the lever. The reels spin and stop:\n\n  {line}\n\n{verdict} You have ${game.vars['money']}."
        )

    # -- blackjack -----------------------------------------------------------------

    def _blackjack_start(self, game: Game) -> None:
        if not self._near(game, 56, 120):
            game.print("The blackjack table is in the middle of the floor. Walk up to it and sit like you belong.")
            return
        if self.bj is not None:
            game.print("You're already at the table. Bet, hit, or stand; those are the words.")
            return
        self.bj = {"bet": 0, "player": [], "dealer": [], "deck": []}
        game.print(
            'The dealer nods. "Minimum five, maximum a hundred." Type BET and a number, '
            "like BET 20. Then HIT or STAND. LEAVE when you've had enough, or nothing left."
        )

    def _deck(self, game: Game) -> list[str]:
        deck = [r + s for r in RANKS for s in SUITS]
        game.rng.shuffle(deck)
        return deck

    def _blackjack_bet(self, game: Game, amount: int | None) -> None:
        if self.bj is None:
            game.print("Bet on what? Sit at the blackjack table first, or pull a lever like an honest loser.")
            return
        if self.bj["player"]:
            game.print("The hand's in play. HIT or STAND.")
            return
        money = game.vars.get("money", 0)
        if amount is None or not MIN_BET <= amount <= MAX_BET:
            game.print('"Five to a hundred," says the dealer. "Numbers. You know numbers?"')
            return
        if amount > money:
            game.print(f"\"You've got ${money}.\" The dealer doesn't need to say the rest.")
            return
        game.vars["money"] = money - amount
        deck = self._deck(game)
        player = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]
        self.bj.update({"bet": amount, "player": player, "dealer": dealer, "deck": deck})
        if hand_value(player) == 21:
            self._settle(game, natural=True)
            return
        game.print(f"You bet ${amount}.\n\nYou: {show(player)}\nDealer shows: {dealer[0]}\n\nHIT or STAND?")

    def _blackjack_said(self, game: Game, p: Parsed) -> bool:
        assert self.bj is not None
        in_hand = bool(self.bj["player"])
        if p.said("hit") or p.said("hit", "self"):
            if not in_hand:
                game.print("Bet first. BET 20, say. Then we'll talk about hitting.")
                return True
            deck: list[str] = self.bj["deck"]  # type: ignore[assignment]
            player: list[str] = self.bj["player"]  # type: ignore[assignment]
            player.append(deck.pop())
            if hand_value(player) > 21:
                self._settle(game, bust=True)
            else:
                dealer: list[str] = self.bj["dealer"]  # type: ignore[assignment]
                game.print(f"You: {show(player)}\nDealer shows: {dealer[0]}\n\nHIT or STAND?")
            return True
        if p.said("stand"):
            if not in_hand:
                game.print("You're standing. Metaphorically you're sitting. Bet something.")
                return True
            self._settle(game)
            return True
        if p.verb in ("drop", "enter", "stand") and (len(p.words) == 1 or p.has("blackjack", "stool")):
            if in_hand:
                game.print("Finish the hand. The dealer's eyes say so, and so does the man by the door.")
            else:
                self.bj = None
                game.print(f"You leave the table with ${game.vars.get('money', 0)}, which is a number, and a lesson.")
            return True
        return False

    def _settle(self, game: Game, natural: bool = False, bust: bool = False) -> None:
        assert self.bj is not None
        bet: int = self.bj["bet"]  # type: ignore[assignment]
        player: list[str] = self.bj["player"]  # type: ignore[assignment]
        dealer: list[str] = self.bj["dealer"]  # type: ignore[assignment]
        deck: list[str] = self.bj["deck"]  # type: ignore[assignment]
        if bust:
            outcome = f"You: {show(player)}\n\nBust. The dealer sweeps ${bet} away without a flicker."
        else:
            while hand_value(dealer) < 17:
                dealer.append(deck.pop())
            pv, dv = hand_value(player), hand_value(dealer)
            head = f"You: {show(player)}\nDealer: {show(dealer)}\n\n"
            if natural:
                win = bet + bet * 3 // 2
                game.vars["money"] += win
                game.award("blackjack_win", 2)
                outcome = head + f"Blackjack! Paid three to two: ${win}."
            elif dv > 21 or pv > dv:
                game.vars["money"] += bet * 2
                game.award("blackjack_win", 2)
                outcome = head + ("Dealer busts. " if dv > 21 else "You win. ") + f"${bet * 2} slides your way."
            elif pv == dv:
                game.vars["money"] += bet
                outcome = head + "Push. Your money comes back, unimpressed."
            else:
                outcome = head + f"Dealer wins. ${bet} goes home with the house."
        self.bj.update({"bet": 0, "player": [], "dealer": [], "deck": []})
        game.print(f"{outcome} You have ${game.vars['money']}.\n\nBET again, or LEAVE.")

    # -- the ring ------------------------------------------------------------------

    def _buy_ring(self, game: Game) -> None:
        if not self._near(game, 116, 160):
            game.print("The prize counter is on the right. Walk over; the lady won't shout prices.")
            return
        if game.has("ring"):
            game.print("You have the ring. One is traditional. Two is a conversation you don't want.")
            return
        money = game.vars.get("money", 0)
        if money < RING_PRICE:
            game.print(
                f'"Two hundred and fifty." You have ${money}. "The tables are that way," she says, kindly, '
                "which is worse."
            )
            return
        game.vars["money"] = money - RING_PRICE
        game.give("ring")
        game.award("ring", 5)
        game.print(
            f"You count out ${RING_PRICE}. The prize lady lifts the ring from its velvet finger "
            'and drops it in your palm. "Congratulations," she says, "or condolences. It\'s '
            f'the same box." You have ${game.vars["money"]} left.'
        )
