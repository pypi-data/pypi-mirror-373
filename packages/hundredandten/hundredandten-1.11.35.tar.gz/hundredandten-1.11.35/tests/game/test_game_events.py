'''Test to ensure game events are returned properly'''
from unittest import TestCase

from hundredandten.constants import GameStatus, RoundStatus
from hundredandten.events import (GameEnd, GameStart, RoundEnd, RoundStart,
                                  TrickEnd)
from tests import arrange

# tests in this file run off of seeded games to avoid setting up everything necessary for the tests
# seeds and their expected values in different situations are recorded here

PLAYER_3_WIN_SEED = 'ba297348-77d7-42bb-9164-03712b05ba21'


class TestGameEvents(TestCase):
    '''Unit tests for returning events in a game'''

    def test_start_with_no_events(self):
        '''At game start, event list is empty'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        self.assertEqual([], game.events)

    def test_new_game(self):
        '''Before any plays, just the game start event exists'''
        game = arrange.game(RoundStatus.BIDDING)
        events = game.events

        self.assertEqual(2, len(events))
        self.assertIsInstance(events[0], GameStart)
        self.assertIsInstance(events[1], RoundStart)

    def test_partial_trick(self):
        '''While round isn't over, no RoundEnd event exists'''

        game = arrange.game(RoundStatus.TRICKS)
        init_events = game.events

        self.assertGreater(len(init_events), 0)
        self.assertFalse(any(isinstance(e, TrickEnd) for e in init_events))
        arrange.play_trick(game)
        self.assertTrue(any(isinstance(e, TrickEnd) for e in game.events))

    def test_partial_round(self):
        '''While round isn't over, no RoundEnd event exists'''

        for status in [RoundStatus.BIDDING,
                       RoundStatus.TRUMP_SELECTION,
                       RoundStatus.TRICKS,
                       RoundStatus.TRUMP_SELECTION]:
            game = arrange.game(status)
            events = game.events

            self.assertGreater(len(events), 0)
            self.assertFalse(any(isinstance(e, RoundEnd) for e in events))

    def test_completed_round(self):
        '''Once the round is over, it will have a RoundEnd event'''

        game = arrange.game(RoundStatus.TRICKS, arrange.play_round)
        events = game.events

        self.assertGreater(len(events), 0)
        self.assertTrue(any(isinstance(e, RoundEnd) for e in events))

    def test_completed_game(self):
        '''Once the game is over, it will have a GameEnd event'''

        game = arrange.game(GameStatus.WON, seed=PLAYER_3_WIN_SEED)
        events = game.events

        self.assertEqual(len(events), 330)  # known from seed
        self.assertTrue(isinstance(events[-1], GameEnd))
