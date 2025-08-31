'''Unit test role operations on a list of persons'''
from unittest import TestCase

from hundredandten.constants import GameRole, RoundRole
from hundredandten.group import Person, Group


class TestPeopleRoles(TestCase):
    '''Role operations on People unit tests'''

    def test_add_role_with_no_players(self):
        '''Does nothing when adding a role to a player an in empty list'''

        persons = Group([])
        persons.add_role('any', GameRole.ORGANIZER)

        self.assertEqual(0, len(persons))

    def test_add_role_to_player_with_no_roles(self):
        '''Adds a role to a player with no roles'''

        person = Person('id')
        role = GameRole.ORGANIZER
        persons = Group([person])
        persons.add_role(person.identifier, role)

        self.assertEqual(1, len(persons))
        self.assertIn(role, persons[0].roles)

    def test_add_role_to_player_with_existing_roles(self):
        '''Adds a role to a player with existing roles'''

        person = Person('id', {GameRole.PLAYER})
        role = GameRole.ORGANIZER
        persons = Group([person])
        persons.add_role(person.identifier, role)

        self.assertEqual(1, len(persons))
        self.assertLess(1, len(persons[0].roles))
        self.assertIn(role, persons[0].roles)

    def test_remove_role_with_no_players(self):
        '''Does nothing when removing a role from a player an in empty list'''

        persons = Group([])
        persons.remove_role('any', GameRole.ORGANIZER)

        self.assertEqual(0, len(persons))

    def test_remove_role_from_player_with_no_roles(self):
        '''Removes a role from a player with no roles'''

        person = Person('id')
        role = GameRole.ORGANIZER
        persons = Group([person])
        persons.remove_role(person.identifier, role)

        self.assertEqual(1, len(persons))
        self.assertNotIn(role, persons[0].roles)

    def test_remove_role_from_player_with_existing_roles(self):
        '''Removes a role from a player with existing roles'''

        initial_roles = {GameRole.PLAYER, RoundRole.DEALER}
        initial_len = len(initial_roles)
        remove_role = next(iter(initial_roles))
        person = Person('id', initial_roles)
        persons = Group([person])
        persons.remove_role(person.identifier, remove_role)

        self.assertEqual(1, len(persons))
        self.assertEqual(initial_len - 1, len(persons[0].roles))
        self.assertNotIn(remove_role, persons[0].roles)

    def test_swap_role(self):
        '''Swaps a role between players'''

        role = RoundRole.DEALER
        person_one = Person('one', {role})
        person_two = Person('two')
        persons = Group([person_one, person_two])

        self.assertIn(role, persons[0].roles)
        self.assertNotIn(role, persons[1].roles)

        persons.swap_role(person_one.identifier, person_two.identifier, role)

        self.assertEqual(2, len(persons))
        self.assertNotIn(role, persons[0].roles)
        self.assertIn(role, persons[1].roles)
