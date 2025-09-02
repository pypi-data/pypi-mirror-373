import random
from typing import List
from standard_playing_card import Card, CARD_RANKS, CARD_SUITS

class CardShoe:
    def __init__(self, num_of_decks: int = 1) -> None:
        '''Deck constructor'''
        self.deck = [Card(a, b) for a in CARD_RANKS for b in CARD_SUITS] * num_of_decks
        self.shuffle()

    def shuffle(self) -> None:
        '''Shuffle the deck'''
        random.shuffle(self.deck)

    def draw_card(self) -> Card:
        '''Draw a card'''
        return self.deck.pop(0)
    
    def return_cards(self, pile: List[Card]) -> None:
        '''Return a pile of discards to the deck and shuffle'''
        self.deck.extend(pile)
        self.shuffle()