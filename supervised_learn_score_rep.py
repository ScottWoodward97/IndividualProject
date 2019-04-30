"""
---supervised_learn_score_rep.py---
Trains a neural network via supervised learning to learn the scoring sytsem of the game of Golf with hands 
    using the index of the card as opposed to its value.
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

def score_hand(hand):
    """
    Calculate the score of a hand of Golf.
    Args:
        hand ([int]): Represents the hand of golf where each card is represented by its value
    """
    score = 0
    val_hand = [get_val(card) for card in hand]
    for i in range(3):
        card_1, card_2 = val_hand[i], val_hand[i+3]
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

def get_val(index):
    """
    Given the index of the card in the deck, return the value of the card.
    The index of the card is calculated by (s-1)*13 + 1
    Args:
        index (int): The index of the card in the deck
    Returns: The value of the card as an integer(1-13 or -1 if Joker)
    """
    suit = (index // 13) + 1 if index <= 51 else (-2 if index == 52 else -1)
    return (index - (suit-1)*13 + 1) if index >= 0 else -1

def convert(hand):
    """
    Encodes the hand into a larger, more abstracted one hot representation.
    Each card in the deck is represented by one of seven states, 
        one for each position in the hand and one for it not being in the hand.
    Args:
        hand ([int]): A list of 6 integers representing a hand of Golf.
    Returns: The hand represented under the larger one hot encoding 
    """
    state = [-1]*54
    #Identify the indexes of the cards in the hand
    for c,i in enumerate(hand):
        state[i] = c
    one_hot_state = []
    for card_pos in state:
        one_hot_card_pos = [0]*7
        one_hot_card_pos[card_pos] = 1
        one_hot_state += one_hot_card_pos
    return one_hot_state


t_start = time.time()
#Initialise the deck
deck = [i for i in range(54)]
TRAINING_SIZE = 100000
TESTING_SIZE  = 100000

#Generate the dataset of hands of golf and their target scores, both the training and testing set
data = [np.random.choice(deck, 6, False) for _ in range(TRAINING_SIZE + TESTING_SIZE)]
targets = np.array([score_hand(hand) for hand in data])
data = np.stack([convert(hand) for hand in data])

t_data = time.time()
print("Time taken to generating dataset: %.3f" % (t_data - t_start))

#Trains the MLPRegressor with on the training set
nn = MLPRegressor((20,), 'logistic', max_iter=5000)
nn.fit(data[:TRAINING_SIZE], targets[:TRAINING_SIZE])
t_train = time.time()
print("Time taken to train network: %.3f" % (t_train - t_data))

#Run the testing dataset through the network to acquire its predictions
preds = np.array([nn.predict(np.reshape(hand, (1,54*7))) for hand in data[TRAINING_SIZE:]])
print("Total time taken: %.3f" % (time.time() - t_start))

#Calculates the mean absolute error and r^2 value of the trained network 
print("Average difference between target and prediction: %.3f" % sklearn.metrics.mean_absolute_error(targets[TRAINING_SIZE:], preds))
print("R^2 value of the network: %.3f" % sklearn.metrics.r2_score(targets[TRAINING_SIZE:], preds))
