def find_winners(game):
    players_in = []
    for player in game['players']:
        if not player.isOut:
            players_in.append(player)
    if len(players_in) == 1:
        players_in[0].isWinner = True
        players_in[0].chips += game['pot']
    else:
        list_of_stakes = []
        for player in players_in:
            list_of_stakes.append(player.stake)
        list_of_stakes = list(set(list_of_stakes))
        list_of_stakes = sorted(list_of_stakes)
        list_of_players_at_stake = []
        list_of_list_of_players_at_stake = []
        for i in range(len(list_of_stakes)):
            for player in players_in:
                if player.stake >= list_of_stakes[i]:
                    list_of_players_at_stake.append(player)
            list_of_list_of_players_at_stake.append(list(set(list_of_players_at_stake)))
            list_of_players_at_stake.clear()
        list_of_pot_seeds = []
        for i in list_of_stakes:
            list_of_pot_seeds.append(i)
        list_of_pot_seeds.reverse()
        for i in range(len(list_of_pot_seeds)):
            try:
                list_of_pot_seeds[i] -= list_of_pot_seeds[i + 1]
            except IndexError:
                pass
        list_of_pot_seeds.reverse()
        list_of_pots = []
        for i in range(len(list_of_pot_seeds)):
            list_of_pots.append(list_of_pot_seeds[i] * len(list_of_list_of_players_at_stake[i]))
        for i in range(len(list_of_pots)):
            winners = []
            list_of_scores_eligible = []
            for player in list_of_list_of_players_at_stake[i]:
                if player.isFolded:
                    pass
                else:
                    list_of_scores_eligible.append(player.score)
            max_score = max(list_of_scores_eligible)
            for player in list_of_list_of_players_at_stake[i]:
                if player.isFolded:
                    pass
                else:
                    if player.score == max_score:
                        player.isWinner = True
                        winners.append(player)
            prize = int(list_of_pots[i] / len(winners))
            for player in winners:
                player.chips += prize
                game['pot'] -= prize
