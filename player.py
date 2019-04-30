"""
---player.py---
Contains all three player classes that will be used to play the game of golf.
The Random_Golf_Player is a player that makes moves randomly, simulating a player with no inteligence.
The Greedy_Golf_Player is a heuristic player that still makes moves randomly but has some knowledge of the game.
    This means that they can make human like decisions and thus simulate a more human-like player.
The Golf_player is the player that makes moves using a funtion approximator. This is trained using various training algorithms.
"""
from abc import ABC, ABCMeta, abstractmethod

import random
import math
from golf import Golf
from actions import Actions
from function_approximator import CoEvo_Func_Approx
from deck import Deck


class Player(ABC):
    """
    An abstract class that contains all methods and attributes that a player needs to play the game of golf.
    Attributes:
        hand (list): Stores the hand of the player
        function_approximator (Func_Approx): The function approximator of the player that is used to evaluate game states.
    """
    def __init__(self, state_function, function_approximator):
        self.hand = []
        #If a function approximator is not provided, create a coevolution one with 27 hidden nodes
        if function_approximator is None:
            self.function_approximator = CoEvo_Func_Approx(27, state_function)
        else:
            self.function_approximator = function_approximator


    @abstractmethod
    def choose_draw(self, top_discard, game_state):
        """
        Given the state of the game and the card on top of the discard pile,
            the player decides whether to draw from the diacrd pile or the deck.
        Args:
            top_discard (Deck.Card): The top card of the discard pile
            game_state ([int]): The current game state
        """
        pass

    @abstractmethod
    def choose_discard(self, drawn_card, game_state):
        """
        Given the state of the game and the card that has been drawn,
            the player decides what card they should discard.
        Args:
            top_discard (Deck.Card): The card drawn
            game_state ([int]): The current game state
        """
        pass

class Golf_Player(Player):
    """
    The Golf_Player is a player that makes decisions using a function approximator.
    This function approximator evaluates any game state and the values help with the decisions making.
    Attributes:
        state_function (function): Converts the game state into a format suitable for the function approximator
        function_approximator (Func_Approx): The function approximator of the player that is used to evaluate game states.
    """
    def __init__(self, state_function, function_approximator=None):
        super().__init__(state_function, function_approximator)

    def choose_draw(self, top_discard, game_state):
        """
        Given the state of the game and the card on top of the discard pile,
            the player decides whether to draw from the diacrd pile or the deck.
        The player uses a policy along with the values returned by the function approximator to decide on the drawing location/
        If the maximum value of the card on top of the discard pile is better than 50% of the cards that could be in the deck,
            then the player draws from the discard pile.
        If not, or if the card does not improve the value of the hand at all, then the player draws from the deck.
        Args:
            top_discard (Deck.Card): The top card of the discard pile
            game_state ([int]): The current game state
        Returns: The drawing location as an Action
        """
        #Calculate the maximum value of the card and the current value of the game state
        val_discard, _ = self.max_val_ind_exchange(Golf.get_card_index(top_discard), game_state)
        val_current = self.function_approximator.value_of_state(game_state)

        #Draw from the deck if the card doesn't improve the hand
        if val_current > val_discard:
            return Actions.DRAW_DECK

        over, leq = 0, 0
        for i in range(len(game_state)):
            #Counts the number of unknwon cards that have a greater maxmimum value
            if game_state[i] == -1: 
                val, _ = self.max_val_ind_exchange(i, game_state)
                if val > val_discard:
                    over += 1
                else:
                    leq += 1

        #Draw from deck if there are more unknwon cards that are better, else draw from the deck
        return Actions.DRAW_DECK if over > leq else Actions.DRAW_DISCARD

    def choose_discard(self, drawn_card, game_state):
        """
        Given the state of the game and the card that has been drawn,
            the player decides what card they should discard.
        The player finds the exchange that produces the highest state evaluation.
        If the card does not improve on the hand then it is discarded, unless it has been drawn from the discard pile.
        Otherwise, the player exchanges with the card that produces the best game state.
        Args:
            top_discard (Deck.Card): The card drawn
            game_state ([int]): The current game state
        Returns: The discarded card location as an Action
        """
        
        val, ind = self.max_val_ind_exchange(Golf.get_card_index(drawn_card), game_state)

        #Prevent player from discarding card drawn from discard pile
        if game_state[Golf.get_card_index(drawn_card)] == -2:
            index = ind
        else:
            #Check if card improves upon current hand
            max_val = self.function_approximator.value_of_state(game_state)
            index = ind if val > max_val else 8

        return Actions(index)

    def max_val_ind_exchange(self, exchange_index, game_state):
        """
        Calculates the maximum value of a card by evaluating all potential states obtained by exchanging it 
            with every card in the player's hand.
        Args:
            exchange_index (int): The index of the card that is being exchanged. Allows for easier manipulation of the game states.
            game_state ([int]): The current game state
        Returns: A tuple containing the maximum value of the card and the index of exchanged card that results in that maximum value
        """
        max_val, index = -math.inf, 0

        #Cycles over each card in the player's hand.
        for i, card in enumerate(self.hand):
            #Prevents game state from being overwritten
            temp_state = game_state[:]
            temp_state[exchange_index] = i

            ind = Golf.get_card_index(card)
            #If the card is not hidden, then the player would known what card would go to the discard pile
            if ind is not None:
                temp_state[ind] = -2

            val = self.function_approximator.value_of_state(temp_state)
            if val > max_val:
                max_val, index = val, i

        return max_val, index

    def update_network(self, opposing_player, crossover=0.05):
        """
        Updates the weights of the neural network in accordance with the coevolution algorithm.
        Moves the weights of the network in the direction of opposing_func_approx by the crossover rate.
        Args:
            opposing_func_approx (CoEvo_Func_Approx): The opposing (better) function approximator of the opponent
            crossover (float): The crossover rate of the update, the percentage in which the weights are moved in the direction of the opposing_func_approx.
                By default, this is set to 0.05.
        Returns: None
        """
        self.function_approximator.update(opposing_player.function_approximator, crossover)

    def add_noise(self, mean=0.0, sd=0.1):
        """
        Adds Guassian noise to all weights in the nerual network via the numpy.random.normal method.
        Args:
            mean (float): The centre of the distribution. Default set to 0.0.
            sd (float): The standard deviation of the distribution. Default set to 0.1.
        Returns: None
        """
        self.function_approximator.add_noise(mean, sd)

