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
        Initialises/Resets the  deck and discard pile.
        """
        self.discard_pile = []
        if stock is None:
            self.stock = Deck(deck=[], jokers=True)
        else:
            self.stock = copy.deepcopy(stock)

    def init_hand(self):
        """
        """
        return np.empty((6,), dtype=Deck.Card)

    def get_state(self, player, other_players):
        """
        """
        #-3 IOH, -2 IDP, -1 UNK, 0-5 POSITION IN HAND
        state = [-1]*54 #[Locations.UNKNOWN]*54
        for card in self.discard_pile:
            ind = self.get_card_index(card)
            if ind is not None:
                state[ind] = -2
            #v,s = card.get_val_suit()
            #if v == -1:
            #    state[s] = -2 #Locations.IN_DISC_PILE
            #else:
            #    state[ (s-1)*13 + v-1 ] = -2 #Locations.IN_DISC_PILE

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
        """
        return all([card.hidden == False for card in player.hand])

    def reveal_hand(self, player):
        """
        """
        for card in player.hand:
            card.hidden = False

    @staticmethod
    def get_card_index(card):
        """
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
        """
        return 0 if value == 13 else (10 if value > 10 else (-2 if value == -1 else value))

    @staticmethod
    def card_to_char(card):
        """
        """
        index = Golf.get_card_index(card)
        if index is None:
            char = '#'
        else:
            if index < 0:
                index = 54 + index
            char = chr(65 + index)
        return char

    def score_hand(self, hand):
        """
        """
        score = 0
        for i in range(3):
            card_1, card_2 = hand[i], hand[i+3]
            if card_1.get_val() != card_2.get_val():
                score += self.card_score(card_1.get_val()) + self.card_score(card_2.get_val())
        return score

    def play(self, *players):
        """
        """
        #Extract players
        #PLAYERS = [player for player in players]
        #SCORES = [0]*len(players)

        GAME = ""

        for r in range(9):

            #Initialise game state  WONT WORK FOR PLAY SET
            self.initialise()
            #THIS METHOD NEEDS TO CHANGE
            g = self.play_round(r, *players)
            GAME += g + '\n'
            #SCORES = [SCORES[i]+s[i] for i in range(len(players))]

            ##End game
        return GAME #SCORES

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

        for r in range(9):
            np_seed = int(time.time())
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
