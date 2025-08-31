'''Test behavior of the Game when going around discarding'''
from unittest import TestCase

from hundredandten.actions import Discard
from hundredandten.constants import HAND_SIZE, RoundStatus
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange


class TestDiscard(TestCase):
    '''Unit tests for discarding within a round of Game'''

    def test_error_when_not_discarding(self):
        '''Can't discard if not in discard status'''

        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(HundredAndTenError, game.act, Discard('', []))

    def test_cant_discard_when_not_active(self):
        '''Can't discard if not the active player'''

        game = arrange.game(RoundStatus.DISCARD)
        inactive_player = game.active_round.inactive_players[0]

        self.assertRaises(HundredAndTenError, game.act, Discard(
            inactive_player.identifier, inactive_player.hand))

    def test_cant_discard_other_players_cards(self):
        '''Can't discard cards that aren't your own'''

        game = arrange.game(RoundStatus.DISCARD)

        self.assertRaises(HundredAndTenError, game.act, Discard(
            game.active_round.active_player.identifier, game.active_round.inactive_players[0].hand))

    def test_discard_whole_hand(self):
        '''Can discard your whole hand'''

        game = arrange.game(RoundStatus.DISCARD)

        player = game.active_round.active_player
        initial_hand = list(player.hand)
        game.act(Discard(player.identifier,
                         player.hand))

        self.assertEqual(HAND_SIZE, len(player.hand))
        self.assertEqual(HAND_SIZE, len(initial_hand))
        self.assertFalse(any(card in player.hand for card in initial_hand))

    def test_discard_part_of_hand(self):
        '''Can discard a part of your hand'''

        game = arrange.game(RoundStatus.DISCARD)

        player = game.active_round.active_player
        discard = Discard(player.identifier,
                          [player.hand[1], player.hand[3]])

        remaining_in_hand = [player.hand[0], player.hand[2], player.hand[4]]
        game.act(discard)

        self.assertEqual(HAND_SIZE, len(player.hand))
        self.assertTrue(all(card in player.hand for card in remaining_in_hand))
        self.assertFalse(any(card in player.hand for card in discard.cards))
