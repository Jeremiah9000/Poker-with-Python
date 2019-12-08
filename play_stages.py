import itertools
from collections import Counter
from card_and_deck import *
from gui import ask_app


def clear_board(game, standard_deck):
    game['possible_responses'].clear()
    game['community_cards'].clear()
    game['deck'] = standard_deck
    game['deck'].shuffle()
    game['pot'] = 0
    game['pot_dict'].clear()
    game['action_counter'] = 0
    game['highest_stake'] = 0
    game['round_over'] = False
    for player in game['players']:
        player.refresh()

    #  Find first player not out and rotate them to the back, then break
    #  This is to help rotate assignments
    for player in game['players']:
        if player.isOut:
            pass
        else:
            game['players'].append(game['players'].pop(game['players'].index(player)))
            break


def end_round(game):
    for player in game['players']:
        if player.chips <= 0:
            player.isOut = True
            print(f"{player.name} is out of the game!")
    players_still_in = []
    for player in game['players']:
        if not player.isOut:
            players_still_in.append(player)
    if len(players_still_in) == 1:
        players_still_in[0].isWinner = True
        game['game_over'] = True
        print(f"Game is over: {players_still_in[0].name} wins with {players_still_in[0].chips}!")
        quit()
    clear_board(game, StandardDeck())
    #  if str(ask_app("Start a new round? (yes/no)")) == "yes":
    #      print("\n\n\t\t\t\t--ROUND OVER--")
    #      print("\n\n\t\t\t--STARTING NEW ROUND--\n")
    #      game['round_counter'] += 1
    #      return
    #  else:
    #      quit()


def score_all(game):
    [hand_scorer(game, player) for player in game['players'] if not player.isOut]
    [score_interpreter(player) for player in game['players'] if not player.isOut]


