import time
import os
from operator import add
import glob
import numpy as np
import itertools

from golf import Golf_Analyser

DIR_PATH = os.path.join('games', 'coevo_score_with_random_analysis', 'one_hot_hand_2', 'training')

files = glob.glob('%s/*.txt' % DIR_PATH)


#Open the files in pairs which will allow for the games to be stored in chronological order of when they were played
scores = []
hands = []
turns = []
end = []
            
pair_files = np.reshape(files, (len(files)//2, 2))
for pair in pair_files:
    #scores_0, scores_1 = [],[]
    #hands_0, hands_1 = [],[]
            
    with open(pair[0], 'r') as f0:
        games_0 = f0.read().split('\n\n')[:-1]
    for game in games_0:
        scores.append(Golf_Analyser.extract_scores(game + '\n'))
        hands += Golf_Analyser.extract_hands(game + '\n')
        turns += Golf_Analyser.extract_number_of_turns(game + '\n')
        end += Golf_Analyser.extract_rounds_ended(game + '\n')
            
    with open(pair[1], 'r') as f1:
        games_1 = f1.read().split('\n\n')[:-1]
    for game in games_1:
        scores.append(Golf_Analyser.extract_scores(game + '\n')[::-1])
        tmp_hands = Golf_Analyser.extract_hands(game + '\n')
        hands += [h[::-1] for h in tmp_hands]
        turns += Golf_Analyser.extract_number_of_turns(game + '\n')
        tmp_ends = Golf_Analyser.extract_rounds_ended(game + '\n')[0]
        end += [tmp_ends[:-1][::-1] + tmp_ends[-1:]]

    #scores += [s for s in itertools.chain.from_iterable(zip(scores_0, scores_1))]
    #hands += [h for h in itertools.chain.from_iterable(zip(hands_0, hands_1))]


np_scores = np.array(scores)
#print(np_scores)

score_means = np.mean(np_scores, axis=0)
score_mins = np.amin(np_scores, axis=0)
score_maxs = np.amax(np_scores, axis=0)

matches=[]
for hand_pair in hands:
    asc_vals_player = [ord(card) for card in hand_pair[0]]
    player_matches = sum((asc_vals_player[i] > 116 and asc_vals_player[i+3] > 116) 
                        or (asc_vals_player[i] < 117 and asc_vals_player[i+3] < 117 and (asc_vals_player[i] - asc_vals_player[i+3])%13==0) for i in range(3))
                
    asc_vals_opponent = [ord(card) for card in hand_pair[1]]
    opponent_matches = sum((asc_vals_opponent[i] > 116 and asc_vals_opponent[i+3] > 116) 
                        or (asc_vals_opponent[i] < 117 and asc_vals_opponent[i+3] < 117 and (asc_vals_opponent[i] - asc_vals_opponent[i+3])%13==0) for i in range(3))
    matches.append([player_matches, opponent_matches])

match_mean = np.mean(matches, axis=0)*9

end_dist = 100*np.sum(end, axis=0)/np.sum(end)


print("Player average: %.2f points per game" % score_means[0])
print("Player score range: [%d, %d]" % (score_mins[0], score_maxs[0]))
print("Player makes %.2f matches per game on average " % match_mean[0])
print("Player ends %.2f%% of matches" % end_dist[0])
print()
print("Opponent average: %.2f points per game" % score_means[1])
print("Opponent score range: [%d, %d]" % (score_mins[1], score_maxs[1]))
print("Opponent makes %.2f matches per game on average " % match_mean[1])
print("Opponent ends %.2f%% of matches" % end_dist[1])
print()
print("Rounds take %.2f turns on average" % np.mean(turns))

print()