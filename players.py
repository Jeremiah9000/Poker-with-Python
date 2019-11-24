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
        #  if self.isDealer:
        #      all_info += " DEALER"
        #  if self.isSmallBlind:
        #      all_info += " SMALL BLIND"
        #  if self.isBigBlind:
        #      all_info += " BIG BLIND"
        #  if self.isFirstActor:
        #      all_info += " FIRST ACTOR"
        if self.winning_hand:
            all_info += f" best hand combo: {self.winning_hand}"
        if self.isWinner:
            all_info += " -WINNER-"
        return all_info
