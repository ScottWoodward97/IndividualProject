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
        self.network.W_hidden = (opposing_func_approx.network.W_hidden - self.network.W_hidden)*0.05 + self.network.W_hidden
        self.network.W_output = (opposing_func_approx.network.W_output - self.network.W_output)*0.05 + self.network.W_output
        
        #self.network.coevo_update(opposing_func_approx.network)

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