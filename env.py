import time
import os
from operator import add

from golf import Golf, Golf_Analyser
#import deck
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
#import actions
#import numpy as np
import file_write as fw


g = Golf()

#GOT STUCK IN AN INFINITE LOOP
#LOOK AT PREVENTING A PLAYER DISCARDING CARD DRAWN FROM DISCARD PILE, although this should not be a problem???? Need to investigate player policy method.
p1 = Golf_Player() #Greedy_Golf_Player() 
p2 = Golf_Player() #Random_Golf_Player() 

counter = 0

GAME = ["",""]
t = time.time()
for i in range(10):
    game = g.play_pair(p1, p2)
    print(i)
    GAME = list(map(add, GAME, game))
    GAME[0]+='\n'
    GAME[1]+='\n' 


#GAME = [g.play_pair(p1, p2)]
#GAME += [g.play_pair(p1, p2)]

t_2 = time.time()

#print(os.getcwd())

#if not os.path.exists('games'):
#    os.makedirs('games')

for g in range(2):
    with open(os.path.join('games', 'test_game_%d.txt'%g), 'w+') as f:
        f.write("".join(GAME[g]))
#    fw.write_game(None, None)

#    with open(os.path.join('games', 'test_game%d_1.txt'%g), 'w+') as f:
#        f.write(GAME[g][1])
#    fw.write_game(None, None)


#print(GAME)
#print(Golf_Analyser.extract_scores(GAME[0]))
#print(Golf_Analyser.extract_scores(GAME[1]))
print(t_2-t)
