#! /usr/bin/python

import calendar
import datetime
import re

"""
This is needed because 'datetime' doesn't allow incomplete dates and times
(needed for time templates in MkyHs).  While I was there, I included an
increment.
"""

class MomentFactory(object):

    # match = re.match('noise:\s*(?P<noise_level>[-0-9]+)\s+dbm', cleaned)
    # if match.groupdict()['noise_level'] is not None:

    # TODO:
    # inc by itself is relative to the arming time
    # time+inc is relative to time

    time = '(?P<time>[0-9\*]+:[0-9:\.\*]+)'  # Numbers(required),colons(required),period
    days = '(?P<days>[A-Za-z, ]+)'  # Just strings, spaces, and commas (no numbers)
    date = '(?P<date>[^:]*[0-9\*][^:]*)'  # a string w/numbers or a star (no colons)
    inc = ' *(?P<inc>\+[0-9]+ [a-zA-Z]+)?'
    just_time = re.compile('^ *' + time + inc + ' *$')
    days_first = re.compile(
            ' *' + days + '[ ,]+' + time  + inc + ' *$')
    days_second = re.compile(
            ' *' + time + inc + '[ ,]+' + days + ' *$')
    date_second = re.compile(
            ' *' + time + inc + '[ ,]+' + date + ' *$')
    date_first = re.compile(
            ' *' + date + '[ ,]+' + time + inc + ' *$')

    @staticmethod
    def MakeMoment(string):
        print '\tSetTemplate: checking \'%s\'' % string
        increment_string = None

        # TODO: 'FromArmed + <increment>'
        if not string or re.match('[Nn][Oo][Ww]', string):
            print '-NOW-'
            return DateTime(date_string=None,
                            time_string=None,
                            increment_string=None)

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
            print  'DAYS FIRST'
            inc_string = (None if 'inc' not in match.groupdict()
                               else match.groupdict()['inc'])
            return DayOfWeekTime(days_string=match.groupdict()['days'],
                                 time_string=match.groupdict()['time'],
                                 increment_string=inc_string)

        match = MomentFactory.days_second.match(string)
        if match:
            print  'DAYS SECOND'
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
    SECOND, MINUTE, HOUR = range(3)
    min_value = [0, 0, 0]
    max_value = [23, 59, 59]
    # Used for parsing the date.
    ALPHA, NUMBER, SLASH, COMMA, DASH, ASTERISK = range(6)

    def __init__(self, time_string, increment_string):
        self._last_occurrence = None
        self._lastfired = None

        # Do the time, here, in the base class since _everything_ needs a
        # time.
        self._template = [None, None, None]  # self.SECOND, .MINUTE, and .HOUR
        # TODO: build increment from increment_string -- +3 months is an
        # interesting one

        print '__time_from_string: starting with \'%s\'' % time_string
        if time_string is not None:
            pieces = time_string.split(':')

            self._template[self.HOUR] = None if pieces[0] == '*' else int(pieces[0])
            self._template[self.MINUTE] = None if pieces[1] == '*' else int(pieces[1])

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

    def _do_increment(self):
        if self._lastfired is None:
            None

        # TODO: first firing should: self._lastfired = []

        # Add the increment.
        # TODO: _lastfired should be an array instead of a dict
        for i in range(len(self._increment)):
            self._lastfired[i] += self._increment[i]

        # Fix any overflows.
        self._carry_the_minute(self._lastfired)

        # Build a datetime object and return it.
        return DateTime.datetime.datetime(self._lastfired[self.YEAR],
                                          self._lastfired[self.MONTH],
                                          self._lastfired[self.DAY],
                                          self._lastfired[self.HOUR],
                                          self._lastfired[self.MINUTE],
                                          self._lastfired[self.SECOND])


    def get_next_occurrence(self):
        now = self._datetime.now()
        if self._lastfired is None:
            candidate = self._first_occurrence(now)
        else:
            candidate = self._do_increment()
            while candidate < now:
                candidate = self._do_increment()
        return candidate


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

    @staticmethod
    def _carry_the_minute(moment):
        """
        Well, it's really 'carry_the_second_and_the_minute_and_...'
        """
        self.max_value[self.DAY] = calendar.monthrange(
                moment[self.YEAR], moment[self.MONTH])[1]
        found_one = True  # Just for the first time, through.
        # Look, from second to year, for values that exceed their maximum.
        # When you find one, subtract out the max value and increment the next
        # higher item.  For example, if your month is 13, subtract 12 and add
        # one to the year.
        #
        # May have to go through a few times when changing month or year
        # changes the number of days in a month.
        while found_one:
            found_one = False
            for i in range(len(moment)):
                while moment[i] > self.max_value[i]:
                    found_one = True
                    moment[i] -= self.max_value[i]
                    moment[i+1] += 1

    @property
    def second(self):
        return self._template[self.SECOND]

    @property
    def minute(self):
        return self._template[self.MINUTE]

    @property
    def hour(self):
        return self._template[self.HOUR]

