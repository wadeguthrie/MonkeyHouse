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
        print 'checking %s vs. %r-%r-%r %r:%r:%r' % (when, year, month, day,
                                                     hour, minute, second)
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
        when = DateTime.MomentFactory.MakeMoment("now")

        when = DateTime.MomentFactory.MakeMoment("10:11:12")
        self.__assert_time(when, None, None, None, 10, 11, 12)

        # TODO: am/pm

    def testTimeDateFirst(self):
        print '\n----- testTimeDateFirst -----'
        when = DateTime.MomentFactory.MakeMoment("20 March 1920 10:11:12")
        self.__assert_time(when, 1920, 3, 20, 10, 11, 12)

        when = DateTime.MomentFactory.MakeMoment("April 21, 1922 12:13:14")
        self.__assert_time(when, 1922, 4, 21, 12, 13, 14)

        when = DateTime.MomentFactory.MakeMoment("5/22/1923 13:14:15")
        self.__assert_time(when, 1923, 5, 22, 13, 14, 15)

        when = DateTime.MomentFactory.MakeMoment("23/6/1924 14:15:16")
        self.__assert_time(when, 1924, 6, 23, 14, 15, 16)

        when = DateTime.MomentFactory.MakeMoment("1920-03-20 15:16:17")
        self.__assert_time(when, 1920, 3, 20, 15, 16, 17)

    def testTimeOneAsterisk(self):
        print '\n----- testTimeOneAsterisk -----'
        when = DateTime.MomentFactory.MakeMoment("20 * 1920 10:11:12")
        self.__assert_time(when, 1920, None, 20, 10, 11, 12)

        when = DateTime.MomentFactory.MakeMoment("April 21, * 12:13:14")
        self.__assert_time(when, None, 4, 21, 12, 13, 14)

        when = DateTime.MomentFactory.MakeMoment("5/22/1923 *:14:15")
        self.__assert_time(when, 1923, 5, 22, None, 14, 15)

        when = DateTime.MomentFactory.MakeMoment("*/23/1924 14:15:16")
        self.__assert_time(when, 1924, None, 23, 14, 15, 16)

        when = DateTime.MomentFactory.MakeMoment("1920-03-20 15:*:17")
        self.__assert_time(when, 1920, 3, 20, 15, None, 17)

        when = DateTime.MomentFactory.MakeMoment("1920-03-20 15:16:*")
        self.__assert_time(when, 1920, 3, 20, 15, 16, None)

    def testTimeMultipleAsterisk(self):
        print '\n----- testTimeMultipleAsterisk -----'
        when = DateTime.MomentFactory.MakeMoment("20 * 1920 10:11:*")
        self.__assert_time(when, 1920, None, 20, 10, 11, None)

        when = DateTime.MomentFactory.MakeMoment("* 21, * 12:13:14")
        self.__assert_time(when, None, None, 21, 12, 13, 14)

        when = DateTime.MomentFactory.MakeMoment("5/22/1923 *:14:*")
        self.__assert_time(when, 1923, 5, 22, None, 14, None)

        when = DateTime.MomentFactory.MakeMoment("*/23/1924 *:15:16")
        self.__assert_time(when, 1924, None, 23, None, 15, 16)

        when = DateTime.MomentFactory.MakeMoment("*-*-20 15:*:17")
        self.__assert_time(when, None, None, 20, 15, None, 17)

    def testTimeDateSecond(self):
        print '\n----- testTimeDateSecond -----'
        when = DateTime.MomentFactory.MakeMoment("10:11:12 20 March 1920")
        self.__assert_time(when, 1920, 3, 20, 10, 11, 12)

        when = DateTime.MomentFactory.MakeMoment("12:13:14 April 21, 1922")
        self.__assert_time(when, 1922, 4, 21, 12, 13, 14)

        when = DateTime.MomentFactory.MakeMoment("13:14:15 5/22/1923")
        self.__assert_time(when, 1923, 5, 22, 13, 14, 15)

        when = DateTime.MomentFactory.MakeMoment("14:15:16 23/6/1924")
        self.__assert_time(when, 1924, 6, 23, 14, 15, 16)

        when = DateTime.MomentFactory.MakeMoment("15:16:17 1920-03-20")
        self.__assert_time(when, 1920, 3, 20, 15, 16, 17)

        # swap year/day
        # swap year/month
        # swap day/month

    def testTimeDaysFirst(self):
        print '\n----- testTimeDaysFirst -----'
        when = DateTime.MomentFactory.MakeMoment("mondays,TUES 10:11:12")
        self.__assert_days(when=when,
                           mon=True,  tue=True,  wed=False, thu=False,
                           fri=False, sat=False, sun=False,
                           hour=10, minute=11, second=12)

        when = DateTime.MomentFactory.MakeMoment("tuesday, wednesday 12:13:14")
        self.__assert_days(when=when,
                           mon=False, tue=True,  wed=True,  thu=False,
                           fri=False, sat=False, sun=False,
                           hour=12, minute=13, second=14)

        when = DateTime.MomentFactory.MakeMoment("FRI 13:14:15")
        self.__assert_days(when=when,
                           mon=False, tue=False, wed=False, thu=False,
                           fri=True,  sat=False, sun=False,
                           hour=13, minute=14, second=15)

        when = DateTime.MomentFactory.MakeMoment("sun *:15:16")
        self.__assert_days(when=when,
                           mon=False, tue=False, wed=False, thu=False,
                           fri=False, sat=False, sun=True,
                           hour=None, minute=15, second=16)

    def testTimeDaysSecond(self):
        print '\n----- testTimeDaysSecond -----'
        when = DateTime.MomentFactory.MakeMoment("10:11:12 mondays,TUES")
        self.__assert_days(when=when,
                           mon=True,  tue=True,  wed=False, thu=False,
                           fri=False, sat=False, sun=False,
                           hour=10, minute=11, second=12)

        when = DateTime.MomentFactory.MakeMoment("12:13:14 tuesday, wed")
        self.__assert_days(when=when,
                           mon=False, tue=True,  wed=True,  thu=False,
                           fri=False, sat=False, sun=False,
                           hour=12, minute=13, second=14)

        when = DateTime.MomentFactory.MakeMoment("13:14:15 FRI")
        self.__assert_days(when=when,
                           mon=False, tue=False, wed=False, thu=False,
                           fri=True,  sat=False, sun=False,
                           hour=13, minute=14, second=15)

        when = DateTime.MomentFactory.MakeMoment("*:15:16 sun ")
        self.__assert_days(when=when,
                           mon=False, tue=False, wed=False, thu=False,
                           fri=False, sat=False, sun=True,
                           hour=None, minute=15, second=16)

    def testFirstDateTime(self):
        print '\n----- testFirstDateTime -----'
        # == The result is exactly 'now'.
        print '== one =='
        when = DateTime.MomentFactory.MakeMoment('*-02-* 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2013, 02, 28,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2013, 2, 28, 12, 11, 10)

        # == Carry just up to the year.
        print '== two =='
        when = DateTime.MomentFactory.MakeMoment('*-02-* 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2013, 03, 01,
                                                              12, 00, 10))
        self.__assert_time(next_firing, 2014, 2, 01, 12, 00, 10)

        # == Carry one, deep
        print '== three =='
        when = DateTime.MomentFactory.MakeMoment('*-03-* 11:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2013, 03, 31,
                                                              11, 11, 11))
        self.__assert_time(next_firing, 2013, 3, 31, 11, 12, 10)

        # == Carry multiple places.
        print '== four =='
        when = DateTime.MomentFactory.MakeMoment('*-03-* 11:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2013, 03, 31,
                                                              12, 11, 11))
        # 2013-03-31 12:11:11 - now
        # 2013-03-31 11:11:10 - start
        # ****-03-** 11:**:10 - template
        # 2014-03-01 11:00:10
        self.__assert_time(next_firing, 2014, 3, 1, 11, 0, 10)

        # TODO: check the error paths.

    def testZFirstDayOfWeekTime(self):
        print '\n----- testFirstDayOfWeekTime -----'
        # == The result is exactly 'now'.
        # 11 Mar 2014 is a Tuesday

        print '== one =='
        when = DateTime.MomentFactory.MakeMoment('Mon, Tues 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 11,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 3, 11, 12, 11, 10)

        print '== two =='
        when = DateTime.MomentFactory.MakeMoment('Tues, Thurs 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 11,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 3, 11, 12, 11, 10)

        print '== three =='
        when = DateTime.MomentFactory.MakeMoment('Wed, Sat, Sun 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 11,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 3, 12, 12, 11, 10)

        print '== four =='
        when = DateTime.MomentFactory.MakeMoment('Thurs 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 11,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 3, 13, 12, 11, 10)

        print '== five =='
        when = DateTime.MomentFactory.MakeMoment('Sat, Fri 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 11,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 3, 14, 12, 11, 10)

        print '== six =='
        when = DateTime.MomentFactory.MakeMoment('Saturday 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 11,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 3, 15, 12, 11, 10)

        print '== seven =='
        when = DateTime.MomentFactory.MakeMoment('Monday, Sunday 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 11,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 3, 16, 12, 11, 10)

        print '== eight - crosses a month boundary =='
        # 29 March 2014 is a Saturday
        # 3 April is a Thursday
        when = DateTime.MomentFactory.MakeMoment('Thursday, Friday 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2014, 03, 29,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 4, 3, 12, 11, 10)

        print '== nine - crosses a year boundary =='
        # 30 December 2013 is a Monday
        # 3 January 2014 is a Friday
        when = DateTime.MomentFactory.MakeMoment('Friday 12:*:10')
        next_firing = when.first_occurrence(datetime.datetime(2013, 12, 30,
                                                              12, 11, 10))
        self.__assert_time(next_firing, 2014, 1, 3, 12, 11, 10)


        # TODO: check the error paths.

if __name__ == '__main__':
    unittest.main()  # runs all tests
