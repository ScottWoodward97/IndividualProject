"""
---golf.py---
Contains both the Golf class and Golf_Analyser class.
The Golf class provides all methods for playing the game of Golf with two players.
The Golf_analyser class contains all methods for extracting, analysing and plotting the data form the saved game files.
"""
from operator import add
import random
import time
import copy
import glob
import os
import itertools
import numpy as np
import matplotlib.pyplot as plt
from operator import add

from deck import Deck
from actions import Actions

class Golf():
    """
    Contains all methods and attributes to represent the card game Golf.
    Allows for two players to play a full game consiting of nine rounds in pairs. 
    Attributes:
        discard_pile (list): A list which contains cards in the discard pile.
        stock (Deck): The deck of cards used in the game
    """

    def __init__(self, stock=None):
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

        #Iterate through cards in opposing player hands
        for p in other_players:
            for card in p.hand:
                ind = self.get_card_index(card)
                if ind is None:
                    continue
                else:
                    state[ind] = -3

        #Iterate through cards in the players hand
        for i in range(6):
            ind = self.get_card_index(player.hand[i])
            if ind is None:
                continue
            else:
                state[ind] = i

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

    def play_round(self, round_num, *players):
        """
        Plays a single round of the card game Golf.
        Each player is given a hand of six cards, represented by a numpy array.
        Each turn, players choose where to draw from and what card they want to discard from their hand.
        The game ends once a player starts their turn with all cards face up.
        The aim of the players is to reduce the score of their hand.
        Throughout the game and afterwards, data is added to the cumulative game history 
            which is saved for later analysis but also used to detect loops in gameplay.
        Args:
            round_num (int): The current round number. Determines which player goes first.
            players ([Player]): The players in the game.
        Returns: A string containing the game history
        """
        GAME_HISTORY = ""

        PLAYERS = [player for player in players]    
        turn = round_num % len(PLAYERS) 

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

        #Add initial hands of the players to the game history
        for p in PLAYERS:
            for card in p.hand:
                GAME_HISTORY += self.card_to_char(card)


        self.discard_pile.append(self.stock.draw())

        GAME_HISTORY += '<'

        #Turns of the round
        while not self.has_finished(PLAYERS[turn]):
            s = self.get_state(PLAYERS[turn], PLAYERS[:turn]+PLAYERS[turn+1:])
            
            #The player decides where to draw from
            draw_action = PLAYERS[turn].choose_draw(self.discard_pile[-1], s)

            #Draw from the desired location and add to game history
            if draw_action == Actions.DRAW_DECK:
                drawn_card = self.stock.draw()
                GAME_HISTORY += '+' + self.card_to_char(drawn_card)
            else:
                drawn_card = self.discard_pile.pop()
                GAME_HISTORY += '-' + self.card_to_char(drawn_card)             
            
            #The player decides what card to discard
            discard_action = PLAYERS[turn].choose_discard(drawn_card, s) 

            if discard_action == Actions.DISCARD:
                #Discard the drawn card to the discard pile
                self.discard_pile.append(drawn_card)
                GAME_HISTORY += '6' + GAME_HISTORY[-1]
            else:
                #Exchange the drawn card with the card to discard and add it to the discard pile
                disc_card, PLAYERS[turn].hand[discard_action.value] = PLAYERS[turn].hand[discard_action.value], drawn_card
                disc_card.hidden = False
                self.discard_pile.append(disc_card)
                GAME_HISTORY += str(discard_action.value) + self.card_to_char(disc_card)

            turn = turn + 1 if turn + 1 < len(PLAYERS) else 0
            
            #Check for cycles in the game using String.count(substring, start, end)
            if GAME_HISTORY.count(GAME_HISTORY[-4:]) > 5:
                break

            #Recycle stock if empty
            if self.stock.is_empty():
                for card in self.discard_pile[:-1]:
                    card.hidden = True
                self.stock = Deck(self.discard_pile[:-1], True)
                self.stock.shuffle()
                self.discard_pile = self.discard_pile[-1:]

        GAME_HISTORY += '>' + str(turn)
        
        #Add end game information to the game history
        end_info = []
        for count, player in enumerate(PLAYERS):
            end_info.append([str(sum(card.hidden == True for card in player.hand))])
            ##Reveal the hand of each player
            self.reveal_hand(player)
            end_info[count].append("".join([self.card_to_char(card) for card in player.hand]))
            #Score each hand
            end_info[count].append("%02d" % self.score_hand(player.hand))

        end_info = list(map(list, zip(*end_info)))
        for entry in end_info:
            GAME_HISTORY += "".join(entry)

        #Return the game history
        return GAME_HISTORY


    def play_pair(self, player1, player2):
        """
        Plays a pair games of Golf where the second game is exactly the same as the first but with the player positions reversed.
        This aims to reduce the affect of randomness as both players can equally benefit from the luck of the game.
        Before the rounds are played, 9 seeds are generated which can control the randomness such that the two games can be identical.
        The rounds are played in parallel to allow for efficient use of memory when generating the decks for game play.
        Args:
            player1, player2 (Player): The two players in the game.
        Returns: The game histories of both games in a list
        """
        PLAYERS = [player1, player2]
        num_players = 2 
        games = ["", ""]
        np.random.seed(None)
        #Generates the random seeds
        seeds = np.random.randint(0, 2147483648, size=9)

        for r in range(9):
            np_seed = seeds[r]
            set_deck = Deck(deck=[], jokers=True)
            for g in range(num_players):
                #Initialise the round
                np.random.seed(np_seed)
                self.initialise(set_deck)
                #Play the round
                result = self.play_round(r, *PLAYERS)
                games[g] += result + '\n'
                
                #Reverse player positions
                PLAYERS += [PLAYERS.pop(0)]

        return games

