import numpy as np
from sklearn.neural_network import MLPRegressor
import sklearn.metrics
import time

def score_hand(hand):
        score = 0
        val_hand = [get_val(card) for card in hand]
        for i in range(3):
            card_1, card_2 = val_hand[i], val_hand[i+3]
            #Only add to score if values do not match
            if card_1 != card_2:
                score += card_score(card_1) + card_score(card_2)
        return score

def card_score(value):
    return 0 if value == 13 else (10 if value > 10 else (-2 if value == -1 else value))

def get_val(index):
        suit = (index // 13) + 1 if index <= 51 else (-2 if index == 52 else -1)
        return (index - (suit-1)*13 + 1) if index >= 0 else -1

def convert(hand):
    state = [-1]*54
    for c,i in enumerate(hand):
        state[i] = c
    one_hot_state = []
    for card_pos in state:
        one_hot_card_pos = [0]*7
        one_hot_card_pos[card_pos] = 1
        one_hot_state += one_hot_card_pos
    return one_hot_state




t_start = time.time()
deck = [i for i in range(54)]
TRAINING_SIZE = 100000
TESTING_SIZE  = 100000


data = [np.random.choice(deck, 6, False) for _ in range(TRAINING_SIZE + TESTING_SIZE)]
targets = np.array([score_hand(hand) for hand in data])
data = np.stack([convert(hand) for hand in data])

t_data = time.time()
print("Time taken to generating dataset: %.3f" % (t_data - t_start))

nn = MLPRegressor((20,), 'logistic', max_iter=5000)
nn.fit(data[:TRAINING_SIZE], targets[:TRAINING_SIZE])
t_train = time.time()
print("Time taken to train network: %.3f" % (t_train - t_data))

preds = np.array([nn.predict(np.reshape(hand, (1,54*7))) for hand in data[TRAINING_SIZE:]])
print("Total time taken: %.3f" % (time.time() - t_start))

print("Average difference between target and prediction: %.3f" % sklearn.metrics.mean_absolute_error(targets[TRAINING_SIZE:], preds))
print("R^2 value of the network: %.3f" % sklearn.metrics.r2_score(targets[TRAINING_SIZE:], preds))
