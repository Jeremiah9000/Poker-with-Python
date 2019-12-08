import pprint
from play_stages import play, clear_board, StandardDeck

game_data = {
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


class Player(object):
    def __init__(self, name, starting_chips):
        self.name = name
        self.chips = starting_chips
        self.stake = 0
        self.stake_gap = 0
        self.cards = []
        self.winning_hand = []
        self.score = []
        self.score_interpretation = ""
        self.action = None
        self.isFolded = False
        self.isReady = False
        self.isAll_in = False
        self.isOut = False  # isOut means player has 0 chips and is no longer in game
        self.isDealer = False
        self.isSmallBlind = False
        self.isBigBlind = False
        self.isFirstActor = False
        self.isActing = False
        self.isWinner = False

    #  restarts some player attributes necessary to be ready for a new round
    def refresh(self):
        self.score.clear()
        self.cards.clear()
        self.winning_hand = []
        self.score_interpretation = ""
        self.stake = 0
        self.stake_gap = 0
        self.action = None
        self.isReady = False
        self.isAll_in = False
        self.isFolded = False
        self.isDealer = False
        self.isSmallBlind = False
        self.isBigBlind = False
        self.isFirstActor = False
        self.isActing = False
        self.isWinner = False

    def __repr__(self):
        all_info = self.name
        if self.cards:
            all_info += " " + str(self.cards)
        return all_info


names = ['Jeremiah', 'Anthony', 'Ezekiel', 'Gio', 'Karina']
game_data['players'] = [Player(name, game_data['starting_chips']) for name in names if name != ""]

clear_board(game_data, StandardDeck())

pprint.pprint(game_data)

play(game_data)
