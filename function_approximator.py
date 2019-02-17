from abc import ABC, abstractmethod
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

        #return self.network.feedforward(np.reshape(state, (1, len(state))))[0][0]

        #input_state = np.reshape([1 if s>=0 else s for s in state], (1, len(state))) + 1
        #return self.network.feedforward(input_state)[0][0]

        #opp, dis, unk, hand = [0]*54, [0]*54, [0]*54, [0]*(6*14)
        #for i in range(len(state)):
        #    if state[i] == -3:
        #        opp[i] = 1
        #    elif state[i] == -2:
        #        dis[i] = 1
        #    elif state[i] == -1:
        #        unk[i] = 1
        #    else:
        #        if i <= 51:
        #            s = (i//13) +1
        #            v = i + 1 - (s-1)*13
        #            hand[state[i]*14 + v - 1] = 1
        #        else:
        #            hand[state[i]*14 + 13] = 1
        
        #input_state = opp + dis + unk + hand
        #return self.network.feedforward(np.reshape(input_state, (1, len(input_state))))[0][0]

        #hand = [0]*(6*15)
        #for i in range(6):
        #    try:
        #        ind = state.index(i)
        #        if ind <= 51:
        #            v = ind +1 - (ind//13)*13
        #            hand[i*15 + v] = 1
        #        else:
        #            hand[i*15 + 14] = 1
        #    except ValueError:
        #        hand[i*15] = 1
        
        #return self.network.feedforward(np.reshape(hand, (1, len(hand))))[0][0]




    def update(self, opposing_func_approx, crossover=0.05):
        self.network.W_hidden = (opposing_func_approx.network.W_hidden - self.network.W_hidden)*crossover + self.network.W_hidden
        self.network.W_output = (opposing_func_approx.network.W_output - self.network.W_output)*crossover + self.network.W_output
        

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