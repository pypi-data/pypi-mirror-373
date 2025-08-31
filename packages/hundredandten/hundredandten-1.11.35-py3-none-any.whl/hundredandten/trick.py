'''Track a trick'''
from dataclasses import dataclass, field
from typing import Callable, Optional

from hundredandten.actions import Play
from hundredandten.constants import CardSuit, SelectableSuit
from hundredandten.deck import Card


@dataclass
class Score:
    '''A class to keep track of a player's score in either a trick or a game'''
    identifier: str
    value: int


@dataclass
class Trick:
    '''A class to keep track of one trick'''
    round_trump: SelectableSuit
    plays: list[Play] = field(default_factory=list)

    @property
    def winning_play(self) -> Optional[Play]:
        '''Determine the winner of the trick considering the passed suit as trump'''

        strong_trump_winner = self.__winning_play(
            lambda play: play.card.suit == self.round_trump or play.card.always_trump,
            lambda play: play.card.trump_value
        )

        weak_trump_winner = self.__winning_play(
            lambda play: play.card.suit == self.weak_trump,
            lambda play: play.card.weak_trump_value
        )

        return strong_trump_winner or weak_trump_winner

    @property
    def bleeding(self) -> bool:
        '''True if the trick should force players to play a trump card (if they have one)'''
        return (bool(self.leading_card) and
                (self.leading_card.suit == self.round_trump or self.leading_card.always_trump))

    @property
    def leading_card(self) -> Optional[Card]:
        '''The leading card of this trick'''
        if not self.plays:
            return None
        return self.plays[0].card

    @property
    def weak_trump(self) -> Optional[CardSuit]:
        '''The leading card of this trick'''
        if self.leading_card and self.leading_card.suit != self.round_trump:
            return self.leading_card.suit
        return None

    def __winning_play(
            self,
            filter_fn: Callable[[Play], bool],
            key_fn: Callable[[Play], int]) -> Optional[Play]:
        return max(list(filter(filter_fn, self.plays)), key=key_fn, default=None)
