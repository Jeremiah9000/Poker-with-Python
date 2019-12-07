import random  # For Shuffling Cards
from game_data import game

class Card(object):
    def __init__(self, value, suit):
        self.value = value  # example: Jack or Three
        self.suit = suit  # example: Spade or Diamond
        self.showing = True

    def SuitName(self, suit):
        """
        Return a suit name for a card, from Diamond to Spades 0 - 3.
        :param suit: Suit class variable.
        :return: Suit name.
        """
        return {
            0: "Diamonds",
            1: "Clubs",
            2: "Hearts",
            3: "Spades"
        }[suit]

    def ValueName(self, value):
        """
        Return a name for a value card, from two to ace 0 - 12.
        :param value: Value class variable.
        :return: Card name.
        """
        return {
            0: "Two",
            1: "Three",
            2: "Four",
            3: "Five",
            4: "Six",
            5: "Seven",
            6: "Eight",
            7: "Nine",
            8: "Ten",
            9: "Jack",
            10: "Queen",
            11: "King",
            12: "Ace"
        }[value]

    def __repr__(self):
        """
        Card image file names mirror this repr for calling images in gui.
        :return: Card description.
        """
        if self.showing:
            value_name = self.ValueName(self.value)
            suit_name = self.SuitName(self.suit)
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
        """
        Shuffles the deck.
        :return: Void.
        """
        self.shuffled = True
        random.shuffle(self)
        print("--deck shuffled--")

    def deal(self, location, times=1):
        """
        Deletes a card from the deck and adds it to location.
        :param location: Where we are sending the cards.
        :param times: How many cards we deal to that location.
        :return: Void.
        """
        for i in range(times):
            location.append(self.pop(0))

    def burn(self):
        """
        Deletes a card from the deck.
        :return: Void.
        """
        self.pop(0)
        print('card burnt')
