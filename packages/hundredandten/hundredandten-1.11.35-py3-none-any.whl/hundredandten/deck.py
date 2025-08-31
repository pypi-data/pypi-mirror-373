'''Handle the functions of a deck'''
from dataclasses import dataclass, field
from random import Random
from uuid import uuid4

from hundredandten.constants import (CardNumber, CardSuit, SelectableSuit,
                                     UnselectableSuit)
from hundredandten.hundred_and_ten_error import HundredAndTenError


@dataclass
class CardInfo:
    '''Game metadata about a card'''
    # value when this suit is trumps
    trump_value: int
    # value when this suit is "trumps" for a trick when no trumps are played
    weak_trump_value: int
    # true if the card is _always_ trumps
    always_trump: bool = False


card_info = {
    SelectableSuit.HEARTS: {
        CardNumber.TWO: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.THREE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.FOUR: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=3),
        CardNumber.SIX: CardInfo(trump_value=3, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=4, weak_trump_value=5),
        CardNumber.EIGHT: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.NINE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.TEN: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=11, weak_trump_value=12, always_trump=True)
    },
    SelectableSuit.DIAMONDS: {
        CardNumber.TWO: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.THREE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.FOUR: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=3),
        CardNumber.SIX: CardInfo(trump_value=3, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=4, weak_trump_value=5),
        CardNumber.EIGHT: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.NINE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.TEN: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12)
    },
    SelectableSuit.SPADES: {
        CardNumber.TWO: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.THREE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.FOUR: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=5),
        CardNumber.SIX: CardInfo(trump_value=4, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=3, weak_trump_value=3),
        CardNumber.EIGHT: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.NINE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.TEN: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12)
    },
    SelectableSuit.CLUBS: {
        CardNumber.TWO: CardInfo(trump_value=7, weak_trump_value=8),
        CardNumber.THREE: CardInfo(trump_value=6, weak_trump_value=7),
        CardNumber.FOUR: CardInfo(trump_value=5, weak_trump_value=6),
        CardNumber.FIVE: CardInfo(trump_value=14, weak_trump_value=5),
        CardNumber.SIX: CardInfo(trump_value=4, weak_trump_value=4),
        CardNumber.SEVEN: CardInfo(trump_value=3, weak_trump_value=3),
        CardNumber.EIGHT: CardInfo(trump_value=2, weak_trump_value=2),
        CardNumber.NINE: CardInfo(trump_value=1, weak_trump_value=1),
        CardNumber.TEN: CardInfo(trump_value=0, weak_trump_value=0),
        CardNumber.JACK: CardInfo(trump_value=13, weak_trump_value=9),
        CardNumber.QUEEN: CardInfo(trump_value=8, weak_trump_value=10),
        CardNumber.KING: CardInfo(trump_value=9, weak_trump_value=11),
        CardNumber.ACE: CardInfo(trump_value=10, weak_trump_value=12)
    },
    UnselectableSuit.JOKER: {
        CardNumber.JOKER: CardInfo(trump_value=12, weak_trump_value=12, always_trump=True)
    }
}


@dataclass
class Card:
    '''A playing card'''
    number: CardNumber
    suit: CardSuit

    def __repr__(self):
        return f'{self.number.name} of {self.suit.name}'

    @property
    def trump_value(self):
        '''The value of this card as a trump'''
        return card_info[self.suit][self.number].trump_value

    @property
    def weak_trump_value(self):
        '''The value of this card in a suit with no trumps where its suit leads'''
        return card_info[self.suit][self.number].weak_trump_value

    @property
    def always_trump(self):
        '''Whether the card is always considered trump'''
        return card_info[self.suit][self.number].always_trump


defined_cards = [Card(number, suit) for (suit, number_dict) in card_info.items()
                 for number in number_dict]


@dataclass
class Deck:
    '''A seeded deck of cards'''
    seed: str = field(default_factory=lambda: str(uuid4()))
    pulled: int = 0
    cards: list[int] = field(init=False)

    def __post_init__(self):
        self.cards = [*range(len(defined_cards))]
        Random(self.seed).shuffle(self.cards)

    def draw(self, amount: int) -> list[Card]:
        '''Draw the specified amount of cards from the deck'''
        start = self.pulled
        end = self.pulled + amount
        if amount < 0:
            raise HundredAndTenError("Cannot draw previously drawn cards.")
        if end > len(self.cards):
            raise HundredAndTenError("Deck is overdrawn.")

        self.pulled = end
        return list(map(lambda num: defined_cards[num], self.cards[start:end]))
