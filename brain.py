##DEPRECATED - REPLACING WITH FUNCTION_APPROXIMATOR.PY
#Essentially just a refactor
from abc import ABC, ABCMeta, abstractmethod
import random
from neural_net import Neural_Network
import numpy as np

class Brain(ABC):

    def __init__(self, network=None):
        self.network = network ##LOAD NETWORK FROM FILE

    @abstractmethod
    def value_of_state(self, data_in):
        pass #Output of the neural network

    ##TODO: add methods for training the network

class Random_Brain(Brain):
    def __init__(self):
        super().__init__()

    def value_of_state(self, data_in):
        return random.random()

class Co_Evo_Brain(Brain):
    def __init__(self, n_input, n_hidden, n_output):
        network = Neural_Network(n_input, n_hidden, n_output)
        super().__init__(network)

    def value_of_state(self, data_in):
        return self.network.feedforward(np.reshape(data_in, (1, len(data_in))))

    def update(self, opposing_net):
        self.network.coevo_update(opposing_net)

    def add_noise(self):
        self.add_noise()