class DateTime(Moment):
    DAY, MONTH, YEAR = range(3, 6)  # Leave room for SECOND, MINUTE, HOUR
    min_value = Moment.min_value + [1, 1, 1]
    max_value = Moment.max_value + [31, 12, 10000] # Recalculate max days in month.
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
        # Adding date stuff to the pre-existing time stuff
        self._template.extend((None, None, None)) # self.DAY, .MONTH, & .YEAR

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
            self._template[self.DAY] = self._value(tokens[0][VALUE])
            self._template[self.MONTH] = self._month_from_string(tokens[1][VALUE])
            self._template[self.YEAR] = self._value(tokens[2][VALUE])

        # e.g., March 20, 1920
        elif self._matches(tokens, (self.ALPHA,    # 0
                                    self.NUMBER,   # 1
                                    self.COMMA,    # 2
                                    self.NUMBER)): # 3
            self._template[self.DAY] = self._value(tokens[1][VALUE])
            self._template[self.MONTH] = self._month_from_string(tokens[0][VALUE])
            self._template[self.YEAR] = self._value(tokens[3][VALUE])

        # e.g., 03/20/1920 or 20/03/1920
        elif self._matches(tokens, (self.NUMBER,   # 0
                                    self.SLASH,    # 1
                                    self.NUMBER,   # 2
                                    self.SLASH,    # 3
                                    self.NUMBER)): # 4
            # Default to American order: month/day/year and re-arrange if
            # obviously wrong.
            self._template[self.DAY] = self._value(tokens[2][VALUE])
            self._template[self.MONTH] = self._value(tokens[0][VALUE])
            self._template[self.YEAR] = self._value(tokens[4][VALUE])

        # e.g., 1920-03-20
        elif self._matches(tokens, (self.NUMBER,   # 0
                                    self.DASH,     # 1
                                    self.NUMBER,   # 2
                                    self.DASH,     # 3
                                    self.NUMBER)): # 4
            self._template[self.DAY] = self._value(tokens[4][VALUE])
            self._template[self.MONTH] = self._value(tokens[2][VALUE])
            self._template[self.YEAR] = self._value(tokens[0][VALUE])

        else:
            raise ValueError('String %s looks insufficiently like ' +
                    'ANY date format.' % date_string)

        print 'First cut: %r-%r-%r' % (self._template[self.YEAR], self._template[self.MONTH],
                self._template[self.DAY])

        # Now, re-arrange based on the size of the numbers.
        # See if something else should be the year
        if self._template[self.MONTH] != None and self._template[self.MONTH] >= 1000:
            print 'SWAP YEAR %s and MONTH %s' % (self._template[self.YEAR],
                    self._template[self.MONTH])
            temp = self._template[self.YEAR]
            self._template[self.YEAR] = self._template[self.MONTH]
            self._template[self.MONTH] = temp
        elif self._template[self.DAY] != None and self._template[self.DAY] >= 1000:
            print 'SWAP YEAR %s and DAY %s' % (self._template[self.YEAR],
                    self._template[self.DAY])
            temp = self._template[self.YEAR]
            self._template[self.YEAR] = self._template[self.DAY]
            self._template[self.DAY] = temp

        # The year is set -- see if the month should be the day.
        if self._template[self.MONTH] != None and self._template[self.MONTH] > 12:
            print 'SWAP DAY %s and MONTH %s' % (self._template[self.DAY],
                    self._template[self.MONTH])
            temp = self._template[self.DAY]
            self._template[self.DAY] = self._template[self.MONTH]
            self._template[self.MONTH] = temp

        print 'Date: %r-%r-%r' % (self._template[self.YEAR], self._template[self.MONTH],
                self._template[self.DAY])

    def __repr__(self):
        return '%s-%s-%s %s:%s:%s' % (
                '*' if self._template[self.YEAR] is None
                    else str(self._template[self.YEAR]),
                '*' if self._template[self.MONTH] is None
                    else str(self._template[self.MONTH]),
                '*' if self._template[self.DAY] is None
                    else str(self._template[self.DAY]),
                '*' if self._template[self.HOUR] is None
                    else str(self._template[self.HOUR]),
                '*' if self._template[self.MINUTE] is None
                    else str(self._template[self.MINUTE]),
                '*' if self._template[self.SECOND] is None
                    else str(self._template[self.SECOND]))

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
        """ Value of a string used in instantiation.
        """
        return None if string == '*' else int(string)

    def first_occurrence(self, now_date_time):
        """
        now_date_time - datetime object.
        returns - datetime object.
        """
        self._lastfired = [None, None, None, None, None, None]

        now = [None, None, None, None, None, None]
        now[self.YEAR]   = now_date_time.year
        now[self.MONTH]  = now_date_time.month
        now[self.DAY]    = now_date_time.day
        now[self.HOUR]   = now_date_time.hour
        now[self.MINUTE] = now_date_time.minute
        now[self.SECOND] = now_date_time.second
        print 'Now:      %d-%d-%d %d:%d:%d' % (now[self.YEAR],
                                          now[self.MONTH],
                                          now[self.DAY],
                                          now[self.HOUR],
                                          now[self.MINUTE],
                                          now[self.SECOND])
        print 'Template: %r' % self

        # TODO: make sure that '09' in a date is OK - this is a random place
        # to mention this.

        # We start with the template (but with the '*' values filled-in with
        # the current time - from 'now').
        for i in range(len(now)):
            self._lastfired[i] = (now[i] if self._template[i] is None else 
                                  self._template[i])

        print 'Start:    %d-%d-%d %d:%d:%d' % (self._lastfired[self.YEAR],
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
            #print 'template[%d] == %r' % (i, self._template[i])
            if self._template[i] == None:
                #print '\t\'*\', append to previous_star'
                previous_star.append(i)

            # If we'd already found a moment less than 'now', set all
            # future '*' values to their minimum.
            if found:
                if self._template[i] == None:
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
                    print '(no previous_star) No future times match the template'
                    return None
                star = previous_star.pop()
                while self._lastfired[star] >= self.max_value[star]:
                    #print 'lastfired[%d] (%d) >= max_value[%d] (%d)' % (
                    #    star, self._lastfired[star], star,
                    #    self.max_value[star])

                    self._lastfired[star] = self.min_value[star]
                    if not previous_star:
                        print '(ran out of previous star) No future times match the template'
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


    @property
    def day(self):
        return self._template[self.DAY]

    @property
    def month(self):
        return self._template[self.MONTH]

    @property
    def year(self):
        return self._template[self.YEAR]

class DayOfWeekTime(Moment):
    def __init__(self, days_string, time_string, increment_string):
        """
        days_string is an array of strings, each is a day of the week
        """
        super(DayOfWeekTime, self).__init__(time_string,
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

    def _first_occurrence(self, now):
        """
        now - datetime object.
        returns - datetime object.
        """
        self._lastfired = {}
        # TODO

        # (template = Us)
        # fill result with template (use 'now' values for '*')
        # for i = (year...second)
        #   if Us[i] > Now[i]:
        #     result(i..second) = replace '*' with minimum value
        #   elif Us[i] < Now[i]
        #     if not Increment(result(year..i)):
        #       return None
        #     result(i..second) = replace '*' with minimum value
        # return result
        #
        # Finally, return 'None' if 'result' < 'now'.

        if hour == None:
            hour = now.hour
        if minute == None:
            minute = now.minute
        if second == None:
            second = now.second

        # Handle the 'day of week' format -- start with 'today'
        self.__next_firing_time = datetime.datetime(now.year, now.month,
                                                    now.day, hour, minute,
                                                    second)
        next_valid_day = self.DaysUntilValidDayOfWeek(now.year, now.month,
                                                      now.day)
        if next_valid_day == None:
            self.__next_firing_time = None
        else:
            self.__next_firing_time += next_valid_day

        # Now, adjust for the first firing after 'now'.
        if self.__next_firing_time:
            next_time = (self.__next_firing_time.second,
                         self.__next_firing_time.minute,
                         self.__next_firing_time.hour,
                         self.__next_firing_time.day,
                         self.__next_firing_time.month,
                         self.__next_firing_time.year)
            now_time = (now.second, now.minute, now.hour,
                        now.day, now.month, now.year)

            print ('adjusting firing time starting from %s' %
                    self.__next_firing_time.__str__())

            for i in reversed(range(len(next_time))):
                if next_time[i] > now_time[i]:
                    print '\tindex[%d] : %d > %d -- min', (i, next_time[i], now_time[i])
                    self.ForceMinimum(i)
                    break
                elif next_time[i] < now_time[i]:
                    print '\tindex[%d] : %d < %d -- inc & min', (i, next_time[i], now_time[i])
                    self.IncrementNextTime(i+1)
                    if not self.__next_firing_time:
                        self._log.Print(Logger.Type.VERBOSE, 'Result: none')
                        return None
                    self.ForceMinimum(i)
                    break
                else:
                  print '\tindex[%d] : %d == %d', (i, next_time[i], now_time[i])

            print 'Result: %s', self.__next_firing_time.__str__()

        return DateTime.datetime.datetime(self._lastfired['year'],
                                          self._lastfired['month'],
                                          self._lastfired['day'],
                                          self._lastfired['hour'],
                                          self._lastfired['minute'],
                                          self._lastfired['second'])

    # TODO: from other code...


    def MaybeIncrement(self, inc, template, value, carry, maximum):
      """This will increment a specific component of the time/date (a
         component can be any of year, month, day, hour, minute, second).
      Args:
        inc - If this RepeatingDateTime object includes an increment structure,
              this is the increment value for the component.
        template - If this object does NOT have an increment structure, this is
                   either the template value or wildcard ('*') for the
                   component.
        value - This is the value of _next_firing_time for the component.
        carry - This is any carry that has been forwarded from previous
                components.
        maximum - This is the maximum value for the component.
      Returns:
        value - the new value for the component.
        carry - any carry to forward to the next component.  The sense of what
                'carry' means depends on whether we're using self.__increment
                (where carry actually means the value to add to the next most
                significant component) or not (where carry means to add 1 to the
                next component that has a wildcard).
        keep_going - whether to continue incrementing further components.
      """
      keep_going = False
      applycarry = True
      if inc != None:  # Is this parameter part of an increment block?
        self._log.Print(Logger.Type.DEBUG,
                            '\tINC: Adding value(%d) += inc(%d) + carry(%d)',
                            (value, inc, carry))
        value += inc + carry
        carry = 0
        keep_going = True  # If we do the increment, we (potentially)
                           # increment all the numbers.
      elif template == None:  # Else, we just increment if the template is 0.
        self._log.Print(Logger.Type.DEBUG,
                  '\tTEMPLATE: Adding value(%d) += carry(%d)', (value, carry))
        value += carry
        carry = 0
        keep_going = False  # If we add stuff because of the template, we stop
                            # when we find something unless...
      else:  # else, no increment, yes template value
        self._log.Print(Logger.Type.DEBUG, '\tCAN\'t increment')
        applycarry = False  # Don't apply the carry when we're using templates
                            # but the template doesn't have a wildcard.
        keep_going = True  # Keep looking for a wildcard.
  
      # If we incremented past the max, carry.
      if applycarry:
        self._log.Print(Logger.Type.DEBUG,
            '\tcalculate carry to val(%d) with max(%d)', (value, maximum))
        carry = 0
        while value > maximum:
          value -= (maximum+1)
          carry += 1
          keep_going = True
          # ...unless there's a carry -- then we continue incrementing.
        self._log.Print(Logger.Type.DEBUG, '\tNew val(%d) with carry(%d)',
            (value, carry))
  
      return (value,carry,keep_going)
  
    def IncrementNextTime(self, skip=0):  # year..x
      """
         For cases where xxxx, 'skip' indicates the number of datetime elements
         to skip -- the portion above the 'skip' is incremented. """
      next_valid_time = None
      keep_going = True
  
      if self.__next_firing_time == None:
        return False
  
      self._log.Print(Logger.Type.VERBOSE, 'IncrementNextTime')
      self._log.Print(Logger.Type.VERBOSE,
          ' start at  %s, skip %d', (self.__next_firing_time.__str__(), skip))
      if self.__increment:
        self._log.Print(Logger.Type.VERBOSE,
          ' increment %s', self.__increment.GetString())
      else:
        self._log.Print(Logger.Type.VERBOSE,
          ' template  %s', self.GetDateTimeString())
  
      carry = 0
      if not self.__increment:
        carry = 1
      keep_going = True
  
      if keep_going and skip <= 0:
        self._log.Print(Logger.Type.DEBUG, 'SECOND')
        inc_value = None
        if self.__increment:
          inc_value = self.__increment.second
        (val, carry, keep_going) = self.MaybeIncrement(
                                              inc_value,
                                              self.Second(),
                                              self.__next_firing_time.second,
                                              carry,
                                              59)
        self.__next_firing_time = self.__next_firing_time.replace(second = val)
      else:
        skip -= 1
  
      if keep_going and skip <= 0:
        self._log.Print(Logger.Type.DEBUG, 'MINUTE')
        inc_value = None
        if self.__increment:
          inc_value = self.__increment.minute
        (val, carry, keep_going) = self.MaybeIncrement(
                                              inc_value,
                                              self.Minute(),
                                              self.__next_firing_time.minute,
                                              carry,
                                              59)
        self.__next_firing_time = self.__next_firing_time.replace(minute = val)
      else:
        skip -= 1
  
      if keep_going and skip <= 0:
        self._log.Print(Logger.Type.DEBUG, 'HOUR')
        inc_value = None
        if self.__increment:
          inc_value = self.__increment.hour
        (val, carry, keep_going) = self.MaybeIncrement(
                                              inc_value,
                                              self.Hour(),
                                              self.__next_firing_time.hour,
                                              carry,
                                              23)
        self.__next_firing_time = self.__next_firing_time.replace(hour = val)
      else:
        skip -= 1
  
      if ((self.__date != None or self.__increment != None) and
          keep_going and skip <= 0):
        self._log.Print(Logger.Type.DEBUG, 'DAY')
        inc_value = None
        if self.__increment:
          inc_value = self.__increment.day
        days_this_month = MyDate.DaysInMonth(self.__next_firing_time.month,
                                             self.__next_firing_time.year)
        (val, carry, keep_going) = self.MaybeIncrement(
                                              inc_value,
                                              self.Day(),
                                              self.__next_firing_time.day,
                                              carry,
                                              days_this_month)
        self.__next_firing_time = self.__next_firing_time.replace(day = val)
      else:
        skip -= 1
  
      if ((self.__date != None or self.__increment != None) and
          keep_going and skip <= 0):
        self._log.Print(Logger.Type.DEBUG, 'MONTH')
        inc_value = None
        if self.__increment:
          inc_value = self.__increment.month
        # Change index range for month from 1..12 to 0..11 to make the math in
        # 'MaybeIncrement' work better.  Then change back.
        (val, carry, keep_going) = self.MaybeIncrement(
                                                inc_value,
                                                self.Month(),
                                                self.__next_firing_time.month-1,
                                                carry,
                                                11)
        self.__next_firing_time = self.__next_firing_time.replace(month = val+1)
      else:
        skip -= 1
  
      if ((self.__date != None or self.__increment != None) and
          keep_going and skip <= 0):
        self._log.Print(Logger.Type.DEBUG, 'YEAR')
        inc_value = None
        if self.__increment:
          inc_value = self.__increment.year
        (val, carry, keep_going) = self.MaybeIncrement(
                                                  inc_value,
                                                  self.Year(),
                                                  self.__next_firing_time.year,
                                                  carry,
                                                  3000)
        self.__next_firing_time = self.__next_firing_time.replace(year = val)
      else:
        skip -= 1
  
      if self.__increment != None:
          self._log.Print(Logger.Type.DEBUG,
                          ' to get    %s', self.__next_firing_time.__str__())
          return True
      elif self.__date == None:
        if keep_going:
          self._log.Print(Logger.Type.DEBUG, 'DAY OF WEEK')
          # If we're here, then we couldn't increment any part of time (or, we
          # incremented beyond the maximum time) so we have to increment the
          # day.  Add a day to the next firing time and then look from there
          # for the next valid day of the week.
          self.__next_firing_time += datetime.timedelta(days=1)
          next_valid_time = self.DaysUntilValidDayOfWeek(
                                                  self.__next_firing_time.year,
                                                  self.__next_firing_time.month,
                                                  self.__next_firing_time.day)
  
          # day of week
          if next_valid_time:
            self.__next_firing_time += next_valid_time
            self._log.Print(Logger.Type.DEBUG,
                          ' DOW gets  %s', self.__next_firing_time.__str__())
            return True
      else:
        # If none of these are undefined or if we've wrapped on the most
        # significant, allowable, value, we're done -- there _is_ no next time.
        if keep_going:
          self._log.Print(Logger.Type.DEBUG, ' DATE & KEEP GOING - done firing')
          self.__next_firing_time = None
          return False
        else:
          self._log.Print(Logger.Type.DEBUG,
                ' to get    %s', self.__next_firing_time.__str__())
          return True
  
      self._log.Print(Logger.Type.ERROR, '*** CAN WE GET HERE? ***')
      self.__next_firing_time = None
      return False
  
  
    def DaysUntilValidDayOfWeek(self, year, month, day):
      """Returns 'timedelta' describing number of days until the next valid one.
  
        Starting from the date described by the parameters, this routine
        searches for a valid day of the week.  This code assumes that the
        calling routine has already determined that self.__date is 'None',
        therefore, this RepeatingDateTime has valid days of the week.
  
      Args:
        year, month, day - numeric values describing the first possible valid
                           day
      Returns:
        'timedelta' equal to anywhere between 0 and 6 days until the next valid
        day of the week (starting at year,month,day).  If self.__on_day values
        are all 'False', returns 'None'.
      """
  
      today_weekday = datetime.date(year,month,day).weekday() # 0-6, 0=Monday
      day_list = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
      self._log.Print(Logger.Type.DEBUG,
                'start looking from %d-%d-%d which is a %s',
                (year, month, day, day_list[today_weekday]))
      add_days = None
      for days_ahead in range(0,7):
        # Generate string for day of week 'i' days in the future.
        index = (today_weekday + days_ahead) % 7
        day_of_week = day_list[index]
  
        self._log.Print(Logger.Type.DEBUG, 'checking %s', day_of_week)
        # If that's a valid day for this RepeatingDateTime, we're done.
        if self.__on_day[day_of_week]:
          add_days = days_ahead
          self._log.Print(Logger.Type.DEBUG,
                  '  **YES** %d days from now', add_days)
          break
  
      if add_days == None:
        return None
      return datetime.timedelta(days=add_days)
  
if __name__ == '__main__':
    pass
