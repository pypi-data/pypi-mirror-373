'''Test to ensure bids are compared properly'''
from unittest import TestCase

from hundredandten.actions import Bid
from hundredandten.constants import BidAmount


class TestBidComparison(TestCase):
    '''Unit tests for comparing bids'''

    def test_equals(self):
        '''Bids are equal by the amount'''
        self.assertTrue(Bid('1', BidAmount.FIFTEEN) == Bid('2', BidAmount.FIFTEEN))
        self.assertFalse(Bid('1', BidAmount.FIFTEEN) == Bid('1', BidAmount.TWENTY))

    def test_not_equals(self):
        '''Bids are not equal by the amount'''
        self.assertFalse(Bid('1', BidAmount.FIFTEEN) != Bid('2', BidAmount.FIFTEEN))
        self.assertTrue(Bid('1', BidAmount.FIFTEEN) != Bid('1', BidAmount.TWENTY))

    def test_less_than(self):
        '''Bids are less than by the amount'''
        self.assertFalse(Bid('1', BidAmount.TWENTY) < Bid('1', BidAmount.FIFTEEN))
        self.assertFalse(Bid('1', BidAmount.FIFTEEN) < Bid('2', BidAmount.FIFTEEN))
        self.assertTrue(Bid('1', BidAmount.FIFTEEN) < Bid('1', BidAmount.TWENTY))

    def test_less_than_equal(self):
        '''Bids are less than or equal by the amount'''
        self.assertFalse(Bid('1', BidAmount.TWENTY) <= Bid('1', BidAmount.FIFTEEN))
        self.assertTrue(Bid('1', BidAmount.FIFTEEN) <= Bid('2', BidAmount.FIFTEEN))
        self.assertTrue(Bid('1', BidAmount.FIFTEEN) <= Bid('1', BidAmount.TWENTY))

    def test_greater_than(self):
        '''Bids are greater than by the amount'''
        self.assertTrue(Bid('1', BidAmount.TWENTY) > Bid('1', BidAmount.FIFTEEN))
        self.assertFalse(Bid('1', BidAmount.FIFTEEN) > Bid('2', BidAmount.FIFTEEN))
        self.assertFalse(Bid('1', BidAmount.FIFTEEN) > Bid('1', BidAmount.TWENTY))

    def test_greater_than_equal(self):
        '''Bids are greater than or equal by the amount'''
        self.assertTrue(Bid('1', BidAmount.TWENTY) >= Bid('1', BidAmount.FIFTEEN))
        self.assertTrue(Bid('1', BidAmount.FIFTEEN) >= Bid('2', BidAmount.FIFTEEN))
        self.assertFalse(Bid('1', BidAmount.FIFTEEN) >= Bid('1', BidAmount.TWENTY))

    def test_truthy(self):
        '''Pass bids are falsy, others are not'''
        self.assertTrue(Bid('1', BidAmount.TWENTY))
        self.assertFalse(Bid('1', BidAmount.PASS))
