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
import time
import glob
#import visualize

NUM_FITNESS_GAMES = 10
DIR_PATH = "games/neat/one_hot_state_and_hand_2"
GENERATION = 0

def evaluate_solution(solutions, config):
    ##I wish there was a better way to do this without altering the source code but there isn't
    global GENERATION

    seeds = np.random.randint(0, 2147483648, size=(NUM_FITNESS_GAMES, 9))
    decks = np.reshape([Deck(deck=[], jokers=True) for _ in range(9*NUM_FITNESS_GAMES)], (NUM_FITNESS_GAMES, 9))
    golf = Golf()
    best = None
    games =  ""
    for solution_id, solution in solutions:
        net = neat.nn.FeedForwardNetwork.create(solution, config)

        player1 = Golf_Player(fa.one_hot_state_and_hand, fa.NEAT_Func_Approx(fa.one_hot_state_and_hand, net))
        player2 = copy.deepcopy(player1)

        scores = []
        
        t = time.time()
        for game_num in range(NUM_FITNESS_GAMES):
            ##PLAY GAME
            results = ""
            for round_num in range(9):
                np.random.seed(seeds[game_num][round_num])
                golf.initialise(decks[game_num][round_num])

                results += golf.play_round(round_num, player1, player2) + '\n'

            scores.append(Golf_Analyser.extract_scores(results))
            games += results + '\n'

        print(time.time() - t)
        #Use this to calculate fitness
        min_mean_score = np.mean(np.amin(scores, axis=1))
        solution.fitness = (float)(540 - min_mean_score)

        if best is None or solution.fitness > best.fitness:
            best = solution
    
    with open(DIR_PATH + "/best_solutions/generation-%d" % GENERATION, "wb+") as f:
        pickle.dump(best, f)
    
    filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())    
    with open(DIR_PATH + "/game_files/%s%d.txt" % (filename, GENERATION), 'w+') as f: #look at a+ instead, will append if the file exists
            f.write(games)
    
    GENERATION += 1
    print()

def run(config_file):
    #Again, wish there was a better method of doing this
    global GENERATION
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_file)

    #Import a created checkpoint and resume the algorithm from there
    try:
        checkpoints = glob.glob(DIR_PATH + '/checkpoints/*')
        latest = max(checkpoints, key=os.path.getctime)
        pop = neat.Checkpointer.restore_checkpoint(latest)
        #Update the generation as the neat library saves before updating
        GENERATION = int(latest.split('-')[1]) + 1
        pop.generation += 1
    except ValueError:
        pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(1, None,filename_prefix=DIR_PATH + "/checkpoints/generation-"))


    winner = pop.run(evaluate_solution, 10)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.

    ##Look to copy relevent config file across
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-golf')

    if not os.path.exists(DIR_PATH):
        os.makedirs(DIR_PATH)

    if not os.path.exists(os.path.join(DIR_PATH, "checkpoints")):
        os.makedirs(os.path.join(DIR_PATH, "checkpoints"))
    if not os.path.exists(os.path.join(DIR_PATH, "game_files")):
        os.makedirs(os.path.join(DIR_PATH, "game_files"))
    if not os.path.exists(os.path.join(DIR_PATH, "best_solutions")):
        os.makedirs(os.path.join(DIR_PATH, "best_solutions"))

    run(config_path)