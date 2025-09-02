CARD_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
CARD_SUITS = ["clubs", "diamonds", "hearts", "spades"]
CARD_SUITS_SHORTENED = ["c", "d", "h", "s"]
CARD_SUITS_MAPPING = dict(zip(CARD_SUITS_SHORTENED, CARD_SUITS))

class Card:
    def __init__(self, rank, suit):
        suit = suit.lower()
        rank = rank.lower()
        if rank not in CARD_RANKS:
            raise ValueError("Invalid rank. Expected a string of values 2, 3, 4, 5, 6, 7, 8, 9, 10, jack, queen, king, ace.")
        if suit not in CARD_SUITS and suit not in CARD_SUITS_SHORTENED:
            raise ValueError("Invalid suit. Expected a string of values clubs, diamonds, hearts, spades or c, d, h, s for short.")
        
        self.rank = rank
        self.suit = suit[0]

    def get_rank(self):
        '''Get a card's rank'''
        return self.rank
    
    def get_suit(self):
        '''Get a card's suit'''
        return CARD_SUITS_MAPPING.get(self.suit)
    
    def __str__(self):
        return "% s of % s" % (self.rank, self.get_suit())
    
    def __repr__(self):
        return "% s of % s" % (self.rank, self.get_suit())