'''Interact with a list of people'''
from dataclasses import dataclass, field
from typing import Optional, TypeVar

from hundredandten.constants import AnyRole
from hundredandten.deck import Card
from hundredandten.hundred_and_ten_error import HundredAndTenError


@dataclass
class Person:
    '''A class to keep track of a person'''
    identifier: str
    roles: set[AnyRole] = field(default_factory=set, compare=False)
    automate: bool = field(default=False, compare=False)


@dataclass
class Player(Person):
    '''A class to keep track of player information'''
    hand: list[Card] = field(default_factory=list, compare=False)


P = TypeVar('P', bound=Person)


class Group(list[P]):
    '''A list of persons'''

    def update(self, person: P) -> None:
        '''
        Update the provided person within people
        Will raise an error if the person is not in people already
        '''
        index = self.index(person)
        self[index] = person

    def upsert(self, person: P) -> None:
        '''
        Upsert the provided person into people
        '''
        if person in self:
            self.update(person)
        else:
            self.append(person)

    def by_identifier(self, identifier: str) -> Optional[P]:
        '''
        Find a person with the given identifier
        '''
        return next(iter([p for p in self if p.identifier == identifier]), None)

    def by_role(self, role: AnyRole):
        '''
        Find people with the given identifier
        '''
        return type(self)([p for p in self if role in p.roles] or [])

    def find_or_use(self, example: P) -> P:
        '''
        Find a person matching the example or return the example
        If the example has roles, any found person will append those roles
        '''
        person = self.by_identifier(example.identifier) or example
        person.roles = person.roles.union(example.roles)
        return person

    def add_role(self, identifier: str, role: AnyRole) -> None:
        '''
        Add the provided role to the person with the given identifier
        '''
        person = self.by_identifier(identifier)
        if person:
            person.roles.add(role)

    def remove_role(self, identifier: str, role: AnyRole) -> None:
        '''
        Remove the provided role from the person with the given identifier
        '''
        person = self.by_identifier(identifier)
        if person:
            person.roles.discard(role)

    def swap_role(self, source_identifier: str, dest_identifier: str, role: AnyRole) -> None:
        '''
        Swap a role from the source identifier to the destination identifier
        '''
        self.remove_role(source_identifier, role)
        self.add_role(dest_identifier, role)

    def after(self, identifier: str) -> P:
        '''
        Determine the next player after the identified one
        '''
        return self.__offset(identifier, 1)

    def __offset(self, identifier: str, offset: int) -> P:
        '''
        Determine the player sitting the provided distance away from the identified one
        '''
        person = self.by_identifier(identifier)
        if not self or not person:
            raise HundredAndTenError(f'Unable to find person {offset} away from {identifier}.')
        return self[(self.index(person) + offset) % len(self)]
