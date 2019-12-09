from unittest import (
    TestCase,
    main
)

from cards import (
    Card
)

VALUES = ("Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Jack",
    "Queen",
    "King",
    "Ace",
)

SUITS = ("Spades",
    "Diamonds",
    "Clubs",
    "Hearts",
)

class TestCards(TestCase):
    def test_cards_repr(self):
        zipped_values = zip(range(len(VALUES)), VALUES)
        zipped_suits = zip(range(len(SUITS)), SUITS)

        for value_index, value in zipped_values:
            for suit_index, suit in zipped_suits:
                card = Card(value_index, suit_index)

                self.assertEqual(str(card), f"{value} of {suit}")

if __name__ == "__main__":
    main()