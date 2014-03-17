#! /usr/bin/python

"""
This is needed because 'datetime' doesn't allow incomplete dates and times
(needed for time templates in MkyHs).  While I was there, I included an
increment.
"""
import calendar
import datetime
import re

class MomentFactory(object):
    """
    Generates an object of the appropriate Moment sub-class based on a string
    that contains the time, date, and increment value.
    """
    time = '(?P<time>[0-9\*]+:[0-9:\.\*]+)'
    days = '(?P<days>[A-Za-z, ]+)'
    date = '(?P<date>[^:]*[0-9\*][^:]*)'
    inc = ' *(?P<inc>\+[0-9]+ [a-zA-Z]+)?'
    just_time = re.compile('^ *' + time + inc + ' *$')
    days_first = re.compile(
        ' *' + days + '[ ,]+' + time + inc + ' *$')
    days_second = re.compile(
        ' *' + time + inc + '[ ,]+' + days + ' *$')
    date_second = re.compile(
        ' *' + time + inc + '[ ,]+' + date + ' *$')
    date_first = re.compile(
        ' *' + date + '[ ,]+' + time + inc + ' *$')
    now = re.compile(' *[Nn][Oo][Ww]' + inc + ' *$')
    armed = re.compile(' *[Aa][Rr][Mm][Ee][Dd]' + inc + ' *$')
    increment = re.compile(' *' + inc + ' *$')

    @staticmethod
    def make_moment(string):
        """Factory for Moment objects.

        Generates an object of the appropriate Moment sub-class based on a
        string that contains the time, date, and increment value.

        Param:
            - string - contains description of the time and date.

        Returns: object that's a subclass of 'Moment'
        """
        print '\tSetTemplate: checking \'%s\'' % string

        match = False if not string else MomentFactory.now.match(string)
        if not string or match:
            print '-NOW-'
            inc_string = (None if 'inc' not in match.groupdict()
                          else match.groupdict()['inc'])
            return DateTime(date_string=None,
                            time_string=None,
                            increment_string=inc_string)

        match = MomentFactory.increment.match(string)
        if match:
            print 'INCREMENT'
            inc_string = match.groupdict()['inc']
            return DateTime(date_string=None,
                            time_string=None,
                            increment_string=inc_string)

        match = MomentFactory.armed.match(string)
        if match:
            print 'ARMED'
            inc_string = (None if 'inc' not in match.groupdict()
                          else match.groupdict()['inc'])
            return FromArmedTime(increment_string=inc_string)

        # Same time, every day
        match = MomentFactory.just_time.match(string)
        if match:
            print 'JUST TIME'
            inc_string = (None if 'inc' not in match.groupdict()
                          else match.groupdict()['inc'])
            return DateTime(date_string=None,
                            time_string=match.groupdict()['time'],
                            increment_string=inc_string)

        match = MomentFactory.days_first.match(string)
        if match:
            print 'DAYS FIRST'
            inc_string = (None if 'inc' not in match.groupdict()
                          else match.groupdict()['inc'])
            return DayOfWeekTime(days_string=match.groupdict()['days'],
                                 time_string=match.groupdict()['time'],
                                 increment_string=inc_string)

        match = MomentFactory.days_second.match(string)
        if match:
            print 'DAYS SECOND'
            inc_string = (None if 'inc' not in match.groupdict()
                          else match.groupdict()['inc'])
            return DayOfWeekTime(days_string=match.groupdict()['days'],
                                 time_string=match.groupdict()['time'],
                                 increment_string=inc_string)

        match = MomentFactory.date_second.match(string)
        if match:
            print 'DATE SECOND'
            inc_string = (None if 'inc' not in match.groupdict()
                          else match.groupdict()['inc'])
            return DateTime(date_string=match.groupdict()['date'],
                            time_string=match.groupdict()['time'],
                            increment_string=inc_string)

        match = MomentFactory.date_first.match(string)
        if match:
            print 'DATE FIRST'
            inc_string = (None if 'inc' not in match.groupdict()
                          else match.groupdict()['inc'])
            return DateTime(date_string=match.groupdict()['date'],
                            time_string=match.groupdict()['time'],
                            increment_string=inc_string)

        print 'FOUND NOTHING'
        raise ValueError('String %s does not seem to contain a time/date' %
                         string)


