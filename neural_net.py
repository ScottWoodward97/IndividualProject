import numpy as np

class Neural_Network():
    def __init__(self, n_input, n_hidden, n_output):
        self.n_input = n_input
        self.n_hidden = n_hidden
        self.n_output = n_output

        #Randomly initialise weights of the network such that each weight is independently
        #drawn from a uniform distribution of [-1.0, 1.0).
        #Adding one to the hidden weights to include hidden layer biases
        self.W_hidden = np.zeros((n_input + 1, n_hidden)) #np.random.uniform(-1.0, 1.0, (n_input+1, n_hidden)) #
        self.W_output = np.zeros((n_hidden, n_output)) #np.random.uniform(-1.0, 1.0, (n_hidden, n_output)) #

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
        """
        #Add bias inputs (1) to the input data
        inp = np.append(np.ones((data_in.shape[0], 1)), data_in, axis=1)
        hidden_out = self._sigmoid(np.dot(inp, self.W_hidden))
        output = np.dot(hidden_out, self.W_output) #self._sigmoid() #might not want this 'sigmoided'
        return output

    #Dont know if this is something that should be in here
    #def coevo_update(self, network):
    #    """
    #    """
    #    #W_new = (W_network - W_self)*0.05 + W_self
    #    self.W_hidden = (network.W_hidden - self.W_hidden)*0.05 + self.W_hidden
    #    self.W_output = (network.W_output - self.W_output)*0.05 + self.W_output

    #def add_noise(self, mean=0.0, sd=0.1):
    #    """
    #    Adds Guassian noise to all weights in the network via the numpy.random.normal method.
    #    Args:
    #        mean (float): The centre of the distribution. Default set to 0.0.
    #        sd (float): The standard deviation of the distribution. Default set to 0.1.
    #    Returns: None
    #    """
    #    self.W_hidden += np.random.normal(mean, sd, (self.n_input, self.n_hidden))
    #    self.W_output += np.random.normal(mean, sd, (self.n_hidden, self.n_output))