import random

class Deck():

    class Card():
        def __init__(self, value, suit, hidden=True):
            self.value = value
            self.suit = suit
            self.hidden = hidden

        def get_val_suit(self):
            if self.hidden:
                return (0,0)
            else:
                return (self.value, self.suit)
        
        def get_val(self):
            return 0 if self.hidden else self.value


    def __init__(self, deck=[], jokers=False):
        self.deck = deck
        self.jokers = jokers
        if not deck:
            self.init_deck()

    def init_deck(self):
        for v in range(1, 14):
            for s in range(1,5):
                self.deck.append(Deck.Card(v,s))
        if self.jokers:
            #Distinguish between two jokers
            self.deck.append(Deck.Card(-1,-1))
            self.deck.append(Deck.Card(-1,-2))

        self.shuffle()

    def draw(self, hidden=False):
        try:
            card = self.deck.pop()
            card.hidden = hidden
            return card      
        except:
            raise IndexError("The deck is empty.\n")

    def shuffle(self):
        random.shuffle(self.deck)

    def is_empty(self):
        return self.deck == []