def hand_scorer(game, player):
    #  seven_cards is all the seven cards available to a player (5 community cards + 2 player cards)
    seven_cards = player.cards + game['community_cards']

    #  all_hand_combos is a list of all possible combinations of 5 cards from the 7 cards total
    all_hand_combos = list(itertools.combinations(seven_cards, 5))

    #  the following empty dict will be used to put hand combo as key, and its score as value
    all_score_possibilities = {}

    for hand_combo in all_hand_combos:
        #  for all cards in hand_combo, we are going to separate values and suits in their
        #  own lists for easier evaluation
        suit_list = []
        value_list = []
        for card in hand_combo:
            suit_list.append(card.suit)
            value_list.append(card.value)

        #  scores for an individual player will look like:
        #  [score0, score1, score2, score3, score4, score5, score6, score7]
        #  a score, like score0, will be an integer
        #
        #  I put all scores from all players in a list
        #  so we will have a list of lists of integers, representing scores from all players
        #
        #  I take advantage of how the max() function works with lists of integers.
        #  max() looks at the integer at index 0 when provided with multiple lists.
        #  if the integers at index 0 are the same number for every list,
        #  it will then look at and compare the integer at the next index
        #
        #  score0 is used to indicate hand rank
        #  with 0 being lowest (high card) to 9 as highest (royal flush)...
        #  ranks found at: https://www.cardplayer.com/rules-of-poker/hand-rankings
        #              or  https://www.cardschat.com/poker-hands.php
        #
        #  score0, score1, and score2 are somewhat like score modifiers,
        #               score1 will tell us the value of the pair or the three of a kind
        #               if two pair: score2 will tell us the value of the lowest value pair
        #               if full house: score2 will be value of the pair
        #  while score3 to score7 are initially set as the value for the cards in the hand
        #               in the order from highest value 12 (ace) to lowest value 0 (two)
        #
        #  for example: if a player has no special hand like pairs or a flush,
        #               all modifier scores will be 0
        #               the player will have to rely on their highest card
        #               which will start at score3.
        #               if any other player has even a pair (score0 = 1)
        #               the max() function used on a list of lists of integers
        #               will select the player with a pair...
        #               if no player has a special hand, then the high card will be the deciding factor
        #               if more than one player has the same high card
        #                       then the max() function will move on to next index
        #                       and the next highest card will be evaluated
        #
        #  the list of values is put in order from highest value to lowest value
        initial_value_check = list(reversed(sorted(value_list)))
        score0 = 0  # everyone was initially given a score0 of 0 (high card),
        score1 = 0  # their cards may later trigger an if statement giving them them a higher score0, score1, or score2
        score2 = 0
        score3 = initial_value_check.pop(0)
        score4 = initial_value_check.pop(0)
        score5 = initial_value_check.pop(0)
        score6 = initial_value_check.pop(0)
        score7 = initial_value_check.pop(0)
        list_of_pair_values = []
        other_cards_not_special = []
        pair_present = False
        pair_value = int
        value_counter = dict(Counter(value_list))  # provides frequency of each value in hand
        for value_name, count in value_counter.items():
            if count == 2:
                pair_present = True  # a pair has been found in a hand
                pair_value = value_name
                list_of_pair_values.append(value_name)
        if pair_present:
            for value in value_list:
                if value not in list_of_pair_values:  # finds values in hand, but not in pair
                    other_cards_not_special.append(value)
            other_cards_not_special = list(reversed(sorted(other_cards_not_special)))
            if len(set(list_of_pair_values)) == 1:
                score0 = 1  # because a pair was found, player at least has a score0 of 1 at this point
                score1 = max(list_of_pair_values)  # score1 becomes the value of a card in the pair
                try:
                    score2 = other_cards_not_special.pop(0)  # the rest of the scores are set
                    score3 = other_cards_not_special.pop(0)  # to the value of the other cards
                    score4 = other_cards_not_special.pop(0)  # that are not a part of the pair
                    score5 = other_cards_not_special.pop(0)  # starting with the highest of those cards
                    score6 = other_cards_not_special.pop(0)  # because this list of values was sorted and
                    score7 = other_cards_not_special.pop(0)  # then reversed
                except IndexError:
                    pass
            if len(set(list_of_pair_values)) == 2:
                # Two pairs have been found
                list_of_pair_values = list(reversed(sorted(list_of_pair_values)))
                score0 = 2
                score1 = list_of_pair_values.pop(0)
                score2 = list_of_pair_values.pop(0)
                try:
                    score3 = other_cards_not_special.pop(0)
                    score4 = other_cards_not_special.pop(0)
                    score5 = other_cards_not_special.pop(0)
                    score6 = other_cards_not_special.pop(0)
                    score7 = other_cards_not_special.pop(0)
                except IndexError:
                    pass
        three_of_a_kind_value = int
        other_cards_not_special = []
        three_of_a_kind_present = False
        for value_name, count in value_counter.items():
            if count == 3:
                three_of_a_kind_present = True  # Three of a kind has been found
                three_of_a_kind_value = value_name
        if three_of_a_kind_present:
            for value in value_list:
                if value != three_of_a_kind_value:
                    other_cards_not_special.append(value)
            other_cards_not_special = list(reversed(sorted(other_cards_not_special)))
            score0 = 3
            score1 = three_of_a_kind_value
            try:
                score2 = other_cards_not_special.pop(0)
                score3 = other_cards_not_special.pop(0)
                score4 = other_cards_not_special.pop(0)
                score5 = other_cards_not_special.pop(0)
                score6 = other_cards_not_special.pop(0)
                score7 = other_cards_not_special.pop(0)
            except IndexError:
                pass
        if sorted(value_list) == list(range(min(value_list), max(value_list) + 1)):
            # values of hand have been found to be in sequential continuous order (straight)
            score0 = 4
            score1 = max(value_list)
        if sorted(value_list) == [0, 1, 2, 3, 12]:
            # special case straight because ace can be highest and lowest value
            score0 = 4
            score1 = 3
        if len(set(suit_list)) == 1:
            # set() is used to get rid of any duplicates in list of suits in the hand
            # if the length of that set is 1, that means all suits in the hand were the same (duplicate)
            # this means a flush has been found
            score0 = 5
            score1 = max(value_list)
        if three_of_a_kind_present and pair_present:
            # a full house has been found
            score0 = 6
            score1 = three_of_a_kind_value
            score2 = pair_value
        four_of_a_kind_value = int
        other_card_value = int
        four_of_a_kind = False
        for value_name, count in value_counter.items():
            if count == 4:
                # a four of a kind has been found
                four_of_a_kind_value = value_name
                four_of_a_kind: True
        for value in value_list:
            if value != four_of_a_kind_value:
                other_card_value = value
        if four_of_a_kind:
            score0 = 7
            score1 = four_of_a_kind_value
            score2 = other_card_value
        if sorted(value_list) == [0, 1, 2, 3, 12] and len(set(suit_list)) == 1:
            # a special case straight flush has been found
            score0 = 8
            score1 = 3
        if sorted(value_list) == list(range(min(value_list), max(value_list) + 1)) and len(set(suit_list)) == 1:
            # a straight flush has been found
            score0 = 8
            score1 = max(value_list)
            if max(value_list) == 12:
                # a royal flush has been found
                score0 = 9
        all_score_possibilities[hand_combo] = [score0, score1, score2, score3, score4, score5, score6, score7]
    for hand, score in all_score_possibilities.items():
        if score == max(all_score_possibilities.values()):
            player.winning_hand = hand
            player.score = max(all_score_possibilities.values())


