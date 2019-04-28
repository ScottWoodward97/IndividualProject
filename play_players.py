"""
---play_players.py---
Allows for two golf players to play against each other over a period of 100 games (50 pairs).
The command line arguments provide information for the construction/reinisialisation of the players from file.
The data from the games are then saved to a specified directory.
Args:
    player_flags (String): The first and third command line arguments. Specifies the type of player in the player_path directory.
        Allows for the player to be created correctly. Coevolution flag '-c', NEAT flag '-n', Random flag (includes greedier random) '-r'.
    player_path (String): The second and fourth command line arguments. The path fo the directory that contains the serialised players.
        If the random or greedier random player is chosen, then the path is either random or greedy respectively.
    save_path (String): the fifth command line argument. The path of the directory where the game files are to be saved.
"""
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
    """
    Re-initialise the player given its directory and relevant flag.
    Args:
        flag (String):  Specifies the type of player in the player_path directory.
            Allows for the player to be created correctly. Coevolution flag '-c', NEAT flag '-n', Random flag (includes greedier random) '-r'.
        path (String):  The path fo the directory that contains the serialised players. 
            If the random or greedier random player is chosen, then the path is either random or greedy respectively.
    Returns: The reinistialsed player (Player)
    """
    if flag == '-c':
        #Load the coevolution player file
        with open(os.path.join(path, "PLAYER_PICKLE.p"), 'rb') as f:
            p = pickle.load(f)
    elif flag == '-n':
        #Load the NEAT player
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        path+'/config-golf')
        
        #Determine the state function from the config file
        num_inputs = config.genome_config.num_inputs
        state_function = fa.one_hot_hand if num_inputs == 90 else (fa.one_hot_state_and_hand if num_inputs == 252 else fa.one_hot_state)
        
        #Find and load the most recent 'best solution'
        solutions = glob.glob(os.path.join(path, "best_solutions", "*"))
        latest = max(solutions, key=os.path.getctime)
        with open(latest, 'rb') as f:
            genome = pickle.load(f)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        p = player.Golf_Player(state_function, fa.NEAT_Func_Approx(state_function, net))
    elif flag == '-r':
        #Initialises the requestion random player
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
#Play 50 pairs of games between the two loaded players
for _ in range(50):
    results = g.play_pair(player1, player2)
    GAMES = list(map(add, GAMES, results))
    GAMES[0]+='\n'
    GAMES[1]+='\n'

#Create a directory for the game files of the two players to be saved to.
save_dir = os.path.join(save_path, re.split(r'/|\\', sys.argv[2])[-1] + sys.argv[1] +  "_vs_" + re.split(r'/|\\', sys.argv[4])[-1] + sys.argv[3])
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
#Save games to files
for i in range(2):
    with open(os.path.join(save_dir, '%s%d.txt' % (filename, i)), 'w+') as f:
        f.write(GAMES[i])