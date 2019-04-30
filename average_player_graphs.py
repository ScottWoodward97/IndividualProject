"""
--average_player_graphs.py---
Averages the data obtained by many players in a directory that begin with a given prefix.
This averaged data is then plotted using the Golf_Analyser class.
"""
from golf import Golf_Analyser
import analyse_neat as an
import os
import sys
import numpy as np
import glob


def average_mean_scores(dir_path, prefix, sub_dir="", xlabel="Epochs"):
    """
    Averages the mean scores obtained by several players in a directory and plot their results.
    Data from any player is truncated if it exceeds the length of the shortest data array to ensure averages can be drawn.
    Args:
        dir_path (String): The path where the player directories exists.
        prefix (String): The prefix of the player directory, distinguishes between the differing player types.
        sub_dir (String): The subdirectory that contains the game data due to difference in the way game data is stored. Optional and set to nothing by default.
    Returns: None
    """
    #Find all subdirectories in the path with the prefix and sub_directory
    if sub_dir == "":
        paths = glob.glob('%s/%s_[0-9]' % (dir_path, prefix))
    else:
        paths = glob.glob('%s/%s_[0-9]/%s' % (dir_path, prefix, sub_dir))
    
    data = [np.array(Golf_Analyser.extract_all_mean_scores(path)) for path in paths]
    min_length = min([len(d) for d in data])
    agg = np.zeros((min_length, data[0].shape[1]))

    #Truncate all data arrays longer than the smallest to ensure all over exact same duration
    for d in data:
        agg += d[:min_length]
    agg /= len(paths)

    #Plots the data
    Golf_Analyser.plot_data(agg, 2, xlabel, "Mean Score", "Mean scores per game across " + xlabel, "Player", "Opponent")

def average_number_matches(dir_path, prefix, sub_dir="", xlabel="Epochs"):
    """
    Averages the mean number of matches obtained by several players in a directory and plot their results.
    Data from any player is truncated if it exceeds the length of the shortest data array to ensure averages can be drawn.
    Args:
        dir_path (String): The path where the player directories exists.
        prefix (String): The prefix of the player directory, distinguishes between the differing player types.
        sub_dir (String): The subdirectory that contains the game data due to difference in the way game data is stored. Optional and set to nothing by default.
    Returns: None
    """
    #Find all subdirectories in the path with the prefix and sub_directory
    if sub_dir == "":
        paths = glob.glob('%s/%s_[0-9]' % (dir_path, prefix))
    else:
        paths = glob.glob('%s/%s_[0-9]/%s' % (dir_path, prefix, sub_dir))
    
    data = [np.array(Golf_Analyser.extract_all_matches(path)) for path in paths]
    min_length = min([len(d) for d in data])
    agg = np.zeros((min_length, data[0].shape[1]))

    #Truncate all data arrays longer than the smallest to ensure all over exact same duration
    for d in data:
        agg += d[:min_length]
    agg /= len(paths)

    #Plot data
    Golf_Analyser.plot_data(agg, 2, xlabel, "Number of Matches", "Number of Matches per game across " + xlabel, "Player", "Opponent")

def average_card_frequency(dir_path, prefix, sub_dir="", xlabel="Epochs"):
    """
    Averages the card frequency of several players in a directory and plot their results.
    Data from any player is truncated if it exceeds the length of the shortest data array to ensure averages can be drawn.
    Args:
        dir_path (String): The path where the player directories exists.
        prefix (String): The prefix of the player directory, distinguishes between the differing player types.
        sub_dir (String): The subdirectory that contains the game data due to difference in the way game data is stored. Optional and set to nothing by default.
    Returns: None
    """
    #Find all subdirectories in the path with the prefix and sub_directory
    if sub_dir == "":
        paths = glob.glob('%s/%s_[0-9]' % (dir_path, prefix))
    else:
        paths = glob.glob('%s/%s_[0-9]/%s' % (dir_path, prefix, sub_dir))
    
    data = [np.array(Golf_Analyser.extract_all_card_frequency(path)[0]) for path in paths]
    min_length = min([len(d) for d in data])
    agg = np.zeros((min_length, data[0].shape[1]))

    #Truncate all data arrays longer than the smallest to ensure all over exact same duration
    for d in data:
        agg += d[:min_length]
    agg /= len(paths)

    #Graph display information
    colours = ['red', 'blue', 'green', 'magenta', 'orange', 'cyan', 'purple', 'grey', 'lime', 'yellow', 'black', 'salmon', 'teal', 'navy']
    labels = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Joker']

    #Plot data
    Golf_Analyser.plot_data_stacked_bar(agg, 14, xlabel, "Number of times cards in hand", "Popularity of cards per " + xlabel + " for Player", labels, colours, 540)

