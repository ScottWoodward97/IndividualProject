##DEPRECATED - REPLACING WITH FUNCTION_APPROXIMATOR.PY
from abc import ABC, ABCMeta, abstractmethod
import random
from neural_net import Neural_Network
import numpy as np

class Func_Approx(ABC):

    def __init__(self, network=None):
        self.network = network

    @abstractmethod
    def value_of_state(self, data_in):
        pass 

class Random_Func_Approx(Func_Approx):
    def __init__(self):
        super().__init__()

    def value_of_state(self, data_in):
        return random.random()

class CoEvo_Func_Approx(Func_Approx):
    def __init__(self, n_input, n_hidden):
        network = Neural_Network(n_input, n_hidden, 1)
        super().__init__(network)

    def value_of_state(self, state):
        one_hot_state = []
        for card_pos in state:
            one_hot_card_pos = [0]*9
            one_hot_card_pos[card_pos] = 1
            one_hot_state += one_hot_card_pos

        return self.network.feedforward(np.reshape(one_hot_state, (1, len(one_hot_state))))[0][0]

    def update(self, opposing_func_approx):
        self.network.coevo_update(opposing_func_approx.network)

    def add_noise(self):
        self.network.add_noise()