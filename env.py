"""
---coevo_play_training_and_random.py---
Plays the coevolution trained player against its training opponent and the random player over 5,000 games (2,500 pairs) each.
Game data is saved after every 250 games to DIR_PATH_SAVE.
Args:
    DIR_PATH (String): First command line argument. The directory where the relevant coevolution player files are located.
    DIR_PATH_SAVE (String): Second command line argument. The path to the directory where the game data will be saved.
"""
import os
from operator import add
import sys

from golf import Golf, Golf_Analyser
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import function_approximator as fa
import pickle


g = Golf()

DIR_PATH = sys.argv[1] #os.path.join('games', 'coevo_score_with_random', 'one_hot_state_5')
DIR_PATH_SAVE = os.path.join(sys.argv[2] , re.split(r'/|\\', sys.argv[1])[-1]) #os.path.join('games', 'coevo_score_with_random_analysis', 'one_hot_state_5')

#Creates the save directory and its subdirectories if they do not already exist
if not os.path.exists(DIR_PATH_SAVE):
    os.makedirs(DIR_PATH_SAVE)
if not os.path.exists(os.path.join(DIR_PATH_SAVE, "training")):
    os.makedirs(os.path.join(DIR_PATH_SAVE, "training"))
if not os.path.exists(os.path.join(DIR_PATH_SAVE, "random")):
    os.makedirs(os.path.join(DIR_PATH_SAVE, "random"))

#Loads in the player, opponent and random player
with open(os.path.join(DIR_PATH, 'PLAYER_PICKLE.p'), 'rb') as f:
    player = pickle.load(f)
with open(os.path.join(DIR_PATH, 'OPPONENT_PICKLE.p'), 'rb') as f:
    opponent = pickle.load(f)

random_player = Random_Golf_Player()

GAMES = ["",""]
RANDOM_GAMES = ["",""]
for n in range(2500):
    #Play a pair of games against the training opponent
    games = g.play_pair(player, opponent)
    GAMES = list(map(add, GAMES, games))
    GAMES[0]+='\n'
    GAMES[1]+='\n' 

    #Play a pair of games against the random player
    random_games = g.play_pair(player, random_player)
    RANDOM_GAMES = list(map(add, RANDOM_GAMES, random_games))
    RANDOM_GAMES[0]+='\n'
    RANDOM_GAMES[1]+='\n'

    #Save the game data to file every 250 games (125 pairs)
    if (n+1)%125 == 0:
        filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
        #Saves games at each position to separate files
        for i in range(2):
            with open(os.path.join(DIR_PATH_SAVE, "training", '%s%d.txt' % (filename, i)), 'w+') as f: 
                f.write(GAMES[i])
            with open(os.path.join(DIR_PATH_SAVE, "random", '%s%d.txt' % (filename, i)), 'w+') as f:
                f.write(RANDOM_GAMES[i])
        GAMES = ["",""]
        RANDOM_GAMES = ["",""]
