"""
---function_approximator.py---
Contains the function approximator classes as well as functions that can convert game states to the different input representations.
"""
from abc import ABC, abstractmethod
import random
from neural_net import Neural_Network
import numpy as np
import neat

class Func_Approx(ABC):
    """
    The function approximator of a player, which allows for game states to be evaluated and assigned a numerical value.
    Attributes:
        state_function (function): A function which converts the game state into a suitable format for the neural network.
        network (Neural_Network): The neural network that calculates the value of the game state once the input has been converted.
    """

    def __init__(self, state_function, network=None):
        self.state_function = state_function
        self.network = network

    @abstractmethod
    def value_of_state(self, state):
        pass

class CoEvo_Func_Approx(Func_Approx):
    """
    The function approximator for players trained with the coevolution algorithm.
    Contains the relevent methods for updating and mutating the weights of the network.
    Attributes:
        n_hidden (int): The number of nodes in the hidden layer of the neural network.
        state_function (function): A function which converts the game state into a suitable format for the neural network.
    """
    def __init__(self, n_hidden, state_function):
        #Use the state function to calculate the number of inputs
        n_input = len(state_function([0]*54))
        network = Neural_Network(n_input, n_hidden, 1)
        super().__init__(state_function, network)

    def update(self, opposing_func_approx, crossover=0.05):
        """
        Updates the weights of the neural network in accordance with the coevolution algorithm.
        Moves the weights of the network in the direction of opposing_func_approx by the crossover rate.
        Args:
            opposing_func_approx (CoEvo_Func_Approx): The opposing (better) function approximator of the opponent
            crossover (float): The crossover rate of the update, the percentage in which the weights are moved in the direction of the opposing_func_approx.
        Returns: None
        """
        self.network.W_hidden = (opposing_func_approx.network.W_hidden - self.network.W_hidden)*crossover + self.network.W_hidden
        self.network.W_output = (opposing_func_approx.network.W_output - self.network.W_output)*crossover + self.network.W_output
        
    def value_of_state(self, state):
        """
        Calculates the value of the given game state via the neural network.
        The state_function is used to convert the input into a suitable format for the network.
        Args:
            state ([int]): The game state to be evaluated.
        Returns: A float which denotes the value of the given game state.
        """
        input_state = self.state_function(state)
        return self.network.feedforward(np.reshape(input_state, (1, len(input_state))))[0][0]

    def add_noise(self, mean=0.0, sd=0.1):
        """
        Adds Guassian noise to all weights in the nerual network via the numpy.random.normal method.
        Args:
            mean (float): The centre of the distribution. Default set to 0.0.
            sd (float): The standard deviation of the distribution. Default set to 0.1.
        Returns: None
        """
        self.network.W_hidden += np.random.normal(mean, sd, self.network.W_hidden.shape)
        self.network.W_output += np.random.normal(mean, sd, self.network.W_output.shape)

class NEAT_Func_Approx(Func_Approx):
    """
    The function approximator for players trained with the NEAT algorithm.
    Attributes:
        state_function (function): A function which converts the game state into a suitable format for the neural network.
        network (Neural_Network): The neural network that calculates the value of the game state once the input has been converted.
    """
    def __init__(self, state_function, network):
        super().__init__(state_function, network)

    def value_of_state(self, state):
        """
        Calculates the value of the given game state via the neural network.
        The state_function is used to convert the input into a suitable format for the network.
        Args:
            state ([int]): The game state to be evaluated.
        Returns: A float which denotes the value of the given game state.
        """
        input_state = self.state_function(state)
        return self.network.activate(input_state)[0] 

def one_hot_hand(state):
    """
    Converts the given game state into the one hot hand input representation.
    This input representation contains only in values of the cards in the player's hand using one hot encoding.
    Args:
        state([int]): The game state to be converted to the representation.
    Returns: An int array containing the new representation of the state.
    """
    hand = [0]*(6*15)
    for i in range(6):
        try:
            #Attempt to find each card in the players hand in the given game state
            ind = state.index(i)
            #If a card does, calculate its value and update the relevant element of the representation
            if ind <= 51:
                v = ind +1 - (ind//13)*13
                hand[i*15 + v] = 1
            else:
                hand[i*15 + 14] = 1
        #If the card is not in the player hand, update the relevant element of the representation
        except ValueError:
            hand[i*15] = 1
    return hand

def one_hot_state(state):
    """
    Converts the given game state into the one hot state input representation.
    This input representation denotes each card in the game and where it is located if known (values of -3 to 5) using one hot encoding.
    Args:
        state([int]): The game state to be converted to the representation.
    Returns: An int array containing the new representation of the state.
    """
    one_hot_state = []
    for card_pos in state:
        one_hot_card_pos = [0]*9
        #Update index of array based on card location (values of -3 to 5)
        one_hot_card_pos[card_pos] = 1
        one_hot_state += one_hot_card_pos
    return one_hot_state

def one_hot_state_and_hand(state):
    """
    Converts the given game state into the one hot state and hand input representation.
    This input representation denotes each card in the game and where it is located if known (values of -3 to 5) using one hot encoding.
    It makes use of the one hot hand representation to represent cards in the hand of the player.
    Args:
        state([int]): The game state to be converted to the representation.
    Returns: An int array containing the new representation of the state.
    """
    opp, dis, unk, hand = [0]*54, [0]*54, [0]*54, [0]*(6*15)
    
    #Add each card in the opponents hand, discard pile, or uknown to the relevant arrays
    for i in range(len(state)):
        if state[i] == -3:
            opp[i] = 1
        elif state[i] == -2:
            dis[i] = 1
        elif state[i] == -1:
            unk[i] = 1

    for i in range(6):
        try:
            #Attempt to find each card in the players hand in the given game state
            ind = state.index(i)
            #If a card does, calculate its value and update the relevant element of the representation
            if ind <= 51:
                v = ind +1 - (ind//13)*13
                hand[i*15 + v] = 1
            else:
                hand[i*15 + 14] = 1
        #If the card is not in the player hand, update the relevant element of the representation
        except ValueError:
            hand[i*15] = 1
    
    #Recombine separate arrays to form full input
    input_state = opp + dis + unk + hand
    return input_state