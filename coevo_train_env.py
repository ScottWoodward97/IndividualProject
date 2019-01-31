"""
PSUEDO
SYS.ARGS: file location to save games to, loction of player pickled files

Try to load in players from file
If not possible, create them from new

loop until termination, either time based or number of batches made
    
    loop batch_size number of times
        play game
        add results to variable
        update the players function approximators
    write the game results to file
    back-up the players to file (or func approx)
    
    determine if user has entered terminating phrase, exit if so

"""

import time
import pickle
import os
import sys

from golf import Golf, Golf_Analyser
from player import Golf_Player

player = Golf_Player()
opponent = Golf_Player()


g = Golf()

for _ in range(50):
    player_wins = 0
    for _ in range(2):
        game_1, game_2 = g.play_pair(player, opponent)
        scores_1 = Golf_Analyser.extract_scores(game_1)
        if scores_1[0] < scores_1[1]:
            player_wins += 1
        scores_2 = Golf_Analyser.extract_scores(game_2)
        if scores_2[1] < scores_2[0]:
            player_wins += 1
        print(scores_1)
        print(scores_2[::-1])

    print()
    if player_wins <= 2:

        #print(player.function_approximator.network.W_hidden[0])
        #print(opponent.function_approximator.network.W_hidden[0])

        #print(player.function_approximator.network.W_output)
        #print(opponent.function_approximator.network.W_output)

        player.update_network(opponent)

    opponent.add_noise()

print("Break")



#argc = len(sys.argv) 
#if argc < 3:
#    print("Need more args")
    #Exit
#else:
#    dir_path = sys.argv[1]
#    batch_size = int(sys.argv[2])
    ##COULD SEARCH DIR FOR CORRECT FILE EXTENTIONS?
#    if argc > 3:
#        player_func = sys.argv[3]
#        opp_func = sys.argv[4]
#    else:
#        player_func, opp_func = None, None