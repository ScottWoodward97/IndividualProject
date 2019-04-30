"""
---neat_play_random.py---
Plays the best solution from the final population against the random player over 5,000 games (2,500 pairs).
Game data is saved after every 250 games to DIR_PATH_SAVE.
Args:
    DIR_PATH (String): First command line argument. The directory where the relevant NEAT files are located.
    DIR_PATH_SAVE (String): Second command line argument. The path to the directory where the game data will be saved.
"""
import time
import os
from operator import add
import sys
import re

from golf import Golf, Golf_Analyser
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import function_approximator as fa
import pickle
import neat

g = Golf()

DIR_PATH = sys.argv[1]
#Create the path to the folder in the given directory where the game data is saved
DIR_PATH_SAVE = os.path.join(sys.argv[2] , re.split(r'/|\\', sys.argv[1])[-1])
#Load in the correct config file for the solutions
CONFIG_PATH = os.path.join(DIR_PATH ,'config-golf')

if not os.path.exists(DIR_PATH_SAVE):
    os.makedirs(DIR_PATH_SAVE)

#Loads in the best solution of the final generation of training
with open(os.path.join(DIR_PATH, 'best_solutions', 'generation-49'), 'rb') as f:
    genome = pickle.load(f)

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        CONFIG_PATH)

#Given the number of inputs, determine the state function used
num_inputs = config.genome_config.num_inputs
state_function = fa.one_hot_hand if num_inputs == 90 else (fa.one_hot_state_and_hand if num_inputs == 252 else fa.one_hot_state)

network = neat.nn.FeedForwardNetwork.create(genome, config)
#Creates a player using the solution as a function approximator
player = Golf_Player(state_function, fa.NEAT_Func_Approx(state_function, network))

random_player = Random_Golf_Player()

RANDOM_GAMES = ["",""]
#Play the games against the random player
for n in range(2500):
    random_games = g.play_pair(player, random_player)
    RANDOM_GAMES = list(map(add, RANDOM_GAMES, random_games))
    RANDOM_GAMES[0]+='\n'
    RANDOM_GAMES[1]+='\n'

    #Save the game data to file every 250 games (125 pairs)
    if (n+1)%125 == 0:  
        filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
        #Saves games at each position to separate files
        for i in range(2):
            with open(os.path.join(DIR_PATH_SAVE, '%s%d.txt' % (filename, i)), 'w+') as f:
                f.write(RANDOM_GAMES[i])
        RANDOM_GAMES = ["",""]
