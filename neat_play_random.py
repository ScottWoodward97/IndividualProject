import time
import os
from operator import add

from golf import Golf, Golf_Analyser
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import function_approximator as fa
import pickle
import neat


g = Golf()

DIR_PATH = os.path.join('games', 'neat', 'one_hot_state')
DIR_PATH_SAVE = os.path.join('games', 'neat_analysis', 'one_hot_state')
CONFIG_PATH = DIR_PATH + '\config-golf'

if not os.path.exists(DIR_PATH_SAVE):
    os.makedirs(DIR_PATH_SAVE)

with open(os.path.join(DIR_PATH, 'best_solutions', 'generation-49'), 'rb') as f:
    genome = pickle.load(f)
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        CONFIG_PATH)
    network = neat.nn.FeedForwardNetwork.create(genome, config)
    player = Golf_Player(fa.one_hot_state, fa.NEAT_Func_Approx(fa.one_hot_state, network))

random_player = Random_Golf_Player()

RANDOM_GAMES = ["",""]
t = time.time()
for n in range(2500):
    random_games = g.play_pair(player, random_player)
    RANDOM_GAMES = list(map(add, RANDOM_GAMES, random_games))
    RANDOM_GAMES[0]+='\n'
    RANDOM_GAMES[1]+='\n'

    #print(n)
    if (n+1)%125 == 0:
        print(n+1)   
        filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
        for i in range(2):
            with open(os.path.join(DIR_PATH_SAVE, '%s%d.txt' % (filename, i)), 'w+') as f: #look at a+ instead, will append if the file exists
                f.write(RANDOM_GAMES[i])
        RANDOM_GAMES = ["",""]

t_2 = time.time()
print(t_2-t)
