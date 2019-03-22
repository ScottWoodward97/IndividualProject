from golf import Golf_Analyser
import glob
import os
import numpy as np


def plot_mean_scores(dir_path, games_per_solution=10):
    files = glob.glob('%s/game_files/*.txt' % dir_path)
    best_score, mean_score = [],[]

    for game_file in files:
        with open(game_file, "r") as f:
            games = f.read().split('\n\n')[:-1]
        all_scores = [Golf_Analyser.extract_scores(game + '\n') for game in games]
        solution_scores = np.reshape(all_scores, (len(all_scores)//games_per_solution, games_per_solution, 2))
        
        mean_solution_scores = np.mean(np.amin(solution_scores, axis=2), axis=1)
        
        best_score.append(float(min(mean_solution_scores)))
        mean_score.append(float(np.mean(mean_solution_scores)))

    Golf_Analyser.plot_data(list(zip(best_score, mean_score)), 2, "Generations", "Mean Score", "Mean Score over Generations", "Best Solution", "Population Average")



plot_mean_scores("games/neat/one_hot_hand_2")