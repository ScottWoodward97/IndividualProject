from __future__ import print_function
import os
import neat
import numpy as np
import copy
from golf import Golf, Golf_Analyser
from deck import Deck
from player import Golf_Player
from function_approximator import NEAT_Func_Approx
#import visualize

NUM_FITNESS_GAMES = 10

def evaluate_solution(solutions, config):
    seeds = np.random.randint(0, 2147483648, size=(NUM_FITNESS_GAMES, 9))
    decks = np.reshape([Deck(deck=[], jokers=True) for _ in range(9*NUM_FITNESS_GAMES)], (NUM_FITNESS_GAMES, 9))
    golf = Golf()
    for solution_id, solution in solutions:
        net = neat.nn.FeedForwardNetwork.create(solution, config)

        player1 = Golf_Player(NEAT_Func_Approx(net))
        player2 = copy.deepcopy(player1)

        scores = []

        for game_num in range(NUM_FITNESS_GAMES):
            ##PLAY GAME
            results = ""
            for round_num in range(9):
                np.random.seed(seeds[game_num][round_num])
                golf.initialise(decks[game_num][round_num])

                results += golf.play_round(round_num, player1, player2) + '\n'

            scores.append(Golf_Analyser.extract_scores(results))

        #Use this to calculate fitness
        min_total_score = np.sum(np.amin(scores, axis=1))
        solution.fitness = (int)(6000 - min_total_score)

def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_file)

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(1))

    #Encounters error with parse_config, apparantly one of the defaults does not have a parse_config method??
    winner = pop.run(evaluate_solution, 10)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-golf')
    run(config_path)