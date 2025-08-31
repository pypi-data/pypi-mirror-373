'''Test behavior of the Game when playing a card'''
from unittest import TestCase

from hundredandten.actions import Play
from hundredandten.constants import (HAND_SIZE, CardNumber, RoundStatus,
                                     SelectableSuit)
from hundredandten.deck import Card
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange


class TestPlayCard(TestCase):
    '''Unit tests for playing a card in a trick'''

    def test_non_trick_game(self):
        '''A game not ready for tricks has no active trick'''

        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(HundredAndTenError, lambda: game.active_round.active_trick)

    def test_play_first_card_of_round(self):
        '''The player after the bidder plays the first card of the round'''

        game = arrange.game(RoundStatus.TRICKS)

        assert game.active_round.active_bidder
        self.assertEqual(game.active_round.active_player, game.active_round.players.after(
            game.active_round.active_bidder.identifier))

        original_active_player = game.active_round.active_player
        play = Play(original_active_player.identifier, original_active_player.hand[0])

        game.act(play)

        self.assertEqual(HAND_SIZE - 1, len(original_active_player.hand))
        self.assertNotIn(play.card, original_active_player.hand)
        self.assertNotEqual(original_active_player, game.active_round.active_player)

    def test_cannot_play_twice_in_a_trick(self):
        '''Each person can only play once per trick'''

        game = arrange.game(RoundStatus.TRICKS)

        active_player = game.active_round.active_player
        play = Play(active_player.identifier, active_player.hand[0])

        game.act(play)
        self.assertRaises(HundredAndTenError, game.act, play)

    def test_cannot_play_other_players_card(self):
        '''A player can only play their own cards'''

        game = arrange.game(RoundStatus.TRICKS)

        self.assertRaises(HundredAndTenError, game.act, Play(
            game.active_round.active_player.identifier,
            game.active_round.inactive_players[0].hand[0]))

    def test_cannot_play_non_trump_when_bleeding(self):
        '''A player can only play trumps while the trick is bleeding'''

        game = arrange.game(RoundStatus.TRICKS)
        assert game.active_round.trump

        non_trump = next(iter(SelectableSuit))

        active_player = game.active_round.active_player
        next_player = game.active_round.players.after(active_player.identifier)

        # overwrite to ensure this trick will bleed
        active_player.hand[0] = Card(CardNumber.TEN, game.active_round.trump)
        # overwrite to ensure next player breaks rules
        next_player.hand = [Card(CardNumber.TWO, non_trump)
                            ]*4 + [Card(CardNumber.NINE, game.active_round.trump)]

        self.assertFalse(game.active_round.active_trick.bleeding)

        game.act(Play(active_player.identifier, active_player.hand[0]))

        self.assertTrue(game.active_round.active_trick.bleeding)

        self.assertRaises(HundredAndTenError, game.act, Play(
            game.active_round.active_player.identifier,
            game.active_round.active_player.hand[0]))

    def test_can_play_non_trump_when_bleeding(self):
        '''A player can play non-trumps while the trick is bleeding if they have no trumps'''

        game = arrange.game(RoundStatus.TRICKS)
        assert game.active_round.trump

        non_trump = next(iter(SelectableSuit))

        active_player = game.active_round.active_player
        next_player = game.active_round.players.after(active_player.identifier)

        # overwrite to ensure this trick will bleed
        active_player.hand[0] = Card(CardNumber.TEN, game.active_round.trump)
        # overwrite to ensure next player breaks rules
        next_player.hand = [Card(CardNumber.TWO, non_trump)]*5

        self.assertFalse(game.active_round.active_trick.bleeding)

        game.act(Play(active_player.identifier, active_player.hand[0]))

        self.assertTrue(game.active_round.active_trick.bleeding)

        game.act(Play(game.active_round.active_player.identifier,
                      game.active_round.active_player.hand[0]))

        self.assertTrue(game.active_round.active_trick.bleeding)
        self.assertEqual(2, len(game.active_round.active_trick.plays))

    def test_play_through_trick(self):
        '''A new trick is created after all players have played'''

        game = arrange.game(RoundStatus.TRICKS, arrange.play_trick)

        winning_play = game.active_round.tricks[-2].winning_play
        assert winning_play

        self.assertEqual(2, len(game.active_round.tricks))
        self.assertEqual(
            winning_play.identifier,
            game.active_round.active_player.identifier)

    def test_play_through_round(self):
        '''A new round is created after all tricks are played'''

        game = arrange.game(RoundStatus.TRICKS, arrange.play_round)

        self.assertEqual(2, len(game.rounds))
