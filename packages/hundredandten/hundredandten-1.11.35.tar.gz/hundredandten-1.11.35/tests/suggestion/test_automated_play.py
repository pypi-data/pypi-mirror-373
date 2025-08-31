'''Test to ensure automated games will play completely'''
from unittest import TestCase
from uuid import uuid4

from hundredandten.constants import GameStatus, RoundStatus
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange

AUTOMATED_SEED = 'a92475b9-3df3-458d-b0df-486f9a305015'


class TestAutomatedPlay(TestCase):
    '''Unit tests for playing a game with all machine players'''

    def test_game_will_complete_from_start(self):
        '''When playing with all automated players, the game will complete'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS, seed=AUTOMATED_SEED)
        for player in game.players:
            game.automate(player.identifier)

        game.start_game()

        self.assertIsNotNone(game.winner)

    def test_game_will_complete_after_start(self):
        '''When playing with all automated players after starting, the game will complete'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS, seed=AUTOMATED_SEED)

        game.start_game()

        for player in game.players:
            game.automate(player.identifier)

        self.assertIsNotNone(game.winner)

    def test_no_suggestions_after_completion(self):
        '''When playing with all automated players, the game will complete'''
        game = arrange.game(GameStatus.WON, seed=AUTOMATED_SEED)

        self.assertRaises(HundredAndTenError, game.suggestion)

    def test_wont_automate_unknown_player(self):
        '''Trying to automate an unknown player will do nothing'''
        game = arrange.game(RoundStatus.BIDDING)

        unknown_id = str(uuid4())

        game.automate(unknown_id)

        self.assertFalse(any(person.identifier == unknown_id for person in game.people))
        self.assertFalse(any(person.automate for person in game.people))
