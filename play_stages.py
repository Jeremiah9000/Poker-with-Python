from gui import ask_app
from hand_scoring import score_all
from find_winners import *
from establish_player_attributes import establish_player_attributes
from dealing_cards import *
from gui import game_info_q
from game_data import show_game_info
from end_round import end_round


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


def prep_and_start_ask_loop(game):
    players_not_out = []
    first_actor = object
    players_ready = []
    for player in game['players']:
        if not player.isOut:
            players_not_out.append(player)
            if player.isFirstActor:
                first_actor = player
    starting_index = players_not_out.index(first_actor)
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


def play(game):
    game['deck'].shuffle()
    establish_player_attributes(game['players'])
    deal_hole(game['players'], game['deck'])
    act_one(game)
    prep_and_start_ask_loop(game)
    if not game['round_over']:
        deal_flop(game['community_cards'], game['deck'])
    if not game['round_over']:
        prep_and_start_ask_loop(game)
    if not game['round_over']:
        deal_turn(game['community_cards'], game['deck'])
    if not game['round_over']:
        prep_and_start_ask_loop(game)
    if not game['round_over']:
        deal_river(game['community_cards'], game['deck'])
    if not game['round_over']:
        prep_and_start_ask_loop(game)
    if not game['round_over']:
        score_all(game)
    find_winners(game)
    game_info_q.put(game)
    show_game_info(game)

    game['round_over'] = True
    print('winners: ', [player for player in game['players'] if player.isWinner])
    end_round(game)