class Random_Golf_Player(Player):
    """
    The Random_Golf_Player is a player that can play the game of golf 
        but all decisions, draw and discard, are made randomly with equal probability.
    """
    def __init__(self):
        super().__init__([], [])

    def choose_draw(self, top_discard, game_state):
        """
        Decides randomly whether to draw from the deck or to draw from the discard pile.
        It uses the choice method from the python random module.
        The decision is returned as an instance of the Actions IntEnum class.
        Args:
            top_discard (Card): Not used.
            game_state ([int]): Not used.
        Returns: An Actions object corresponding to the chosen draw location.
        """
        return random.choice([Actions.DRAW_DECK, Actions.DRAW_DISCARD])

    def choose_discard(self, drawn_card, game_state):
        """
        Decides randomly which card in its hand to exchange with the drawn_card or whether to discard it.
        It uses the choice method from the python random module.
        The decision is returned as an instance of the Actions IntEnum class.
        Args:
            drawn_card (Card): Not used.
            game_state ([int]): Not used.
        Returns: An Actions object corresponding to the card being discarded.
        """
        disc_options = [0,1,2,3,4,5]
        #Prevents the player discarding a card drawn from the discard pile
        if game_state[Golf.get_card_index(drawn_card)] != -2:
            disc_options += [8]
        return Actions(random.choice(disc_options))

class Greedy_Golf_Player(Player):
    """
    A (heuristic) player that can play the game of golf with some understanding of the game.
    The decisions made are greedier and most akin to how a human would play the game.
    """
    def __init__(self):
        super().__init__([], [])

    def choose_draw(self, top_discard, game_state):
        """
        Decides whether to draw from the deck or the discard pile.
        If the card on the top of the discard pile scores more than 6, then the player chooses to draw from the deck.
        Otherwise the player chooses to draw from the discard pile.
        The decision is returned as an instance of the Actions IntEnum class.
        Args:
            top_discard (Card): The card on top of the discard pile.
            game_state ([int]): Not used.
        Returns: An Actions object corresponding to the chosen draw location.
        """
        return Actions.DRAW_DECK if 6 < top_discard.get_val_suit()[0] < 13 else Actions.DRAW_DISCARD

    def choose_discard(self, drawn_card, game_state):
        """
        Decides which card in its hand to exchange with the drawn_card or whether to discard it.
        If there are any cards in the hand that score more than the drawn card, then the first card that scores more is exchanged.
        If the drawn card scores more than all visible cards in the hand, then it chooses from the remaining legal moves randomly.
        This random decision is made using pythons random choice method.        
        The decision is returned as an instance of the Actions IntEnum class.
        Args:
            drawn_card (Card): The card that has been drawn by the player.
            game_state ([int]): Not used.
        Returns: An Actions object corresponding to the card being discarded.
        """
        v, _ = drawn_card.get_val_suit()
        for i in range(6):
            #Exchanges the drawn card with the first card that scores more
            if self.hand[i].hidden == False and Golf.card_score(v) < Golf.card_score(self.hand[i].get_val_suit()[0]):
                return Actions(i)
        
        disc_options = [i for i in range(6) if self.hand[i].hidden == True]
        #Prevents the player discarding a card drawn from the discard pile
        if game_state[Golf.get_card_index(drawn_card)] != -2:
            disc_options += [8]
        #If no card scores more, choose from remaining legal moves randomly
        return Actions(random.choice(disc_options))
