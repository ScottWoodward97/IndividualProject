from abc import ABC, ABCMeta, abstractmethod

import random
import math
from golf import Golf
from actions import Actions
from brain import Random_Brain
from deck import Deck


class Player(ABC):
    def __init__(self, brain):
        self.hand = [] ##Create a custom hand for the game
        self.brain = brain ##Load in a brain


    ##POLICIES
    @abstractmethod
    def choose_draw(self, top_discard, game_state):
        #Store values of all states with all possible cards drawn from deck
        #Store values of all states with card drawn from discard
        #If deck state is better more than 50% of the time draw from deck, else from discard
        #ACTIONS.DRAW_DECK or ACTIONS.DRAW_DISCARD

        pass 
    
    @abstractmethod
    def choose_discard(self, drawn_card, game_state):
        pass

class Golf_Player(Player):
    def __init__(self, brain=Random_Brain()):
        super().__init__(brain)

    def choose_draw(self, top_discard, game_state):
        val, suit = top_discard.get_val_suit()
        val_discard, _ = self.max_val_ind_exchange(val, suit, game_state)

        #Tallys if unknown exchange is over or less than or equal to val_discard
        over, leq = 0,0

        for i in range(len(game_state)):
            if game_state[i] == -1: #Locations.UNKNOWN:
                v,s = self.get_val_suit(i)
                val,_ = self.max_val_ind_exchange(v,s, game_state)
                if val > val_discard:
                    over += 1
                else:
                    leq += 1

        return Actions.DRAW_DECK if over > leq else Actions.DRAW_DISCARD
        

    def choose_discard(self, drawn_card, game_state):
        ##If unknown, just add drawn card to hand to evaluate,
        ##If known, also add discarded card to discard pile

        ##Should also compare all switches with an unswitched version of the hand.
        max_val = self.brain.value_of_state(game_state)
        v_d, s_d = drawn_card.get_val_suit()
        
        val, ind = self.max_val_ind_exchange(v_d, s_d, game_state)

        index = ind if val > max_val else 8

        return Actions(index)

    def max_val_ind_exchange(self, value, suit, game_state):
        
        max_val, index = -math.inf, 0
        ind_d = (suit-1)*13 + value-1

        for i, card in enumerate(self.hand):
            temp_state = game_state[:]
            temp_state[ind_d] = i #Locations(i)
            
            v,s = card.get_val_suit()
            if v>0:
                ind = (s-1)*13 + v-1
                temp_state[ind] = -2 #Locations.IN_DISC_PILE

            val = self.brain.value_of_state(temp_state)
            if val > max_val:
                max_val, index = val, i

        return max_val, index

    def get_val_suit(self, value):
        s = (value // 13) + 1 if value <=51 else (-2 if value == 52 else -1)

        v = (value - (s-1)*13 + 1) if value >= 0 else -1   

        return (v,s)

class Random_Golf_Player(Player):

    def __init__(self):
        super().__init__(None)

    def choose_draw(self, top_discard, game_state):
        return random.choice([Actions.DRAW_DECK, Actions.DRAW_DISCARD])

    def choose_discard(self, drawn_card, game_state):
        return Actions( random.choice([0,1,2,3,4,5,8]) )

class Greedy_Golf_Player(Player):
    def __init__(self):
        super().__init__(None)

    def choose_draw(self, top_discard, game_state):
        return Actions.DRAW_DECK if 6 < top_discard.get_val_suit()[0] < 13 else Actions.DRAW_DISCARD

    def choose_discard(self, drawn_card, game_state):
        v, _ = drawn_card.get_val_suit()
        for i in range(6):
            if self.hand[i].hidden == False and Golf.card_score(v) < Golf.card_score(self.hand[i].get_val_suit()[0]):
                return Actions(i)

        return Actions( random.choice([i for i in range(6) if self.hand[i].hidden == True] + [8]) )