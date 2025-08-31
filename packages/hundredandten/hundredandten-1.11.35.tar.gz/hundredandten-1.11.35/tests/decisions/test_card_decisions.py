'''Test to ensure card decisions are made consistently'''
from unittest import TestCase

from hundredandten.constants import (CardNumber, SelectableSuit,
                                     UnselectableSuit)
from hundredandten.decisions import best_card, worst_card, worst_card_beating
from hundredandten.deck import Card


class TestCardDecisions(TestCase):
    '''Unit tests for deciding on card value'''

    def test_finds_best_card(self):
        '''Finds the highest value trump as the best card'''
        suit = SelectableSuit.CLUBS
        card = Card(CardNumber.FIVE, suit)
        self.assertEqual(card, best_card([
            Card(CardNumber.FIVE, SelectableSuit.DIAMONDS),
            card,
            Card(CardNumber.ACE, suit)
        ], suit))

    def test_finds_best_card_as_joker(self):
        '''Finds the joker as the best card with no trumps'''
        suit = SelectableSuit.HEARTS
        card = Card(CardNumber.JOKER, UnselectableSuit.JOKER)
        self.assertEqual(card, best_card([
            Card(CardNumber.FIVE, SelectableSuit.DIAMONDS),
            card,
            Card(CardNumber.ACE, SelectableSuit.CLUBS)
        ], suit))

    def test_finds_worst_card_with_trumps(self):
        '''Finds the lowest value non trump as the worst card'''
        card = Card(CardNumber.TWO, SelectableSuit.DIAMONDS)
        self.assertEqual(card, worst_card([
            Card(CardNumber.FIVE, SelectableSuit.SPADES),
            card,
            Card(CardNumber.ACE, SelectableSuit.CLUBS)
        ], SelectableSuit.CLUBS))

    def test_finds_worst_card_with_only_trumps(self):
        '''Finds the lowest value trump as the worst card'''
        suit = SelectableSuit.DIAMONDS
        card = Card(CardNumber.TWO, suit)
        self.assertEqual(card, worst_card([
            Card(CardNumber.FIVE, suit),
            card,
            Card(CardNumber.ACE, suit)
        ], SelectableSuit.DIAMONDS))

    def test_finds_worst_card_beating(self):
        '''Finds the lowest value card that beats the provided card with all trump'''
        suit = SelectableSuit.DIAMONDS
        card_to_beat = Card(CardNumber.TWO, suit)
        card = Card(CardNumber.ACE, suit)
        self.assertEqual(card, worst_card_beating(
            [
                Card(CardNumber.FIVE, suit),
                Card(CardNumber.JACK, suit),
                card
            ],
            card_to_beat,
            suit
        ))

    def test_finds_worst_card_beating_non_trump(self):
        '''Finds the lowest value card that beats the provided card with all trump'''
        trump = SelectableSuit.DIAMONDS
        card_to_beat = Card(CardNumber.THREE, SelectableSuit.SPADES)
        card = Card(CardNumber.TWO, SelectableSuit.SPADES)
        self.assertEqual(card, worst_card_beating(
            [
                Card(CardNumber.FIVE, trump),
                Card(CardNumber.JACK, trump),
                card
            ],
            card_to_beat,
            trump
        ))
