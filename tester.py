from players import Player
from game_data import *

from card_and_deck import StandardDeck
from end_round import *
from play_stages import *

clear_board(game, StandardDeck())

names = ['Jeremiah', 'Anthony', 'Ezekiel', 'Gio', 'Karina']
game['players'] = [Player(name, game['starting_chips']) for name in names if name != ""]


play(game)
