#! /usr/bin/python

import datetime
import re

"""
This is needed because 'datetime' doesn't allow incomplete dates and times
(needed for time templates in MkyHs).  While I was there, I included an
increment.
"""

class WhenFactory(object):

    # match = re.match('noise:\s*(?P<noise_level>[-0-9]+)\s+dbm', cleaned)
    # if match.groupdict()['noise_level'] is not None:


    time = '(?P<time>[0-9\*]+:[0-9:\.\*]+)'  # Numbers(required),colons(required),period
    days = '(?P<days>[A-Za-z, ]+)'  # Just strings, spaces, and commas (no numbers)
    date = '(?P<date>[^:]*[0-9\*][^:]*)'  # a string w/numbers or a star (no colons)
    just_time = re.compile('^ *' + time + ' *$')
    days_first = re.compile(
            ' *' + days + '[ ,]+' + time  + ' *$')
    days_second = re.compile(
            ' *' + time + '[ ,]+' + days + ' *$')
    date_second = re.compile(
            ' *' + time + '[ ,]+' + date + ' *$')
    date_first = re.compile(
            ' *' + date + '[ ,]+' + time + ' *$')

    @staticmethod
    def MakeWhen(date_time, string):
        print '\tSetTemplate: checking \'%s\'' % string
        increment_string = None

        if not string or re.match('[Nn][Oo][Ww]', string):
            print '-NOW-'
            return DateTime(date_time, date_string=None,
                                       time_string=None,
                                       increment_string=increment_string)

        # Same time, every day
        match = WhenFactory.just_time.match(string)
        if match:
            print 'JUST TIME'
            return DateTime(date_time, date_string=None,
                                       time_string=match.groupdict()['time'],
                                       increment_string=increment_string)

        match = WhenFactory.days_first.match(string)
        if match:
            print  'DAYS FIRST'
            return DayOfWeekTime(date_time,
                                 days_string=match.groupdict()['days'],
                                 time_string=match.groupdict()['time'],
                                 increment_string=increment_string)

        match = WhenFactory.days_second.match(string)
        if match:
            print  'DAYS SECOND'
            return DayOfWeekTime(date_time,
                                 days_string=match.groupdict()['days'],
                                 time_string=match.groupdict()['time'],
                                 increment_string=increment_string)

        match = WhenFactory.date_second.match(string)
        if match:
            print 'DATE SECOND'
            return DateTime(date_time,
                            date_string=match.groupdict()['date'],
                            time_string=match.groupdict()['time'],
                            increment_string=increment_string)

        match = WhenFactory.date_first.match(string)
        if match:
            print 'DATE FIRST'
            return DateTime(date_time,
                            date_string=match.groupdict()['date'],
                            time_string=match.groupdict()['time'],
                            increment_string=increment_string)

        print 'FOUND NOTHING'
        raise ValueError('String %s does not seem to contain a time/date' %
                         string)


class When(object):
    """
    Base class for date/day-of-week/time-of-day classes.  Handles the
    time-of-day since that's common among the children.  Provides some support
    for the children classes.
    """
    # Used for parsing the date.
    ALPHA, NUMBER, SLASH, COMMA, DASH, ASTERISK = range(6)

    def __init__(self, date_time, time_string, increment_string):
        self._date_time = date_time # datetime object, permits mocking.
        self._last_occurrence = None

        # Do the time, here, in the base class since _everything_ needs a
        # time.
        self.second = None
        self.minute = None
        self.hour = None
        # TODO: build increment from increment_string -- +3 months is an
        # interesting one

        print '__time_from_string: starting with \'%s\'' % time_string
        if time_string is not None:
            pieces = time_string.split(':')

            self.hour = None if pieces[0] == '*' else int(pieces[0])
            self.minute = None if pieces[1] == '*' else int(pieces[1])

            if len(pieces) > 2:
                if pieces[2] == '*':
                    self.second = None
                else:
                    pieces = pieces[2].split('.')
                    self.second = int(pieces[0])
            else:
                self.second = 0

        print '__time_from_string: %r:%r:%r' % (self.hour,
                                                self.minute,
                                                self.second)

    def get_next_occurrence(self):
        now = self._datetime.now()
        if self._last_occurrence is None:
            self._last_occurrence = self._first_occurrence(self, now)
        else:
            while self._last_occurrence < now:
                self._last_occurrence = self._add_increment(self)
        return self._last_occurrence


    def _matches(self, input, template):
        """
        input - array of tuple (token, value)
        template - a list of token

        Returns True if each token in input matches the token in the same
        location in template; False, otherwise.  Matches a '*' in the input if
        the template is ALPHA or NUMBER.
        """
        if len(input) != len(template):
            return False
        for i in range(len(template)):
            token, value = input[i]
            if token == self.ASTERISK:
                if template[i] != self.ALPHA and template[i] != self.NUMBER:
                    return False
            elif token != template[i]:
                return False
        return True

