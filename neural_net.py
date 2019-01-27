import numpy as np

class Neural_Network():
    def __init__(self, n_input, n_hidden, n_output):
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output

        self.W_hidden = np.zeros((n_input, n_hidden)) #Need to change to random values
        self.W_output = np.zeros((n_hidden, n_output)) #Need to change to random values

    def _sigmoid(self, x):
        """
        Performs an element-wise sigmoid activation function on an array 'x'.
        Args:
            x (numpy.ndarray): An ndarray of float values.
        Returns: An ndarray containing all sigmoid outputs.
        """
        return 1/(1 + np.exp(-x))

    def feedforward(self, data_in):
        hidden_out = self._sigmoid(np.dot(data_in, self.W_hidden))
        output = self._sigmoid(np.dot(hidden_out, self.W_output)) #might not want this 'sigmoided'
        return output

    def coevo_update(self, network):
        #W_new = (W_network - W_self)*0.05 + W_self
        self.W_hidden = (network.W_hidden - self.W_hidden)*0.05 + self.W_hidden
        self.W_output = (network.W_output - self.W_output)*0.05 + self.W_output

    def add_noise(self, mean=0, sd=0.1):
        self.W_hidden += np.random.normal(mean, sd, (self.n_input, self.n_hidden))
        self.W_output += np.random.normal(mean, sd, (self.n_hidden, self.n_output))