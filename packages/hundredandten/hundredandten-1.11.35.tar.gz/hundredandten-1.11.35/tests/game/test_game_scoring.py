'''Test to ensure games are scored properly'''
from unittest import TestCase

from hundredandten.constants import WINNING_SCORE, GameStatus
from tests import arrange

# tests in this file run off of seeded games to avoid setting up everything necessary for the tests
# seeds and their expected values in different situations are recorded here

PLAYER_3_WIN_SEED = 'ba297348-77d7-42bb-9164-03712b05ba21'
BIDDER_WINS_IN_DISPUTE_SEED = 'c3f48eea-3f7e-42f5-bd54-8504d759e3d5'
FIRST_TO_SCORE_WINS_IN_DISPUTE_SEED = 'ae1f037b-6b39-474e-99f3-6468be19bfd5'


SEEDS_TO_SCORES = {
    PLAYER_3_WIN_SEED: {'0': 10, '1': -5, '2': 15, '3': 115},
    BIDDER_WINS_IN_DISPUTE_SEED: {'0': 120, '1': 0, '2': 115, '3': 80},
    FIRST_TO_SCORE_WINS_IN_DISPUTE_SEED: {'0': 55, '1': 110, '2': 50, '3': 110}}


class TestGameScoring(TestCase):
    '''Unit tests for scoring a game'''

    def test_start_at_zeroes(self):
        '''At game start, scores are all zeroes'''
        game = arrange.game(GameStatus.WAITING_FOR_PLAYERS)

        self.assertEqual([0] * len(game.players), list(game.scores.values()))
        self.assertEqual([0] * len(game.players), list(game.scores_by_round[-1].values()))

    def test_win_at_winning_score(self):
        '''At the end of the game, the winner has 110'''
        seed = PLAYER_3_WIN_SEED
        game = arrange.game(GameStatus.WON, seed=seed)

        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores_by_round[-1])

    def test_bidder_wins_when_sharing(self):
        '''If multiple players including the bidder reach 110, the bidder wins'''
        seed = BIDDER_WINS_IN_DISPUTE_SEED
        game = arrange.game(GameStatus.WON, seed=seed)

        assert game.winner
        assert game.active_round.active_bidder
        self.assertEqual(game.winner.identifier, game.active_round.active_bidder.identifier)
        self.assertTrue(
            len([score for score in game.scores.values() if score >= WINNING_SCORE]) == 2)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores_by_round[-1])

    def test_first_to_score_wins_when_sharing(self):
        '''If multiple players NOT including the bidder reach 110, the first to 110 wins'''
        seed = FIRST_TO_SCORE_WINS_IN_DISPUTE_SEED
        game = arrange.game(GameStatus.WON, seed=seed)

        winners = [key for key, value in game.scores.items() if value >= WINNING_SCORE]
        winning_scores = [
            score for score in game.score_history
            if score.identifier in winners and score.value >= WINNING_SCORE]

        assert game.winner
        assert game.active_round.active_bidder
        self.assertNotEqual(game.winner.identifier, game.active_round.active_bidder.identifier)
        self.assertEqual(winning_scores[0].identifier, game.winner.identifier)
        self.assertLess(game.scores[game.active_round.active_bidder.identifier], WINNING_SCORE)
        self.assertTrue(len(winners) > 1)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores)
        self.assertEqual(SEEDS_TO_SCORES[seed], game.scores_by_round[-1])
