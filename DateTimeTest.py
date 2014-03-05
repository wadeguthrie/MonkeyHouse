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

    def testTimeTruncated(self):
        print '\n----- testTimeTruncated -----'
        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, "now")

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, "10:11:12")
        self.__assert_time(when, None, None, None, 10, 11, 12)

        # TODO: am/pm

    def testTimeDateFirst(self):
        print '\n----- testTimeDateFirst -----'
        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "20 March 1920 10:11:12")
        self.__assert_time(when, 1920, 3, 20, 10, 11, 12)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "April 21, 1922 12:13:14")
        self.__assert_time(when, 1922, 4, 21, 12, 13, 14)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "5/22/1923 13:14:15")
        self.__assert_time(when, 1923, 5, 22, 13, 14, 15)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "23/6/1924 14:15:16")
        self.__assert_time(when, 1924, 6, 23, 14, 15, 16)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "1920-03-20 15:16:17")
        self.__assert_time(when, 1920, 3, 20, 15, 16, 17)


    def testTimeDateSecond(self):
        print '\n----- testTimeDateSecond -----'
        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "10:11:12 20 March 1920")
        self.__assert_time(when, 1920, 3, 20, 10, 11, 12)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "12:13:14 April 21, 1922")
        self.__assert_time(when, 1922, 4, 21, 12, 13, 14)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "13:14:15 5/22/1923")
        self.__assert_time(when, 1923, 5, 22, 13, 14, 15)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "14:15:16 23/6/1924")
        self.__assert_time(when, 1924, 6, 23, 14, 15, 16)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "15:16:17 1920-03-20")
        self.__assert_time(when, 1920, 3, 20, 15, 16, 17)

        # swap year/day
        # swap year/month
        # swap day/month

        # TODO: Days second

        # TODO: Days first

        # TODO: '*'

if __name__ == '__main__':
    unittest.main()  # runs all tests
