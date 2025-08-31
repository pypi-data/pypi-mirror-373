'''Test behavior of the Game while in a round of bidding'''
from unittest import TestCase

from hundredandten.actions import Bid, Unpass
from hundredandten.constants import BidAmount, RoundRole, RoundStatus
from hundredandten.hundred_and_ten_error import HundredAndTenError
from tests import arrange


class TestBidding(TestCase):
    '''Unit tests for bidding within a round of Game'''

    def test_error_when_no_dealer(self):
        '''Round must always have a dealer'''

        game = arrange.game(RoundStatus.BIDDING)

        # remove dealer role to put game in invalid state to verify error
        game.active_round.players.remove_role(game.active_round.dealer.identifier, RoundRole.DEALER)

        self.assertRaises(HundredAndTenError, lambda: game.active_round.dealer)

    def test_bid_from_active_player(self):
        '''Active player can place a bid'''

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertEqual(1, len(game.active_round.bids))
        self.assertEqual(BidAmount.FIFTEEN, game.active_round.bids[0].amount)

    def test_low_bid_from_active_player(self):
        '''Active player cannot place a bid below the current bid'''

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.TWENTY))

        self.assertRaises(HundredAndTenError, game.act,
                          Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

    def test_equal_bid_from_active_player(self):
        '''Active player cannot place a bid equal to the current bid'''

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertRaises(HundredAndTenError, game.act,
                          Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

    def test_low_bid_from_dealer(self):
        '''Dealer cannot place a bid below to the current bid'''

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.TWENTY))
        arrange.pass_to_dealer(game)

        self.assertRaises(HundredAndTenError, game.act,
                          Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

    def test_equal_bid_from_dealer(self):
        '''Dealer can place a bid equal to the current bid'''

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertNotEqual(game.active_round.active_bidder, game.active_round.dealer)

        arrange.pass_to_dealer(game)

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.FIFTEEN))

        self.assertEqual(game.active_round.active_bidder, game.active_round.dealer)

    def test_bid_from_passed_player(self):
        '''Inactive player cannot place a bid'''

        game = arrange.game(RoundStatus.BIDDING)

        once_active_player = game.active_round.active_player.identifier
        game.act(Bid(once_active_player, BidAmount.PASS))

        self.assertRaises(HundredAndTenError, game.act, Bid(once_active_player, BidAmount.FIFTEEN))

    def test_bid_from_inactive_player(self):
        '''Inactive player cannot place a bid'''

        game = arrange.game(RoundStatus.BIDDING)

        self.assertRaises(HundredAndTenError, game.act,
                          Bid(game.active_round.inactive_players[0].identifier, BidAmount.FIFTEEN))

    def test_pass_from_inactive_player(self):
        '''Inactive player can prepass'''

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.inactive_players[0].identifier, BidAmount.PASS))

        self.assertEqual(0, len(game.active_round.bids))
        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_unpass_from_prepassed_player(self):
        '''Prepassed player can unpass'''

        game = arrange.game(RoundStatus.BIDDING)

        game.act(Bid(game.active_round.inactive_players[0].identifier, BidAmount.PASS))

        self.assertIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

        game.act(Unpass(game.active_round.inactive_players[0].identifier))

        self.assertEqual(0, len(game.active_round.bids))
        self.assertNotIn(RoundRole.PRE_PASSED, game.active_round.inactive_players[0].roles)

    def test_prepass(self):
        '''When the next player has prepassed, auto pass for them'''
        game = arrange.game(RoundStatus.BIDDING)

        next_player = game.active_round.players.after(game.active_round.active_player.identifier)

        game.act(Bid(next_player.identifier, BidAmount.PASS))

        self.assertEqual(0, len(game.active_round.bids))

        game.act(Bid(game.active_round.active_player.identifier, BidAmount.PASS))

        self.assertEqual(2, len(game.active_round.bids))
        self.assertEqual(RoundStatus.BIDDING, game.status)
        self.assertEqual(0, len(game.active_round.players.by_role(RoundRole.PRE_PASSED)))
        self.assertIn(game.active_round.active_player, game.active_round.bidders)
        # play will have passed the previously "next" player since they pre-passed
        self.assertNotEqual(game.active_round.active_player, next_player)
