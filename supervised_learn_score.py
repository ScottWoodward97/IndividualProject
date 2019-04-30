"""
---supervised_learn_score.py---
Trains a neural network via supervised learning to learn the scoring sytsem of the game of Golf with hands using numerical and one hot encoding.
The neural network, from Sci Kit Learn, is trained on 100,000 hands of Golf and their scores.
Once trained, it is evaluated on a further 100,000 games of Golf.
The mean absolute error and r^2 value are extracted and displayed along with the time taken to train.
Args:
    INPUT_SIZE (String): The first command line argument. The representation of the hands when given to the neural network.
            Must be either numeric or one-hot.
"""
import numpy as np
from sklearn.neural_network import MLPRegressor
import sklearn.metrics
import time
import sys

def score_hand(hand):
    """
    Calculate the score of a hand of Golf.
    Args:
        hand ([int]): Represents the hand of golf where each card is represented by its value
    """
    score = 0
    for i in range(3):
        card_1, card_2 = hand[i], hand[i+3]
        #Only add to score if values do not match
        if card_1 != card_2:
            score += card_score(card_1) + card_score(card_2)
    return score

def card_score(value):
    """
    Returns the corresponding score of a cards value.
    Args:
        value (int): The value of a card (1-13 or -1).
    """
    return 0 if value == 13 else (10 if value > 10 else (-2 if value == -1 else value))

def one_hot(hand):
    """
    Represent the values of the cards in the hand with one hot encoding.
    Each card is represented by 14 bits where one bit represents each card Ace-King + Joker.
    Args:
        hand ([int]): A list of 6 integers representing a hand of Golf.
    Returns: A list of integers representing the given hand under one hot encoding
    """
    oh_hand = []
    for card in hand:
        #represent each card in one hot encoding
        oh_card = [0]*14
        if card > 0:
            oh_card[card-1] = 1
        else:
            oh_card[card] = 1
        #Concatenate the cards to form the hand representation
        oh_hand += oh_card
    return oh_hand

t_start = time.time()
#Initialise the deck
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

#Generate the dataset of hands of golf and their target scores, both the training and testing set
data = np.stack([np.random.choice(deck, 6, False) for _ in range(TRAINING_SIZE + TESTING_SIZE)])
targets = np.array([score_hand(hand) for hand in data])

#Encode the hands with one hot encoding if requested
if INPUT_SIZE == 84:
    data = np.stack([one_hot(hand) for hand in data])
t_data = time.time()
print("Time taken to generating dataset: %.3f" % (t_data - t_start))

#Trains the MLPRegressor with on the training set
nn = MLPRegressor((20,), 'logistic', max_iter=5000)
nn.fit(data[:TRAINING_SIZE], targets[:TRAINING_SIZE])
t_train = time.time()
print("Time taken to train network: %.3f" % (t_train - t_data))

#Run the testing dataset through the network to acquire its predictions
preds = np.array([nn.predict(np.reshape(hand, (1,INPUT_SIZE))) for hand in data[TRAINING_SIZE:]])
print("Total time taken: %.3f" % (time.time() - t_start))

#Calculates the mean absolute error and r^2 value of the trained network 
print("Average difference between target and prediction: %.3f" % sklearn.metrics.mean_absolute_error(targets[TRAINING_SIZE:], preds))
print("R^2 value of the network: %.3f" % sklearn.metrics.r2_score(targets[TRAINING_SIZE:], preds))
