#import game
from operator import add
import random
import time
import copy
import numpy as np

from deck import Deck
from actions import Actions

class Golf():
    """
    """

    def __init__(self, stock=None):
        #self.discard_pile = None
        #self.stock = None
        self.initialise(stock)

    def initialise(self, stock=None):
        """
        Initialises/Resets the deck and discard pile.
        If a deck has been specified (via the stock argument) then a deep copy is made, else a new deck is created.
        Args:
            stock (Deck): The deck to initialise the game with, set to None by default.
        Returns: None
        """
        self.discard_pile = []
        if stock is None:
            self.stock = Deck(deck=[], jokers=True)
        else:
            self.stock = copy.deepcopy(stock)

    def init_hand(self):
        """
        Creates and returns an empty object array of a fixed size (6,) to be the hand of a player.
        The object array is an ndarray from the numpy module.
        Returns: A numpy ndarray of size (6,) and dtype object.
        """
        return np.empty((6,), dtype=Deck.Card)

    def get_state(self, player, other_players):
        """
        Converts the current game state into a list of (54) integers from the perspective of one player.
        Each index in the list of integers uniquely represents a card in the deck, calculated by get_card_index.
        Each position that a card can be in is represented by an integer value raning from [-3,5] where;
        In Opponent's Hand  : -3
        In Discard Pile     : -2
        Unknown             : -1
        In Player's Hand    : 0-5 (refers to the index of the card in the hand)
        The function will iterate through all cards in known locations, including the discard pile and player hands,
        updating their position in the list with the relevent integer value.
        Args:
            player (Player): The player whose perspective the state is being generated from.
            other_players ([Player]): A list of the players in the game excluding 'player'.
        Returns: A list of 54 integers representing the game state.
        """
        
        #Initialise a state where all cards are unknown
        state = [-1]*54 

        #Iterate through cards in the discard pile
        for card in self.discard_pile:
            ind = self.get_card_index(card)
            if ind is not None:
                state[ind] = -2
            #v,s = card.get_val_suit()
            #if v == -1:
            #    state[s] = -2 #Locations.IN_DISC_PILE
            #else:
            #    state[ (s-1)*13 + v-1 ] = -2 #Locations.IN_DISC_PILE

        #Iterate through cards in opposing player hands
        for p in other_players:
            for card in p.hand:
                ind = self.get_card_index(card)
                if ind is None:
                    continue
                else:
                    state[ind] = -3
                #v,s = card.get_val_suit()
                #if v == 0:
                #    continue
                #elif v == -1:
                #    state[s] = -3 #Locations.IN_OPP_HAND
                #else:
                #    state[ (s-1)*13 + v-1 ] = -3 #Locations.IN_OPP_HAND

        #Iterate through cards in the players hand
        for i in range(6):
            ind = self.get_card_index(player.hand[i])
            if ind is None:
                continue
            else:
                state[ind] = i
            #v,s = player.hand[i].get_val_suit()
            #if v == 0:
            #    continue
            #elif v == -1:
            #    state[s] = i #Locations(i)
            #else:
            #    state[ (s-1)*13 + v-1 ] = i #Locations(i)

        return state

    def has_finished(self, player):
        """
        Determines if a player has reached the end of the game by checking if all cards in their hand are not hidden.
        Args:
            player (Player): The player whose hand is being checked.
        Returns: A boolean variable which is True if all cards in players hand are not hidden, False otherwise.
        """
        #Can replace card.hidden == False with not card.hidden but the former is more descriptive
        return all([card.hidden == False for card in player.hand])

    def reveal_hand(self, player):
        """
        Reveals all cards in a players hand by setting the hidden attributes to all cards to False.
        This function does so in place.
        Args:
            player (Player): The player whose hand is being revealed.
        Returns: None
        """
        for card in player.hand:
            card.hidden = False

    @staticmethod
    def get_card_index(card):
        """
        Calculates the index of a given card in the game state array using the suit and value of the card.
        For all non-joker cards, the index is calculated as (suit-1)*13 + value -1.
        The two jokers in the deck have indexes of 52 and 53.
        If the card is hidden then no index will be returned.
        Args:
            card (Deck.Card): The card whose index is being calculated.
        Returns: The calculated index of card or None if the card is 'hidden' (hidden == True)
        """
        v, s = card.get_val_suit()
        if v == 0:
            return None
        elif v == -1:
            return s
        else:
            return (s-1)*13 + v-1

    @staticmethod
    def card_score(value):
        """
        Calculates the score that a card (value) has.
        This is used when scoring an entire player hand at the end of the game.
        The scoring is as follows;
            Ace (1) - 10            : 1 - 10
            Jack (11), Queen (12)   : 10
            King (13)               : 0
            Joker (-1)              : -2
        Args:
            value (int): The value of the card in question
        Returns: An int representing the score of the value.
        """
        return 0 if value == 13 else (10 if value > 10 else (-2 if value == -1 else value))

    @staticmethod
    def card_to_char(card):
        """
        Converts a given card into a character for use in recording the game history.
        The character is determined by adding the index of the card (via the get_card_index method) to 65,
        allowing for all 54 cards to be represented by the characters [A-v] (ascii values 65-118).
        If the card is hidden (hidden == True) then it is represented by the character '#'.
        Args:
            card (Deck.Card): The card whose character is to be calculated.
        Returns: A char that unqiuely represents 'card'.
        """
        index = Golf.get_card_index(card)
        if index is None:
            char = '#'
        else:
            #Converts the joker indexes to 52 and 53
            if index < 0:
                index = 54 + index
            char = chr(65 + index)
        return char

    def score_hand(self, hand):
        """
        Calculates the total score of a given hand.
        The scoring is iterated over each column of the hand where each card 
        is scored using the score_hand method and they are added to a running total.
        If the values of the cards match, however, then their scores are not added to the total.
        Args:
            hand ([Deck.Card]): The hand of the player, a numpy ndarray.
        Returns: An integer value representing the score of the hand.      
        """
        score = 0
        for i in range(3):
            card_1, card_2 = hand[i], hand[i+3]
            #Only add to score if values do not match
            if card_1.get_val() != card_2.get_val():
                score += self.card_score(card_1.get_val()) + self.card_score(card_2.get_val())
        return score

    def play(self, *players):
        """
        """

        GAME = ""

        for r in range(9):

            #Initialise game state 
            self.initialise()
            g = self.play_round(r, *players)
            GAME += g + '\n'

        return GAME

    def play_round(self, round_num, *players):
        """
        """
        GAME_HISTORY = ""

        PLAYERS = [player for player in players]    #len(PLAYERS) for number of players in game
        turn = round_num % len(PLAYERS)             #turn is the player indeex who starts

        GAME_HISTORY += str(len(PLAYERS)) + str(turn)

        #Create player hands
        for p in PLAYERS:
            p.hand = self.init_hand()

        #Pre-game initialisation
        for i in range(6):
            for p in PLAYERS:
                p.hand[i] = self.stock.draw(hidden=True)

        #Turn two cards face up in each players hand
        for p in PLAYERS:
            face_up = np.random.choice(p.hand, 2, False)
            face_up[0].hidden = False
            face_up[1].hidden = False

        #Will have access to the starting hands of the players here
        for p in PLAYERS:
            for card in p.hand:
                GAME_HISTORY += self.card_to_char(card)


        self.discard_pile.append(self.stock.draw())

        #Game starts here, '<'
        GAME_HISTORY += '<'

        #Player turns
        while not self.has_finished(PLAYERS[turn]):
            s = self.get_state(PLAYERS[turn], PLAYERS[:turn]+PLAYERS[turn+1:])
            draw_action = PLAYERS[turn].choose_draw(self.discard_pile[-1], s) #draw_action shows where drawn from

            if draw_action == Actions.DRAW_DECK:
                drawn_card = self.stock.draw()
                GAME_HISTORY += '+' + self.card_to_char(drawn_card)
            else:
                drawn_card = self.discard_pile.pop()
                GAME_HISTORY += '-' + self.card_to_char(drawn_card)             #convert drawn_card here

            discard_action = PLAYERS[turn].choose_discard(drawn_card, s)        #discard_action shows where discarding

            if discard_action == Actions.DISCARD:
                self.discard_pile.append(drawn_card)
                GAME_HISTORY += '6' + GAME_HISTORY[-1]
            else:
                disc_card, PLAYERS[turn].hand[discard_action.value] = PLAYERS[turn].hand[discard_action.value], drawn_card
                disc_card.hidden = False
                self.discard_pile.append(disc_card)
                GAME_HISTORY += str(discard_action.value) + self.card_to_char(disc_card)                         #convert discarded card here, might need refactoring to make it nicer

            turn = turn + 1 if turn + 1 < len(PLAYERS) else 0

            #Recycle stock if empty
            if self.stock.is_empty():
                for card in self.discard_pile[:-1]:
                    card.hidden = True
                self.stock = Deck(self.discard_pile[:-1], True)
                self.stock.shuffle()
                self.discard_pile = self.discard_pile[-1:]

        GAME_HISTORY += '>' + str(turn)
        #At this point the round has ended and thus all end game data can be calculated and added

        end_info = []
        for count, player in enumerate(PLAYERS):
            end_info.append([str(sum(card.hidden == True for card in player.hand))])
            self.reveal_hand(player)
            end_info[count].append("".join([self.card_to_char(card) for card in player.hand]))
            end_info[count].append("%02d" % self.score_hand(player.hand))

        end_info = list(map(list, zip(*end_info)))
        for entry in end_info:
            GAME_HISTORY += "".join(entry)


        return GAME_HISTORY #[self.score_hand(player.hand) for player in PLAYERS]


    def play_pair(self, player1, player2):
        """
        """
        PLAYERS = [player1, player2]
        num_players = 2 #len(PLAYERS)
        games = ["", ""]
        np.random.seed(None)
        seeds = np.random.randint(0, 2147483648, size=9)

        for r in range(9):

            np_seed = seeds[r] #int(time.time())

            set_deck = Deck(deck=[], jokers=True)
            for g in range(num_players):
                np.random.seed(np_seed)

                self.initialise(set_deck)

                result = self.play_round(r, *PLAYERS)
                games[g] += result + '\n'
                #scores = Golf_Analyser.extract_scores(game.rstrip())
                PLAYERS += [PLAYERS.pop(0)]

                #results[g] = [results[g][i-g] + scores[i-g] for i in range(num_players)]

        return games