def score_interpreter(player):
    hand_ranks = ["High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush",
                  "Full House",
                  "Four of a Kind", "Straight Flush", "Royal Flush"]
    value_names = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                   "Jack",
                   "Queen",
                   "King", "Ace"]
    hand_rank = hand_ranks[player.score[0]]
    mod1 = value_names[player.score[1]]
    mod2 = value_names[player.score[2]]
    mod3 = value_names[player.score[3]]
    mod4 = value_names[player.score[4]]
    mod5 = value_names[player.score[5]]
    mod6 = value_names[player.score[6]]
    mod7 = value_names[player.score[7]]
    if player.score[0] == 0:
        player.score_interpretation = hand_rank + ": " + mod3 + " -Kickers:" + mod4 + mod5 + mod6 + mod7
    elif player.score[0] == 1:
        player.score_interpretation = hand_rank + ": " + mod1 + "s -Kickers:" + mod2 + mod3 + mod4
    elif player.score[0] == 2:
        player.score_interpretation = hand_rank + ": " + mod1 + "s" + " and " + mod2 + "s -Kicker:" + mod3
    elif player.score[0] == 3:
        player.score_interpretation = hand_rank + ": " + mod1 + "s -Kickers:" + mod2 + mod3
    elif player.score[0] == 4:
        player.score_interpretation = hand_rank + ": " + mod1 + " High"
    elif player.score[0] == 5:
        player.score_interpretation = hand_rank + ": " + mod1 + " High"
    elif player.score[0] == 6:
        player.score_interpretation = hand_rank + ": " + mod1 + "s" + " and " + mod2 + "s"
    elif player.score[0] == 7:
        player.score_interpretation = hand_rank + ": " + mod1 + "s -Kicker:" + mod2
    elif player.score[0] == 8:
        player.score_interpretation = hand_rank + ": " + mod1 + " High"
    elif player.score[0] == 9:
        player.score_interpretation = hand_rank


def find_winners(game):
    players_in = []
    for player in game['players']:
        if not player.isOut:
            players_in.append(player)
    if len(players_in) == 1:
        players_in[0].isWinner = True
        players_in[0].chips += game['pot']
    else:
        list_of_stakes = []
        for player in players_in:
            list_of_stakes.append(player.stake)
        list_of_stakes = list(set(list_of_stakes))
        list_of_stakes = sorted(list_of_stakes)
        list_of_players_at_stake = []
        list_of_list_of_players_at_stake = []
        for i in range(len(list_of_stakes)):
            for player in players_in:
                if player.stake >= list_of_stakes[i]:
                    list_of_players_at_stake.append(player)
            list_of_list_of_players_at_stake.append(list(set(list_of_players_at_stake)))
            list_of_players_at_stake.clear()
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
            list_of_pots.append(list_of_pot_seeds[i] * len(list_of_list_of_players_at_stake[i]))
        for i in range(len(list_of_pots)):
            winners = []
            list_of_scores_eligible = []
            for player in list_of_list_of_players_at_stake[i]:
                if player.isFolded:
                    pass
                else:
                    list_of_scores_eligible.append(player.score)
            max_score = max(list_of_scores_eligible)
            for player in list_of_list_of_players_at_stake[i]:
                if player.isFolded:
                    pass
                else:
                    if player.score == max_score:
                        player.isWinner = True
                        winners.append(player)
            prize = int(list_of_pots[i] / len(winners))
            for player in winners:
                player.chips += prize
                game['pot'] -= prize


