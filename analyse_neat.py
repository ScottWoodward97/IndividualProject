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

def plot_mean_number_of_matches(dir_path, games_per_solution=10):
    files = glob.glob('%s/game_files/*.txt' % dir_path)
    best_solution, worst_solution, pop_av, highest, lowest = [],[],[], [], []

    for game_file in files:
        with open(game_file, "r") as f:
            games = f.read().split('\n\n')[:-1]
        all_scores = [Golf_Analyser.extract_scores(game + '\n') for game in games]
        all_matches = [extract_matches_round(Golf_Analyser.extract_hands(game + '\n')) for game in games]

        solution_scores = np.reshape(all_scores, (len(all_scores)//games_per_solution, games_per_solution, 2))
        solution_matches = np.reshape(all_matches, (len(all_matches)//games_per_solution, games_per_solution, 9, 2))
        solution_matches = [np.sum(sol) for sol in solution_matches]
        
        mean_solution_scores = np.mean(np.amin(solution_scores, axis=2), axis=1)

        best_solution.append(float(solution_matches[np.argmin(mean_solution_scores)]/(9*2)))
        worst_solution.append(float(solution_matches[np.argmax(mean_solution_scores)]/(9*2)))

        lowest.append(float(min(solution_matches)/(9*2)))
        highest.append(float(max(solution_matches)/(9*2)))
        pop_av.append(float(np.mean(solution_matches)/(9*2)))
        
    Golf_Analyser.plot_data(list(zip(best_solution, worst_solution, pop_av, highest, lowest)), 5, "Generations", "Average Matches per Game", "Average Matches per Game over Generations", "Best Solution", "Worst Solution", "Population Average", "Population Highest", "Population Lowest")

def extract_matches_round(hands):
    matches = []
    for h in hands:
        asc_vals_player = [ord(card) for card in h[0]]
        player_matches = sum((asc_vals_player[i] > 116 and asc_vals_player[i+3] > 116) 
                        or (asc_vals_player[i] < 117 and asc_vals_player[i+3] < 117 and (asc_vals_player[i] - asc_vals_player[i+3])%13==0) for i in range(3))
                
        asc_vals_opponent = [ord(card) for card in h[1]]
        opponent_matches = sum((asc_vals_opponent[i] > 116 and asc_vals_opponent[i+3] > 116) 
                        or (asc_vals_opponent[i] < 117 and asc_vals_opponent[i+3] < 117 and (asc_vals_opponent[i] - asc_vals_opponent[i+3])%13==0) for i in range(3))
        matches.append([player_matches, opponent_matches])
    return matches

plot_mean_number_of_matches("games/neat/one_hot_state_and_hand_3")