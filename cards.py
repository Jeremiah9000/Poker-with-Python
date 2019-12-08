import random


class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        value_name = ""
        suit_name = ""
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
            suit_name = "Spades"
        elif self.suit == 1:
            suit_name = "Diamonds"
        elif self.suit == 2:
            suit_name = "Clubs"
        elif self.suit == 3:
            suit_name = "Hearts"
        return value_name + " of " + suit_name


class StandardDeck(list):
    def __init__(self):
        super().__init__()
        suits = list(range(4))
        values = list(range(13))
        for value in values:
            for suit in suits:
                self.append(Card(value, suit))

    def shuffle(self):
        random.shuffle(self)
        print("deck shuffled")

    def deal(self, location):
        location.cards.append(self.pop(0))


deck = StandardDeck()
