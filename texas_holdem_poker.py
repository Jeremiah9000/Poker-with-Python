import random
import itertools
from collections import Counter
from tkinter import *
from PIL import ImageTk, Image  #  only non_standard dependency you need to DL
import threading
import queue
import time

VALUES = [
    "TWO", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
    "Jack", "Queen", "King", "Ace"
]
VALUE_NAME_MAP = dict(zip(range(12), VALUES))
SUIT_MAP = dict(zip(range(4), ["Diamonds", "Clubs", "Hearts", "Spades"]))


def main():
    class Card(object):
        def __init__(self, value, suit):
            self.value = value
            self.suit = suit
            self.showing = True

        def __repr__(self):
            if self.showing:
                value_name = VALUE_NAME_MAP[self.value]
                suit_name = SUIT_MAP[self.suit]
                return f"{value_name} of {suit_name}"
            return "[CARD]"

    class StandardDeck(list):
        def __init__(self):
            super().__init__()
            suits = list(range(4))
            values = list(range(13))
            [[self.append(Card(i, j)) for j in suits] for i in values]

        def __repr__(self):
            return f"Standard deck of cards\n{len(self)} cards remaining"

        def shuffle(self):
            random.shuffle(self)
            print("\n\n--deck shuffled--")

        def deal(self, location, times=1):
            for i in range(times):
                location.cards.append(self.pop(0))

        def burn(self):
            self.pop(0)

    class Player(object):
        def __init__(self, name=None):
            self.name = name
            self.chips = 0
            self.stake = 0
            self.stake_gap = 0
            self.cards = []
            self.score = []
            self.fold = False
            self.ready = False
            self.all_in = False
            self.list_of_special_attributes = []
            self.win = False

        def __repr__(self):
            name = self.name
            return name

    class Game(object):
        def __init__(self):
            self.need_raise_info = False
            self.game_over = False
            self.acting_player = Player()
            self.possible_responses = []
            self.round_counter = 0
            self.cards = []
            self.pot = 0
            self.pot_dict = {}
            self.pot_in_play = 0
            self.list_of_player_names = []
            self.dealer = Player()
            self.small_blind = Player()
            self.big_blind = Player()
            self.first_actor = Player()
            self.winners = []
            self.deck = StandardDeck()
            self.list_of_scores_from_eligible_winners = []
            self.setup = ask_app("Start?")
            while True:
                try:
                    self.number_of_players = len(self.setup["players"])
                    break
                except ValueError:
                    print("Invalid response")
            if 1 < self.number_of_players < 11:
                pass
            else:
                print("Invalid number of players")
                main()
            self.list_of_players = [Player(name) for name in self.setup["players"] if name != ""]
            while True:
                try:
                    self.starting_chips = int(self.setup["chips"][0])
                    if self.starting_chips > 0:
                        break
                    print("Invalid number, try greater than 0")
                except ValueError:
                    print("Invalid response")
                    continue
            for player in self.list_of_players:
                player.chips = self.starting_chips
            self.ready_list = []
            while True:
                try:
                    self.small_blind_amount = int(self.setup["chips"][1])
                    if self.starting_chips > self.small_blind_amount > 0:
                        break
                    print("Invalid number: try bigger than zero, smaller than starting chips")
                except ValueError:
                    print("Invalid response")
                    continue
            while True:
                try:
                    self.big_blind_amount = int(self.setup["chips"][2])
                    if self.starting_chips > self.big_blind_amount > self.small_blind_amount:
                        break
                    print("Invalid number: try bigger than small blind, smaller than starting chips")
                except ValueError:
                    print("Invalid response")
                    continue
            self.winner = None
            self.action_counter = 0
            self.attribute_list = ["d", "sb", "bb", "fa"]
            self.highest_stake = 0
            self.fold_list = []
            self.not_fold_list = []
            self.round_ended = False
            self.fold_out = False
            self.list_of_scores_eligible = []
            self.list_of_players_not_out = list(set(self.list_of_players))
            self.number_of_player_not_out = int(len(list(set(self.list_of_players))))

        def print_game_info(self):
            pass

        def print_round_info(self):
            print("\n")
            for player in self.list_of_players:
                print("\n")
                print(f"Name: {player.name}")
                print(f"Cards: {player.cards}")
                print(f"Player score: {player.score}")
                print(f"Chips: {player.chips}")
                print(f"Special Attributes: {player.list_of_special_attributes}")
                if player.fold:
                    print(f"Folded")
                if player.all_in:
                    print(f"All-in")
                print(f"Stake: {player.stake}")
                print(f"Stake-gap: {player.stake_gap}")
                print("\n")
            print(f"Pot: {self.pot}")
            print(f"Community cards: {self.cards}")
            print("\n")

        def establish_player_attributes(self):
            address_assignment = 0
            self.dealer = self.list_of_players_not_out[address_assignment]
            self.dealer.list_of_special_attributes.append("dealer")
            address_assignment += 1
            address_assignment %= len(self.list_of_players_not_out)
            self.small_blind = self.list_of_players_not_out[address_assignment]
            self.small_blind.list_of_special_attributes.append("small blind")
            address_assignment += 1
            address_assignment %= len(self.list_of_players_not_out)
            self.big_blind = self.list_of_players_not_out[address_assignment]
            self.big_blind.list_of_special_attributes.append("big blind")
            address_assignment += 1
            address_assignment %= len(self.list_of_players_not_out)
            self.first_actor = self.list_of_players_not_out[address_assignment]
            self.first_actor.list_of_special_attributes.append("first actor")
            self.list_of_players_not_out.append(self.list_of_players_not_out.pop(0))

        def deal_hole(self):
            for player in self.list_of_players_not_out:
                self.deck.deal(player, 2)

        def deal_flop(self):
            self.deck.burn()
            self.deck.deal(self, 3)

        def deal_turn(self):
            self.deck.burn()
            print("\n--card burned--")
            self.deck.deal(self, 1)
            print(f"\nCommunity Cards: {self.cards}")

        def deal_river(self):
            self.deck.burn()
            print("\n--card burned--")
            self.deck.deal(self, 1)
            print(f"\n\nCommunity Cards: {self.cards}")

        def hand_scorer(self, player):
            seven_cards = player.cards + self.cards
            all_hand_combos = list(itertools.combinations(seven_cards, 5))
            list_of_all_score_possibilities = []
            for i in all_hand_combos:
                suit_list = []
                value_list = []
                for j in i:
                    suit_list.append(j.suit)
                    value_list.append(j.value)
                initial_value_check = list(reversed(sorted(value_list)))
                score1 = 0
                score2 = 0
                score3 = 0
                score4 = initial_value_check.pop(0)
                score5 = initial_value_check.pop(0)
                score6 = initial_value_check.pop(0)
                score7 = initial_value_check.pop(0)
                score8 = initial_value_check.pop(0)
                list_of_pair_values = []
                other_cards_not_special = []
                pair_present = False
                pair_value = int
                value_counter = dict(Counter(value_list))
                for value_name, count in value_counter.items():
                    if count == 2:
                        pair_present = True
                        pair_value = value_name
                        list_of_pair_values.append(value_name)
                if pair_present:
                    for value in value_list:
                        if value not in list_of_pair_values:
                            other_cards_not_special.append(value)
                    other_cards_not_special = list(reversed(sorted(other_cards_not_special)))
                    if len(set(list_of_pair_values)) == 1:
                        score1 = 1
                        score2 = max(list_of_pair_values)
                        try:
                            score3 = other_cards_not_special.pop(0)
                            score4 = other_cards_not_special.pop(0)
                            score5 = other_cards_not_special.pop(0)
                            score6 = other_cards_not_special.pop(0)
                            score7 = other_cards_not_special.pop(0)
                            score8 = other_cards_not_special.pop(0)
                        except IndexError:
                            pass
                    if len(set(list_of_pair_values)) == 2:
                        list_of_pair_values = list(reversed(sorted(list_of_pair_values)))
                        score1 = 2
                        score2 = list_of_pair_values.pop(0)
                        score3 = list_of_pair_values.pop(0)
                        try:
                            score4 = other_cards_not_special.pop(0)
                            score5 = other_cards_not_special.pop(0)
                            score6 = other_cards_not_special.pop(0)
                            score7 = other_cards_not_special.pop(0)
                            score8 = other_cards_not_special.pop(0)
                        except IndexError:
                            pass
                three_of_a_kind_value = int
                other_cards_not_special = []
                three_of_a_kind_present = False
                for value_name, count in value_counter.items():
                    if count == 3:
                        three_of_a_kind_present = True
                        three_of_a_kind_value = value_name
                if three_of_a_kind_present:
                    for value in value_list:
                        if value != three_of_a_kind_value:
                            other_cards_not_special.append(value)
                    other_cards_not_special = list(reversed(sorted(other_cards_not_special)))
                    score1 = 3
                    score2 = three_of_a_kind_value
                    try:
                        score3 = other_cards_not_special.pop(0)
                        score4 = other_cards_not_special.pop(0)
                        score5 = other_cards_not_special.pop(0)
                        score6 = other_cards_not_special.pop(0)
                        score7 = other_cards_not_special.pop(0)
                        score8 = other_cards_not_special.pop(0)
                    except IndexError:
                        pass
                if sorted(value_list) == list(range(min(value_list), max(value_list) + 1)):
                    score1 = 4
                    score2 = max(value_list)
                if sorted(value_list) == [0, 1, 2, 3, 12]:
                    score1 = 4
                    score2 = 3
                if len(set(suit_list)) == 1:
                    score1 = 5
                    score2 = max(value_list)
                if three_of_a_kind_present and pair_present:
                    score1 = 6
                    score2 = three_of_a_kind_value
                    score3 = pair_value
                four_of_a_kind_value = int
                other_card_value = int
                four_of_a_kind = False
                for value_name, count in value_counter.items():
                    if count == 4:
                        four_of_a_kind_value = value_name
                        four_of_a_kind: True
                for value in value_list:
                    if value != four_of_a_kind_value:
                        other_card_value = value
                if four_of_a_kind:
                    score1 = 7
                    score2 = four_of_a_kind_value
                    score3 = other_card_value
                if sorted(value_list) == [0, 1, 2, 3, 12] and len(set(suit_list)) == 1:
                    score1 = 8
                    score2 = 3
                if sorted(value_list) == list(range(min(value_list), max(value_list) + 1)) and len(set(suit_list)) == 1:
                    score1 = 8
                    score2 = max(value_list)
                    if max(value_list) == 12:
                        score1 = 9
                list_of_all_score_possibilities.append([score1, score2, score3, score4, score5, score6, score7, score8])
            best_score = max(list_of_all_score_possibilities)
            player.score = best_score

        def score_all(self):
            for player in self.list_of_players_not_out:
                self.hand_scorer(player)

        def find_winners(self):
            if self.fold_out:
                for player in list(set(self.winners)):
                    player.chips += int((self.pot / len(list(set(self.winners)))))
                    print(f"{player.name} wins {int((self.pot / len(list(set(self.winners)))))} chips!")
            else:
                list_of_stakes = []
                for player in self.list_of_players_not_out:
                    list_of_stakes.append(player.stake)
                list_of_stakes = list(set(list_of_stakes))
                list_of_stakes = sorted(list_of_stakes)
                for stake in list_of_stakes:
                    print(stake)
                for player in self.list_of_players_not_out:
                    print(player.name)
                    print(player.stake)
                print(self.list_of_players_not_out)
                list_of_players_at_stake = []
                list_of_list_of_players_at_stake = []
                for i in range(len(list_of_stakes)):
                    for player in self.list_of_players_not_out:
                        if player.stake >= list_of_stakes[i]:
                            list_of_players_at_stake.append(player)
                    list_of_list_of_players_at_stake.append(list(set(list_of_players_at_stake)))
                    list_of_players_at_stake.clear()
                print(list_of_list_of_players_at_stake)
                list_of_pot_seeds = []
                for i in list_of_stakes:
                    list_of_pot_seeds.append(i)
                list_of_pot_seeds.reverse()
                for i in range(len(list_of_pot_seeds)):
                    try:
                        list_of_pot_seeds[i] -= list_of_pot_seeds[i + 1]
                    except IndexError:
                        pass
                list_of_pot_seeds.reverse()
                list_of_pots = []
                for i in range(len(list_of_pot_seeds)):
                    print(len(list_of_list_of_players_at_stake[i]))
                for i in range(len(list_of_pot_seeds)):
                    list_of_pots.append(list_of_pot_seeds[i] * len(list_of_list_of_players_at_stake[i]))
                for i in range(len(list_of_pots)):
                    winners = []
                    self.list_of_scores_eligible.clear()
                    for player in list_of_list_of_players_at_stake[i]:
                        if player.fold:
                            pass
                        else:
                            self.list_of_scores_eligible.append(player.score)
                    max_score = max(self.list_of_scores_eligible)
                    for player in list_of_list_of_players_at_stake[i]:
                        if player.fold:
                            pass
                        else:
                            if player.score == max_score:
                                player.win = True
                                winners.append(player)
                    prize = int(list_of_pots[i] / len(winners))
                    for player in winners:
                        print(f"{player.name} wins {prize} chips!")
                        player.chips += prize
                        self.pot -= prize
                for player in self.list_of_players_not_out:
                    if player.win:
                        print(
                            "\n" + player.name + ": " + str(
                                player.cards) + "\t<-WINNER WINNER WINNER WINNER WINNER WINNER "
                                                "WINNER WINNER" + "\n\t" + score_interpreter(player))
                    elif player.fold:
                        print("\n" + player.name + ": " + str(player.cards) + "\n\t" + "[FOLDED]")
                    else:
                        print("\n" + player.name + ": " + str(player.cards) + "\n\t" + score_interpreter(player))
                    print(f"\tScoreCode: {player.score}")
                    print(f"Pot: {self.pot}")
                [print(player.name, player.chips) for player in self.list_of_players_not_out]

        def clear_board(self):
            self.possible_responses.clear()
            self.cards.clear()
            self.deck = StandardDeck()
            self.deck.shuffle()
            self.pot = 0
            self.pot_dict.clear()
            self.winners.clear()
            self.list_of_scores_from_eligible_winners.clear()
            self.action_counter = 0
            self.highest_stake = 0
            self.fold_list.clear()
            self.not_fold_list.clear()
            self.fold_out = False
            self.list_of_scores_eligible.clear()
            self.round_ended = False
            for player in self.list_of_players:
                player.score.clear()
                player.cards.clear()
                player.stake = 0
                player.stake_gap = 0
                player.ready = False
                player.all_in = False
                player.fold = False
                player.list_of_special_attributes.clear()
                player.win = False

        def end_round(self):
            self.list_of_players_not_out = list(set(self.list_of_players_not_out))
            for player in self.list_of_players_not_out:
                if player.chips <= 0:
                    self.list_of_players_not_out.remove(player)
                    print(f"{player.name} is out of the game!")
            self.number_of_player_not_out = len(set(self.list_of_players_not_out))
            if self.number_of_player_not_out == 1:
                self.game_over = True
                self.winner = self.list_of_players_not_out[0]
                print(f"Game is over: {self.winner} wins with {self.winner.chips}!")
                quit()
            new_round = str(ask_app("Start a new round? (yes/no)"))
            if new_round == "yes":
                print("\n\n\t\t\t\t--ROUND OVER--")
                print("\n\n\t\t\t--STARTING NEW ROUND--\n")
                self.round_counter += 1
                pass
            else:
                quit()
            time.sleep(0.3)
            self.clear_board()

        def answer(self, player):
            player.stake_gap = self.highest_stake - player.stake
            if player.all_in or player.fold or self.fold_out:
                return True
            if player.chips <= 0:
                print(f"{player.name} is all in!")
                player.all_in = True
            print(f"Highest stake: {self.highest_stake}")
            print(f"Put in at least {player.stake_gap} to stay in.\nDon't Have that much? You'll have to go all-in!")
            print(f"Chips available: {player.chips}")
            self.possible_responses.clear()
            if player.stake_gap > 0:
                self.possible_responses.append("fold")
                if player.stake_gap == player.chips:
                    self.possible_responses.append("all_in_exact")
                if player.stake_gap > player.chips:
                    self.possible_responses.append("all_in_partial")
                if player.stake_gap < player.chips:
                    self.possible_responses.append("call_exact")
                    self.possible_responses.append("call_and_raise")
                    self.possible_responses.append("call_and_all_in")
            if player.stake_gap == 0:
                self.possible_responses.append("check")
                self.possible_responses.append("raise")
                self.possible_responses.append("fold")
                self.possible_responses.append("all_in")
            while True:
                print(self.possible_responses)
                response = str(ask_app(f"{player}'s action\n->", self))
                if response not in self.possible_responses:
                    print("Invalid response")
                    continue
                if response == "all_in_partial":
                    player.stake += player.chips
                    self.pot += player.chips
                    player.stake_gap -= player.chips
                    player.chips = 0
                    print(f"{player.name} is all-in!")
                    player.all_in = True
                    return True
                if response == "all_in_exact":
                    print(f"{player.name} is all-in!")
                    player.all_in = True
                    player.stake += player.stake_gap
                    self.pot += player.stake_gap
                    player.chips = 0
                    player.stake_gap = 0
                    return True
                if response == "fold":
                    player.fold = True
                    self.fold_list.append(player)
                    if len(self.fold_list) == (len(self.list_of_players_not_out) - 1):
                        for player in self.list_of_players_not_out:
                            if player not in self.fold_list:
                                self.fold_out = True
                                print(f"{player} wins!")
                                self.winners.append(player)
                                for player in self.winners:
                                    player.win = True
                                self.round_ended = True
                    return True
                if response == "call_exact":
                    player.stake += player.stake_gap
                    self.pot += player.stake_gap
                    player.chips -= player.stake_gap
                    player.stake_gap = 0
                    return True
                if response == "check":
                    player.stake_gap = 0
                    return True
                if response == "raise":
                    self.need_raise_info = True
                    while True:
                        bet = int(
                            ask_app(f"How much would {player.name} like to raise? ({player.chips} available)\n->",
                                    self))
                        if bet > player.chips or bet <= 0:
                            print("Invalid response")
                            continue
                        if bet == player.chips:
                            print(f"{player.name} is all-in!")
                            player.all_in = True
                        self.need_raise_info = False
                        player.stake += bet
                        self.pot += bet
                        player.chips -= bet
                        self.highest_stake = player.stake
                        self.ready_list.clear()
                        player.stake_gap = 0
                        return True
                if response == "call_and_raise":
                    self.need_raise_info = True
                    player.stake += player.stake_gap
                    self.pot += player.stake_gap
                    player.chips -= player.stake_gap
                    player.stake_gap = 0
                    while True:
                        try:
                            bet = int(
                                ask_app(f"How much would {player.name} like to raise? ({player.chips} available)\n->",
                                        self))
                        except ValueError:
                            continue
                        if bet > player.chips or bet <= 0:
                            print("Invalid response")
                            continue
                        if bet == player.chips:
                            print(f"{player.name} is all-in!")
                            player.all_in = True
                        self.need_raise_info = False
                        player.stake += bet
                        self.pot += bet
                        player.chips -= bet
                        self.highest_stake = player.stake
                        self.ready_list.clear()
                        return True
                if response == "call_and_all_in":
                    player.stake += player.stake_gap
                    self.pot += player.stake_gap
                    player.chips -= player.stake_gap
                    player.stake_gap = 0
                    player.stake += player.chips
                    self.pot += player.chips
                    player.stake_gap -= player.chips
                    player.chips = 0
                    print(f"{player.name} is all-in!")
                    player.all_in = True
                    self.highest_stake = player.stake
                    self.ready_list.clear()
                    return True
                if response == "all_in":
                    player.stake_gap = 0
                    player.stake += player.chips
                    self.pot += player.chips
                    player.chips = 0
                    print(f"{player.name} is all-in!")
                    player.all_in = True
                    self.highest_stake = player.stake
                    self.ready_list.clear()
                    return True
                print("Invalid Response")

        def ask_players(self):
            self.ready_list.clear()
            starting_index = self.list_of_players_not_out.index(self.first_actor)
            for player in self.list_of_players_not_out:
                player.ready = False
            while True:
                self.acting_player = self.list_of_players_not_out[starting_index]
                player_ready = self.answer(self.list_of_players_not_out[starting_index])
                starting_index += 1
                starting_index %= len(self.list_of_players_not_out)
                if player_ready:
                    self.ready_list.append("gogo")
                if len(self.ready_list) == len(self.list_of_players_not_out):
                    break

        def act_one(self):
            if self.small_blind_amount > self.small_blind.chips:
                self.small_blind.stake += self.small_blind.chips
                self.highest_stake = self.small_blind.chips
                self.pot += self.small_blind.chips
                self.small_blind.chips = 0
                print(f"{self.small_blind.name} is all-in!")
                self.small_blind.all_in = True
            else:
                self.small_blind.chips -= self.small_blind_amount
                self.small_blind.stake += self.small_blind_amount
                self.highest_stake = self.small_blind_amount
                self.pot += self.small_blind_amount
            if self.big_blind_amount > self.big_blind.chips:
                self.big_blind.stake += self.big_blind.chips
                self.highest_stake = self.big_blind.chips
                self.pot += self.big_blind.chips
                self.big_blind.chips = 0
                print(f"{self.big_blind} is all-in!")
                self.big_blind.all_in = True
            else:
                self.big_blind.chips -= self.big_blind_amount
                self.big_blind.stake += self.big_blind_amount
                self.highest_stake = self.big_blind_amount
                self.pot += self.big_blind_amount
            self.ask_players()

    class App(Tk):
        def __init__(self, *args, **kwargs):
            Tk.__init__(self, *args, **kwargs)
            self.game_object = object

            container = Frame(self)
            container.pack(side="top", fill="both", expand=True)
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            self.frames = {}

            list_of_frames = [StartPage, GamePage]

            for F in list_of_frames:
                frame = F(container, self)
                self.frames[F] = frame
                frame.grid(row=0, column=0, sticky="nsew")

            self.fresh = True
            self.show_frame(StartPage)

        def show_frame(self, context):
            frame = self.frames[context]
            print("waiting")
            if not self.fresh:
                time.sleep(0.1)
                frame.update(game_info_q.get())
            self.fresh = False
            frame.tkraise()

    class StartPage(Frame):
        def __init__(self, parent, controller):
            Frame.__init__(self, parent)

            height = 500
            width = 800
            canvas = Canvas(self, height=height, width=width, bg="light green")
            canvas.pack()

            left_frame = Frame(canvas, bg='green', bd=5)
            left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1, anchor='nw')
            name_frame = Frame(left_frame, bg="light green", bd=5)
            name_frame.place(relx=0.5, rely=0.17, relwidth=0.9, relheight=0.7, anchor="n")
            self.entry_p0 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p0.place(relwidth=0.5, relheight=0.2)
            self.entry_p1 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p1.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.2)
            self.entry_p2 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p2.place(relx=0, rely=0.2, relwidth=0.5, relheight=0.2)
            self.entry_p3 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p3.place(relx=0.5, rely=0.2, relwidth=0.5, relheight=0.2)
            self.entry_p4 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p4.place(relx=0, rely=0.4, relwidth=0.5, relheight=0.2)
            self.entry_p5 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p5.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.2)
            self.entry_p6 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p6.place(relx=0, rely=0.6, relwidth=0.5, relheight=0.2)
            self.entry_p7 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p7.place(relx=0.5, rely=0.6, relwidth=0.5, relheight=0.2)
            self.entry_p8 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p8.place(relx=0, rely=0.8, relwidth=0.5, relheight=0.2)
            self.entry_p9 = Entry(name_frame, font=("Courier", 12), bd=3)
            self.entry_p9.place(relx=0.5, rely=0.8, relwidth=0.5, relheight=0.2)
            enter_player_label = Label(left_frame, text="Player Names:", font=("Courier", 12), bd=3)
            enter_player_label.place(relx=0.25, rely=0.07, relwidth=0.5, relheight=0.05)
            # self.entry.bind("<Return>", lambda _: self.button_click(self.entry.get()))

            right_frame = Frame(canvas, bg='green', bd=5)
            right_frame.place(relx=1, rely=0, relwidth=0.5, relheight=1, anchor='ne')
            self.sc_label = Label(right_frame, text="Starting Chips:", font=("Courier", 12), bd=3)
            self.sc_label.place(relx=0.25, rely=0.1, relwidth=0.5, relheight=0.05)
            self.sc_entry = Entry(right_frame, font=("Courier"), bd=3)
            self.sc_entry.place(relx=0.5, rely=0.17, relwidth=0.5, relheight=0.07, anchor="n")

            self.sb_label = Label(right_frame, text="Small-Blind Chips:", font=("Courier", 12), bd=3)
            self.sb_label.place(relx=0.25, rely=0.33, relwidth=0.5, relheight=0.05)
            self.sb_entry = Entry(right_frame, font=("Courier"), bd=3)
            self.sb_entry.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.07, anchor="n")

            self.bb_label = Label(right_frame, text="Big-Blind Chips:", font=("Courier", 12), bd=3)
            self.bb_label.place(relx=0.25, rely=0.56, relwidth=0.5, relheight=0.05)
            self.bb_entry = Entry(right_frame, font=("Courier"), bd=3)
            self.bb_entry.place(relx=0.5, rely=0.63, relwidth=0.5, relheight=0.07, anchor="n")
            self.bb_entry.bind("<Return>", lambda _: self.button_click(self.entry_p0.get(), self.entry_p1.get(),
                                                                       self.entry_p2.get(), self.entry_p3.get(),
                                                                       self.entry_p4.get(), self.entry_p5.get(),
                                                                       self.entry_p6.get(),
                                                                       self.entry_p7.get(), self.entry_p8.get(),
                                                                       self.entry_p9.get(), self.sc_entry.get(),
                                                                       self.sb_entry.get(), self.bb_entry.get(),
                                                                       controller))

            button = Button(right_frame, text="START", font=("Courier", 12),
                            command=lambda: self.button_click(self.entry_p0.get(), self.entry_p1.get(),
                                                              self.entry_p2.get(), self.entry_p3.get(),
                                                              self.entry_p4.get(), self.entry_p5.get(),
                                                              self.entry_p6.get(),
                                                              self.entry_p7.get(), self.entry_p8.get(),
                                                              self.entry_p9.get(), self.sc_entry.get(),
                                                              self.sb_entry.get(), self.bb_entry.get(), controller))
            button.place(relx=0.5, rely=0.9, relwidth=0.3, relheight=0.1, anchor="n")

        def button_click(self, entry0, entry1, entry2, entry3, entry4, entry5, entry6, entry7, entry8, entry9, entrysc,
                         entrysb, entrybb, controller):
            entry_list = [entry0, entry1, entry2, entry3, entry4, entry5, entry6, entry7, entry8, entry9, entrysc,
                          entrysb, entrybb]
            player_entry_list = [entry0, entry1, entry2, entry3, entry4, entry5, entry6, entry7, entry8, entry9]
            print(player_entry_list)
            player_entry_list = list(set(player_entry_list))
            for player in player_entry_list:
                if player == "":
                    player_entry_list.remove(player)
            print(player_entry_list)
            if len(player_entry_list) < 2:
                print("not enough players")
                return
            chip_entry_list = [entrysc, entrysb, entrybb]
            for chips in chip_entry_list:
                try:
                    chips = int(chips)
                except ValueError:
                    print("Value Error")
                    return
                if chips == "" or chips <= 0:
                    print("chip entry error")
                    return
            if not int(entrysc) > int(entrybb) > int(entrysb):
                print("chip entry error2 ")
                return
            setup = {
                "players": player_entry_list,
                "chips": chip_entry_list
            }
            response_q.put(setup)
            game_event.set()
            controller.show_frame(GamePage)

    class GamePage(Frame):
        def __init__(self, parent, controller):
            Frame.__init__(self, parent)

            self.restart = False
            self.responses = []
            self.list_of_button_r = []
            height = 500
            width = 800
            canvas = Canvas(self, height=height, width=width, bg="light green")
            canvas.pack()

            left_frame = Frame(canvas, bg='green', bd=5)
            left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1, anchor='nw')
            name_frame = Frame(left_frame, bg="light green", bd=5)
            name_frame.place(relx=0.5, rely=0, relwidth=1, relheight=1, anchor="n")

            self.frame_p0 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p0.place(relwidth=0.5, relheight=0.2)
            self.name_label_p0 = Label(self.frame_p0, font=("Courier", 10), bd=3)
            self.name_label_p0.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p0 = Label(self.frame_p0, font=("Courier", 10), bd=3)
            self.chips_label_p0.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p0 = Frame(self.frame_p0, bd=3, relief="groove")
            self.cards_frame_p0.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p0 = Label(self.cards_frame_p0)
            self.card1_p0.place(relwidth=0.5, relheight=1)
            self.card2_p0 = Label(self.cards_frame_p0)
            self.card2_p0.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p0 = Label(self.frame_p0, bd=1, relief="groove")
            self.stake_label_p0.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p1 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p1.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.2)
            self.name_label_p1 = Label(self.frame_p1, font=("Courier", 10), bd=3)
            self.name_label_p1.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p1 = Label(self.frame_p1, font=("Courier", 10), bd=3)
            self.chips_label_p1.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p1 = Frame(self.frame_p1, bd=3, relief="groove")
            self.cards_frame_p1.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p1 = Label(self.cards_frame_p1)
            self.card1_p1.place(relwidth=0.5, relheight=1)
            self.card2_p1 = Label(self.cards_frame_p1)
            self.card2_p1.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p1 = Label(self.frame_p1, bd=1, relief="groove")
            self.stake_label_p1.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p2 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p2.place(relx=0, rely=0.2, relwidth=0.5, relheight=0.2)
            self.name_label_p2 = Label(self.frame_p2, font=("Courier", 10), bd=3)
            self.name_label_p2.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p2 = Label(self.frame_p2, font=("Courier", 10), bd=3)
            self.chips_label_p2.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p2 = Frame(self.frame_p2, bd=3, relief="groove")
            self.cards_frame_p2.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p2 = Label(self.cards_frame_p2)
            self.card1_p2.place(relwidth=0.5, relheight=1)
            self.card2_p2 = Label(self.cards_frame_p2)
            self.card2_p2.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p2 = Label(self.frame_p2, bd=1, relief="groove")
            self.stake_label_p2.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p3 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p3.place(relx=0.5, rely=0.2, relwidth=0.5, relheight=0.2)
            self.name_label_p3 = Label(self.frame_p3, font=("Courier", 10), bd=3)
            self.name_label_p3.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p3 = Label(self.frame_p3, font=("Courier", 10), bd=3)
            self.chips_label_p3.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p3 = Frame(self.frame_p3, bd=3, relief="groove")
            self.cards_frame_p3.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p3 = Label(self.cards_frame_p3)
            self.card1_p3.place(relwidth=0.5, relheight=1)
            self.card2_p3 = Label(self.cards_frame_p3)
            self.card2_p3.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p3 = Label(self.frame_p3, bd=1, relief="groove")
            self.stake_label_p3.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p4 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p4.place(relx=0, rely=0.4, relwidth=0.5, relheight=0.2)
            self.name_label_p4 = Label(self.frame_p4, font=("Courier", 10), bd=3)
            self.name_label_p4.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p4 = Label(self.frame_p4, font=("Courier", 10), bd=3)
            self.chips_label_p4.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p4 = Frame(self.frame_p4, bd=3, relief="groove")
            self.cards_frame_p4.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p4 = Label(self.cards_frame_p4)
            self.card1_p4.place(relwidth=0.5, relheight=1)
            self.card2_p4 = Label(self.cards_frame_p4)
            self.card2_p4.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p4 = Label(self.frame_p4, bd=1, relief="groove")
            self.stake_label_p4.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p5 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p5.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.2)
            self.name_label_p5 = Label(self.frame_p5, font=("Courier", 10), bd=3)
            self.name_label_p5.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p5 = Label(self.frame_p5, font=("Courier", 10), bd=3)
            self.chips_label_p5.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p5 = Frame(self.frame_p5, bd=3, relief="groove")
            self.cards_frame_p5.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p5 = Label(self.cards_frame_p5)
            self.card1_p5.place(relwidth=0.5, relheight=1)
            self.card2_p5 = Label(self.cards_frame_p5)
            self.card2_p5.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p5 = Label(self.frame_p5, bd=1, relief="groove")
            self.stake_label_p5.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p6 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p6.place(relx=0, rely=0.6, relwidth=0.5, relheight=0.2)
            self.name_label_p6 = Label(self.frame_p6, font=("Courier", 10), bd=3)
            self.name_label_p6.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p6 = Label(self.frame_p6, font=("Courier", 10), bd=3)
            self.chips_label_p6.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p6 = Frame(self.frame_p6, bd=3, relief="groove")
            self.cards_frame_p6.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p6 = Label(self.cards_frame_p6)
            self.card1_p6.place(relwidth=0.5, relheight=1)
            self.card2_p6 = Label(self.cards_frame_p6)
            self.card2_p6.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p6 = Label(self.frame_p6, bd=1, relief="groove")
            self.stake_label_p6.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p7 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p7.place(relx=0.5, rely=0.6, relwidth=0.5, relheight=0.2)
            self.name_label_p7 = Label(self.frame_p7, font=("Courier", 10), bd=3)
            self.name_label_p7.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p7 = Label(self.frame_p7, font=("Courier", 10), bd=3)
            self.chips_label_p7.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p7 = Frame(self.frame_p7, bd=3, relief="groove")
            self.cards_frame_p7.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p7 = Label(self.cards_frame_p7)
            self.card1_p7.place(relwidth=0.5, relheight=1)
            self.card2_p7 = Label(self.cards_frame_p7)
            self.card2_p7.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p7 = Label(self.frame_p7, bd=1, relief="groove")
            self.stake_label_p7.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p8 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p8.place(relx=0, rely=0.8, relwidth=0.5, relheight=0.2)
            self.name_label_p8 = Label(self.frame_p8, font=("Courier", 10), bd=3)
            self.name_label_p8.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p8 = Label(self.frame_p8, font=("Courier", 10), bd=3)
            self.chips_label_p8.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p8 = Frame(self.frame_p8, bd=3, relief="groove")
            self.cards_frame_p8.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p8 = Label(self.cards_frame_p8)
            self.card1_p8.place(relwidth=0.5, relheight=1)
            self.card2_p8 = Label(self.cards_frame_p8)
            self.card2_p8.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p8 = Label(self.frame_p8, bd=1, relief="groove")
            self.stake_label_p8.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            self.frame_p9 = Frame(name_frame, bd=3, relief="groove")
            self.frame_p9.place(relx=0.5, rely=0.8, relwidth=0.5, relheight=0.2)
            self.name_label_p9 = Label(self.frame_p9, font=("Courier", 10), bd=3)
            self.name_label_p9.place(relx=0, rely=0, relheight=(1 / 3), relwidth=0.38)
            self.chips_label_p9 = Label(self.frame_p9, font=("Courier", 10), bd=3)
            self.chips_label_p9.place(relx=0, rely=(1 / 3), relheight=(1 / 3), relwidth=0.38)
            self.cards_frame_p9 = Frame(self.frame_p9, bd=3, relief="groove")
            self.cards_frame_p9.place(relx=0.38, relheight=1, relwidth=0.62)
            self.card1_p9 = Label(self.cards_frame_p9)
            self.card1_p9.place(relwidth=0.5, relheight=1)
            self.card2_p9 = Label(self.cards_frame_p9)
            self.card2_p9.place(relx=0.5, relwidth=0.5, relheight=1)
            self.stake_label_p9 = Label(self.frame_p9, bd=1, relief="groove")
            self.stake_label_p9.place(relx=0, rely=(2 / 3), relheight=(1 / 3), relwidth=0.38)

            # self.entry.bind("<Return>", lambda _: self.button_click(self.entry.get()))

            right_frame = Frame(canvas, bg='green', bd=5)
            right_frame.place(relx=1, rely=0, relwidth=0.5, relheight=1, anchor='ne')

            self.cc_frame = Frame(right_frame, bd=2, relief="raised")
            self.cc_frame.place(relx=0, rely=0, relwidth=1, relheight=0.2)

            self.cc_1 = Label(self.cc_frame, bg="green")
            self.cc_1.place(relwidth=(.50 / 3), relheight=1)
            card_d1 = ImageTk.PhotoImage(
                Image.open("cards\default0.png").resize((55, 85), Image.ANTIALIAS))
            self.cc_1.image = card_d1
            self.cc_1.configure(image=card_d1)

            self.cc_2 = Label(self.cc_frame, bg="green")
            self.cc_2.place(relx=(.50 / 3), relwidth=(.50 / 3), relheight=1)
            card_d2 = ImageTk.PhotoImage(
                Image.open("cards\default1.png").resize((55, 85), Image.ANTIALIAS))
            self.cc_2.image = card_d2
            self.cc_2.configure(image=card_d2)

            self.cc_3 = Label(self.cc_frame, bg="green")
            self.cc_3.place(relx=(.50 / 3) * 2, relwidth=(.50 / 3), relheight=1)
            card_d3 = ImageTk.PhotoImage(
                Image.open("cards\default1.png").resize((55, 85), Image.ANTIALIAS))
            self.cc_3.image = card_d3
            self.cc_3.configure(image=card_d3)

            self.cc_4 = Label(self.cc_frame, bg="green")
            self.cc_4.place(relx=(.50 / 3) * 3, relwidth=0.25, relheight=1)
            card_d4 = ImageTk.PhotoImage(
                Image.open("cards\default1.png").resize((55, 85), Image.ANTIALIAS))
            self.cc_4.image = card_d4
            self.cc_4.configure(image=card_d4)

            self.cc_5 = Label(self.cc_frame, bg="green")
            self.cc_5.place(relx=((.50 / 3) * 3) + 0.25, relwidth=0.25, relheight=1)
            card_d5 = ImageTk.PhotoImage(
                Image.open("cards\default1.png").resize((55, 85), Image.ANTIALIAS))
            self.cc_5.image = card_d5
            self.cc_5.configure(image=card_d5)

            self.pot_label = Label(right_frame, text="pot: ", font=("Courier", 12), bd=3)
            self.pot_label.place(relx=0, rely=0.2, relwidth=0.5, relheight=0.04)

            # self.dealer_label = Label(right_frame, text="dealer: ", font=("Courier", 12), bd=3)
            # self.dealer_label.place(relx=0, rely=0.28, relwidth=0.5, relheight=0.04)

            # self.sb_label = Label(right_frame, text="small-blind: ", font=("Courier", 12), bd=3)
            # self.sb_label.place(relx=0, rely=0.33, relwidth=0.5, relheight=0.04)

            # self.bb_label = Label(right_frame, text="big-blind: ", font=("Courier", 12), bd=3)
            # self.bb_label.place(relx=0, rely=0.38, relwidth=0.5, relheight=0.04)

            self.action_frame = Frame(right_frame, bd=2, relief="raised", bg="green")
            self.action_frame.place(rely=0.5, relwidth=1, relheight=0.5)
            self.action_cover_label = Label(self.action_frame, bg="light green")
            self.action_cover_label.place(relx=0, rely=0, relheight=1, relwidth=1)

            self.actor_label = Label(self.action_frame, text="Actor: ", font=("Courier", 12), bd=3)
            self.actor_label.place(relwidth=1, relheight=0.06)

            self.new_round_label = Label(self.action_frame, text="New Round?", font=("Courier", 9), bd=3)
            self.new_round_label.place(relx=0.8, rely=0.05, relheight=0.1, relwidth=0.2)
            self.button_y = Button(self.action_frame, text="Yes", command=lambda: self.action_input("yes"))
            self.button_y.place(relx=0.8, rely=0.15, relheight=0.1, relwidth=0.2)
            self.button_n = Button(self.action_frame, text="No", command=lambda: self.action_input("no"))
            self.button_n.place(relx=0.8, rely=0.25, relheight=0.1, relwidth=0.2)

            self.raise_entry = Entry(self.action_frame, font=("Courier", 9), bd=3)
            self.raise_entry.place(relx=0, rely=1, relheight=0.12, relwidth=0.22, anchor="sw")
            self.raise_button = Button(self.action_frame, text="RAISE", font=("Courier", 9), bd=3, command=lambda: self.action_input(self.raise_entry.get()))
            self.raise_button.place(relx=0.22, rely=1, relheight=0.12, relwidth=0.22, anchor="sw")

            self.winner_label = Label(self.action_frame, font=("Courier", 12), bd=3)
            self.winner_label.place(relx=0, rely=(1/3), relwidth=0.75, relheight=0.3)



        def update(self, game):
            self.new_round_label.lower(self.action_cover_label)
            self.button_y.lower(self.action_cover_label)
            self.button_n.lower(self.action_cover_label)
            self.raise_entry.lower(self.action_cover_label)
            self.raise_button.lower(self.action_cover_label)
            self.winner_label.lower(self.action_cover_label)
            if self.restart:
                card1 = ImageTk.PhotoImage(Image.open(str("cards\default0.png")).resize((55, 85), Image.ANTIALIAS))
                self.cc_1.image = card1
                self.cc_1.configure(image=card1)

                card1 = ImageTk.PhotoImage(Image.open(str("cards\default0.png")).resize((55, 85), Image.ANTIALIAS))
                self.cc_2.image = card1
                self.cc_2.configure(image=card1)

                card1 = ImageTk.PhotoImage(Image.open(str("cards\default0.png")).resize((55, 85), Image.ANTIALIAS))
                self.cc_3.image = card1
                self.cc_3.configure(image=card1)

                card1 = ImageTk.PhotoImage(Image.open(str("cards\default0.png")).resize((55, 85), Image.ANTIALIAS))
                self.cc_4.image = card1
                self.cc_4.configure(image=card1)

                card1 = ImageTk.PhotoImage(Image.open(str("cards\default0.png")).resize((55, 85), Image.ANTIALIAS))
                self.cc_5.image = card1
                self.cc_5.configure(image=card1)
                self.restart = False
            if game.round_ended:
                time.sleep(0.3)
                self.new_round_label.lift(self.action_cover_label)
                self.button_y.lift(self.action_cover_label)
                self.button_n.lift(self.action_cover_label)
                winners = []
                scores = []
                for player in game.list_of_players_not_out:
                    if player.win:
                        winners.append(player)
                        scores.append(player.score)
                print(f"gui thinks winners are: {winners}")
                print(f"and thinks scores are: {scores}")
                if scores == [[]]:
                    self.winner_label["text"] = "Winner: " + str(winners)
                else:
                    try:
                        for player in game.list_of_players_not_out:
                            if player.win:
                                if player.score == max(scores):
                                    self.winner_label["text"] = "Winner: " + str(winners) + "\n" + score_interpreter(player)
                    except IndexError:
                        pass
                self.winner_label.lift(self.action_cover_label)

                self.restart = True

                return
            if game.need_raise_info:
                self.raise_entry.lift(self.action_cover_label)
                self.raise_button.lift(self.action_cover_label)
            try:
                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.cc_1.image = card1
                self.cc_1.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.cc_2.image = card1
                self.cc_2.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.cards[2]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.cc_3.image = card1
                self.cc_3.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.cards[3]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.cc_4.image = card1
                self.cc_4.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.cards[4]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.cc_5.image = card1
                self.cc_5.configure(image=card1)
            except IndexError:
                pass
            try:
                self.name_label_p0["text"] = game.list_of_players[0]
                self.name_label_p1["text"] = game.list_of_players[1]
                self.name_label_p2["text"] = game.list_of_players[2]
                self.name_label_p3["text"] = game.list_of_players[3]
                self.name_label_p4["text"] = game.list_of_players[4]
                self.name_label_p5["text"] = game.list_of_players[5]
                self.name_label_p6["text"] = game.list_of_players[6]
                self.name_label_p7["text"] = game.list_of_players[7]
                self.name_label_p8["text"] = game.list_of_players[8]
                self.name_label_p9["text"] = game.list_of_players[9]
            except IndexError:
                pass
            try:
                self.chips_label_p0["text"] = "Chips:\n" + str(game.list_of_players[0].chips)
                self.chips_label_p1["text"] = "Chips:\n" + str(game.list_of_players[1].chips)
                self.chips_label_p2["text"] = "Chips:\n" + str(game.list_of_players[2].chips)
                self.chips_label_p3["text"] = "Chips:\n" + str(game.list_of_players[3].chips)
                self.chips_label_p4["text"] = "Chips:\n" + str(game.list_of_players[4].chips)
                self.chips_label_p5["text"] = "Chips:\n" + str(game.list_of_players[5].chips)
                self.chips_label_p6["text"] = "Chips:\n" + str(game.list_of_players[6].chips)
                self.chips_label_p7["text"] = "Chips:\n" + str(game.list_of_players[7].chips)
                self.chips_label_p8["text"] = "Chips:\n" + str(game.list_of_players[8].chips)
                self.chips_label_p9["text"] = "Chips:\n" + str(game.list_of_players[9].chips)
            except IndexError:
                pass
            try:
                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[0].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p0.image = card1
                self.card1_p0.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[1].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p1.image = card1
                self.card1_p1.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[2].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p2.image = card1
                self.card1_p2.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[3].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p3.image = card1
                self.card1_p3.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[4].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p4.image = card1
                self.card1_p4.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[5].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p5.image = card1
                self.card1_p5.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[6].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p6.image = card1
                self.card1_p6.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[7].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p7.image = card1
                self.card1_p7.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[8].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p8.image = card1
                self.card1_p8.configure(image=card1)

                card1 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[9].cards[0]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card1_p9.image = card1
                self.card1_p9.configure(image=card1)
            except IndexError:
                pass
            try:
                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[0].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p0.image = card2
                self.card2_p0.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[1].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p1.image = card2
                self.card2_p1.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[2].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p2.image = card2
                self.card2_p2.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[3].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p3.image = card2
                self.card2_p3.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[4].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p4.image = card2
                self.card2_p4.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[5].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p5.image = card2
                self.card2_p5.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[6].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p6.image = card2
                self.card2_p6.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[7].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p7.image = card2
                self.card2_p7.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[8].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p8.image = card2
                self.card2_p8.configure(image=card2)

                card2 = ImageTk.PhotoImage(
                    Image.open("cards\\" + str(game.list_of_players[9].cards[1]) + ".png").resize((55, 85), Image.ANTIALIAS))
                self.card2_p9.image = card2
                self.card2_p9.configure(image=card2)
            except IndexError:
                pass
            try:
                self.stake_label_p0["text"] = "Stake: " + str(game.list_of_players[0].stake)
                self.stake_label_p1["text"] = "Stake: " + str(game.list_of_players[1].stake)
                self.stake_label_p2["text"] = "Stake: " + str(game.list_of_players[2].stake)
                self.stake_label_p3["text"] = "Stake: " + str(game.list_of_players[3].stake)
                self.stake_label_p4["text"] = "Stake: " + str(game.list_of_players[4].stake)
                self.stake_label_p5["text"] = "Stake: " + str(game.list_of_players[5].stake)
                self.stake_label_p6["text"] = "Stake: " + str(game.list_of_players[6].stake)
                self.stake_label_p7["text"] = "Stake: " + str(game.list_of_players[7].stake)
                self.stake_label_p8["text"] = "Stake: " + str(game.list_of_players[8].stake)
                self.stake_label_p9["text"] = "Stake: " + str(game.list_of_players[9].stake)
            except IndexError:
                pass
            self.pot_label["text"] = "Pot: " + str(game.pot)
            if game.game_over:
                self.actor_label["text"] = "Winner!: " + str(game.winner.name)
                return
            print(f"round ended {game.round_ended}")

            self.actor_label["text"] = str(game.acting_player.name)

            variable = StringVar(self.action_frame)
            variable.initialize("ACTION")
            w = OptionMenu(self.action_frame, variable, *game.possible_responses)
            w.place(relx=0, rely=0.05, relheight=0.1, relwidth=0.3)
            button_go = Button(self.action_frame, text="GO", font=("Courier", 10), command=lambda: self.action_input(variable.get()))
            button_go.place(relx=1, rely=1, relheight=0.3, relwidth=0.3, anchor="se")


        def action_input(self, entry0):

            response_q.put(entry0)
            game_event.set()
            time.sleep(0.1)
            if not game_info_q.empty():
                self.update(game_info_q.get())

    def score_interpreter(player):
        list_of_hand_types = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush",
                              "Full House",
                              "Four of a Kind", "Straight Flush", "Royal Flush"]
        list_of_values_to_interpret = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                                       "Jack",
                                       "Queen",
                                       "King", "Ace"]
        hand_type = list_of_hand_types[player.score[0]]
        mod1 = list_of_values_to_interpret[player.score[1]]
        mod2 = list_of_values_to_interpret[player.score[2]]
        mod3 = list_of_values_to_interpret[player.score[3]]
        if player.score[0] == 0:
            return hand_type + ": " + mod3
        if player.score[0] == 1:
            return hand_type + ": " + mod1 + "s"
        if player.score[0] == 2:
            return hand_type + ": " + mod1 + "s" + " and " + mod2 + "s"
        if player.score[0] == 3:
            return hand_type + ": " + mod1 + "s"
        if player.score[0] == 4:
            return hand_type + ": " + mod1 + " High"
        if player.score[0] == 5:
            return hand_type + ": " + mod1 + " High"
        if player.score[0] == 6:
            return hand_type + ": " + mod1 + "s" + " and " + mod2 + "s"
        if player.score[0] == 7:
            return hand_type + ": " + mod1 + "s"
        if player.score[0] == 8:
            return hand_type + ": " + mod1 + " High"
        if player.score[0] == 9:
            return hand_type

    def ask_app(question, game=""):
        print("asking...")
        print(question)
        answer = ""
        if game != "":
            game_info_q.put(game)
        game_event.wait()
        if not response_q.empty():
            answer = response_q.get()
        game_event.clear()

        return answer

    def update_gui(game1):
        print("updating gui...")
        print(game1)

    def play(game):
        game.deck.shuffle()
        game_info_q.put(game)
        update_gui(game)
        game.establish_player_attributes()
        game.deal_hole()
        game.print_round_info()
        game.act_one()
        game.print_round_info()
        if not game.round_ended:
            game.deal_flop()
            game.print_round_info()
        if not game.round_ended:
            game.ask_players()
            game.print_round_info()
        if not game.round_ended:
            game.deal_turn()
            game.print_round_info()
        if not game.round_ended:
            game.ask_players()
            game.print_round_info()
        if not game.round_ended:
            game.deal_river()
            game.print_round_info()
        if not game.round_ended:
            game.ask_players()
            game.print_round_info()
        if not game.round_ended:
            game.score_all()
            game.print_round_info()
        game.find_winners()
        game_info_q.put(game)

        game.print_round_info()
        game.round_ended = True
        print(game.winners, game.winner, [player for player in game.list_of_players_not_out if player.win])
        game.end_round()

    def run_app():
        app = App()
        app.mainloop()

    def run_game_data():
        game0 = Game()
        while True:
            play(game0)

    game_event = threading.Event()
    response_q = queue.Queue()
    game_info_q = queue.Queue()
    end_update = threading.Event()
    t1 = threading.Thread(target=run_app)
    t1.start()
    t2 = threading.Thread(target=run_game_data())
    t2.start()


if __name__ == "__main__":
    main()
