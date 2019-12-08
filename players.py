class Player(object):
    def __init__(self, name=None):
        self.name = name
        self.chips = 0
        self.stake = 0
        self.stake_gap = 0
        self.cards = []
        self.score = []
        self.fold = False
        self.ready = False
        self.all_in = False
        self.list_of_special_attributes = []
        self.win = False

player1 = Player("Mike")

