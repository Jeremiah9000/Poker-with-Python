import random  # For Shuffling Cards
from game_data import game


class Card(object):
    def __init__(self, value, suit):
        self.value = value  # example: Jack or Three
        self.suit = suit  # example: Spade or Diamond
        self.showing = True

    def __repr__(self):
        value_name = ""
        suit_name = ""
        #  card image file names mirror this repr for calling images in gui
        #
        #  Two cards to Ace cards, with values 0 to 12
        #  Diamonds to Spades, with values 0 to 3
        if self.showing:
            if self.value == 0:
                value_name = "Two"
            elif self.value == 1:
                value_name = "Three"
            elif self.value == 2:
                value_name = "Four"
            elif self.value == 3:
                value_name = "Five"
            elif self.value == 4:
                value_name = "Six"
            elif self.value == 5:
                value_name = "Seven"
            elif self.value == 6:
                value_name = "Eight"
            elif self.value == 7:
                value_name = "Nine"
            elif self.value == 8:
                value_name = "Ten"
            elif self.value == 9:
                value_name = "Jack"
            elif self.value == 10:
                value_name = "Queen"
            elif self.value == 11:
                value_name = "King"
            elif self.value == 12:
                value_name = "Ace"
            if self.suit == 0:
                suit_name = "Diamonds"
            elif self.suit == 1:
                suit_name = "Clubs"
            elif self.suit == 2:
                suit_name = "Hearts"
            elif self.suit == 3:
                suit_name = "Spades"
            return value_name + " of " + suit_name
        else:
            return "default"


class StandardDeck(list):
    def __init__(self):
        super().__init__()
        self.shuffled = False
        suits = list(range(4))
        values = list(range(13))
        for value in values:
            for suit in suits:
                self.append(Card(value, suit))

    def __repr__(self):
        if self.shuffled:
            return f"Standard deck of cards: {len(self)} cards remaining -shuffled-"
        else:
            return f"Standard deck of cards: {len(self)} cards remaining -not shuffled-"

    def shuffle(self):
        self.shuffled = True
        random.shuffle(self)
        print("--deck shuffled--")

    #  'location' is where we are sending the cards, 'times' is how many cards we deal to that location.
    def deal(self, location, times=1):
        for i in range(times):
            location.append(self.pop(0))

    def burn(self):
        self.pop(0)
        print('card burnt')