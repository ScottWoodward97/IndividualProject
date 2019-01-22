from golf import Golf, Golf_Analyser
import deck
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import actions
import numpy as np

import time

g = Golf()

p1 = Greedy_Golf_Player() #Golf_Player()
p2 = Random_Golf_Player() #Golf_Player()

t = time.time()

GAME = g.play_pair(p1, p2)
#SCORES += g.play_pair(p1, p2)

t_2 = time.time()


#print(GAME)
print(Golf_Analyser.extract_scores(GAME[0]))
print(Golf_Analyser.extract_scores(GAME[1]))
print(t_2-t)

print(GAME[0].split('\n'))
print()
print(GAME[1].split('\n'))