class Moment(object):
    """
    Base class for date/day-of-week/time-of-day classes.  Handles the
    time-of-day since that's common among the children.  Provides some support
    for the children classes.
    """
    SECOND, MINUTE, HOUR, DAY, MONTH, YEAR = range(6)
    min_value = [0, 0, 0, 1, 1, 1]
    max_value = [59, 59, 59, 31, 12, 10000]

    # Used for parsing the date.
    ALPHA, NUMBER, SLASH, COMMA, DASH, ASTERISK = range(6)

    def __init__(self, time_string, increment_string):
        self._last_occurrence = None
        self._lastfired = None

        # self.SECOND, .MINUTE, .HOUR, .DAY, .MONTH, and .YEAR
        self._template = [None] * len(self.min_value)
        self._increment = None
        if increment_string is not None:
            units = {'yea': self.YEAR,
                     'mon': self.MONTH,
                     'day': self.DAY,
                     'hou': self.HOUR,
                     'min': self.MINUTE,
                     'sec': self.SECOND}
            pieces = re.match('\+ *([0-9]+) *([a-zA-Z]+)', increment_string)
            count = int(pieces.group(1))
            unit = pieces.group(2)
            short_unit = unit[:3].lower()
            print 'short_unit: \'%s\'' % short_unit
            if short_unit in units:
                self._increment = [0] * len(self.min_value)
                self._increment[units[short_unit]] = count
            else:
                raise ValueError('Increment %s doesn\'t look right' %
                                 increment_string)

        print '__time_from_string: starting with \'%s\'' % time_string
        if time_string is not None:
            pieces = time_string.split(':')

            self._template[self.HOUR] = (None if pieces[0] == '*'
                                         else int(pieces[0]))
            self._template[self.MINUTE] = (None if pieces[1] == '*'
                                           else int(pieces[1]))

            if len(pieces) > 2:
                if pieces[2] == '*':
                    self._template[self.SECOND] = None
                else:
                    pieces = pieces[2].split('.')
                    self._template[self.SECOND] = int(pieces[0])
            else:
                self._template[self.SECOND] = 0

        print '__time_from_string: %r:%r:%r' % (self._template[self.HOUR],
                                                self._template[self.MINUTE],
                                                self._template[self.SECOND])

    def _first_occurrence(self, datetime_now):
        """
        datetime_now - datetime object.
        returns - datetime object.
        """

        now = [None, None, None, None, None, None]
        now[self.YEAR] = datetime_now.year
        now[self.MONTH] = datetime_now.month
        now[self.DAY] = datetime_now.day
        now[self.HOUR] = datetime_now.hour
        now[self.MINUTE] = datetime_now.minute
        now[self.SECOND] = datetime_now.second
        print 'Now:      %d-%d-%d %02d:%02d:%02d' % (now[self.YEAR],
                                                     now[self.MONTH],
                                                     now[self.DAY],
                                                     now[self.HOUR],
                                                     now[self.MINUTE],
                                                     now[self.SECOND])
        print 'Template: %r' % self
        self._lastfired = self._last_fired_from_template(now)
        print 'Start:    %d-%d-%d %02d:%02d:%02d' % (
            self._lastfired[self.YEAR],
            self._lastfired[self.MONTH],
            self._lastfired[self.DAY],
            self._lastfired[self.HOUR],
            self._lastfired[self.MINUTE],
            self._lastfired[self.SECOND])
        # Go from year to second:
        #  - if it's < now, increment the next '*' above &
        #    minimize every '*' below -- you're done
        #  - if it's == now, keep going
        #  - if it's > now, we're good -- you're done

        # What's the last day of the current month?
        self.max_value[self.DAY] = calendar.monthrange(
            self._lastfired[self.YEAR], self._lastfired[self.MONTH])[1]
        previous_star = []  # Keep track of the '*' values in the _template.
        found = False  # Did we find a value less than 'now'?
        # Examining from year down to second.
        for i in reversed(range(len(self._lastfired))):
            # print 'template[%d] == %r' % (i, self._template[i])
            if self._template[i] is None:
                # print '\t\'*\', append to previous_star'
                previous_star.append(i)

            # If we'd already found a moment less than 'now', set all
            # future '*' values to their minimum.
            if found:
                if self._template[i] is None:
                    self._lastfired[i] = self.min_value[i]
            elif self._lastfired[i] < now[i]:
                #print '\tnext-fired[%d] (%d) < now (%d)' % (i,
                #        self._lastfired[i], now[i])
                found = True
                # Increment the next highest '*'.  If it's already maxed-out
                # (say, the month is currently 'December', then minimize it
                # and incement the _next_ highest.
                #print '\t\tprevious_star:%r' % previous_star
                if not previous_star:
                    print ('(no previous_star) No future times match ' +
                           'the template')
                    return None
                star = previous_star.pop()
                while self._lastfired[star] >= self.max_value[star]:
                    #print 'lastfired[%d] (%d) >= max_value[%d] (%d)' % (
                    #    star, self._lastfired[star], star,
                    #    self.max_value[star])

                    self._lastfired[star] = self.min_value[star]
                    if not previous_star:
                        print ('(ran out of previous star) No future ' +
                               'times match the template')
                        return None
                    star = previous_star.pop()
                self._lastfired[star] += 1
            # If we've found a _future_ value, then we're done.
            elif self._lastfired[i] > now[i]:
                #print '\tnext-fired[%d] (%d) > now (%d)' % (i,
                #        self._lastfired[i], now[i])
                break
            #else:
            #    print '\tnext-fired[%d] (%d) == now (%d)' % (i,
            #            self._lastfired[i], now[i])

        result = datetime.datetime(self._lastfired[self.YEAR],
                                   self._lastfired[self.MONTH],
                                   self._lastfired[self.DAY],
                                   self._lastfired[self.HOUR],
                                   self._lastfired[self.MINUTE],
                                   self._lastfired[self.SECOND])
        print 'Result:   %s' % result.__str__()
        return result

    def _last_fired_from_template(self, now):
        """Very basic value that matches the object's template for now

        Fills-in missing part of the template with values from |now|.  Doesn't
        worry about exceeding maxima for the various slots since this is
        called by _first_occurrence which addresses that.

        Params:
            - now - the current time in the form of an array (one element,
                each, for year, month, etc.)

        Returns: filled-in template value in the form of an array (one
        element, each, for year, month, etc.)
        """
        return None

    def _do_increment(self):
        """Increment the time."""
        if self._lastfired is None or self._increment is None:
            return None

        print 'Start:    %d-%d-%d %02d:%02d:%02d' % (
            self._lastfired[self.YEAR],
            self._lastfired[self.MONTH],
            self._lastfired[self.DAY],
            self._lastfired[self.HOUR],
            self._lastfired[self.MINUTE],
            self._lastfired[self.SECOND])

        # Add the increment.  Save the pre-carried version as 'last_fired' but
        # put the current firing time as 'firing_time' and carry that value.
        # This allows 1 month to be added to 30 January (and that result to be
        # rounded up to 2 March) and then another month to be added (and
        # _that_ result to be rounded up to 30 March).
        print 'Increment:%d-%d-%d %02d:%02d:%02d' % (
            self._increment[self.YEAR],
            self._increment[self.MONTH],
            self._increment[self.DAY],
            self._increment[self.HOUR],
            self._increment[self.MINUTE],
            self._increment[self.SECOND])
        for i in range(len(self._increment)):
            self._lastfired[i] += self._increment[i]
        firing_time = self._lastfired * 1  # Copies the list

        # Fix any overflows.
        self._carry_the_minute(firing_time)

        # Build a datetime object and return it.
        return datetime.datetime(firing_time[self.YEAR],
                                 firing_time[self.MONTH],
                                 firing_time[self.DAY],
                                 firing_time[self.HOUR],
                                 firing_time[self.MINUTE],
                                 firing_time[self.SECOND])

    def get_next_occurrence(self, now):
        """Builds time after 'now' that matches the template."""
        if self._lastfired is None or self._increment is None:
            candidate = self._first_occurrence(now)
        else:
            candidate = self._do_increment()
            while candidate < now:
                candidate = self._do_increment()
        return candidate

    def _matches(self, token_value, template):
        """
        token_value - array of tuple (token, value)
        template - a list of token

        Returns True if each token in token_value matches the token in the
        same location in template; False, otherwise.  Matches a '*' in the
        input if the template is ALPHA or NUMBER.
        """
        if len(token_value) != len(template):
            return False
        for i in range(len(template)):
            token, unused = token_value[i]
            if token == self.ASTERISK:
                if template[i] != self.ALPHA and template[i] != self.NUMBER:
                    return False
            elif token != template[i]:
                return False
        return True

    @staticmethod
    def _carry_the_minute(moment):
        """
        Well, it's really 'carry_the_second_and_the_minute_and_...'
        """
        Moment.max_value[Moment.DAY] = calendar.monthrange(
            moment[Moment.YEAR], moment[Moment.MONTH])[1]
        found_one = True  # Just for the first time, through.
        # Look, from second to year, for values that exceed their maximum.
        # When you find one, subtract out the max value and increment the next
        # higher item.  For example, if your month is 13, subtract 12 and add
        # one to the year.
        #
        # May have to go through a few times when changing month or year
        # changes the number of days in a month.

        units = {Moment.YEAR: 'year',
                 Moment.MONTH: 'month',
                 Moment.DAY: 'day',
                 Moment.HOUR: 'hour',
                 Moment.MINUTE: 'minute',
                 Moment.SECOND: 'second'}
        while found_one:
            found_one = False
            for i in range(len(moment)):
                while moment[i] > Moment.max_value[i]:
                    found_one = True
                    subtract = Moment.max_value[i] + (
                        1 if (Moment.min_value[i] == 0) else 0)
                    print '%s is %d: minus %d and %s+1 gets %d' % (
                        units[i], moment[i], subtract, units[i+1],
                        moment[i+1]+1)
                    moment[i] -= subtract
                    moment[i+1] += 1
        print 'all carried: ', moment

    @property
    def second(self):
        """Template value for |second|."""
        return self._template[self.SECOND]

    @property
    def minute(self):
        """Template value for |minute|."""
        return self._template[self.MINUTE]

    @property
    def hour(self):
        """Template value for |hour|."""
        return self._template[self.HOUR]


