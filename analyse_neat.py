from golf import Golf_Analyser
import glob
import os
import numpy as np


def plot_mean_scores(dir_path, games_per_solution=10):
    files = glob.glob('%s/game_files/*.txt' % dir_path)
    best_solution, worst_solution, pop_av = [],[],[]

    for game_file in files:
        with open(game_file, "r") as f:
            games = f.read().split('\n\n')[:-1]
        all_scores = [Golf_Analyser.extract_scores(game + '\n') for game in games]
        solution_scores = np.reshape(all_scores, (len(all_scores)//games_per_solution, games_per_solution, 2))
        
        mean_solution_scores = np.mean(np.amin(solution_scores, axis=2), axis=1)
        
        best_solution.append(float(min(mean_solution_scores)))
        worst_solution.append(float(max(mean_solution_scores)))
        pop_av.append(float(np.mean(mean_solution_scores)))

    Golf_Analyser.plot_data(list(zip(best_solution, worst_solution, pop_av)), 3, "Generations", "Mean Score", "Mean Score over Generations", "Best Solution", "Worst Solution", "Population Average")

def plot_mean_number_of_turns(dir_path, games_per_solution=10):
    files = glob.glob('%s/game_files/*.txt' % dir_path)
    best_solution, worst_solution, pop_av, highest, lowest = [],[],[], [], []

    for game_file in files:
        with open(game_file, "r") as f:
            games = f.read().split('\n\n')[:-1]
        all_scores = [Golf_Analyser.extract_scores(game + '\n') for game in games]
        all_turns = [sum(Golf_Analyser.extract_number_of_turns(game + '\n')) for game in games]

        solution_scores = np.reshape(all_scores, (len(all_scores)//games_per_solution, games_per_solution, 2))
        solution_turns = np.sum(np.reshape(all_turns, (len(all_turns)//games_per_solution, games_per_solution)), axis=1)
        
        mean_solution_scores = np.mean(np.amin(solution_scores, axis=2), axis=1)

        best_solution.append(float(solution_turns[np.argmin(mean_solution_scores)]/(9*games_per_solution)))
        worst_solution.append(float(solution_turns[np.argmax(mean_solution_scores)]/(9*games_per_solution)))

        lowest.append(float(min(solution_turns)/(9*games_per_solution)))
        highest.append(float(max(solution_turns)/(9*games_per_solution)))
        pop_av.append(float(np.mean(solution_turns)/(9*games_per_solution)))
        
    Golf_Analyser.plot_data(list(zip(best_solution, worst_solution, pop_av, highest, lowest)), 5, "Generations", "Average Number of Turns per Round", "Average Number of Turns per Round over Generations", "Best Solution", "Worst Solution", "Population Average", "Population Highest", "Population Lowest")



plot_mean_number_of_turns("games/neat/one_hot_state_2")