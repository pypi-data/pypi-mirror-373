'''Helpers to set up a game for testing'''
from typing import Callable, Optional
from uuid import uuid4

from hundredandten.actions import Bid, Discard, Play, SelectTrump
from hundredandten.constants import (AnyStatus, BidAmount, GameRole,
                                     GameStatus, RoundStatus, SelectableSuit)
from hundredandten.decisions import trumps
from hundredandten.game import Game
from hundredandten.group import Group, Person


def game(
        status: AnyStatus,
        massage: Callable[[Game], None] = lambda f_game: None,
        seed: Optional[str] = None) -> Game:
    '''
    Return a game in the requested status.
    If passed, will call the massage function on the game before returning
    '''

    new_game = {
        GameStatus.WAITING_FOR_PLAYERS: __get_waiting_for_players_game,
        RoundStatus.BIDDING: __get_bidding_game,
        RoundStatus.COMPLETED_NO_BIDDERS: __get_completed_no_bidders_game,
        RoundStatus.TRUMP_SELECTION: __get_trump_selection_game,
        RoundStatus.DISCARD: __get_discard_game,
        RoundStatus.TRICKS: __get_tricks_game,
        GameStatus.WON: __get_won_game
    }[status](seed)
    massage(new_game)
    return new_game


def make_space(game_to_open: Game) -> None:
    '''Make space in the game, which will be full by default when arranged by this file'''
    game_to_open.leave(game_to_open.players[-1].identifier)


def pass_round(game_to_pass: Game) -> None:
    '''Pass the current round of the provided game'''
    for player in game_to_pass.active_round.bidders:
        game_to_pass.act(Bid(player.identifier, BidAmount.PASS))


def pass_to_dealer(game_to_pass: Game) -> None:
    '''Pass the current round until reaching the dealer'''
    for player in filter(
            lambda player: player != game_to_pass.active_round.dealer,
            game_to_pass.active_round.bidders):
        game_to_pass.act(Bid(player.identifier, BidAmount.PASS))


def bid(game_to_bid: Game) -> None:
    '''Have the active player place a bid'''
    for player in game_to_bid.active_round.inactive_players:
        game_to_bid.act(Bid(player.identifier, BidAmount.PASS))
    game_to_bid.act(Bid(game_to_bid.active_round.active_player.identifier, BidAmount.FIFTEEN))


def select_trump(game_to_select: Game) -> None:
    '''Have the active player select a trump'''
    game_to_select.act(SelectTrump(
        game_to_select.active_round.active_player.identifier, SelectableSuit.SPADES))


def discard(game_to_discard: Game) -> None:
    '''Have all players discard'''
    while game_to_discard.status == RoundStatus.DISCARD:
        game_to_discard.act(Discard(game_to_discard.active_round.active_player.identifier, []))


def play_trick(game_to_play: Game) -> None:
    '''Play through the current trick of the provided game'''
    starting_active_trick = game_to_play.active_round.active_trick
    while len(starting_active_trick.plays) < len(game_to_play.players):
        active_player = game_to_play.active_round.active_player
        trump_cards = trumps(active_player.hand, game_to_play.active_round.trump)
        game_to_play.act(
            Play(
                active_player.identifier, next(
                    iter(trump_cards + active_player.hand))))


def play_round(game_to_play: Game) -> None:
    '''Play through the current trick of the provided game'''
    while game_to_play.status == RoundStatus.TRICKS:
        play_trick(game_to_play)


def __get_waiting_for_players_game(seed: Optional[str]) -> Game:
    '''Returns a game that is waiting for players'''
    new_game = Game(
        people=Group(
            list(map(
                lambda identifier: Person(str(identifier), roles={GameRole.PLAYER}),
                range(4)))), seed=seed or str(uuid4()))
    new_game.people.add_role(new_game.people[0].identifier, GameRole.ORGANIZER)
    return new_game


def __get_bidding_game(seed: Optional[str]) -> Game:
    '''Returns a game in the bidding status'''
    new_game = __get_waiting_for_players_game(seed)
    new_game.start_game()
    return new_game


def __get_completed_no_bidders_game(seed: Optional[str]) -> Game:
    '''Returns a game in the completed no bidders status'''
    new_game = __get_bidding_game(seed)
    pass_round(new_game)
    return new_game


def __get_trump_selection_game(seed: Optional[str]) -> Game:
    '''Return a game in the trump selection status'''
    new_game = __get_bidding_game(seed)
    bid(new_game)
    return new_game


def __get_discard_game(seed: Optional[str]) -> Game:
    '''Return a game in the discard status'''
    new_game = __get_trump_selection_game(seed)
    select_trump(new_game)
    return new_game


def __get_tricks_game(seed: Optional[str]) -> Game:
    '''Return a game in the tricks status'''
    new_game = __get_discard_game(seed)
    discard(new_game)

    return new_game


def __get_won_game(seed: Optional[str]) -> Game:
    '''Return a game in the won status'''
    new_game = __get_bidding_game(seed)
    while new_game.status != GameStatus.WON:
        bid(new_game)
        select_trump(new_game)
        discard(new_game)
        play_round(new_game)

    return new_game