class Golf_Analyser():
    """
    A class containing methods to extract, analyse and plot data from game files.
    """

    @staticmethod
    def extract_scores(game):
        """
        Extract the final scores obtained by both players in a game of Golf.
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

    @staticmethod
    def extract_hands(game):
        """
        Extract the final hands obtained by both players in a game of Golf.
        It does so by iteritively extracting the hands from each round in game.
        Args:
            game (String): A string containing the history of a game, which is nine rounds separated by '\n' characters.
        Returns: A list of the final (String) hands of each player.
        """
        hands = []
        rounds = game.split('\n')[:-1]
        for r in rounds:
            hands.append(Golf_Analyser.extract_hands_round(r))
        return hands

    @staticmethod
    def extract_number_of_turns(game):
        """
        Extract the number of turns taken in each round of a game of golf.
        Args:
            game (String): A string containing the history of a game, which is nine rounds separated by '\n' characters.
        Returns: A list of the total number of turns (int) for each round.
        """
        turns = []
        rounds = game.split('\n')[:-1]
        for r in rounds:
            turns.append(Golf_Analyser.extract_number_of_turns_round(r))
        return turns

    @staticmethod
    def extract_rounds_ended(game):
        """
        Extract the number of rounds obtained by both players, and those that were terminated, in a game of Golf.
        Args:
            game (String): A string containing the history of a game, which is nine rounds separated by '\n' characters.
        Returns: A list of the number of times each player ended a round and the number of times it was terminated.
        """
        total = []
        rounds = game.split('\n')[:-1]
        for r in rounds:
            total.append(Golf_Analyser.extract_round_ended(r))
        return [list(np.sum(total, axis=0))]
        

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

    @classmethod
    def extract_hands_round(cls, game_round):
        """
        Extracts the hands of each player from a single round 'game_round'
        Args:
            game_round (string): A string containing the history of a single round.
        Returns: A list containing the hands of each player for this round.
        """
        num_players = int(game_round[0])
        #Extract and reformat the final hands of the player from the game history
        concat_hands = game_round.split('>')[1][3:-2*num_players]
        hands = [concat_hands[i*6:(i+1)*6] for i in range(num_players)]
        return hands

    @classmethod
    def extract_number_of_turns_round(cls, game_round):
        """
        Extracts the number of turns in a round of golf.
        Args:
            game_round (string): A string containing the history of a single round.
        Returns: The number of turns taken.
        """
        turns = game_round.split('<')[1].split('>')[0]
        return len(turns)//4

    @classmethod
    def extract_round_ended(cls, game_round):
        """
        Extracts what player ended the current round or whether it was terminated.
        Args:
            game_round (string): A string containing the history of a single round.
        Returns: A list containing the what player ended the round or if it was terminated.
        """
        num_players = int(game_round[0])
        info = list(map(int, game_round.split('>')[1][0:(num_players + 1)]))
        tally = [0]*(num_players + 1)
        ind = info[0] if info[info[0]+1] == 0 else -1
        tally[ind] = 1
        return tally

    @staticmethod
    def extract_all_mean_scores(dir_path, games_per_epoch=10):
        """
        Extracts and calculates the mean scores from all game files in a directory.
        This method is used when games are played in pairs, and as such orders the extracted data chronologically.
        When extracting scores from the reversed positions, the scores are also reversed to allgins the scores of both players.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
        Returns: A nested list containing all of the mean scores of both players 
        """
        #Retreive the path of all game files in the directory
        files = glob.glob('%s/*.txt' % dir_path)
        data = []

        #Open the files in pairs which will allow for the games to be stored in chronological order of when they were played
        pair_files = np.reshape(files, (len(files)//2, 2))
        for pair in pair_files:
            scores_0, scores_1 = [],[]
            
            #Extract the scores from the first file
            with open(pair[0], 'r') as f0:
                games_0 = f0.read().split('\n\n')[:-1]
            for game in games_0:
                scores_0.append(Golf_Analyser.extract_scores(game + '\n'))
            
            #Extract and reverses the order of the scores from the second file
            with open(pair[1], 'r') as f1:
                games_1 = f1.read().split('\n\n')[:-1]
            for game in games_1:
                scores_1.append(Golf_Analyser.extract_scores(game + '\n')[::-1])

            #Collate the scores together such that they are in chronological order
            scores = [s for s in itertools.chain.from_iterable(zip(scores_0, scores_1))]
            #Average the scores over the number of games per epoch
            for i in range(len(scores)//games_per_epoch):
                data.append(np.mean(scores[i*games_per_epoch:(i+1)*games_per_epoch], axis=0))
        return data

    @staticmethod
    def extract_all_matches(dir_path, games_per_epoch=10):
        """
        Extracts and calculates the mean number of matches made from all game files in a directory.
        The number of matches are calculated by extracting the hands obtained in each round of the games.
        From the hands, the number of cards matching are counted by converting the character back to their value.
        This method is used when games are played in pairs, and as such orders the extracted data chronologically.
        When extracting the hands from the reversed positions, the hands are also reversed to allgins the hands of both players.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
        Returns: A nested list containing all of the mean number of matches of both players 
        """
        #Retreive the path of all game files in the directory
        files = glob.glob('%s/*.txt' % dir_path)
        data = []

        #Open the files in pairs which will allow for the games to be stored in chronological order of when they were played
        pair_files = np.reshape(files, (len(files)//2, 2))
        for pair in pair_files:
            hands_0, hands_1 = [],[]
            
            #Extract the hands from the first file
            with open(pair[0], 'r') as f0:
                games_0 = f0.read().split('\n\n')[:-1]
            for game in games_0:
                hands_0 += Golf_Analyser.extract_hands(game + '\n')
            
            #Extract and reverses the order of the hands from the second file
            with open(pair[1], 'r') as f1:
                games_1 = f1.read().split('\n\n')[:-1]
            for game in games_1:
                tmp_hands = Golf_Analyser.extract_hands(game + '\n')
                hands_1 += [h[::-1] for h in tmp_hands]

            #Collate the hands together such that they are in chronological order
            hands = [h for h in itertools.chain.from_iterable(zip(hands_0, hands_1))]
            matches = []
            #Counts the number of matches made by each hand in a round
            for hand_pair in hands:
                asc_vals_player = [ord(card) for card in hand_pair[0]]
                player_matches = sum((asc_vals_player[i] > 116 and asc_vals_player[i+3] > 116) 
                                    or (asc_vals_player[i] < 117 and asc_vals_player[i+3] < 117 and (asc_vals_player[i] - asc_vals_player[i+3])%13==0) for i in range(3))
                
                asc_vals_opponent = [ord(card) for card in hand_pair[1]]
                opponent_matches = sum((asc_vals_opponent[i] > 116 and asc_vals_opponent[i+3] > 116) 
                                    or (asc_vals_opponent[i] < 117 and asc_vals_opponent[i+3] < 117 and (asc_vals_opponent[i] - asc_vals_opponent[i+3])%13==0) for i in range(3))
                matches.append([player_matches, opponent_matches])
            
            #Average the number of matches made over the number of games per epoch
            for i in range(len(matches)//(9*games_per_epoch)):
                data.append(np.sum(matches[i*9*games_per_epoch:(i+1)*9*games_per_epoch], axis=0)/games_per_epoch)
        return data

    @staticmethod
    def extract_all_turn_nums(dir_path, games_per_epoch=10):
        """
        Extracts and calculates the duration of each round made from all game files in a directory.
        This method is used when games are played in pairs, and as such orders the extracted data chronologically.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
        Returns: A nested list containing the average number of turns made per round 
        """
        #Retreive the path of all game files in the directory
        files = glob.glob('%s/*.txt' % dir_path)
        data = []

        #Open the files in pairs which will allow for the games to be stored in chronological order of when they were played
        pair_files = np.reshape(files, (len(files)//2, 2))
        for pair in pair_files:
            turns_0, turns_1 = [],[]
            
            #Extract the number of turns from the first file
            with open(pair[0], 'r') as f0:
                games_0 = f0.read().split('\n\n')[:-1]
            for game in games_0:
                turns_0 += Golf_Analyser.extract_number_of_turns(game + '\n')
            
            #Extract the number of turns from the second file
            with open(pair[1], 'r') as f1:
                games_1 = f1.read().split('\n\n')[:-1]
            for game in games_1:
                turns_1 += Golf_Analyser.extract_number_of_turns(game + '\n')

            #Collate the number of turns together such that they are in chronological order
            turns = [t for t in itertools.chain.from_iterable(zip(turns_0, turns_1))]
            
            #Average the number of turns over the number of games per epoch
            for i in range(len(turns)//(9*games_per_epoch)):
                data.append(np.mean(turns[i*9*games_per_epoch:(i+1)*9*games_per_epoch], axis=0))
        return data

    @staticmethod
    def extract_all_rounds_ended(dir_path, games_per_epoch=10):
        """
        Extracts and calculates the number of rounds ended by each player from all game files in a directory.
        This method is used when games are played in pairs, and as such orders the extracted data chronologically.
        When extracting the number of round ended from the reversed positions, the scores are also reversed to allgins the number of rounds ended of both players.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to sum data.
        Returns: A nested list containing the number of rounds ended by each player 
        """
        #Retreive the path of all game files in the directory
        files = glob.glob('%s/*.txt' % dir_path)
        data = []

        #Open the files in pairs which will allow for the games to be stored in chronological order of when they were played
        pair_files = np.reshape(files, (len(files)//2, 2))
        for pair in pair_files:
            end_0, end_1 = [],[]
            
            #Extract the number of rounds ended from the first file
            with open(pair[0], 'r') as f0:
                games_0 = f0.read().split('\n\n')[:-1]
            for game in games_0:
                end_0 += Golf_Analyser.extract_rounds_ended(game + '\n')
            
            #Extract and reverses the order of the number of rounds ended from the second file
            with open(pair[1], 'r') as f1:
                games_1 = f1.read().split('\n\n')[:-1]
            for game in games_1:
                tmp_ends = Golf_Analyser.extract_rounds_ended(game + '\n')[0]
                end_1 += [tmp_ends[:-1][::-1] + tmp_ends[-1:]]

            #Collate the number of rounds ended together such that they are in chronological order
            ended = [e for e in itertools.chain.from_iterable(zip(end_0, end_1))]
            
            #Sums the number of rounds ended over the number of games per epoch
            for i in range(len(ended)//games_per_epoch):
                data.append(np.sum(ended[i*games_per_epoch:(i+1)*games_per_epoch], axis=0))
        
        return data

    @staticmethod
    def extract_all_card_frequency(dir_path, games_per_epoch=10):
        """
        Extracts and calculates the frequency of cards in the final hands of players from all game files in a directory.
        The frequency of cards are calculated by extracting the hands obtained in each round of the games.
        From the hands, the number of times cards appear are counted by converting the character back to their value.
        This method is used when games are played in pairs, and as such orders the extracted data chronologically.
        When extracting the hands from the reversed positions, the hands are also reversed to allgins the hands of both players.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
        Returns: A tuple of two lists containing the frequency of cards of each players 
        """
        #Retreive the path of all game files in the directory
        files = glob.glob('%s/*.txt' % dir_path)
        data_0, data_1 = [], []

        #Open the files in pairs which will allow for the games to be stored in chronological order of when they were played
        pair_files = np.reshape(files, (len(files)//2, 2))
        for pair in pair_files:
            hands_0, hands_1 = [],[]
            
            #Extract the hands from the first file
            with open(pair[0], 'r') as f0:
                games_0 = f0.read().split('\n\n')[:-1]
            for game in games_0:
                hands_0 += Golf_Analyser.extract_hands(game + '\n')
            
            #Extract and reverses the order of the hands from the second file
            with open(pair[1], 'r') as f1:
                games_1 = f1.read().split('\n\n')[:-1]
            for game in games_1:
                tmp_hands = Golf_Analyser.extract_hands(game + '\n')
                hands_1 += [h[::-1] for h in tmp_hands]

            #Collate the hands together such that they are in chronological order
            hands = [h for h in itertools.chain.from_iterable(zip(hands_0, hands_1))]

            hands = np.array(hands)
            #Lambda function to convert the character to its value
            val = lambda c: (ord(c)-65) - ((ord(c)-65)//13)*13 +1 if ord(c) -65 < 52 else -1

            #Sums the frequency of cards over the number of games per epoch
            for i in range(len(hands)//(9*games_per_epoch)):
                tally_0, tally_1 = [0]*14, [0]*14
                h_0, h_1 = hands[:,0], hands[:,1]
                #Sums the frequency for the first player
                for h in h_0[i*9*games_per_epoch:(i+1)*9*games_per_epoch]:
                    values = list(map(val, h))
                    for v in values:
                        if v >0:
                            tally_0[v-1] += 1
                        else:
                            tally_0[v] += 1
                data_0.append(tally_0)
                #Sums the frequency of the second player
                for h in h_1[i*9*games_per_epoch:(i+1)*9*games_per_epoch]:
                    values = list(map(val, h))
                    for v in values:
                        if v >0:
                            tally_1[v-1] += 1
                        else:
                            tally_1[v] += 1
                data_1.append(tally_1)

        return (data_0, data_1)

    @staticmethod
    def plot_data(data, num_columns, xlabel, ylabel, title, *data_labels):
        """
        Plots the given data as a line graph by using matplotlib.pyploy.
        Each item of data is given as a column in the input data and is plotted iteratively.
        Each data item is assigned a colour from a cyclic colour variable.
        Args:
            data (list/numpy.ndarray): A nested list or numpy.ndarray containing the data to be plotted.
            num_columns (int): The number of columns of data in the input data.
            xlabel, ylabel, title (String): The labels of the axes and the title of the graph
            data_labels ([String]): A list of labels assigned to each columns of data
        Returns: None
        """
        np_data = np.array(data)
        #Generate the x axis
        x_axis = np.linspace(1, len(data), len(data), dtype=int)

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        
        #Iteratively add each column of data to the graph
        colours = 'brgmck'
        for i in range(num_columns, 0, -1):
            plt.plot(x_axis, np_data[:, i-1], '%c-' % colours[(i-1)%len(colours)], label=data_labels[i-1])

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

    @staticmethod
    def plot_mean_scores(dir_path, games_per_epoch=10, xlabel="Epochs"):
        """
        Extracts and plots the mean scores obtained by both players from the game files in the given directory.
        The mean scores are plotted on a line graph.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
            xlabel (String): The label for the x axis of the resulting graph. By default set to 'Epochs'
        Returns: None
        """
        data = Golf_Analyser.extract_all_mean_scores(dir_path, games_per_epoch)
        Golf_Analyser.plot_data(data, 2, xlabel, "Mean Score", "Mean scores per game across " + xlabel, "Player", "Opponent")

    @staticmethod
    def plot_number_matching(dir_path, games_per_epoch=10, xlabel="Epochs"):
        """
        Extracts and plots the mean number of matches made by both players from the game files in the given directory.
        The mean number of matches are plotted on a line graph.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
            xlabel (String): The label for the x axis of the resulting graph. By default set to 'Epochs'
        Returns: None
        """
        data = Golf_Analyser.extract_all_matches(dir_path, games_per_epoch)
        Golf_Analyser.plot_data(data, 2, xlabel, "Number of Matches", "Number of Matches per game across " + xlabel, "Player", "Opponent")

    @staticmethod
    def plot_number_of_turns(dir_path, games_per_epoch=10, xlabel="Epochs"):
        """
        Extracts and plots the mean number of turns in a round from the game files in the given directory.
        The mean number of turns are plotted on a line graph.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
            xlabel (String): The label for the x axis of the resulting graph. By default set to 'Epochs'
        Returns: None
        """
        data = Golf_Analyser.extract_all_turn_nums(dir_path, games_per_epoch)
        Golf_Analyser.plot_data(np.reshape(data, (len(data), 1)), 1, xlabel, "Average Number of Turns", "Average Number of Turns per round per " + xlabel, "Total number of turns")

    @staticmethod
    def plot_rounds_ended(dir_path, games_per_epoch=10, xlabel="Epochs"):
        """
        Extracts and plots the number of rounds ended by both players and those that were terminated 
            from the game files in the given directory.
        The number of rounds ended are plotted on a stacked bar chart.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
            xlabel (String): The label for the x axis of the resulting graph. By default set to 'Epochs'
        Returns: None
        """
        data = Golf_Analyser.extract_all_rounds_ended(dir_path, games_per_epoch)
        Golf_Analyser.plot_data_stacked_bar(data, 3, xlabel, "Rounds Ended", "Number of rounds ended per "+ xlabel, ["Player", "Opponent", "Ended due to loop"], ["blue", "red", "green"])

    @staticmethod
    def plot_card_popularity(dir_path, games_per_epoch=10, xlabel="Epochs"):
        """
        Extracts and plots the frequency of cards of both players from the game files in the given directory.
        The card frequencies are plotted on a stacked bar chart, one for each player.
        Args:
            dir_path (String): The path of the directory containing the game files.
            games_per_epoch (int): The number of games played per epoch. This specifies the intervals at which to average data.
            xlabel (String): The label for the x axis of the resulting graph. By default set to 'Epochs'
        Returns: None
        """
        data_0, data_1 = Golf_Analyser.extract_all_card_frequency(dir_path, games_per_epoch)

        #The labels and colours of the data
        colours = ['red', 'blue', 'green', 'magenta', 'orange', 'cyan', 'purple', 'grey', 'lime', 'yellow', 'black', 'salmon', 'teal', 'navy']
        labels = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Joker']

        Golf_Analyser.plot_data_stacked_bar(data_0, 14, xlabel, "Number of times cards in hand", "Popularity of cards per " + xlabel + " for Player", labels, colours, 540)
        Golf_Analyser.plot_data_stacked_bar(data_1, 14, xlabel, "Number of times cards in hand", "Popularity of cards per " + xlabel + " for Opponent", labels, colours, 540)

    @staticmethod
    def plot_data_stacked_bar(data, num_bars, xlabel, ylabel, title, data_labels, colours, ylimit=None):
        """
        Plots the given data as a stacked bar graph by using matplotlib.pyploy.
        Each item of data is given as a column in the input data and is plotted iteratively.
        Args:
            data (list/numpy.ndarray): A nested list or numpy.ndarray containing the data to be plotted.
            num_bars (int): The number of columns of data in the input data/ bars on the graph.
            xlabel, ylabel, title (String): The labels of the axes and the title of the graph
            data_labels ([String]): A list of labels assigned to each columns of data.
            colours ([String]): A list of colours accepted by matplotlib.pyplot for each data item.
            ylimit (int/float): The maximum y value the graph can display. Optional and set to None by default
        Returns: None
        """
        np_data = np.array(data)
        #Generates the x axis
        x_axis = np.linspace(1, len(data), len(data), dtype=int)

        #Iteratively plots each bar of data
        for i in range(num_bars):
            plt.bar(x_axis, np_data[:,i], width=1.0, bottom=np.sum(np_data[:,:i], axis=1), color=colours[i], label=data_labels[i]) 
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        #Sets a y limit of the graph if one is specified
        if ylimit:
            plt.ylim(top=ylimit)
    
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()


            
