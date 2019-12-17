# Python Poker
Texas Holdem Poker made with Python and TKinter

module dependencies: PIL

![showing gui](https://i.imgur.com/xjsWugc.png)

The organization of this repository and its branches is a work in progress. ihsansaktia is helping with this effort: https://github.com/ihsansaktia


youtube playlist I am making to explain this code: https://youtu.be/0_G9XElINRE


the "cards" folder holds all of the card images

there is an operating version found in master branch called 'texas_holdem_poker.py'

download the "cards" folder and make sure it is in the same directory where you launch the 'texas_holdem_poker v0.1.py' file.

All the other files are modulations of all the objects/functions. This is something I should have done in the first place, but I am still learning.



Discord: https://discord.gg/pFbdWx 
    helped organized by Muhsin7: https://github.com/muhsin7











Some information about how I handled scoring, since it is the most complex part of the code IMO:
  
        #  scores for an individual player will look like:
        #  [score0, score1, score2, score3, score4, score5, score6, score7]
        #  a score, like score0, will be an integer
        #
        #  I put all scores from all players in a list
        #  so we will have a list of lists of integers, representing scores from all players
        #
        #  I take advantage of how the max() function works with lists of integers.
        #  max() looks at the integer at index 0 when provided with multiple lists.
        #  if the integers at index 0 are the same number for every list,
        #  it will then look at and compare the integer at the next index
        #
        #  score0 is used to indicate hand rank
        #  with 0 being lowest (high card) to 9 as highest (royal flush)...
        #  ranks found at: https://www.cardplayer.com/rules-of-poker/hand-rankings
        #              or  https://www.cardschat.com/poker-hands.php
        #
        #  score0, score1, and score2 are somewhat like score modifiers,
        #               score1 will tell us the value of the pair or the three of a kind
        #               if two pair: score2 will tell us the value of the lowest value pair
        #                            or even the value of the pair when there is a full house
        #  while score3 to score7 are initially set as the value of the five cards in the hand
        #      in the order from highest value 12 (ace) to lowest value 0 (two)
        #
        #  for example: if a player has no special hand like pairs or a flush,
        #               all modifier scores will be 0
        #               the player will have to rely on their highest card 
        #               which will start at score3.
        #               if any other player has a pair (score0 = 1)
        #               the max() function used on a list of lists of integers
        #                           will select the player with a pair...
        #               if no player has a special hand, then the high card will be the deciding factor
        #               if more than one player has the same high card
        #                       then the max() function will move on to next index
        #                       and the next highest card will be evaluated

