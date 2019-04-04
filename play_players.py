import sys
import os
import re
import glob
import pickle
import time
from operator import add
import neat
import player
import function_approximator as fa
from golf import Golf

def extract_player(flag, path):
    if flag == '-c':
        with open(os.path.join(path, "PLAYER_PICKLE.p"), 'rb') as f:
            p = pickle.load(f)
    elif flag == '-n':
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        path+'/config-golf')
        
        num_inputs = config.genome_config.num_inputs
        state_function = fa.one_hot_hand if num_inputs == 90 else (fa.one_hot_state_and_hand if num_inputs == 252 else fa.one_hot_state)
        
        solutions = glob.glob(os.path.join(path, "best_solutions", "*"))
        latest = max(solutions, key=os.path.getctime)
        with open(latest, 'rb') as f:
            genome = pickle.load(f)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        p = player.Golf_Player(state_function, fa.NEAT_Func_Approx(state_function, net))
    elif flag == '-r':
        if path == "random":
            p = player.Random_Golf_Player()
        elif path == "greedy":
            p = player.Greedy_Golf_Player()
        else:
            raise FileNotFoundError("Enter 'random' or 'greedy' for a -r flag")
    else:
        raise AttributeError("Unknown flag %s" % flag)
    return p


player1 = extract_player(sys.argv[1], sys.argv[2])
player2 = extract_player(sys.argv[3], sys.argv[4])
save_path = sys.argv[5] 

g = Golf()
GAMES = ["",""]
for _ in range(50):
    results = g.play_pair(player1, player2)
    GAMES = list(map(add, GAMES, results))
    GAMES[0]+='\n'
    GAMES[1]+='\n'

save_dir = os.path.join(save_path, re.split(r'/|\\', sys.argv[2])[-1] + sys.argv[1] +  "_vs_" + re.split(r'/|\\', sys.argv[4])[-1] + sys.argv[3])
os.mkdir(os.path.join(save_dir))
filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())

for i in range(2):
    with open(os.path.join(save_dir, '%s%d.txt' % (filename, i)), 'w+') as f:
        f.write(GAMES[i])