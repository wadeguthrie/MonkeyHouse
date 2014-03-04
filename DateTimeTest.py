#! /usr/bin/python

import datetime
import mock
import unittest

import DateTime


class DateTimeTestCase(unittest.TestCase):

    """Tests the MonkeyHouse |Trigger|."""

    def __init__(self, *args, **kwargs):
        """ Initializes the test.

        Just initializes the counter that will be used to mark the entries for
        debugging.

        """
        super(DateTimeTestCase, self).__init__(*args, **kwargs)

    @staticmethod
    def __assert_time(when, year, month, day, hour, minute, second):
        assert when.year == year
        assert when.month == month
        assert when.day == day
        assert when.hour == hour
        assert when.minute == minute
        assert when.second == second

    def testMessageTrigger(self):
        print '\n----- testMessageTrigger -----'
        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, "now")

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, "10:11:12")
        self.__assert_time(when, None, None, None, 10, 11, 12)

        # TODO: Date second

        # 20 March 1920
        # March 20, 1920
        # 03/20/1920 or 20/03/1920
        # 1920-03-20

        # swap year/day
        # swap year/month
        # swap day/month

        # TODO: Days second

        # TODO: Days first

if __name__ == '__main__':
    unittest.main()  # runs all tests
