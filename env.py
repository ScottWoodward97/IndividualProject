import time
import os
from operator import add

from golf import Golf, Golf_Analyser
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import file_write as fw
import pickle


g = Golf()

#DIR_PATH_PLAYERS = os.path.join('games', 'coevo', 'test_3')
DIR_PATH_SAVE = os.path.join('games', 'analysis', 'random')

if not os.path.exists(DIR_PATH_SAVE):
    os.makedirs(DIR_PATH_SAVE)

#with open(os.path.join(DIR_PATH_PLAYERS, 'PLAYER_PICKLE.p'), 'rb') as f:
#    p1 = pickle.load(f)
#with open(os.path.join(DIR_PATH_PLAYERS, 'OPPONENT_PICKLE.p'), 'rb') as f:
#    p2 = pickle.load(f)
p1 = Random_Golf_Player()
p2 = Random_Golf_Player()



GAME = ["",""]
t = time.time()
for _ in range(10000):
    game = g.play_pair(p1, p2)

    GAME = list(map(add, GAME, game))
    GAME[0]+='\n'
    GAME[1]+='\n' 



t_2 = time.time()

#print(os.getcwd())

#if not os.path.exists('games'):
#    os.makedirs('games')

for g in range(2):
    with open(os.path.join(DIR_PATH_SAVE, 'test_game_%d.txt'%g), 'w+') as f:
        f.write("".join(GAME[g]))
#    fw.write_game(None, None)

#    with open(os.path.join('games', 'test_game%d_1.txt'%g), 'w+') as f:
#        f.write(GAME[g][1])
#    fw.write_game(None, None)


#print(GAME)
#print(Golf_Analyser.extract_scores(GAME[0]))
#print(Golf_Analyser.extract_scores(GAME[1]))
print(t_2-t)
