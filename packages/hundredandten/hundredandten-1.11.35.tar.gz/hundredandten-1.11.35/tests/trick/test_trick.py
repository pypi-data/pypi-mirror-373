'''Test behavior of a trick'''
from unittest import TestCase

from hundredandten.actions import Play
from hundredandten.constants import CardNumber, SelectableSuit
from hundredandten.deck import Card
from hundredandten.trick import Trick


class TestTrick(TestCase):
    '''Unit tests for a trick'''

    def test_no_winning_play(self):
        '''With no plays, there is no winning play'''

        trick = Trick(SelectableSuit.HEARTS)

        self.assertIsNone(trick.winning_play)

    def test_no_weak_trump(self):
        '''With no plays, there is no weak trump'''

        trick = Trick(SelectableSuit.CLUBS)

        self.assertIsNone(trick.weak_trump)

    def test_winning_play_with_one_play(self):
        '''With only one play, that is always the winning play'''

        play = Play('', Card(CardNumber.TWO, SelectableSuit.HEARTS))

        for suit in SelectableSuit:
            self.assertEqual(play, Trick(suit, plays=[play]).winning_play)

    def test_winning_play_with_strong_trump(self):
        '''When a strong trump is played, it will beat non-trumps'''

        plays = [Play('', Card(CardNumber.TWO, SelectableSuit.HEARTS)),
                 Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS)),
                 Play('', Card(CardNumber.TWO, SelectableSuit.CLUBS)),
                 Play('', Card(CardNumber.TWO, SelectableSuit.SPADES))]

        for play in plays:
            assert isinstance(play.card.suit, SelectableSuit)
            self.assertEqual(play, Trick(play.card.suit, plays).winning_play)

    def test_winning_play_with_weak_trump(self):
        '''When no strong trump is played, the weak trump will win'''

        trick = Trick(
            SelectableSuit.CLUBS,
            plays=[Play('', Card(CardNumber.TWO, SelectableSuit.HEARTS)),
                   Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS)),
                   Play('', Card(CardNumber.THREE, SelectableSuit.DIAMONDS)),
                   Play('', Card(CardNumber.FOUR, SelectableSuit.DIAMONDS))])

        self.assertEqual(trick.plays[0], trick.winning_play)

    def test_winning_play_with_all_trump(self):
        '''When all strong trumps are played, the highest trump value wins'''

        winning_play = Play('', Card(CardNumber.FIVE, SelectableSuit.DIAMONDS))
        trick = Trick(
            SelectableSuit.DIAMONDS,
            plays=[Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS)),
                   Play('', Card(CardNumber.TWO, SelectableSuit.DIAMONDS)),
                   winning_play,
                   Play('', Card(CardNumber.FOUR, SelectableSuit.DIAMONDS))])

        self.assertEqual(winning_play, trick.winning_play)
