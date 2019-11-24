import pprint

game = {
    "game_over": False,
    "round_over": False,
    "need_raise_info": False,  # Helps prompt asking how much chips to raise in gui
    "players": [],
    "possible_responses": [],
    "community_cards": [],
    "round_counter": 0,
    "action_counter": 0,  # Keeps track of number of actions during 1 turn
    "highest_stake": 0,  # Highest bet so far in a round
    "pot": 0,
    "pot_dict": {},  # Helps with split-pots
    "deck": [],
    "starting_chips": 500,
    "small_blind": 25,
    "big_blind": 50
}


def show_game_info(game):
    pprint.pprint(game)