class DateTime(When):
    def __init__(self, date_time, date_string, time_string, increment_string):
        """
        If date and time are None, means 'now'
        Convert time and date strings into our internal representation.

        Args:
          date_string  Date in any number of formats.  A '*' may take the
                place of zero or more slots (but, beware -- we assume various
                default positions for day, month, and year based on the format
                and the values in the positions).  Year is expected to be 4
                digits.
        """
        super(DateTime, self).__init__(date_time,
                                       time_string,
                                       increment_string)
        self.day = None
        self.month = None
        self.year = None

        if date_string is None:
            print 'Date: None-None-None'
            return

        # Figure out the format for the date and extract the information.

        scanner=re.Scanner([
          (r'[a-zA-Z]+',    lambda scanner,token:(self.ALPHA, token)),
          (r'[0-9]+',       lambda scanner,token:(self.NUMBER, token)),
          (r'/',            lambda scanner,token:(self.SLASH, token)),
          (r',',            lambda scanner,token:(self.COMMA, token)),
          (r'-',            lambda scanner,token:(self.DASH, token)),
          (r'\*',           lambda scanner,token:(self.ASTERISK, token)),
          (r'\s+', None),   # Skip whitespace.
        ])

        TOKEN, VALUE = range(2) # Indexes into scanner.scan's tokens
        tokens, remainder = scanner.scan(date_string)
        if len(remainder) > 0:
            raise ValueError('String %s has odd character for a date' %
                             date_string)

        # e.g., 20 March 1920
        if self._matches(tokens, (self.NUMBER, self.ALPHA, self.NUMBER)):
            self.day = self._value(tokens[0][VALUE])
            self.month = self._month_from_string(tokens[1][VALUE])
            self.year = self._value(tokens[2][VALUE])

        # e.g., March 20, 1920
        elif self._matches(tokens, (self.ALPHA,    # 0
                                    self.NUMBER,   # 1
                                    self.COMMA,    # 2
                                    self.NUMBER)): # 3
            self.day = self._value(tokens[1][VALUE])
            self.month = self._month_from_string(tokens[0][VALUE])
            self.year = self._value(tokens[3][VALUE])

        # e.g., 03/20/1920 or 20/03/1920
        elif self._matches(tokens, (self.NUMBER,   # 0
                                    self.SLASH,    # 1
                                    self.NUMBER,   # 2
                                    self.SLASH,    # 3
                                    self.NUMBER)): # 4
            # Default to American order: month/day/year and re-arrange if
            # obviously wrong.
            self.day = self._value(tokens[2][VALUE])
            self.month = self._value(tokens[0][VALUE])
            self.year = self._value(tokens[4][VALUE])

        # e.g., 1920-03-20
        elif self._matches(tokens, (self.NUMBER,   # 0
                                    self.DASH,     # 1
                                    self.NUMBER,   # 2
                                    self.DASH,     # 3
                                    self.NUMBER)): # 4
            self.day = self._value(tokens[4][VALUE])
            self.month = self._value(tokens[2][VALUE])
            self.year = self._value(tokens[0][VALUE])

        else:
            raise ValueError('String %s looks insufficiently like ' +
                    'ANY date format.' % date_string)

        print 'First cut: %r-%r-%r' % (self.year, self.month, self.day)

        # Now, re-arrange based on the size of the numbers.
        # See if something else should be the year
        if self.month != None and self.month >= 1000:
            print 'SWAP YEAR %s and MONTH %s' % (self.year, self.month)
            temp = self.year
            self.year = self.month
            self.month = temp
        elif self.day != None and self.day >= 1000:
            print 'SWAP YEAR %s and DAY %s' % (self.year, self.day)
            temp = self.year
            self.year = self.day
            self.day = temp

        # The year is set -- see if the month should be the day.
        if self.month != None and self.month > 12:
            print 'SWAP DAY %s and MONTH %s' % (self.day, self.month)
            temp = self.day
            self.day = self.month
            self.month = temp

        print 'Date: %r-%r-%r' % (self.year, self.month, self.day)


    def _month_from_string(self, string):
        if string == '*':
            return None

        mymonth = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                   'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11,
                   'dec': 12}
        short_month = string[:3].lower()
        if short_month not in mymonth:
            raise ValueError('String %s doesn\'t look like a month name' %
                             string)
        return mymonth[short_month]

    def _value(self, string):
        return None if string == '*' else int(string)


class DayOfWeekTime(When):
    def __init__(self, date_time, days_string, time_string, increment_string):
        """
        days_string is an array of strings, each is a day of the week
        """
        super(DayOfWeekTime, self).__init__(date_time,
                                            time_string,
                                            increment_string)
        days = days_string.split(',')

        self.__day_of_week = {}
        self.__day_of_week['mon'] = False
        self.__day_of_week['tue'] = False
        self.__day_of_week['wed'] = False
        self.__day_of_week['thu'] = False
        self.__day_of_week['fri'] = False
        self.__day_of_week['sat'] = False
        self.__day_of_week['sun'] = False

        for day in days:
            print 'Found day %s' % day
            # Strip whitespace, take the first 3 characters, lower-case them.
            short_day = day.strip()[:3].lower()
            print '\tshortened: \'%s\'', short_day
            if short_day in self.__day_of_week:
                self.__day_of_week[short_day] = True
            else:
                raise ValueError('String %s does not seem to contain day' %
                                 string)

        print 'ALL DAYS RECOGNIZED'

    # The following are largely for tests since the class is expected to be
    # used polymorphically and DateTime doesn't have week days.

    @property
    def monday(self):
        return self.__day_of_week['mon']

    @property
    def tuesday(self):
        return self.__day_of_week['tue']

    @property
    def wednesday(self):
        return self.__day_of_week['wed']

    @property
    def thursday(self):
        return self.__day_of_week['thu']

    @property
    def friday(self):
        return self.__day_of_week['fri']

    @property
    def saturday(self):
        return self.__day_of_week['sat']

    @property
    def sunday(self):
        return self.__day_of_week['sun']

if __name__ == '__main__':
    pass
