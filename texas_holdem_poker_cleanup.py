import random
import itertools
from collections import Counter

import requests



import time

import card_and_deck


def main():
    class Game(object):
        def __init__(self):




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

        





    def update_gui(game1):
        print("updating gui...")
        print(game1)



    def run_app():
        app = App()
        app.mainloop()

    def run_game_data():
        game0 = Game()
        while True:
            play(game0)




    end_update = threading.Event()

    t2 = threading.Thread(target=run_game_data())
    t2.start()


if __name__ == "__main__":
    main()



setup = ask_app("Start?")
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
