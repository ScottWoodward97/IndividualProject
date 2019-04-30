"""
---extract_statistics.py---
Extracts and displays the statistics of both players from a directory of game files.
The statistics displayed are the mean score, the win percentage, the percetage of rounds ended, 
    the average number of matches made per game and the average duration of a round.
"""
import time
import os
from operator import add
import glob
import numpy as np
import itertools
import sys
from golf import Golf_Analyser

scores = []
hands = []
turns = []
end = []

DIR_PATH = sys.argv[1]
#Finds paths of all texts files in the given directory
files = glob.glob('%s/*.txt' % DIR_PATH)

#Open the files in pairs which will allow for the games to be stored in chronological order of when they were played            
pair_files = np.reshape(files, (len(files)//2, 2))
for pair in pair_files:
            
    #Extract the scores, hands, turns, and number of rounds ended of the first file in the pair
    with open(pair[0], 'r') as f0:
        games_0 = f0.read().split('\n\n')[:-1]
    for game in games_0:
        scores.append(Golf_Analyser.extract_scores(game + '\n'))
        hands += Golf_Analyser.extract_hands(game + '\n')
        turns += Golf_Analyser.extract_number_of_turns(game + '\n')
        end += Golf_Analyser.extract_rounds_ended(game + '\n')
            
    #Extract the scores, hands, turns, and number of rounds ended of the first file in the pair
    with open(pair[1], 'r') as f1:
        games_1 = f1.read().split('\n\n')[:-1]
    for game in games_1:
        #Reverses the data to account for the reversed player positions
        scores.append(Golf_Analyser.extract_scores(game + '\n')[::-1])
        tmp_hands = Golf_Analyser.extract_hands(game + '\n')
        hands += [h[::-1] for h in tmp_hands]
        turns += Golf_Analyser.extract_number_of_turns(game + '\n')
        tmp_ends = Golf_Analyser.extract_rounds_ended(game + '\n')[0]
        end += [tmp_ends[:-1][::-1] + tmp_ends[-1:]]


#Calculates the average scores obtained by both players
np_scores = np.array(scores)
score_means = np.mean(np_scores, axis=0)

#Calculates the win percetnage of both players
num_wins = [sum(s[0] < s[1] for s in np_scores), sum(s[1] < s[0] for s in np_scores)]
win_perc = 100*np.array(num_wins)/len(np_scores)

matches=[]
#Calculates the number of matches made per game on average by both players
for hand_pair in hands:
    asc_vals_player = [ord(card) for card in hand_pair[0]]
    player_matches = sum((asc_vals_player[i] > 116 and asc_vals_player[i+3] > 116) 
                        or (asc_vals_player[i] < 117 and asc_vals_player[i+3] < 117 and (asc_vals_player[i] - asc_vals_player[i+3])%13==0) for i in range(3))
                
    asc_vals_opponent = [ord(card) for card in hand_pair[1]]
    opponent_matches = sum((asc_vals_opponent[i] > 116 and asc_vals_opponent[i+3] > 116) 
                        or (asc_vals_opponent[i] < 117 and asc_vals_opponent[i+3] < 117 and (asc_vals_opponent[i] - asc_vals_opponent[i+3])%13==0) for i in range(3))
    matches.append([player_matches, opponent_matches])

match_mean = np.mean(matches, axis=0)*9

#Calculates the percentage of rounds ended by both players
end_dist = 100*np.sum(end, axis=0)/np.sum(end)

#Displays the results of both players
print("Player wins %.2f%% of games" % win_perc[0])
print("Player average: %.2f points per game" % score_means[0])
print("Player makes %.2f matches per game on average" % match_mean[0])
print("Player ends %.2f%% of matches" % end_dist[0])
print()
print("Opponent wins %.2f%% of games" % win_perc[1])
print("Opponent average: %.2f points per game" % score_means[1])
print("Opponent makes %.2f matches per game on average" % match_mean[1])
print("Opponent ends %.2f%% of matches" % end_dist[1])
print()
print("Rounds take %.2f turns on average" % np.mean(turns))
print()