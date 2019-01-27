import time
import os

from golf import Golf, Golf_Analyser
#import deck
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
#import actions
#import numpy as np
import file_write as fw


g = Golf()

p1 = Greedy_Golf_Player() #Golf_Player()
p2 = Random_Golf_Player() #Golf_Player()

t = time.time()

GAME = [g.play_pair(p1, p2)]
GAME += [g.play_pair(p1, p2)]

t_2 = time.time()

#print(os.getcwd())

if not os.path.exists('games'):
    os.makedirs('games')

for g in range(2):
    with open(os.path.join('games', 'test_game%d_0.txt'%g), 'w+') as f:
        f.write(GAME[g][0])
#    fw.write_game(None, None)

    with open(os.path.join('games', 'test_game%d_1.txt'%g), 'w+') as f:
        f.write(GAME[g][1])
#    fw.write_game(None, None)


#print(GAME)
#print(Golf_Analyser.extract_scores(GAME[0]))
#print(Golf_Analyser.extract_scores(GAME[1]))
print(t_2-t)
