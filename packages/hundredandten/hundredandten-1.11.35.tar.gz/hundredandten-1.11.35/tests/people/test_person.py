'''Person unit tests'''
from unittest import TestCase

from hundredandten.constants import CardNumber, GameRole, SelectableSuit
from hundredandten.deck import Card
from hundredandten.group import Person, Player


class TestPerson(TestCase):
    '''Person unit tests'''

    def test_persons_equal_by_identifier_only(self):
        '''When checking if persons are equal, only the identifier matters'''
        identifier = "1"
        self.assertEqual(Person(identifier), Person(identifier, {GameRole.INVITEE}))
        self.assertNotEqual(Person('one'), Person('two'))

    def test_players_equal_by_identifier_only(self):
        '''When checking if players are equal, only the identifier matters'''
        identifier = "1"
        self.assertEqual(
            Player(identifier),
            Player(
                identifier, {GameRole.INVITEE},
                hand=[Card(CardNumber.ACE, SelectableSuit.CLUBS)]))
        self.assertNotEqual(Player('one'), Player('two'))