class DateTime(Moment):
    """Moment sub-class composed of date and time."""
    TOKEN, VALUE = range(2)  # Indexes into scanner.scan's tokens
    def __init__(self, date_string, time_string, increment_string):
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
        super(DateTime, self).__init__(time_string,
                                       increment_string)
        if date_string is None:
            print 'Date: None-None-None'
            return

        # Figure out the format for the date and extract the information.

        scanner = re.Scanner([
            (r'[a-zA-Z]+', lambda scanner, token:(self.ALPHA, token)),
            (r'[0-9]+', lambda scanner, token:(self.NUMBER, token)),
            (r'/', lambda scanner, token:(self.SLASH, token)),
            (r',', lambda scanner, token:(self.COMMA, token)),
            (r'-', lambda scanner, token:(self.DASH, token)),
            (r'\*', lambda scanner, token:(self.ASTERISK, token)),
            (r'\s+', None),   # Skip whitespace.
        ])

        tokens, remainder = scanner.scan(date_string)
        if len(remainder) > 0:
            raise ValueError('String %s has odd character for a date' %
                             date_string)

        # e.g., 20 March 1920
        if self._matches(tokens, (self.NUMBER, self.ALPHA, self.NUMBER)):
            self._template[self.DAY] = self._value(tokens[0][self.VALUE])
            self._template[self.MONTH] = self._month_from_string(
                tokens[1][self.VALUE])
            self._template[self.YEAR] = self._value(tokens[2][self.VALUE])

        # e.g., March 20, 1920
        elif self._matches(tokens, (self.ALPHA,     # 0
                                    self.NUMBER,    # 1
                                    self.COMMA,     # 2
                                    self.NUMBER)):  # 3
            self._template[self.DAY] = self._value(tokens[1][self.VALUE])
            self._template[self.MONTH] = self._month_from_string(
                tokens[0][self.VALUE])
            self._template[self.YEAR] = self._value(tokens[3][self.VALUE])

        # e.g., 03/20/1920 or 20/03/1920
        elif self._matches(tokens, (self.NUMBER,    # 0
                                    self.SLASH,     # 1
                                    self.NUMBER,    # 2
                                    self.SLASH,     # 3
                                    self.NUMBER)):  # 4
            # Default to American order: month/day/year and re-arrange if
            # obviously wrong.
            self._template[self.DAY] = self._value(tokens[2][self.VALUE])
            self._template[self.MONTH] = self._value(tokens[0][self.VALUE])
            self._template[self.YEAR] = self._value(tokens[4][self.VALUE])

        # e.g., 1920-03-20
        elif self._matches(tokens, (self.NUMBER,    # 0
                                    self.DASH,      # 1
                                    self.NUMBER,    # 2
                                    self.DASH,      # 3
                                    self.NUMBER)):  # 4
            self._template[self.DAY] = self._value(tokens[4][self.VALUE])
            self._template[self.MONTH] = self._value(tokens[2][self.VALUE])
            self._template[self.YEAR] = self._value(tokens[0][self.VALUE])

        else:
            raise ValueError('String %s looks insufficiently like ' +
                             'ANY date format.' % date_string)

        print 'First cut: %r-%r-%r' % (self._template[self.YEAR],
                                       self._template[self.MONTH],
                                       self._template[self.DAY])

        # Now, re-arrange based on the size of the numbers.
        # See if something else should be the year
        if (self._template[self.MONTH] is not None and
                self._template[self.MONTH] >= 1000):
            print 'SWAP YEAR %s and MONTH %s' % (self._template[self.YEAR],
                                                 self._template[self.MONTH])
            temp = self._template[self.YEAR]
            self._template[self.YEAR] = self._template[self.MONTH]
            self._template[self.MONTH] = temp
        elif (self._template[self.DAY] is not None and
                self._template[self.DAY] >= 1000):
            print 'SWAP YEAR %s and DAY %s' % (self._template[self.YEAR],
                                               self._template[self.DAY])
            temp = self._template[self.YEAR]
            self._template[self.YEAR] = self._template[self.DAY]
            self._template[self.DAY] = temp

        # The year is set -- see if the month should be the day.
        if (self._template[self.MONTH] is not None and
                self._template[self.MONTH] > 12):
            print 'SWAP DAY %s and MONTH %s' % (self._template[self.DAY],
                                                self._template[self.MONTH])
            temp = self._template[self.DAY]
            self._template[self.DAY] = self._template[self.MONTH]
            self._template[self.MONTH] = temp

        print 'Date: %r-%r-%r' % (self._template[self.YEAR],
                                  self._template[self.MONTH],
                                  self._template[self.DAY])

    def __repr__(self):
        return '%s-%s-%s %s:%s:%s' % (
            '*' if self._template[self.YEAR] is None else str(
                self._template[self.YEAR]),
            '*' if self._template[self.MONTH] is None else str(
                self._template[self.MONTH]),
            '*' if self._template[self.DAY] is None else str(
                self._template[self.DAY]),
            '*' if self._template[self.HOUR] is None else str(
                self._template[self.HOUR]),
            '*' if self._template[self.MINUTE] is None else str(
                self._template[self.MINUTE]),
            '*' if self._template[self.SECOND] is None else str(
                self._template[self.SECOND]))

    @staticmethod
    def _month_from_string(string):
        """Returns a month number matching the month in |string|."""
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

    @staticmethod
    def _value(string):
        """ Value of a string used in instantiation.
        """
        return None if string == '*' else int(string)

    def _last_fired_from_template(self, now):
        """Returns template with '*' values filled-in by |now|."""
        lastfired = []
        for i in range(len(now)):
            lastfired.append(now[i] if self._template[i] is None else
                             self._template[i])
        return lastfired

    @property
    def day(self):
        """Template value for |day|."""
        return self._template[self.DAY]

    @property
    def month(self):
        """Template value for |month|."""
        return self._template[self.MONTH]

    @property
    def year(self):
        """Template value for |year|."""
        return self._template[self.YEAR]


