"""
---neural_net.py---
Contains the bespoke neural network class.
"""
import numpy as np

class Neural_Network():
    """
    Contains all methods and attirbutes to represent a neural network.
    This neural network has a single input, hidden, and output layer with a customisable number of nodes in each layer (> 0).
    This neural network uses the sigmoid activation function and has biases at the hidden layer only.
    The weights of the network are initialised by drawing from a uniform distribution of [-1.0, 1.0).
    Args:
        n_input, n_hidden, n_output (int): The number of nodes at the input, hidden, and output layers of the network. (> 0)
        W_hidden, W_output (numpy.ndarray): Arrays of the weights of the hidden and output layers respectively.
    """
    def __init__(self, n_input, n_hidden, n_output):
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output

        #Randomly initialise weights of the network such that each weight is independently drawn from a uniform distribution of [-1.0, 1.0).
        self.W_hidden = np.random.uniform(-1.0, 1.0, (n_input+1, n_hidden)) #Adding one to the hidden weights to include hidden layer biases #np.zeros((n_input + 1, n_hidden))
        self.W_output = np.random.uniform(-1.0, 1.0, (n_hidden, n_output)) #np.zeros((n_hidden, n_output)) #

    def _sigmoid(self, x):
        """
        Performs an element-wise sigmoid activation function on an array 'x'.
        Args:
            x (numpy.ndarray): An ndarray of float values.
        Returns: An ndarray containing all sigmoid outputs.
        """
        return 1/(1 + np.exp(-x))

    def feedforward(self, data_in):
        """
        Feed the data forards through the neural network and return the output.
        Args:
            data_in (numpy.ndarray): The input data for the neural network.
        Returns: A float representing the output of the neural network
        """
        #Add bias inputs (1) to the input data
        inp = np.append(np.ones((data_in.shape[0], 1)), data_in, axis=1)
        hidden_out = self._sigmoid(np.dot(inp, self.W_hidden))
        output = np.dot(hidden_out, self.W_output)
        return output