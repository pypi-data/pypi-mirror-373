'''Unit test determining the next person within a list of persons'''
from unittest import TestCase

from hundredandten.group import Group, Person
from hundredandten.hundred_and_ten_error import HundredAndTenError


class TestNextPerson(TestCase):
    '''Next Person of People unit tests'''

    def test_after_with_no_players(self):
        '''Finds no player in empty list'''

        persons = Group([])

        self.assertRaises(HundredAndTenError, persons.after, 'any')

    def test_after_with_unknown_player(self):
        '''Finds no player when not in list'''

        persons = Group([Person('1')])

        self.assertRaises(HundredAndTenError, persons.after, persons[0].identifier + 'bad')

    def test_after_with_one_player(self):
        '''Determines the next player in a list of 1'''

        person_one = Person('1')
        persons = Group([person_one])

        self.assertEqual(person_one, persons.after(person_one.identifier))

    def test_after_with_two_players(self):
        '''Determines the next player in a list of 2'''

        person_one = Person('1')
        person_two = Person('2')
        persons = Group([person_one, person_two])

        self.assertEqual(person_two, persons.after(person_one.identifier))
        self.assertEqual(person_one, persons.after(person_two.identifier))

    def test_after_with_three_players(self):
        '''Determines the next player in a list of 3'''

        person_one = Person('1')
        person_two = Person('2')
        person_three = Person('3')

        persons = Group([person_one, person_two, person_three])

        self.assertEqual(person_two, persons.after(person_one.identifier))
        self.assertEqual(person_three, persons.after(person_two.identifier))
        self.assertEqual(person_one, persons.after(person_three.identifier))

    def test_after_with_four_players(self):
        '''Determines the next player in a list of 4'''

        person_one = Person('1')
        person_two = Person('2')
        person_three = Person('3')
        person_four = Person('4')

        persons = Group([person_one, person_two, person_three, person_four])

        self.assertEqual(person_two, persons.after(person_one.identifier))
        self.assertEqual(person_three, persons.after(person_two.identifier))
        self.assertEqual(person_four, persons.after(person_three.identifier))
        self.assertEqual(person_one, persons.after(person_four.identifier))