class FromArmedTime(DateTime):
    """
    This is _just_ like a DateTime (now) except that _do_increment starts
    from the time it's called rather than from the last time it was called.
    """
    def __init__(self, increment_string):
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
        super(FromArmedTime, self).__init__(
            date_string=None, time_string=None,
            increment_string=increment_string)

    def get_next_occurrence(self, datetime_now):
        """Builds time after 'now' that matches the template.

        Param:
            - datetime_now - datetime object that contains the value for now.

        Returns: filled-in template, with overflows addressed, as a 'datetime'
        object.
        """
        firing_time = [None] * 6
        firing_time[self.YEAR] = datetime_now.year
        firing_time[self.MONTH] = datetime_now.month
        firing_time[self.DAY] = datetime_now.day
        firing_time[self.HOUR] = datetime_now.hour
        firing_time[self.MINUTE] = datetime_now.minute
        firing_time[self.SECOND] = datetime_now.second

        print 'Start:    %d-%d-%d %02d:%02d:%02d' % (firing_time[self.YEAR],
                                                     firing_time[self.MONTH],
                                                     firing_time[self.DAY],
                                                     firing_time[self.HOUR],
                                                     firing_time[self.MINUTE],
                                                     firing_time[self.SECOND])

        print 'Increment:%d-%d-%d %02d:%02d:%02d' % (
            self._increment[self.YEAR],
            self._increment[self.MONTH],
            self._increment[self.DAY],
            self._increment[self.HOUR],
            self._increment[self.MINUTE],
            self._increment[self.SECOND])

        # Add the increment
        for i in range(len(self._increment)):
            firing_time[i] += self._increment[i]

        # Fix any overflows.
        self._carry_the_minute(firing_time)

        # Build a datetime object and return it.
        return datetime.datetime(firing_time[self.YEAR],
                                 firing_time[self.MONTH],
                                 firing_time[self.DAY],
                                 firing_time[self.HOUR],
                                 firing_time[self.MINUTE],
                                 firing_time[self.SECOND])


