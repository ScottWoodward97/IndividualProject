"""
---coevo_train_env.py---
An environment for training players using a coevolution algorithm.
Player files are loaded from the given directory or created if the do not exist.
Players play an epoch of 10 games against their training opponent, either the player or opponent is updated as a result of their games.
Players also an epoch of play 10 games against the random player but these games make no impact on the training.
After 25 epochs, the player files are serialised and games written to the directory specified.

Args:
    DIR_PATH (String): First command line argument. The path of the directory where player files exist or are to be saved.
    STATE_FUNCTION (String): Second command line argument. The name of the function approximator used by the player.
        Must be one of either "one_hot_hand", "one_hot_state_and_hand", or "one_hot_state". Only used when no player files exist in DIR_PATH
"""
import pickle
import os
import sys
import queue
import threading
import copy
from operator import add
import numpy as np

from golf import Golf, Golf_Analyser
from player import Golf_Player, Random_Golf_Player
import function_approximator as fa

def check_exit(input_queue):
    """
    Monitors the user input to allow for the training to be stopped safely.
    Data is added to input_queue if the user enters "exit".
    Args:
        input_queue(queue): A queue object representing a user buffer
    Returns: None
    """
    while True:
        inp = sys.stdin.readline().rstrip()
        if inp == "exit":
            #Breaks infinte loop if the user stops the training
            input_queue.put(inp)
            print("Exiting")
            break

BATCH_SIZE = 25
NUM_PAIRS = 5
POINTS_THRESHOLD = 15*NUM_PAIRS*2

#Handles command line arguments
DIR_PATH = sys.argv[1]
if sys.argv[2] == "one_hot_hand":
    STATE_FUNCTION = fa.one_hot_hand
elif sys.argv[2] == "one_hot_state_and_hand":
    STATE_FUNCTION = fa.one_hot_state_and_hand
elif sys.argv[2] ==  "one_hot_state":
    STATE_FUNCTION = fa.one_hot_state
else:
    raise AttributeError("Input representation must be either one_hot_hand, one_hot_state_and_hand, or one_hot_state")

#Creates relevant directories if they do not exist
if not os.path.exists(DIR_PATH):
    os.makedirs(DIR_PATH)
if not os.path.exists(os.path.join(DIR_PATH, "training")):
    os.makedirs(os.path.join(DIR_PATH, "training"))
if not os.path.exists(os.path.join(DIR_PATH, "random")):
    os.makedirs(os.path.join(DIR_PATH, "random"))

#Search given directory for player and opponent back-up files. Load if exist, create new if they do not 
try:
    with open(os.path.join(DIR_PATH, 'PLAYER_PICKLE.p'), 'rb') as f:
        player = pickle.load(f)
except FileNotFoundError:
    player = Golf_Player(STATE_FUNCTION)
try:
    with open(os.path.join(DIR_PATH, 'OPPONENT_PICKLE.p'), 'rb') as f:
        opponent = pickle.load(f)
except FileNotFoundError:
    opponent = Golf_Player(STATE_FUNCTION)
    opponent.add_noise()    #DELETE?????

#Create a golf and random_player instance
g = Golf()
random_player = Random_Golf_Player()

#initialise parameters to monitor user input
run = True
input_queue = queue.Queue()
#Daemon means thread will stop running once main program terminates
input_thread = threading.Thread(target=check_exit, args=(input_queue,), daemon=True)
input_thread.start()

##TRAINING##
while run:
    GAMES = ["",""]
    RANDOM_GAMES = ["",""]
    for _ in range(BATCH_SIZE):
        
        #Play games against the random player
        for _ in range(NUM_PAIRS):
            game_1, game_2 = g.play_pair(player, random_player)
            #Appends the result strings to each element in RANDOM_GAMES
            RANDOM_GAMES = list(map(add, RANDOM_GAMES, [game_1, game_2]))
            RANDOM_GAMES[0]+='\n'
            RANDOM_GAMES[1]+='\n'
        
        scores = []
        for _ in range(NUM_PAIRS):
            game_1, game_2 = g.play_pair(player, opponent)
            scores_1 = Golf_Analyser.extract_scores(game_1)
            scores_2 = Golf_Analyser.extract_scores(game_2)
        
            #print(scores_1)
            #print(scores_2[::-1])
            
            #Append the scores from the pair of games to the scores variable
            scores.append(scores_1)
            scores.append(scores_2[::-1]) #Reverse scores due to reversed positions
            
            #Appends the result strings to each element in RANDOM_GAMES
            GAMES = list(map(add, GAMES, [game_1, game_2]))
            GAMES[0]+='\n'
            GAMES[1]+='\n'

        #print() #ADD BETTER DISPLAY
        
        total_scores = np.sum(scores, axis=0)
        print("End of Epoch")
        print("Player mean score  : %.2f" % total_scores[0]/(NUM_PAIRS*2))
        print("Opponent mean score: %.2f\n" % total_scores[1]/(NUM_PAIRS*2))
        
        #Update the relevant player according to the differences in their scores
        if total_scores[0] < total_scores[1] - 2*POINTS_THRESHOLD:
            opponent = copy.deepcopy(player)
            opponent.add_noise()
        elif total_scores[0] < total_scores[1] - POINTS_THRESHOLD:
            opponent.update_network(player)
        elif total_scores[0] > total_scores[1] + 2*POINTS_THRESHOLD:
            player = copy.deepcopy(opponent)
            player.add_noise()
        elif total_scores[0] > total_scores[1] + POINTS_THRESHOLD:
            player.update_network(opponent)
        else:
            opponent.add_noise()


    print("Writing to file")
    filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
    #Write games to file. Separate files are written for each permuitation of player positions to aid with analysis  
    for i in range(2):
        with open(os.path.join(DIR_PATH, "training", '%s%d.txt' % (filename, i)), 'w+') as f:
            f.write(GAMES[i])
        with open(os.path.join(DIR_PATH, "random", '%s%d.txt' % (filename, i)), 'w+') as f:
            f.write(RANDOM_GAMES[i])

    #Serialise players to file
    with open(os.path.join(DIR_PATH, 'PLAYER_PICKLE.p'), 'wb+') as f:
        pickle.dump(player, f)
    with open(os.path.join(DIR_PATH, 'OPPONENT_PICKLE.p'), 'wb+') as f:
        pickle.dump(opponent, f)

    #Detect if user has entered "exit"
    run = input_queue.empty()