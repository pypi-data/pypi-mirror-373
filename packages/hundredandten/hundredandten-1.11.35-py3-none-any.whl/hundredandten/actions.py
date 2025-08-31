'''All the actions a player can take to interact with the game'''
from dataclasses import dataclass, field

from hundredandten.constants import BidAmount, SelectableSuit
from hundredandten.deck import Card
from hundredandten.events import Event


@dataclass
class Action(Event):
    '''A superclass for actions in the game'''
    identifier: str


@dataclass
class Unpass(Action):
    '''A class to represent the unpass action'''


@dataclass(order=True)
class Bid(Action):
    '''A class to keep track of bid information'''
    identifier: str = field(compare=False)
    amount: BidAmount

    def __bool__(self) -> bool:
        return self.amount.value > 0


@dataclass
class SelectTrump(Action):
    '''A class to represent the select trump action'''
    suit: SelectableSuit


@dataclass
class Discard(Action):
    '''A class to keep track of one player's discard action'''
    cards: list[Card]


@dataclass
class DetailedDiscard(Discard):
    '''A class to keep track of all details of one player's discard action'''
    kept: list[Card]


@dataclass
class Play(Action):
    '''A class to keep track of one play in a trick'''
    card: Card
