'''Test behavior of the Game while it is Waiting for Players'''
from unittest import TestCase
from uuid import UUID

from hundredandten.constants import Accessibility, GameStatus
from hundredandten.game import Game
from hundredandten.group import Person
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange


class TestWaitingForPlayersGame(TestCase):
    '''Unit tests for a Waiting for Players Game'''

    def test_generates_seed_when_none_passed(self):
        '''Game defaults a seed if none is passed'''
        game = Game()

        self.assertIsNotNone(game.seed)
        self.assertEqual(str(UUID(game.seed)), game.seed)

    def test_default_inits_to_waiting(self):
        '''Game status defaults to waiting for players'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        self.assertEqual(game.status, GameStatus.WAITING_FOR_PLAYERS)
        self.assertRaises(HundredAndTenError, lambda: game.active_round)

    def test_invite(self):
        '''Test inviting a player to a game'''
        invitee = 'invitee'
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        self.assertFalse(invitee in map(lambda i: i.identifier, game.invitees))

        game.invite(game.players[0].identifier, invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.invitees))

    def test_invite_as_non_player(self):
        '''Test inviting a player without being in the game yourself'''
        invitee = 'invitee'
        inviter = 'inviter'
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        self.assertRaises(HundredAndTenError, game.invite, inviter, invitee)

    def test_join(self):
        '''Test a player joining a game'''
        invitee = 'invitee'
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS, arrange.make_space)

        game.join(invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.players))

    def test_join_too_many_players(self):
        '''Test joining a full game'''
        invitee = 'invitee'
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_not_invited_to_private(self):
        '''Test joining a private game without an invite'''
        invitee = 'invitee'
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS, arrange.make_space)
        game.accessibility = Accessibility.PRIVATE

        self.assertRaises(HundredAndTenError, game.join, invitee)

    def test_join_invited_to_private(self):
        '''Test joining a public game without an invite'''
        invitee = 'invitee'
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS, arrange.make_space)
        game.accessibility = Accessibility.PRIVATE
        game.invite(game.organizer.identifier, invitee)

        game.join(invitee)

        self.assertTrue(invitee in map(lambda i: i.identifier, game.players))

    def test_leave(self):
        '''Test leaving a game as a non player'''
        no_one = 'no one'
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        game.leave(no_one)

        self.assertNotIn(Person(no_one), game.players)

    def test_leave_as_invited_player(self):
        '''Test leaving a game as an invited player'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        # want to ensure leaving doesn't rescind an invite so invate someone already in the game
        invited_player = game.players[-1].identifier
        game.invite(game.organizer.identifier, invited_player)

        self.assertIn(Person(invited_player), game.players)

        game.leave(invited_player)

        self.assertNotIn(Person(invited_player), game.players)
