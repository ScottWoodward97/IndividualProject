from golf import Golf, Golf_Analyser
import deck
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import actions
import numpy as np

import time
import os

g = Golf()

p1 = Greedy_Golf_Player() #Golf_Player()
p2 = Random_Golf_Player() #Golf_Player()

t = time.time()

GAME = g.play_pair(p1, p2)
#SCORES += g.play_pair(p1, p2)

t_2 = time.time()

print(os.getcwd())
#comment to test git saved credentials

#if not os.path.exists('games'):
#    os.makedirs('games')
    
#with open(os.path.join('games','test_game_0.txt'), 'w+') as f:
#    f.write(GAME[0])

#with open(os.path.join('games','test_game_1.txt'), 'w+') as f:
#    f.write(GAME[1])

#print(GAME)
print(Golf_Analyser.extract_scores(GAME[0]))
print(Golf_Analyser.extract_scores(GAME[1]))
print(t_2-t)