def establish_player_attributes(players):
    address_assignment = 0
    players_still_in = []

    for player in players:
        if player.isOut:
            pass
        else:
            players_still_in.append(player)

    players_still_in[address_assignment].isDealer = True
    address_assignment = (address_assignment + 1) % len(players_still_in)
    players_still_in[address_assignment].isSmallBlind = True
    address_assignment = (address_assignment + 1) % len(players_still_in)
    players_still_in[address_assignment].isBigBlind = True
    address_assignment = (address_assignment + 1) % len(players_still_in)
    players_still_in[address_assignment].isFirstActor = True


def act_one(game):
    small_blind = object
    big_blind = object
    for player in game['players']:
        if player.isSmallBlind:
            small_blind = player
        elif player.isBigBlind:
            big_blind = player
    if game['small_blind'] > small_blind.chips:
        small_blind.stake += small_blind.chips
        game['highest_stake'] = small_blind.chips
        game['pot'] += small_blind.chips
        small_blind.chips = 0
        print(f"{small_blind.name} is all-in!")
        small_blind.all_in = True
    else:
        small_blind.chips -= game['small_blind']
        small_blind.stake += game['small_blind']
        game['highest_stake'] = game['small_blind']
        game['pot'] += game['small_blind']
    if game['big_blind'] > big_blind.chips:
        big_blind.stake += big_blind.chips
        game['highest_stake'] = big_blind.chips
        game['pot'] += big_blind.chips
        big_blind.chips = 0
        print(f"{big_blind.name} is all-in!")
        big_blind.all_in = True
    else:
        big_blind.chips -= game['big_blind']
        big_blind.stake += game['big_blind']
        game['highest_stake'] = game['big_blind']
        game['pot'] += game['big_blind']


def find_starting_index(game):
    players_not_out = []
    first_actor = object
    for player in game['players']:
        if not player.isOut:
            players_not_out.append(player)
            if player.isFirstActor:
                first_actor = player
    return players_not_out.index(first_actor), players_not_out


def start_asking_loop(game, starting_index, players_not_out):
    players_ready = []
    for player in players_not_out:
        player.ready = False
    while True:
        acting_player = players_not_out[starting_index]
        acting_player.isActing = True
        ready_player, players_ready = ask_and_receive_answers(game, acting_player, players_ready)
        acting_player.isActing = False
        starting_index += 1
        starting_index %= len(players_not_out)
        if ready_player:
            players_ready.append(ready_player)
        if len(players_ready) == len(players_not_out):
            break