def average_rounds_ended(dir_path, prefix, sub_dir="", xlabel="Epochs"):
    """
    Averages the number of rounds ended several players in a directory and plot their results.
    Data from any player is truncated if it exceeds the length of the shortest data array to ensure averages can be drawn.
    Args:
        dir_path (String): The path where the player directories exists.
        prefix (String): The prefix of the player directory, distinguishes between the differing player types.
        sub_dir (String): The subdirectory that contains the game data due to difference in the way game data is stored. Optional and set to nothing by default.
    Returns: None
    """
    #Find all subdirectories in the path with the prefix and sub_directory
    if sub_dir == "":
        paths = glob.glob('%s/%s_[0-9]' % (dir_path, prefix))
    else:
        paths = glob.glob('%s/%s_[0-9]/%s' % (dir_path, prefix, sub_dir))
    
    data = [np.array(Golf_Analyser.extract_all_rounds_ended(path)) for path in paths]
    min_length = min([len(d) for d in data])
    agg = np.zeros((min_length, data[0].shape[1]))

    #Truncate all data arrays longer than the smallest to ensure all over exact same duration
    for d in data:
        agg += d[:min_length]
    agg /= len(paths)

    #Plot data
    Golf_Analyser.plot_data_stacked_bar(agg, 3, xlabel, "Rounds Ended", "Number of rounds ended per "+ xlabel, ["Player", "Opponent", "Ended due to loop"], ["blue", "red", "green"], 90)

def average_population_mean_scores(dir_path, prefix):
    """
    Averages the mean scores made by players in the population of various trials of NEAT.
    The mean scores averaged are of the best solution, worst solution, and population average.
    Data from any population is truncated if it exceeds the length of the shortest data array to ensure averages can be drawn.
    Args:
        dir_path (String): The path where the player directories exists.
        prefix (String): The prefix of the player directory, distinguishes between the differing player types.
    Returns: None
    """
    #Find all subdirectories in the path with the prefix
    paths = glob.glob('%s/%s_[0-9]' % (dir_path, prefix))
    
    data = [np.array(an.extract_mean_scores(path)) for path in paths]
    min_length = min([len(d) for d in data])
    agg = np.zeros((min_length, data[0].shape[1]))

    #Truncate all data arrays longer than the smallest to ensure all over exact same duration
    for d in data:
        agg += d[:min_length]
    agg /= len(paths)

    #Plot data
    Golf_Analyser.plot_data(agg, 3, "Generations", "Mean Score", "Mean Score over Generations", "Best Solution", "Worst Solution", "Population Average")

def average_population_mean_matches(dir_path, prefix):
    """
    Averages the mean number of matches made by players in the population of various trials of NEAT.
    The mean number of matches averaged are of the best solution, worst solution, the population highest, lowest and average.
    Data from any population is truncated if it exceeds the length of the shortest data array to ensure averages can be drawn.
    Args:
        dir_path (String): The path where the player directories exists.
        prefix (String): The prefix of the player directory, distinguishes between the differing player types.
    Returns: None
    """
    #Find all subdirectories in the path with the prefix
    paths = glob.glob('%s/%s_[0-9]' % (dir_path, prefix))
    
    data = [np.array(an.extract_mean_number_of_matches(path)) for path in paths]
    min_length = min([len(d) for d in data])
    agg = np.zeros((min_length, data[0].shape[1]))

    #Truncate all data arrays longer than the smallest to ensure all over exact same duration
    for d in data:
        agg += d[:min_length]
    agg /= len(paths)

    #Plot data
    Golf_Analyser.plot_data(agg, 5, "Generations", "Average Matches per Game", "Average Matches per Game over Generations", "Best Solution", "Worst Solution", "Population Average", "Population Highest", "Population Lowest")

p = "one_hot_hand"
average_mean_scores("games/neat_random", p, xlabel="Generations")
average_number_matches("games/neat_random", p, xlabel="Generations")
average_card_frequency("games/neat_random", p, xlabel="Generations")
average_rounds_ended("games/neat_random", p, xlabel="Generations")
#average_population_mean_scores("games/neat", p)
#average_population_mean_matches("games/neat", p)