class DayOfWeekTime(Moment):
    """Moment sub-class composed of day of the week and time."""
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)
    __day_of_week = {'mon': MONDAY, 'tue': TUESDAY, 'wed': WEDNESDAY,
                     'thu': THURSDAY, 'fri': FRIDAY, 'sat': SATURDAY,
                     'sun': SUNDAY}

    def __init__(self, days_string, time_string, increment_string):
        """
        days_string is an array of strings, each is a day of the week
        """
        super(DayOfWeekTime, self).__init__(time_string,
                                            increment_string)
        days = days_string.split(',')

        self.__valid_day = [False, False, False, False, False, False, False]

        for day in days:
            print 'Found day %s' % day
            # Strip whitespace, take the first 3 characters, lower-case them.
            short_day = day.strip()[:3].lower()
            print '\tshortened: \'%s\'' % short_day
            if short_day in self.__day_of_week:
                self.__valid_day[self.__day_of_week[short_day]] = True
            else:
                raise ValueError('String %s does not seem to contain day' %
                                 days_string)

        print 'ALL DAYS RECOGNIZED'

    # The following are largely for tests since the class is expected to be
    # used polymorphically and DateTime doesn't have week days.

    def __repr__(self):
        return '%s%s%s%s%s%s%s %s:%s:%s' % (
            'Mon, ' if self.__valid_day[self.MONDAY] else '',
            'Tues, ' if self.__valid_day[self.TUESDAY] else '',
            'Wed, ' if self.__valid_day[self.WEDNESDAY] else '',
            'Thur, ' if self.__valid_day[self.THURSDAY] else '',
            'Fri, ' if self.__valid_day[self.FRIDAY] else '',
            'Sat, ' if self.__valid_day[self.SATURDAY] else '',
            'Sun, ' if self.__valid_day[self.SUNDAY] else '',
            '*' if self._template[self.HOUR] is None else str(
                self._template[self.HOUR]),
            '*' if self._template[self.MINUTE] is None else str(
                self._template[self.MINUTE]),
            '*' if self._template[self.SECOND] is None else str(
                self._template[self.SECOND]))

    @property
    def monday(self):
        """Template value for 'Monday'."""
        return self.__valid_day[self.MONDAY]

    @property
    def tuesday(self):
        """Template value for 'Tuesday'."""
        return self.__valid_day[self.TUESDAY]

    @property
    def wednesday(self):
        """Template value for 'Wednesday'."""
        return self.__valid_day[self.WEDNESDAY]

    @property
    def thursday(self):
        """Template value for 'Thursday'."""
        return self.__valid_day[self.THURSDAY]

    @property
    def friday(self):
        """Template value for 'Friday'."""
        return self.__valid_day[self.FRIDAY]

    @property
    def saturday(self):
        """Template value for 'Saturday'."""
        return self.__valid_day[self.SATURDAY]

    @property
    def sunday(self):
        """Template value for 'Sunday'."""
        return self.__valid_day[self.SUNDAY]

    def _last_fired_from_template(self, now):
        """Returns template with '*' values filled-in by |now|.
        
        It's expected that day, month, and year will be 'None' for the
        DayOfWeekTime class.  That's OK.
        """
        lastfired = []
        for i in range(len(now)):
            lastfired.append(now[i] if self._template[i] is None else
                             self._template[i])

        # What day is today.
        weekday = calendar.weekday(lastfired[self.YEAR],
                                   lastfired[self.MONTH],
                                   lastfired[self.DAY])

        # Search (starting with 'now') for a valid day.
        for i in range(len(self.__valid_day)):
            j = (i + weekday) % len(self.__valid_day)
            if self.__valid_day[j]:
                lastfired[self.DAY] += i
                # If we had to move the day forward, minimize the '*' time
                # values.
                if i != 0:
                    if self._template[self.HOUR] is None:
                        lastfired[self.HOUR] = self.min_value[self.HOUR]
                    if self._template[self.MINUTE] is None:
                        lastfired[self.MINUTE] = self.min_value[self.MINUTE]
                    if self._template[self.SECOND] is None:
                        lastfired[self.SECOND] = self.min_value[self.SECOND]
                self._carry_the_minute(lastfired)
                return lastfired

        raise ValueError('No days selected for WeekDayTime')


if __name__ == '__main__':
    pass
