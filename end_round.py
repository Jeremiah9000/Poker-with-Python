from card_and_deck import StandardDeck


def clear_board(game, standard_deck):
    game['possible_responses'].clear()
    game['community_cards'].clear()
    game['deck'] = standard_deck
    game['deck'].shuffle()
    game['pot'] = 0
    game['pot_dict'].clear()
    game['action_counter'] = 0
    game['highest_stake'] = 0
    game['round_over'] = False
    for player in game['players']:
        player.refresh()

    #  Find first player not out and rotate them to the back, then break
    #  This is to help rotate assignments
    for player in game['players']:
        if player.isOut:
            pass
        else:
            game['players'].append(game['players'].pop(game['players'].index(player)))
            break


def end_round(game):
    for player in game['players']:
        if player.chips <= 0:
            player.isOut = True
            print(f"{player.name} is out of the game!")
    players_still_in = []
    for player in game['players']:
        if not player.isOut:
            players_still_in.append(player)
    if len(players_still_in) == 1:
        players_still_in[0].isWinner = True
        game['game_over'] = True
        print(f"Game is over: {players_still_in[0].name} wins with {players_still_in[0].chips}!")
        quit()
    clear_board(game, StandardDeck())
    #  if str(ask_app("Start a new round? (yes/no)")) == "yes":
    #      print("\n\n\t\t\t\t--ROUND OVER--")
    #      print("\n\n\t\t\t--STARTING NEW ROUND--\n")
    #      game['round_counter'] += 1
    #      return
    #  else:
    #      quit()
