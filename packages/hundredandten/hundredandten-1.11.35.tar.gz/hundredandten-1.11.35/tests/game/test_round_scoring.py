'''Test to ensure rounds are scored properly'''
from unittest import TestCase

from hundredandten.actions import Bid
from hundredandten.constants import BidAmount, RoundStatus
from hundredandten.trick import Score
from tests import arrange

# tests in this file run off of seeded games to avoid setting up everything necessary for the tests
# seeds and their expected values in different situations are recorded here
BIDDER_GOES_BACK_SEED = '57eaf68e-1c52-4a34-a1e1-1a12905c5069'
TWO_FIFTEENS_SEED = '5b46ca51-5967-4a9e-b894-c9886ba1794b'
SHOOT_THE_MOON_SEED = 'ba2acf5d-3dbf-48d6-9cf3-b0cf353384d5'

SEEDS_TO_SCORES = {
    BIDDER_GOES_BACK_SEED: {
        BidAmount.FIFTEEN: [
            Score('1', -15),
            Score('2', 10),
            Score('0', 5),
            Score('3', 5),
            Score('3', 5)
        ]},
    TWO_FIFTEENS_SEED: {
        BidAmount.FIFTEEN: [
            Score('0', 10),
            Score('1', 5),
            Score('1', 5),
            Score('1', 5),
            Score('0', 5)
        ],
        BidAmount.TWENTY: [
            Score('1', -20),
            Score('0', 10),
            Score('0', 5)
        ],
        BidAmount.SHOOT_THE_MOON:  [
            Score('1', -60),
            Score('0', 10),
            Score('0', 5)
        ]},
    SHOOT_THE_MOON_SEED: {
        BidAmount.FIFTEEN: [
            Score('1', 5),
            Score('1', 10),
            Score('1', 5),
            Score('1', 5),
            Score('1', 5)
        ],
        BidAmount.SHOOT_THE_MOON: [Score('1', 60)]}
}


class TestRoundScoring(TestCase):
    '''Unit tests for scoring a round'''

    def test_bidder_goes_back(self):
        '''Score a round where the bidder bids fifteen and loses the points'''
        seed = BIDDER_GOES_BACK_SEED
        game = arrange.game(RoundStatus.TRICKS, arrange.play_round, seed=seed)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(
            [Score(old_round.active_bidder.identifier, -15)],
            [score for score in old_round.scores
             if score.identifier == old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_share_fifteen(self):
        '''Score a round where the bidder and one other player wins fifteen'''
        seed = TWO_FIFTEENS_SEED
        game = arrange.game(RoundStatus.TRICKS, arrange.play_round, seed=seed)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(
            [Score(old_round.active_bidder.identifier, 5),
             Score(old_round.active_bidder.identifier, 5),
             Score(old_round.active_bidder.identifier, 5)],
            [score for score in old_round.scores
             if score.identifier == old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_lose_twenty(self):
        '''Score a round where the bidder bids twenty and loses'''
        seed = TWO_FIFTEENS_SEED
        game = arrange.game(RoundStatus.TRICKS, seed=seed)
        assert game.active_round.active_bidder

        game.active_round.bids.append(
            Bid(identifier=game.active_round.active_bidder.identifier, amount=BidAmount.TWENTY))

        arrange.play_round(game)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(
            [Score(old_round.active_bidder.identifier, -20)],
            [score for score in old_round.scores
             if score.identifier == old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_shoot_the_moon(self):
        '''Score a round where the bidder shoots the moon and wins'''
        seed = SHOOT_THE_MOON_SEED
        game = arrange.game(RoundStatus.TRICKS, seed=seed)
        assert game.active_round.active_bidder

        game.active_round.bids.append(
            Bid(identifier=game.active_round.active_bidder.identifier,
                amount=BidAmount.SHOOT_THE_MOON))

        arrange.play_round(game)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(
            [Score(old_round.active_bidder.identifier, 60)],
            [score for score in old_round.scores
             if score.identifier == old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_thirty(self):
        '''Score a round where the bidder wins all tricks without shooting the moon'''
        seed = SHOOT_THE_MOON_SEED
        game = arrange.game(RoundStatus.TRICKS, arrange.play_round, seed=seed)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(
            [Score(old_round.active_bidder.identifier, 5),
             Score(old_round.active_bidder.identifier, 10),
             Score(old_round.active_bidder.identifier, 5),
             Score(old_round.active_bidder.identifier, 5),
             Score(old_round.active_bidder.identifier, 5)],
            [score for score in old_round.scores
             if score.identifier == old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)

    def test_lose_shoot_the_moon(self):
        '''Score a round where the bidder shoots the moon and loses'''
        seed = TWO_FIFTEENS_SEED
        game = arrange.game(RoundStatus.TRICKS, seed=seed)
        assert game.active_round.active_bidder

        game.active_round.bids.append(
            Bid(identifier=game.active_round.active_bidder.identifier,
                amount=BidAmount.SHOOT_THE_MOON))

        arrange.play_round(game)

        old_round = game.rounds[-2]

        assert old_round.active_bidder
        assert old_round.active_bid
        self.assertEqual(
            [Score(old_round.active_bidder.identifier, -60)],
            [score for score in old_round.scores
             if score.identifier == old_round.active_bidder.identifier])
        self.assertEqual(SEEDS_TO_SCORES[seed][old_round.active_bid], old_round.scores)
