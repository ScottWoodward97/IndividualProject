import numpy as np
from sklearn.neural_network import MLPRegressor
import sklearn.metrics
import time
import sys

def score_hand(hand):
        score = 0
        for i in range(3):
            card_1, card_2 = hand[i], hand[i+3]
            #Only add to score if values do not match
            if card_1 != card_2:
                score += card_score(card_1) + card_score(card_2)
        return score

def card_score(value):
    return 0 if value == 13 else (10 if value > 10 else (-2 if value == -1 else value))

def one_hot(hand):
    oh_hand = []
    for card in hand:
        oh_card = [0]*14
        if card > 0:
            oh_card[card-1] = 1
        else:
            oh_card[card] = 1
        oh_hand += oh_card
    return oh_hand

t_start = time.time()
deck = [1,2,3,4,5,6,7,8,9,10,11,12,13]*4 + [-1,-1]
TRAINING_SIZE = 100000
TESTING_SIZE  = 100000

try:
    if sys.argv[1] == 'one-hot':
        INPUT_SIZE = 84
    elif sys.argv[1] == 'numeric':
        INPUT_SIZE = 6
    else:
        raise ValueError("Invalid command line argument. Enter either 'numeric' or 'one-hot'.")
except Exception:
    raise IndexError("Missing command line argument. Enter either 'numeric' or 'one-hot'.")

data = np.stack([np.random.choice(deck, 6, False) for _ in range(TRAINING_SIZE + TESTING_SIZE)])
targets = np.array([score_hand(hand) for hand in data])
if INPUT_SIZE == 84:
    data = np.stack([one_hot(hand) for hand in data])
t_data = time.time()
print("Time taken to generating dataset: %.3f" % (t_data - t_start))

nn = MLPRegressor((20,), 'logistic', max_iter=5000)
nn.fit(data[:TRAINING_SIZE], targets[:TRAINING_SIZE])
t_train = time.time()
print("Time taken to train network: %.3f" % (t_train - t_data))

preds = np.array([nn.predict(np.reshape(hand, (1,INPUT_SIZE))) for hand in data[TRAINING_SIZE:]])
print("Total time taken: %.3f" % (time.time() - t_start))

print("Average difference between target and prediction: %.3f" % sklearn.metrics.mean_absolute_error(targets[TRAINING_SIZE:], preds))
print("R^2 value of the network: %.3f" % sklearn.metrics.r2_score(targets[TRAINING_SIZE:], preds))
