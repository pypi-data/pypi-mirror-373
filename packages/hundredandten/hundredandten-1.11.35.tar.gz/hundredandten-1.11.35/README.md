[![Code Quality](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/lint.yaml/badge.svg?branch=main)](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/lint.yaml)
[![100% Coverage](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/coverage.yaml/badge.svg?branch=main)](https://github.com/seamuslowry/hundred-and-ten/actions/workflows/coverage.yaml)

# Hundred and Ten

A python package to provide an engine for playing the game Hundred and Ten.

```python
from hundredandten import HundredAndTen

game = HundredAndTen()
```

## How To Play

Hundred and Ten is a trick-taking game structured into rounds of five tricks each that continue until one player has reached a score of 110 or above.

The game is played with a normal 52 card deck and includes one Joker for a total deck of 53 cards.

### Dealer

For each round, one player is considered the dealer. In an over-the-table game, this player would be responsible for shuffling the deck and dealing out the cards. With this package, that is all handled. However, the dealer still retains some additional privileges that go along with the role:

1. Bidding begins to the left of the dealer. This means that the dealer is always the last to place a bid and can make their decision with the context of other players' bids.

2. Normally, to steal a bid, players must bid _above_ the current amount. The dealer, however, can steal a bid for the current amount.

The position of dealer moves to the current dealer's left at the end of the round, except with conditions described in [passing](#passing).

### Bidding

Before the round begins, players are dealt a hand of five cards, which they will use to determine if they wish to "bid" any points. The highest bidder will decide which suit is trumps for the round. However, if the highest bidder fails to earn at least the amount of points they bid, they instead lose that amount (see [scoring](#scoring)).

Bidding begins to the left of the [dealer](#dealer) and continues clockwise around the table until either all players have passed or a single bidder remains.

#### Passing

If players do not believe their hand is strong enough to bid, they can pass on their turn. If all players pass, the round ends.

The same player will remain dealer after a round when all players pass, for a maximum of three rounds. If the current dealer has been the dealer for the last three rounds, then [dealer](#dealer) will pass to the left.

#### Options

Players may only bid one of the following options:

- 15
- 20
- 25
- 30
- Shoot the Moon (see: [Scoring](#scoring))

#### Stealing a Bid

When a player places a bid, other players in the round must bid above this amount (unless they are the [dealer](#dealer)) or pass. Bidding above (or at, see: [dealer](#dealer)) the current highest bid is called Stealing the Bid and bidding continues around the table until all but one player has passed.

#### Selecting Trump

The highest bidder selects the trump suit for the round. Once the trump is selected, all players at the table may choose to discard any or all of their current hand and have their hand refilled from the deck. This begins with the dealer, and continues clockwise until all players have had the opportunity to discard.

### Tricks

Each round consists of five tricks. Each player contributes one card to a trick. When all players have played a card, the trick ends and a winner is determined (see [Winning a Trick](#winning-a-trick)).

The first trick begins with the player to the left of the highest bidder; play continues clockwise until the trick is complete. Subsequent tricks will begin with the winner of the previous trick.

#### Trump Cards

A card is a trump card if it is the suit selected by the highest bidder.

Additionally, the Ace of Hearts and the Joker are both considered trump cards regardless of the suit chosen by the bidder. This is important to remember for [winning a trick](#winning-a-trick) and [bleeding](#bleeding).

#### Winning a Trick

A trick is won by the highest value card in the trick. Trump cards will always beat non-trump cards.

See below for the card hierarchy for each suit, when it is trump. Recall the additional [trump cards](#trump-cards) that will not necessarily be of the selected suit. Note that red suits and black suits follow the same trump hierarchy with the exception of their number cards. Lower value black number cards will beat higher value black number cards.

<table align="center">
  <tr>
    <th>
      Rank
    </th>
    <th>
      Hearts
    </th>
    <th>
      Diamonds
    </th>
    <th>
      Spades
    </th>
    <th>
      Clubs
    </th>
  </tr>
  <tr>
    <td align="center">
      Highest
    </td>
    <td colspan=4 align="center">
      5
    </td>
  </tr>
  <tr>
    <td  rowspan=13 align="center">
      &nbsp
    </td>
    <td colspan=4 align="center">
      Jack
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Joker
    </td>
  </tr>
  <tr>
    <td colspan=1 rowspan=2 align="center">
      Ace
    </td>
    <td colspan=3 align="center">
      Ace of Hearts
    </td>
  </tr>
  <tr>
    <td colspan=3 align="center">
      Ace
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      King
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Queen
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      10
    </td>
    <td colspan=2 align="center">
      2
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      9
    </td>
    <td colspan=2 align="center">
      3
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      8
    </td>
    <td colspan=2 align="center">
      4
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      7
    </td>
    <td colspan=2 align="center">
      6
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      6
    </td>
    <td colspan=2 align="center">
      7
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      4
    </td>
    <td colspan=2 align="center">
      8
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      3
    </td>
    <td colspan=2 align="center">
      9
    </td>
  </tr>
  <tr>
    <td align="center">
      Lowest
    </td>
    <td colspan=2 align="center">
      2
    </td>
    <td colspan=2 align="center">
      10
    </td>
  </tr>
</table>

If no trump card is played, the suit of the first played card is considered trump for the trick. It will not follow the trump order listed above, though. Instead, it will follow a normal Ace-high card hierarchy. The only exception is that lower value black number cards still beat higher value black number cards. The table below describes the full order.

<table align="center">
  <tr>
    <th>
      Rank
    </th>
    <th>
      Hearts
    </th>
    <th>
      Diamonds
    </th>
    <th>
      Spades
    </th>
    <th>
      Clubs
    </th>
  </tr>
  <tr>
    <td align="center">
      Highest
    </td>
    <td colspan=4 align="center">
      Ace
    </td>
  </tr>
  <tr>
    <td rowspan=11>
      &nbsp
    </td>
    <td colspan=4 align="center">
      King
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Queen
    </td>
  </tr>
  <tr>
    <td colspan=4 align="center">
      Jack
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      10
    </td>
    <td colspan=2 align="center">
      2
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      9
    </td>
    <td colspan=2 align="center">
      3
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      8
    </td>
    <td colspan=2 align="center">
      4
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      7
    </td>
    <td colspan=2 align="center">
      5
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      5
    </td>
    <td colspan=2 align="center">
      6
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      6
    </td>
    <td colspan=2 align="center">
      7
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      4
    </td>
    <td colspan=2 align="center">
      8
    </td>
  </tr>
  <tr>
    <td colspan=2 align="center">
      3
    </td>
    <td colspan=2 align="center">
      9
    </td>
  </tr>
  <tr>
    <td align="center">
      Lowest
    </td>
    <td colspan=2 align="center">
      2
    </td>
    <td colspan=2 align="center">
      10
    </td>
  </tr>
</table>

#### Bleeding

If the first card in a trick is a trump card, the trick is "bleeding". This means that all players _must_ play a trump card if they have one in their hand. If they do not have one in their hand, they may play whatever card they wish.

#### Scoring

Each round (which consists of five tricks) normally offers thirty points in total to be won by players. The trick that was won with the highest value card is worth ten points. The remaining four tricks are worth five points each.

If the tricks won by the highest bidder do not equal or exceed the amount they bid, they will instead lose the amount of their bid. The tricks they won will not offset their loss. For example, if a player began the round at zero points, bid fifteen, and won ten points, that player will end the round at negative fifteen points.

Additionally, if the highest bidder decided to [Shoot the Moon](#options), they will earn sixty points if they won every trick that round. Otherwise, they will lose sixty points.

Only the highest bidder can lose points.

### Winning

The game ends if, after a round is scored, one or more players has a total score greater than or equal to 110.

If multiple players are above 110, the winner is determined as follows:

1. If the current highest bidder is among the players above 110, the highest bidder wins.
2. Otherwise, the player who would have reached 110 first within the round wins.

## Players

All players in the game must have a unique string identifier. They may also have a list of applicable roles, but, for most use cases, the engine should manage those roles itself.

### Roles

- `GameRole.ORGANIZER`: This person is organizing the game. They have no more inherent permissions than any other player within the engine, but they can be tracked if consumers want to give them additional permissions.
- `GameRole.PLAYER`: This person is attached to the game and will be playing if or once the game begins.
- `GameRole.INVITEE`: This person is attached to the game as an invitee and will be able to join the game even if the accessibility is set to private.
- `RoundRole.DEALER`: This player is acting as the dealer for the current round. This role is only attached to persons/players at the round level, not the game level. This role describes the invividual as the dealer and does offer inherent play differences as described in the [rules](#how-to-play).
- `RoundRole.PRE_PASSED`: This player has elected to pass before their bidding turn. When play reaches them, they will perform a pass action automatically.

## Inviting, Joining, and Leaving

While not necessary for play, this engine provides support use cases involving a form of player lobby before the start of the game.

### `HundredAndTen.invite`

Any player already in the game can invite any other player.

```python
game = HundredAndTen()
game.join('player_identifier')
# without joining first, this next line would error
game.invite('player_identifier', 'other_player')
```

### `HundredAndTen.join`

Joining a public game (the default) is as easy as calling `join`.

```python
game = HundredAndTen()
# game is public and there are fewer than 4 players
# they will join as the identified player
game.join('player_identifier')
```

Joining a private game requires an invite before the player will be able to join `join`.

```python
# be sure to initialize private games with one player
# otherwise they will not be joinable
game = HundredAndTen(
  Group([Person('organizer')]),
  accessibility=Accessibility.PRIVATE)

game.invite('organizer', 'player_identifier')
# game is private, so this would error without the above invite
game.join('player_identifier')
```

### `HundredAndTen.leave`

To leave a game, simply call `leave`.

```python
game = HundredAndTen()
game.join('player_identifier_1')
game.leave('player_identifier_1')
```

## Starting a Game

### `HundredAndTen.start_game`

Begin play by calling `start_game` on the `HundredAndTen` instance.

```python
game = HundredAndTen()
game.join('player_1')
game.join('player_2')
game.join('player_3')
game.join('player_4')
game.start_game()
```

Once a game has begun, players can no longer join or leave the game.

## Determining the State of a Game

### `HundredAndTen.status`

The status of the game can be one of the following values

- `GameStatus.WAITING_FOR_PLAYERS`: The game has not yet begun. Players may still join or leave.
- `RoundStatus.BIDDING`: Players are bidding in the current round.
- `RoundStatus.COMPLETED_NO_BIDDERS`: The current round is complete, but no player submitted a bid. This should be a transitionary state. Any game that reaches this state should immediately begin a new round and enter `RoundStatus.BIDDING`.
- `RoundStatus.TRUMP_SELECTION`: The bidder in the current round is selecting their trump value.
- `RoundStatus.DISCARD`: Players in the current round are discarding from their hard to refill.
- `RoundStatus.COMPLETED`: The current round is complete with tricks won by the players. This should also be a transitionary state. Any game that reaches this state should either begin a new round and enter `RoundStatus.BIDDING` or determine a winner and enter `GameStatus.WON`
- `GameStatus.WON`: The game is complete and a winner has been determined. No further actions are allowed.

### `HundredAndTen.active_round.active_player`

This field will hold the current active player.

### `HundredAndTen.scores`

This field will hold the current score values. In the form of a `dict[str, int]`.

For example:

```python
{
  'p1': 55,
  'p2': 70,
  'p3': -15,
  'p4': 25
}
```

### `HundredAndTen.winner`

This field will hold the winner of the game, if the game is in `GameStatus.WON`. Otherwise, it will be `None`.

## Playing a Game

Once a game has begun, the `HundredAndTen` instance should only be interacted with through the `act` method. In this manner, players can bid, unpass, select trump, discard cards, or play a card.

Each `act` can only be performed by the current active player. If another player attempts to act, it will result in an error.

The exception to this is pre-passing. Any player may pass before their turn during the bidding stage. A bid of any other amount will still result in an error.

### `HundredAndTen.act` to `Bid`

To bid, call `act` with a `Bid` object.

```python
from hundredandten import HundredAndTen, Bid, BidAmount

# set up and start the game

game.act(Bid('active_player_identifier', BidAmount.FIFTEEN))
```

To pre-pass, a non-active player must bid a pass.

```python
from hundredandten import HundredAndTen, Bid, BidAmount

# set up and start the game

game.act(Bid('non_active_player_identifier', BidAmount.PASS))
# when 'non_active_player_identifier' becomes the active player, they will pass
```

### `HundredAndTen.act` to `Unpass`

If a player has prepassed, but would now like to `Bid` a non-zero amount, they should `Unpass` to avoid automatically passing on their turn.

```python
from hundredandten import HundredAndTen, Bid, BidAmount, Unpass

# set up and start the game
# pass as the non active player

game.act(Unpass('non_active_player_identifier'))
```

### `HundredAndTen.act` to `SelectTrump`

Once a player has won the bid, that player must select the trump suit for that round.

```python
from hundredandten import HundredAndTen, SelectTrump, SelectableSuit

# set up and start the game
# select a bidder

# any of the four SelectableSuit value can be used
game.act(SelectTrump('bidder', SelectableSuit.CLUBS))
```

### `HundredAndTen.act` to `Discard`

Once trump has been selected, each player will have the opportunity to discard a portion of their hand and refill with new cards.
This must be done in player order.

```python
from hundredandten import HundredAndTen, Discard

# set up and start the game
# select a bidder
# select trump

game.act(Discard('active_player', game.active_round.active_player.hand[1:3]))
```

### `HundredAndTen.act` to `Play`

Once bidding, trump selection, and discard have all occurred. Players will play through tricks.

This action will enforce that played cards follow the rule relating to ["bleeding"](#bleeding).

```python
from hundredandten import HundredAndTen, Play

# set up and start the game
# select a bidder
# select trump
# discard

game.act(Play('active_player', game.active_round.active_player.hand[0]))
```

## Machine Play

### `HundredAndTen.suggestion`

At any state of active play (when the game is not `GameStatus.WON` or `GameStatus.WAITING_FOR_PLAYERS`), the game can provide a suggested action.

```python
from hundredandten import HundredAndTen

# set up and start the game

print(game.suggestion()) # will be a Bid, SelectTrump, Discard, or Play action
```

### `HundredAndTen.automate`

Any player can be automated at any time. But, once automated, a player cannot be unautomated. Automated players will always play the suggested action.

```python
from hundredandten import HundredAndTen

game = HundredAndTen()
game.join('machine_player')
game.automate('machine_player')
```
