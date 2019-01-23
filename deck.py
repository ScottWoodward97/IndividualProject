"""The random module is used for shuffling the order of cards in the deck"""
import random

class Deck():
    """
    Contains all methods and attributes to represent a deck of playing cards.
    Attributes:
        deck ([Card]): A list of Card objects representing the cards remaining in the deck
        jokers (boolean): Represents whether the deck contains jokers (True) or not (False)
    """

    class Card():
        """
        Contains all methods and attributes to represent a playing card.
        Attributes:
            value (int): A value between [1-13] to represent Ace-King (or -1 if joker)
            suit (int): A value between [1-4] to represent the suits ([-2,-1] if joker)
            hidden (boolean): Represents whether the card is hidden (True) or not (False)
        """
        def __init__(self, value, suit, hidden=True):
            self.value = value
            self.suit = suit
            self.hidden = hidden

        def get_val_suit(self):
            """
            Returns the value and suit of the card if the card is not hidden,
            the method will return 0 for both if it is hidden.

            Returns: A tuple containing the value and suit (integers)
            """
            if self.hidden:
                return (0, 0)
            else:
                return (self.value, self.suit)

        def get_val(self):
            """
            Returns the value of the card, or 0 if it is hidden.

            Returns: An integer representing the value of the card
            """
            return 0 if self.hidden else self.value


    def __init__(self, deck=[], jokers=False):
        self.deck = deck
        self.jokers = jokers
        if not deck:
            self.init_deck()

    def init_deck(self):
        """
        Initializes the deck attribute with the required Card objects
        from suits 1-4 and values 1-13 and jokers (if requested).
        Returns: None
        """
        for val in range(1, 14):
            for suit in range(1, 5):
                self.deck.append(Deck.Card(val, suit))
        if self.jokers:
            #Jokers have the value -1 and suits -1 and -2 (to distinguish between the two)
            self.deck.append(Deck.Card(-1, -1))
            self.deck.append(Deck.Card(-1, -2))

        #The deck is then shuffled into a random order
        self.shuffle()

    def draw(self, hidden=False):
        """
        Removes the 'top' card of the deck and returns it.
        Whether the card is drawn hidden is determined by the hidden variable.
        Args:
            hidden: A boolean variable representing whether the drawn card remains hidden.
            False by default.
        Returns: The drawn card as a Card object.
        Throws: IndexError if the method is called on an empty deck.
        """
        try:
            card = self.deck.pop()
            card.hidden = hidden
            return card
        except:
            raise IndexError("The deck is empty.\n")

    def shuffle(self):
        """
        Shuffles the deck in place using the random.shuffle method.
        Returns: None
        """
        random.shuffle(self.deck)

    def is_empty(self):
        """
        Determines whether the deck is empty (has no cards).
        Returns: A boolean variable which is True if the deck is empty, false if not.
        """
        return self.deck == []
