import time
import os
from operator import add
import sys
import re
import glob

from golf import Golf, Golf_Analyser
from player import Golf_Player, Random_Golf_Player, Greedy_Golf_Player
import function_approximator as fa
import pickle
import neat


g = Golf()

DIR_PATH = sys.argv[1] #os.path.join('games', 'neat', 'one_hot_state_2')

DIR_PATH_SAVE = os.path.join(sys.argv[2] , re.split(r'/|\\', sys.argv[1])[-1]) #os.path.join('games', 'neat_analysis', 'one_hot_state_2')
CONFIG_PATH = os.path.join(DIR_PATH ,'config-golf')

if not os.path.exists(DIR_PATH_SAVE):
    os.makedirs(DIR_PATH_SAVE)
t = time.time()
gen_files = sorted(glob.glob(os.path.join(DIR_PATH, 'best_solutions/*')), key=os.path.getctime)
for gen_genome in gen_files:
    generation = int(gen_genome.split('-')[-1])
    with open(gen_genome, 'rb') as f:
        genome = pickle.load(f)

        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        CONFIG_PATH)

        num_inputs = config.genome_config.num_inputs
        state_function = fa.one_hot_hand if num_inputs == 90 else (fa.one_hot_state_and_hand if num_inputs == 252 else fa.one_hot_state)

        network = neat.nn.FeedForwardNetwork.create(genome, config)
        player = Golf_Player(state_function, fa.NEAT_Func_Approx(state_function, network))

        random_player = Random_Golf_Player()

        RANDOM_GAMES = ["",""]
        
        for n in range(5):
            random_games = g.play_pair(player, random_player)
            RANDOM_GAMES = list(map(add, RANDOM_GAMES, random_games))
            RANDOM_GAMES[0]+='\n'
            RANDOM_GAMES[1]+='\n'

        filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
        for i in range(2):
            with open(os.path.join(DIR_PATH_SAVE, '%s%d-%d.txt' % (filename, generation, i)), 'w+') as f: #look at a+ instead, will append if the file exists
                f.write(RANDOM_GAMES[i])
        

t_2 = time.time()
print(t_2-t)