def ask_and_receive_answers(game, player, players_ready):
    player.stake_gap = game['highest_stake'] - player.stake
    if player.isAll_in or player.isFolded or game['round_over']:
        return player, players_ready
    if player.chips <= 0:
        print(f"{player.name} is all in!")
        player.isAll_in = True
    print(f"Highest stake: {game['highest_stake']}")
    print(f"Put in at least {player.stake_gap} to stay in.\nDon't Have that much? You'll have to go all-in!")
    print(f"Chips available: {player.chips}")
    game['possible_responses'].clear()
    if player.stake_gap > 0:
        game['possible_responses'].append("fold")
        if player.stake_gap == player.chips:
            game['possible_responses'].append("all_in_exact")
        if player.stake_gap > player.chips:
            game['possible_responses'].append("all_in_partial")
        if player.stake_gap < player.chips:
            game['possible_responses'].append("call_exact")
            game['possible_responses'].append("call_and_raise")
            game['possible_responses'].append("call_and_all_in")
    if player.stake_gap == 0:
        game['possible_responses'].append("check")
        game['possible_responses'].append("raise")
        game['possible_responses'].append("fold")
        game['possible_responses'].append("all_in")
    while True:
        print(game['possible_responses'])
        response = str(ask_app(f"{player}'s action\n->", game))
        if response not in game['possible_responses']:
            print("Invalid response")
            continue
        elif response == "all_in_partial":
            player.stake += player.chips
            game['pot'] += player.chips
            player.stake_gap -= player.chips
            player.chips = 0
            print(f"{player.name} is all-in!")
            player.isAll_in = True
            return player, players_ready
        elif response == "all_in_exact":
            print(f"{player.name} is all-in!")
            player.isAll_in = True
            player.stake += player.stake_gap
            game['pot'] += player.stake_gap
            player.chips = 0
            player.stake_gap = 0
            return player, players_ready
        elif response == "fold":
            player.isFolded = True
            folded_players = []
            players_not_out = []
            for player in game['players']:
                if player.isFolded:
                    folded_players.append(player)
                if not player.isOut:
                    players_not_out.append(player)
            if len(folded_players) == (len(players_not_out) - 1):
                game['round_over'] = True
                for player in players_not_out:
                    if not player.isFolded:
                        print(f"{player} wins!")
                        player.isWinner = True
            return player, players_ready
        elif response == "call_exact":
            player.stake += player.stake_gap
            game['pot'] += player.stake_gap
            player.chips -= player.stake_gap
            player.stake_gap = 0
            return player, players_ready
        elif response == "check":
            player.stake_gap = 0
            return player, players_ready
        elif response == "raise":
            game['need_raise_info'] = True
            while True:
                bet = int(
                    ask_app(f"How much would {player.name} like to raise? ({player.chips} available)\n->",
                            game))
                if bet > player.chips or bet <= 0:
                    print("Invalid response")
                    continue
                elif bet == player.chips:
                    print(f"{player.name} is all-in!")
                    player.isAll_in = True
                game['need_raise_info'] = False
                player.stake += bet
                game['pot'] += bet
                player.chips -= bet
                game['highest_stake'] = player.stake
                players_ready.clear()
                player.stake_gap = 0
                return player, players_ready
        elif response == "call_and_raise":
            game['need_raise_info'] = True
            player.stake += player.stake_gap
            game['pot'] += player.stake_gap
            player.chips -= player.stake_gap
            player.stake_gap = 0
            while True:
                try:
                    bet = int(
                        ask_app(f"How much would {player.name} like to raise? ({player.chips} available)\n->",
                                game))
                except ValueError:
                    continue
                if bet > player.chips or bet <= 0:
                    print("Invalid response")
                    continue
                if bet == player.chips:
                    print(f"{player.name} is all-in!")
                    player.isAll_in = True
                game['need_raise_info'] = False
                player.stake += bet
                game['pot'] += bet
                player.chips -= bet
                game['highest_stake'] = player.stake
                players_ready.clear()
                return player, players_ready
        elif response == "call_and_all_in":
            player.stake += player.stake_gap
            game['pot'] += player.stake_gap
            player.chips -= player.stake_gap
            player.stake_gap = 0
            player.stake += player.chips
            game['pot'] += player.chips
            player.stake_gap -= player.chips
            player.chips = 0
            print(f"{player.name} is all-in!")
            player.isAll_in = True
            game['highest_stake'] = player.stake
            players_ready.clear()
            return player, players_ready
        elif response == "all_in":
            player.stake_gap = 0
            player.stake += player.chips
            game['pot'] += player.chips
            player.chips = 0
            print(f"{player.name} is all-in!")
            player.isAll_in = True
            game['highest_stake'] = player.stake
            players_ready.clear()
            return player, players_ready
        print("Invalid Response")


def play(game):
    game['deck'].shuffle()
    establish_player_attributes(game['players'])
    deal_hole(game['players'], game['deck'])
    act_one(game)
    starting_index, players_not_out = find_starting_index(game)
    start_asking_loop(game, starting_index, players_not_out)
    if not game['round_over']:
        deal_flop(game['community_cards'], game['deck'])
    if not game['round_over']:
        find_starting_index(game)
    if not game['round_over']:
        deal_turn(game['community_cards'], game['deck'])
    if not game['round_over']:
        find_starting_index(game)
    if not game['round_over']:
        deal_river(game['community_cards'], game['deck'])
    if not game['round_over']:
        find_starting_index(game)
    if not game['round_over']:
        score_all(game)
    find_winners(game)
    game_info_q.put(game)
    show_game_info(game)

    game['round_over'] = True
    print('winners: ', [player for player in game['players'] if player.isWinner])
    end_round(game)
