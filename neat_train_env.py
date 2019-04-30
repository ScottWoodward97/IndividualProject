"""
---neat_train_env.py---
An environment for training players using the NEAT algorithm as implemeted by NEAT-python.
The file provides the methods to load in or create a new population to use in the algorithm as well as a method to evaluate the solutions of a population.
Players play 10 games against a copy of themselves to calculate their fitness value.
At the end of each generation, the game files are saved and the best solution from the generation is serialised.

Args:
    DIR_PATH (String): First command line argument. The path of the directory where player files exist or are to be saved.
    STATE_FUNCTION (String): Second command line argument. The name of the function approximator used by the player.
        Must be one of either "one_hot_hand", "one_hot_state_and_hand", or "one_hot_state".
"""

from __future__ import print_function
import os
import neat
import numpy as np
import copy
from golf import Golf, Golf_Analyser
from deck import Deck
from player import Golf_Player
import function_approximator as fa
import pickle
import glob
import sys
import shutil

NUM_FITNESS_GAMES = 10
GENERATION = 0

def evaluate_solution(solutions, config):
    """
    Evalautes each solution in the population and assigns them a fitness value.
    Each solution is evaluated by playing 10 games against a copy of itself.
    Its fitness is calculated from the average of the lowest score obtained by either copy over the 10 games.
    This value is then subtracted from 540 (the highest score) to determine the fitness value.
    After each population has been evaluated, it saves the game data and the best solution at each generation.
    Args:
        solutions: All solutions in the current generation. 
        config: The configuration of the parameters of the solutions and the algorithm
    Returns: None
    """
    ##I wish there was a better way to do this without altering the source code but there isn't
    #Allows for the generation to be monitored for use when saving data to files.
    global GENERATION

    #Generates the seeds and decks to be used in the fitness games
    np.random.seed(None)
    seeds = np.random.randint(0, 2147483648, size=(NUM_FITNESS_GAMES, 9))
    decks = np.reshape([Deck(deck=[], jokers=True) for _ in range(9*NUM_FITNESS_GAMES)], (NUM_FITNESS_GAMES, 9))
    
    golf = Golf()
    best = None
    games =  ""
    
    for solution_id, solution in solutions:
        #Create a neural network from the solution and use it as a function approximator for both players
        net = neat.nn.FeedForwardNetwork.create(solution, config)
        player1 = Golf_Player(STATE_FUNCTION, fa.NEAT_Func_Approx(STATE_FUNCTION, net))
        player2 = copy.deepcopy(player1)

        scores = []

        for game_num in range(NUM_FITNESS_GAMES):
            #Plays a single game of Golf
            results = ""
            for round_num in range(9):
                #Sets the seed and deck of the round
                np.random.seed(seeds[game_num][round_num])
                golf.initialise(decks[game_num][round_num])

                results += golf.play_round(round_num, player1, player2) + '\n'

            scores.append(Golf_Analyser.extract_scores(results))
            games += results + '\n'

        #The fitness calculation
        min_mean_score = np.mean(np.amin(scores, axis=1))
        solution.fitness = (float)(540 - min_mean_score)

        if best is None or solution.fitness > best.fitness:
            best = solution
    
    #Serialise the best solution after evaluating each solution
    with open(DIR_PATH + "/best_solutions/generation-%d" % GENERATION, "wb+") as f:
        pickle.dump(best, f)
    
    #Save the game files to the given directory
    filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())    
    with open(DIR_PATH + "/game_files/%s%d.txt" % (filename, GENERATION), 'w+') as f:
            f.write(games)
    
    GENERATION += 1

def run(config_file):
    """
    Initialises the population of the algorithm and adds any additional reporters to it.
    If a checkpoint exists then the population is loaded from that file. If not then a new population is created.
    Reporters are added to the population to provided visual statistics during training and to save checkpoints of each population.
    Args:
        config_file (String): The path of the configuratio file being used
    Returns: None
    """
    #Load in the config file
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_file)

    try:
        #If there exists a checkpoint, import it and load the most recent population
        checkpoints = glob.glob(DIR_PATH + '/checkpoints/*')
        latest = max(checkpoints, key=os.path.getctime)
        pop = neat.Checkpointer.restore_checkpoint(latest)
        #Update the generation as the neat library saves before updating
        GENERATION = int(latest.split('-')[1]) + 1
        pop.generation += 1
    except ValueError:
        #If no checkpoint exists, start a new population
        pop = neat.Population(config)

    #Add reeporters to generate output whilst training
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    #Add reporter to make a checkpoint after every generation
    pop.add_reporter(neat.Checkpointer(1, None,filename_prefix=DIR_PATH + "/checkpoints/generation-"))

    #Again, wish there was a better method of doing this. Allows for the generations number to be monitored.
    global GENERATION
    if GENERATION >= 50:
        raise ValueError("Algorithm has already run for 50 generations")

    winner = pop.run(evaluate_solution, 50-GENERATION)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    DIR_PATH = sys.argv[1]
    #Creates the relevant directories if the do not already exist
    if not os.path.exists(DIR_PATH):
        os.makedirs(DIR_PATH)
    if not os.path.exists(os.path.join(DIR_PATH, "checkpoints")):
        os.makedirs(os.path.join(DIR_PATH, "checkpoints"))
    if not os.path.exists(os.path.join(DIR_PATH, "game_files")):
        os.makedirs(os.path.join(DIR_PATH, "game_files"))
    if not os.path.exists(os.path.join(DIR_PATH, "best_solutions")):
        os.makedirs(os.path.join(DIR_PATH, "best_solutions"))

    local_dir = os.path.dirname(__file__)
    #Determines the desired state function from the user input and selects the corresponding config file
    if sys.argv[2] == "one_hot_hand":
        config_path = os.path.join(local_dir, 'config-golf-90')
        STATE_FUNCTION = fa.one_hot_hand
    elif sys.argv[2] == "one_hot_state_and_hand":
        config_path = os.path.join(local_dir, 'config-golf-252')
        STATE_FUNCTION = fa.one_hot_state_and_hand
    elif sys.argv[2] ==  "one_hot_state":
        config_path = os.path.join(local_dir, 'config-golf-486')
        STATE_FUNCTION = fa.one_hot_state
    else:
        raise AttributeError("Input representation must be either one_hot_hand, one_hot_state_and_hand, or one_hot_state")

    #Copies the config file to the local directory of the run
    if not os.path.exists(os.path.join(DIR_PATH,"config-golf")):
        shutil.copy2(config_path, os.path.join(DIR_PATH,"config-golf"))
    
    run(os.path.join(DIR_PATH,"config-golf"))