def establish_player_attributes(players):
    address_assignment = 0
    players_still_in = []

    for player in players:
        if player.isOut:
            pass
        else:
            players_still_in.append(player)

    players_still_in[address_assignment].isDealer = True
    address_assignment = (address_assignment + 1) % len(players_still_in)
    players_still_in[address_assignment].isSmallBlind = True
    address_assignment = (address_assignment + 1) % len(players_still_in)
    players_still_in[address_assignment].isBigBlind = True
    address_assignment = (address_assignment + 1) % len(players_still_in)
    players_still_in[address_assignment].isFirstActor = True

