"""
PSUEDO
SYS.ARGS: file location to save games to, loction of player pickled files

Try to load in players from file
If not possible, create them from new

loop until termination, either time based or number of batches made
    
    loop batch_size number of times
        play game
        add results to variable
        update the players function approximators
    write the game results to file
    back-up the players to file (or func approx)
    
    determine if user has entered terminating phrase, exit if so

"""

import time
import pickle
import os
import sys
import queue
import threading
from operator import add

from golf import Golf, Golf_Analyser
from player import Golf_Player

def check_exit(input_queue):
    while True:
        inp = sys.stdin.readline().rstrip()
        if inp == "exit":
            input_queue.put(inp)
            print("Exiting")
            break


#Replace with command line arguments
DIR_PATH = os.path.join('games', 'coevo', 'test')
if not os.path.exists(DIR_PATH):
    os.makedirs(DIR_PATH)

BATCH_SIZE = 10

#Search directory for player and opponent back-up files. Load if exist, create new if don't 
try:
    with open(os.path.join(DIR_PATH, 'PLAYER_PICKLE.p'), 'rb') as f:
        player = pickle.load(f)
        
        print("Loading player")

except FileNotFoundError:

    print("Creating player")

    player = Golf_Player()

try:
    with open(os.path.join(DIR_PATH, 'OPPONENT_PICKLE.p'), 'rb') as f:
        opponent = pickle.load(f)

        print("Loading opponent")

except FileNotFoundError:
    opponent = Golf_Player()

    print("Creating opponent")

g = Golf()


#t_1 = time.time()

##LOOP SETUP##
run = True
input_queue = queue.Queue()

#Daemon means thread will stop running once main program terminates
input_thread = threading.Thread(target=check_exit, args=(input_queue,), daemon=True)
input_thread.start()

##LOOP##
while run:
    GAMES = ["",""]
    for _ in range(BATCH_SIZE):
        player_wins = 0
        for _ in range(2):
            game_1, game_2 = g.play_pair(player, opponent)
            scores_1 = Golf_Analyser.extract_scores(game_1)
            if scores_1[0] < scores_1[1]:
                player_wins += 1
            scores_2 = Golf_Analyser.extract_scores(game_2)
            if scores_2[1] < scores_2[0]:
                player_wins += 1
        
            print(scores_1)
            print(scores_2[::-1])

            GAMES = list(map(add, GAMES, [game_1, game_2]))
            GAMES[0]+='\n'
            GAMES[1]+='\n'

        print()

        if player_wins <= 2:
            player.update_network(opponent)

        opponent.add_noise()

    print("Writing to file")

    filename = time.strftime("%Y%m%d-%H%M%S-", time.gmtime())
    for i in range(2):
        with open(os.path.join(DIR_PATH, '%s%d.txt' % (filename, i)), 'w+') as f: #look at a+ instead, will append if the file exists
            f.write(GAMES[i])

    with open(os.path.join(DIR_PATH, 'PLAYER_PICKLE.p'), 'wb+') as f:
        pickle.dump(player, f)
    with open(os.path.join(DIR_PATH, 'OPPONENT_PICKLE.p'), 'wb+') as f:
        pickle.dump(opponent, f)

    run = input_queue.empty()

##END LOOP##

#t_2 = time.time()
#print(t_2 - t_1)

#argc = len(sys.argv) 
#if argc < 3:
#    print("Need more args")
    #Exit
#else:
#    dir_path = sys.argv[1]
#    batch_size = int(sys.argv[2])