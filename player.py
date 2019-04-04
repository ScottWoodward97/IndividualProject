from abc import ABC, ABCMeta, abstractmethod

import random
import math
from golf import Golf
from actions import Actions
from function_approximator import CoEvo_Func_Approx
from deck import Deck


class Player(ABC):
    """
    """
    def __init__(self, state_function, function_approximator):
        self.hand = [] ##Create a custom hand for the game
        #self.state_function = state_function
        if function_approximator is None:
            self.function_approximator = CoEvo_Func_Approx(27, state_function)
        else:
            self.function_approximator = function_approximator ##Load in a function_approximator


    ##POLICIES
    @abstractmethod
    def choose_draw(self, top_discard, game_state):
        """
        """
        #Store values of all states with all possible cards drawn from deck
        #Store values of all states with card drawn from discard
        #If deck state is better more than 50% of the time draw from deck, else from discard
        #ACTIONS.DRAW_DECK or ACTIONS.DRAW_DISCARD

        pass

    @abstractmethod
    def choose_discard(self, drawn_card, game_state):
        """
        """
        pass

class Golf_Player(Player):
    """
    """
    def __init__(self, state_function, function_approximator=None):
        super().__init__(state_function, function_approximator)

    def choose_draw(self, top_discard, game_state):
        """
        """
        #val, suit = top_discard.get_val_suit()
        val_discard, _ = self.max_val_ind_exchange(Golf.get_card_index(top_discard), game_state)

        val_current = self.function_approximator.value_of_state(game_state)
        if val_current > val_discard:
            return Actions.DRAW_DECK

        #Tallys if unknown exchange is over or less than or equal to val_discard
        over, leq = 0, 0

        #can change to a single variable, if + then over else if - then under
        for i in range(len(game_state)):
            if game_state[i] == -1: #Locations.UNKNOWN:
                #v, s = self.get_val_suit(i)
                val, _ = self.max_val_ind_exchange(i, game_state)
                if val > val_discard:
                    over += 1
                else:
                    leq += 1

        return Actions.DRAW_DECK if over > leq else Actions.DRAW_DISCARD


    def choose_discard(self, drawn_card, game_state):
        """
        """
        ##If unknown, just add drawn card to hand to evaluate,
        ##If known, also add discarded card to discard pile

        ##Should also compare all switches with an unswitched version of the hand.

        #Need to consider difference between card drawn from deck and discard, not let card drawn from discard be discarded.
        #Check what position card was in?? If -2 then don't let discard, if -1 then allow??
        
        
        #v_d, s_d = drawn_card.get_val_suit()

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
        """
        max_val, index = -math.inf, 0
        #ind_d = (suit-1)*13 + value-1 #Can replace with Golf method

        for i, card in enumerate(self.hand):
            temp_state = game_state[:]
            temp_state[exchange_index] = i

            #v, s = card.get_val_suit()
            #if v > 0:
            ind = Golf.get_card_index(card) #(s-1)*13 + v-1 #replace this too
            #get_card_index returns None if card is hidden
            if ind is not None:
                temp_state[ind] = -2

            val = self.function_approximator.value_of_state(temp_state)
            if val > max_val:
                max_val, index = val, i

        return max_val, index

    def get_val_suit(self, index):
        """
        DONT THINK THIS IS NEEDED HERE, MAYBE IN A METHOD TO MAKE DATA VERBOSE??
        """
        suit = (index // 13) + 1 if index <= 51 else (-2 if index == 52 else -1)

        val = (index - (suit-1)*13 + 1) if index >= 0 else -1

        return (val, suit)

    def update_network(self, opposing_player, crossover=0.05):
        self.function_approximator.update(opposing_player.function_approximator, crossover)

    def add_noise(self, mean=0.0, sd=0.1):
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
        ##Uh oh, can't allow it to discard a card is drawn from the discard pile
        disc_options = [0,1,2,3,4,5]
        if game_state[Golf.get_card_index(drawn_card)] == -2:
            disc_options += [8]
        return Actions(random.choice(disc_options))

class Greedy_Golf_Player(Player):
    def __init__(self):
        super().__init__([], [])

    def choose_draw(self, top_discard, game_state):
        """
        """
        return Actions.DRAW_DECK if 6 < top_discard.get_val_suit()[0] < 13 else Actions.DRAW_DISCARD

    def choose_discard(self, drawn_card, game_state):
        """
        """
        v, _ = drawn_card.get_val_suit()
        for i in range(6):
            if self.hand[i].hidden == False and Golf.card_score(v) < Golf.card_score(self.hand[i].get_val_suit()[0]):
                return Actions(i)
        
        disc_options = [i for i in range(6) if self.hand[i].hidden == True]
        #Prevent card drawn from discard pile from being discarded
        if game_state[Golf.get_card_index(drawn_card)] == -2:
            disc_options += [8]
        return Actions(random.choice(disc_options))
