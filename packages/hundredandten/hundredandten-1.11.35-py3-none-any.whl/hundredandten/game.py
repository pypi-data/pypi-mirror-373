'''Represent a game of Hundred and Ten'''
from dataclasses import dataclass, field
from functools import reduce
from random import Random
from typing import Optional
from uuid import UUID, uuid4

from hundredandten.actions import Action, Bid, Play
from hundredandten.constants import (HAND_SIZE, WINNING_SCORE, Accessibility,
                                     AnyStatus, GameRole, GameStatus,
                                     RoundRole, RoundStatus)
from hundredandten.deck import Deck
from hundredandten.events import (Event, GameEnd, GameStart, RoundEnd,
                                  RoundStart)
from hundredandten.group import Group, Person, Player
from hundredandten.hundred_and_ten_error import HundredAndTenError
from hundredandten.round import Round
from hundredandten.trick import Score


@dataclass
class Game:
    '''A game of Hundred and Ten'''

    people: Group[Person] = field(default_factory=Group)
    rounds: list[Round] = field(default_factory=list)
    accessibility: Accessibility = field(default=Accessibility.PUBLIC)
    seed: str = field(default_factory=lambda: str(uuid4()))

    @property
    def status(self) -> AnyStatus:
        '''The status property.'''
        if not self.rounds:
            return GameStatus.WAITING_FOR_PLAYERS
        if self.winner:
            return GameStatus.WON
        return self.active_round.status

    @property
    def active_round(self) -> Round:
        '''The active round'''
        if not self.rounds:
            raise HundredAndTenError("No active round found.")
        return self.rounds[-1]

    @property
    def organizer(self) -> Person:
        '''
        The organizer of the game
        If no player has the role, pick a random player
        '''
        return next(
            iter(self.people.by_role(GameRole.ORGANIZER) or self.people),
            Person('unknown'))

    @property
    def invitees(self) -> Group[Person]:
        '''
        The invitees to the game
        '''
        return self.people.by_role(GameRole.INVITEE)

    @property
    def players(self) -> Group[Person]:
        '''
        The players of the game
        '''
        return self.people.by_role(GameRole.PLAYER)

    @property
    def winner(self) -> Optional[Person]:
        '''
        The winner of the game
        '''
        # if a round is in progess, don't attempt the computation
        if not self.rounds or self.active_round.status != RoundStatus.COMPLETED:
            return None

        winning_scores = [score for score in self.score_history if score.value >= WINNING_SCORE]
        ordered_winning_players = list(map(
            lambda score: self.active_round.players.by_identifier(score.identifier),
            winning_scores))

        winner = (
            self.active_round.active_bidder
            if (self.active_round.active_bidder in ordered_winning_players) else
            next(iter(ordered_winning_players),
                 None))

        return winner

    @property
    def events(self) -> list[Event]:
        '''The events that occurred in the game.'''

        round_events: list[list[Event]] = [
            [
                RoundStart(
                    round.dealer.identifier,
                    {p.identifier: round.original_hand(p.identifier) for p in round.players}),
                *round.events,
                # don't include the round end event if it hasn't ended
                *([RoundEnd(scores=self.__scores(index + 1))] if round.completed else [])
            ]
            for index, round in enumerate(self.rounds)]

        return [
            # don't include game start event if it hasn't started
            *([GameStart()] if self.status != GameStatus.WAITING_FOR_PLAYERS else []),
            *[round_event
              for event_list in round_events for round_event in event_list],
            # don't include the game end event if it hasn't ended
            *([GameEnd(self.winner.identifier)] if self.winner else [])
        ]

    @property
    def score_history(self) -> list[Score]:
        '''A list of all players' scores over time'''

        return self.__score_history(len(self.rounds))

    @property
    def scores_by_round(self) -> list[dict[str, int]]:
        '''
        The scores each player earned for this game
        A dictionary in the form
        key: player identifier
        value: the player's score
        '''
        return [self.__scores(round_num) for round_num in range(len(self.rounds) + 1)]

    @property
    def scores(self) -> dict[str, int]:
        '''
        The scores each player earned for this game
        A dictionary in the form
        key: player identifier
        value: the player's score
        '''
        return self.__scores(len(self.rounds))

    def invite(self, inviter: str, invitee: str) -> None:
        '''Invite a player to the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot invite a player to an in progress game.")
        if self.people.find_or_use(Person(inviter)) not in self.players:
            raise HundredAndTenError("You cannot invite a player to a game you aren't a part of.")

        self.people.upsert(self.people.find_or_use(Person(invitee, {GameRole.INVITEE})))

    def join(self, player: str) -> None:
        '''Add a player to the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot join this game. It has already started.")
        if len(self.players) >= 4:
            raise HundredAndTenError("You cannot join this game. It is at capacity.")
        if (self.accessibility != Accessibility.PUBLIC
                and GameRole.INVITEE not in self.people.find_or_use(Player(player)).roles):
            raise HundredAndTenError("You cannot join this game. You must be invited first.")

        self.people.upsert(self.people.find_or_use(Person(player, {GameRole.PLAYER})))

    def leave(self, player: str) -> None:
        '''Remove a player from the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("You cannot leave an in-progress game.")

        person = Person(player)

        if person in self.people:
            self.people.remove(person)

    def automate(self, player: str) -> None:
        '''Automate a player in the game'''

        person = self.people.find_or_use(Person(player))
        person.automate = True

        if self.rounds:
            self.active_round.automate(player)

        if person in self.people:
            self.people.update(person)
            self.__automated_act()

    def start_game(self) -> None:
        '''Start the game'''

        if self.status != GameStatus.WAITING_FOR_PLAYERS:
            raise HundredAndTenError("Cannot start a game that's already started.")
        if len(self.players) < 2:
            raise HundredAndTenError("You cannot play with fewer than two players.")

        self.__new_round(self.players[0].identifier)
        self.__automated_act()

    def act(self, action: Action) -> None:
        '''Perform an action as a player of the game'''
        self.__act(action)
        self.__automated_act()

    def suggestion(self) -> Action:
        '''Return the suggested action given the state of the game'''
        return self.active_round.suggestion()

    def __automated_act(self):
        while isinstance(self.status, RoundStatus) and self.active_round.active_player.automate:
            self.__act(self.__automated_action())

    def __automated_action(self) -> Action:
        return self.suggestion()

    def __act(self, action: Action) -> None:
        '''Perform an action as a player of the game'''
        self.active_round.act(action)
        # handle creation of new round if appropriate
        if isinstance(action, Bid):
            self.__end_bid()
        if isinstance(action, Play):
            self.__end_play()

    def __end_bid(self):
        if self.status == RoundStatus.COMPLETED_NO_BIDDERS:
            current_dealer = self.active_round.dealer.identifier
            # dealer doesn't rotate on a round with no bidders
            # unless the current dealer has been dealer 3x in a row
            keep_same_dealer = len(self.rounds) < 3 or any(
                r.dealer.identifier != current_dealer for r in self.rounds[-3:])
            next_dealer = current_dealer if keep_same_dealer else self.players.after(
                current_dealer).identifier
            self.__new_round(next_dealer)

    def __end_play(self):
        if self.status == RoundStatus.COMPLETED:
            self.__new_round(self.players.after(self.active_round.dealer.identifier).identifier)

    def __new_round(self, dealer: str) -> None:
        r_deck_seed = self.seed if not self.rounds else self.active_round.deck.seed

        deck = Deck(seed=str(UUID(int=Random(r_deck_seed).getrandbits(128), version=4)))

        round_players = Group(map(lambda p: Player(
            p.identifier, hand=deck.draw(HAND_SIZE), automate=p.automate), self.players))
        round_players.add_role(dealer, RoundRole.DEALER)

        self.rounds.append(Round(players=round_players, deck=deck))

    def __score_history(self, to_round: int) -> list[Score]:
        '''A list of all players' scores up to the provided round'''

        scores = {}
        score_history = []

        all_final_scores = [
            score for round in self.rounds[:to_round] for score in round.scores
            if round.status == RoundStatus.COMPLETED]

        for score in all_final_scores:
            new_score = scores.get(score.identifier, 0) + score.value
            scores[score.identifier] = new_score
            score_history.append(Score(score.identifier, new_score))

        return score_history

    def __scores(self, to_round) -> dict[str, int]:
        '''
        The scores each player earned for this game up to the provided round
        A dictionary in the form
        key: player identifier
        value: the player's score
        '''

        return reduce(lambda acc,
                      player: {
                          **acc,
                          player.identifier: self.__score_at_round(player.identifier, to_round)
                      },
                      self.players, {player.identifier: 0 for player in self.players})

    def __score_at_round(self, identifier: str, to_round: int) -> int:
        '''Return the most recent score for the provided player at the provided round'''

        most_recent_score = next((score for score in reversed(
            self.__score_history(to_round)) if score.identifier == identifier), None)

        return most_recent_score.value if most_recent_score else 0
