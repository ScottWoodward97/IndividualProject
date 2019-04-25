"""
---analyse_neat.py---
Contains the methods that analyse the population data of the NEAT training process.
These plot graphs that map the metrics of the best and worst solutions (fitness) in the population as well as the population average.
Where relevant, the highest and lowest of each metric in the population is also plotted.
"""
from golf import Golf_Analyser
import glob
import os
import numpy as np


def plot_mean_scores(dir_path, games_per_solution=10):
    """
    Plots the mean scores at each generation obtained by the population during training.
    The mean scores of the best and worst players in the population as well as the population average.
    Args:
        dir_path (String): The directory of the player trained under NEAT.
        games_per_solution(int): The number of games each solution plays in its fitness calculation. Default set to 10.
    Returns: None
    """
    #Load the paths of each generation's game file from the relevant directory
    files = glob.glob('%s/game_files/*.txt' % dir_path)
    best_solution, worst_solution, pop_av = [],[],[]

    for game_file in files:
        with open(game_file, "r") as f:
            games = f.read().split('\n\n')[:-1]
        #Extracts the scores from the games
        all_scores = [Golf_Analyser.extract_scores(game + '\n') for game in games]
        solution_scores = np.reshape(all_scores, (len(all_scores)//games_per_solution, games_per_solution, 2))
        
        mean_solution_scores = np.mean(np.amin(solution_scores, axis=2), axis=1)
        #Extracts the best solution's, worst solution's and the population average score
        best_solution.append(float(min(mean_solution_scores)))
        worst_solution.append(float(max(mean_solution_scores)))
        pop_av.append(float(np.mean(mean_solution_scores)))

    Golf_Analyser.plot_data(list(zip(best_solution, worst_solution, pop_av)), 3, "Generations", "Mean Score", "Mean Score over Generations", "Best Solution", "Worst Solution", "Population Average")

def plot_mean_number_of_turns(dir_path, games_per_solution=10):
    """
    Plots the mean number of turns at each generation obtained by the population during training.
    The mean number of turns of the best and worst players in the population (by fitness) as well as the population average.
    The highest and lowest number of turns by solutions in the popualtion are also plotted.
    Args:
        dir_path (String): The directory of the player trained under NEAT.
        games_per_solution(int): The number of games each solution plays in its fitness calculation. Default set to 10.
    Returns: None
    """
    #Load the paths of each generation's game file from the relevant directory
    files = glob.glob('%s/game_files/*.txt' % dir_path)
    best_solution, worst_solution, pop_av, highest, lowest = [],[],[], [], []

    for game_file in files:
        with open(game_file, "r") as f:
            games = f.read().split('\n\n')[:-1]
        #Extracts the scores and number of turns from each file
        all_scores = [Golf_Analyser.extract_scores(game + '\n') for game in games]
        all_turns = [sum(Golf_Analyser.extract_number_of_turns(game + '\n')) for game in games]

        solution_scores = np.reshape(all_scores, (len(all_scores)//games_per_solution, games_per_solution, 2))
        solution_turns = np.sum(np.reshape(all_turns, (len(all_turns)//games_per_solution, games_per_solution)), axis=1)
        
        mean_solution_scores = np.mean(np.amin(solution_scores, axis=2), axis=1)

        #By using the scores, locate the best and worst solution at each generation and add their metrics
        best_solution.append(float(solution_turns[np.argmin(mean_solution_scores)]/(9*games_per_solution)))
        worst_solution.append(float(solution_turns[np.argmax(mean_solution_scores)]/(9*games_per_solution)))

        #Extract the highest, lowest and average number of turns obtained by solutions in the population
        lowest.append(float(min(solution_turns)/(9*games_per_solution)))
        highest.append(float(max(solution_turns)/(9*games_per_solution)))
        pop_av.append(float(np.mean(solution_turns)/(9*games_per_solution)))
        
    Golf_Analyser.plot_data(list(zip(best_solution, worst_solution, pop_av, highest, lowest)), 5, "Generations", "Average Number of Turns per Round", "Average Number of Turns per Round over Generations", "Best Solution", "Worst Solution", "Population Average", "Population Highest", "Population Lowest")

def plot_mean_number_of_matches(dir_path, games_per_solution=10):
    """
    Plots the mean number of matches made at each generation obtained by the population during training.
    The mean number of matches of the best and worst players in the population (by fitness) as well as the population average.
    The highest and lowest number of matches by solutions in the popualtion are also plotted.
    Args:
        dir_path (String): The directory of the player trained under NEAT.
        games_per_solution(int): The number of games each solution plays in its fitness calculation. Default set to 10.
    Returns: None
    """
    #Load the paths of each generation's game file from the relevant directory
    files = glob.glob('%s/game_files/*.txt' % dir_path)
    best_solution, worst_solution, pop_av, highest, lowest = [],[],[], [], []

    for game_file in files:
        with open(game_file, "r") as f:
            games = f.read().split('\n\n')[:-1]
        #Extracts the scores and number of matches from each file
        all_scores = [Golf_Analyser.extract_scores(game + '\n') for game in games]
        all_matches = [extract_matches_round(Golf_Analyser.extract_hands(game + '\n')) for game in games]

        solution_scores = np.reshape(all_scores, (len(all_scores)//games_per_solution, games_per_solution, 2))
        solution_matches = np.reshape(all_matches, (len(all_matches)//games_per_solution, games_per_solution, 9, 2))
        solution_matches = [np.sum(sol) for sol in solution_matches]
        
        mean_solution_scores = np.mean(np.amin(solution_scores, axis=2), axis=1)
        
        #By using the scores, locate the best and worst solution at each generation and add their metrics
        best_solution.append(float(solution_matches[np.argmin(mean_solution_scores)]/2))
        worst_solution.append(float(solution_matches[np.argmax(mean_solution_scores)]/2))

        #Extract the highest, lowest and average number of matches obtained by solutions in the population
        lowest.append(float(min(solution_matches)/2))
        highest.append(float(max(solution_matches)/2))
        pop_av.append(float(np.mean(solution_matches)/2))
        
    Golf_Analyser.plot_data(list(zip(best_solution, worst_solution, pop_av, highest, lowest)), 5, "Generations", "Average Matches per Game", "Average Matches per Game over Generations", "Best Solution", "Worst Solution", "Population Average", "Population Highest", "Population Lowest")

def extract_matches_round(hands):
    """
    Calculates the number of matches made in an array of hands of both players and opponents.
    Args:
        hands([[String, String]]): An array containing the hands of both player and opponent for each round
    Returns: An array containing the number of matches in each hand
    """
    matches = []
    for h in hands:
        #Converts the characters to their ASCII value
        asc_vals_player = [ord(card) for card in h[0]]

        #Sums the number of matches that appear in the hand. Special cases for catching matching jokers
        player_matches = sum((asc_vals_player[i] > 116 and asc_vals_player[i+3] > 116) 
                        or (asc_vals_player[i] < 117 and asc_vals_player[i+3] < 117 and (asc_vals_player[i] - asc_vals_player[i+3])%13==0) for i in range(3))
                
        asc_vals_opponent = [ord(card) for card in h[1]]
        opponent_matches = sum((asc_vals_opponent[i] > 116 and asc_vals_opponent[i+3] > 116) 
                        or (asc_vals_opponent[i] < 117 and asc_vals_opponent[i+3] < 117 and (asc_vals_opponent[i] - asc_vals_opponent[i+3])%13==0) for i in range(3))
        matches.append([player_matches, opponent_matches])
    return matches

import sys
p = sys.argv[1] #"games/neat/one_hot_hand_2"
#plot_mean_scores(p)
#plot_mean_number_of_turns(p)
plot_mean_number_of_matches(p)