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

    @staticmethod
    def __assert_days(when, mon, tue, wed, thu, fri, sat, sun, hour, minute,
            second):
        assert when.monday == mon
        assert when.tuesday == tue
        assert when.wednesday == wed
        assert when.thursday == thu
        assert when.friday == fri
        assert when.saturday == sat
        assert when.sunday == sun
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

    def testTimeOneAsterisk(self):
        print '\n----- testTimeOneAsterisk -----'
        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "20 * 1920 10:11:12")
        self.__assert_time(when, 1920, None, 20, 10, 11, 12)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "April 21, * 12:13:14")
        self.__assert_time(when, None, 4, 21, 12, 13, 14)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "5/22/1923 *:14:15")
        self.__assert_time(when, 1923, 5, 22, None, 14, 15)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "*/23/1924 14:15:16")
        self.__assert_time(when, 1924, None, 23, 14, 15, 16)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "1920-03-20 15:*:17")
        self.__assert_time(when, 1920, 3, 20, 15, None, 17)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "1920-03-20 15:16:*")
        self.__assert_time(when, 1920, 3, 20, 15, 16, None)

    def testTimeMultipleAsterisk(self):
        print '\n----- testTimeMultipleAsterisk -----'
        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "20 * 1920 10:11:*")
        self.__assert_time(when, 1920, None, 20, 10, 11, None)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "* 21, * 12:13:14")
        self.__assert_time(when, None, None, 21, 12, 13, 14)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "5/22/1923 *:14:*")
        self.__assert_time(when, 1923, 5, 22, None, 14, None)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "*/23/1924 *:15:16")
        self.__assert_time(when, 1924, None, 23, None, 15, 16)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime,
                                             "*-*-20 15:*:17")
        self.__assert_time(when, None, None, 20, 15, None, 17)

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

    def testTimeDaysFirst(self):
        print '\n----- testTimeDaysFirst -----'
        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "mondays,TUES 10:11:12")
        self.__assert_days(when=when,
                           mon=True,  tue=True,  wed=False, thu=False,
                           fri=False, sat=False, sun=False,
                           hour=10, minute=11, second=12)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "tuesday, wednesday 12:13:14")
        self.__assert_days(when=when,
                           mon=False, tue=True,  wed=True,  thu=False,
                           fri=False, sat=False, sun=False,
                           hour=12, minute=13, second=14)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "FRI 13:14:15")
        self.__assert_days(when=when,
                           mon=False, tue=False, wed=False, thu=False,
                           fri=True,  sat=False, sun=False,
                           hour=13, minute=14, second=15)

        when = DateTime.WhenFactory.MakeWhen(datetime.datetime, 
                                             "FRI *:15:16")
        self.__assert_days(when=when,
                           mon=False, tue=False, wed=False, thu=False,
                           fri=True,  sat=False, sun=False,
                           hour=None, minute=15, second=16)

        # TODO: Days first


if __name__ == '__main__':
    unittest.main()  # runs all tests