class Golf_Analyser():
    """
    This is a class that can extract data from the encoded game history.
    """

    @staticmethod
    def extract_scores(game):
        """
        Given the history of a game in the stored format, extract the final scores for the players.
        That is, the total score across all nine rounds of the game.
        It does so by iteritively extracting the scores from each round in game.
        Args:
            game (String): A string containing the history of a game, which is nine rounds separated by '\n' characters.
        Returns: A list of the final (int) scores of each player.
        """
        #Extract the number of players in the game
        SCORES = [0]*int(game[0])
        rounds = game.split('\n')[:-1]
        for r in rounds:
            SCORES = list(map(add, SCORES, Golf_Analyser.extract_scores_round(r)))
        return SCORES


    @classmethod
    def extract_scores_round(cls, game_round):
        """
        Extracts the scores of each player from a single round 'game_round'
        Args:
            game_round (string): A string containing the history of a single round.
        Returns: A list containing the scores of each player for this round.
        """
        #Determine the number of players in the game, using that to determine the number of characters
        # at the end of the string that represent the scores.
        num_players = int(game_round[0])
        str_scores = game_round[-2*num_players:]

        #converts the characters into integer values
        int_scores = map(int, [str_scores[i:i+2] for i in range(0, len(str_scores), 2)])
        return list(int_scores)
