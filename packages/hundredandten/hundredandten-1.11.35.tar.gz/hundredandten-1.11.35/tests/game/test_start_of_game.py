'''Test behavior of the Game while it is starting or newly starting'''
from unittest import TestCase

from hundredandten.constants import HAND_SIZE, GameStatus, RoundStatus
from hundredandten.group import Group
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange


class TestStartOfGame(TestCase):
    '''Unit tests for starting a Game'''

    def test_start_game(self):
        '''Adds the first round when starting a game'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        self.assertEqual(0, len(game.rounds))

        game.start_game()

        self.assertEqual(1, len(game.rounds))
        self.assertIsNotNone(game.active_round.deck.seed)
        self.assertIsNotNone(game.active_round)
        self.assertEqual(len(game.players), len(game.active_round.bidders))
        self.assertIsNotNone(game.active_round.dealer)
        self.assertIsNotNone(game.active_round.active_player)
        self.assertNotEqual(game.active_round.dealer, game.active_round.active_player)
        self.assertIsNone(game.active_round.active_bidder)
        self.assertTrue(all(len(p.hand) == HAND_SIZE for p in game.active_round.players))

    def test_games_dont_have_same_seed(self):
        '''Two different games' decks will have different seeds'''
        game_1 = arrange.game(RoundStatus.BIDDING)
        game_2 = arrange.game(RoundStatus.BIDDING)

        self.assertIsNotNone(game_1.active_round.deck.seed)
        self.assertIsNotNone(game_2.active_round.deck.seed)
        self.assertNotEqual(game_2.active_round.deck.seed, game_1.active_round.deck.seed)

    def test_start_game_with_unjoined_players(self):
        '''Does not add unjoined invitees as players'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)
        game.invite(game.organizer.identifier, '5th player')

        self.assertEqual(0, len(game.rounds))

        game.start_game()

        self.assertGreater(len(game.people), len(game.active_round.bidders))
        self.assertEqual(len(game.players), len(game.active_round.bidders))

    def test_start_game_when_started(self):
        '''Will not allow restarting a game'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        game.start_game()
        self.assertRaises(HundredAndTenError, game.start_game)

    def test_start_game_with_no_players(self):
        '''Will not allow starting a game with no players'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)
        game.people = Group()

        self.assertRaises(HundredAndTenError, game.start_game)

    def test_invite_after_start(self):
        '''Cannot invite a player after the game has started'''
        invitee = 'invitee'
        inviter = 'inviter'
        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(HundredAndTenError, game.invite, inviter, invitee)

    def test_join_after_start(self):
        '''Cannot join a game after it has started'''
        invitee = 'invitee'
        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_leave_after_start(self):
        '''Test leaving a game after it has started'''
        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(HundredAndTenError, game.leave, game.players[-1].identifier)
