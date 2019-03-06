import time
import os
from operator import add

from golf import Golf, Golf_Analyser
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import function_approximator as fa
import pickle


g = Golf()

DIR_PATH = os.path.join('games', 'coevo_score_with_random', 'one_hot_hand_1')
DIR_PATH_SAVE = os.path.join('games', 'coevo_score_with_random_analysis', 'one_hot_hand_1')

if not os.path.exists(DIR_PATH_SAVE):
    os.makedirs(DIR_PATH_SAVE)
if not os.path.exists(os.path.join(DIR_PATH_SAVE, "training")):
    os.makedirs(os.path.join(DIR_PATH_SAVE, "training"))
if not os.path.exists(os.path.join(DIR_PATH_SAVE, "random")):
    os.makedirs(os.path.join(DIR_PATH_SAVE, "random"))

with open(os.path.join(DIR_PATH, 'PLAYER_PICKLE.p'), 'rb') as f:
    player = pickle.load(f)
with open(os.path.join(DIR_PATH, 'OPPONENT_PICKLE.p'), 'rb') as f:
    opponent = pickle.load(f)

random_player = Random_Golf_Player()

GAMES = ["",""]
RANDOM_GAMES = ["",""]
t = time.time()
for n in range(2500):
    games = g.play_pair(player, opponent)
    GAMES = list(map(add, GAMES, games))
    GAMES[0]+='\n'
    GAMES[1]+='\n' 

    random_games = g.play_pair(player, random_player)
    RANDOM_GAMES = list(map(add, RANDOM_GAMES, random_games))
    RANDOM_GAMES[0]+='\n'
    RANDOM_GAMES[1]+='\n'

    if (n+1)%125 == 0:
        print(n+1)   
        filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
        for i in range(2):
            with open(os.path.join(DIR_PATH_SAVE, "training", '%s%d.txt' % (filename, i)), 'w+') as f: #look at a+ instead, will append if the file exists
                f.write(GAMES[i])
            with open(os.path.join(DIR_PATH_SAVE, "random", '%s%d.txt' % (filename, i)), 'w+') as f: #look at a+ instead, will append if the file exists
                f.write(RANDOM_GAMES[i])
        GAMES = ["",""]
        RANDOM_GAMES = ["",""]



t_2 = time.time()

print(t_2-t)
