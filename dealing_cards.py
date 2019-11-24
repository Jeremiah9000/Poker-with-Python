#  Two cards to each player who is not out
def deal_hole(players, deck):
    for i in range(2):
        [deck.deal(player.cards, 1) for player in players if not player.isOut]


#  Three Cards to Community Cards in Game['community cards']
def deal_flop(community_cards, deck):
    deck.burn()
    print("\n--card burned--")
    deck.deal(community_cards, 3)
    print(f"\nCommunity Cards: {community_cards}")


#  One Card to Community Cards in Game['community cards']
def deal_turn(community_cards, deck):
    deck.burn()
    print("\n--card burned--")
    deck.deal(community_cards, 1)
    print(f"\nCommunity Cards: {community_cards}")


#  One Card to Community Cards in Game['community cards']
def deal_river(community_cards, deck):
    deck.burn()
    print("\n--card burned--")
    deck.deal(community_cards, 1)
    print(f"\nCommunity Cards: {community_cards}")
