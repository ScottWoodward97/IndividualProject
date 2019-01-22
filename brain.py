from abc import ABC, ABCMeta, abstractmethod
import random

class Brain(ABC):

    def __init__(self, network=None):
        if network is None:
            self.network = [] ##NEW NETWORK
        else:
            self.network = network ##LOAD NETWORK FROM FILE

    @abstractmethod
    def value_of_state(self, input):
        pass #Output of the neural network

    ##TODO: add methods for training the network

class Random_Brain(Brain):
    def __init__(self):
        super().__init__()

    def value_of_state(self, input):
        return random.random()