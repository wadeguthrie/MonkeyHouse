#! /usr/bin/python

"""
Implements Timer Triggers for MonkeyHouse.
"""

import re

import DateTime
import Log
import Trigger

# TODO: time template looks like: [anchor][+increment] where 'anchor' is a
# time/date with, possibly, items missing and 'increment' is a number and a
# time element (e.g., week, months, minutes -- note singular and plural).  The
# anchor is the initial time for the trigger and the increment is added for
# subsequent times.  Without the increment, just match the next missing value
# in 'anchor'.  Without 'anchor', the initial time is 'Now+increment'.  An
# empty string means 'Now'.  Note, 'elapsed time' is no longer necessary.
# TODO: move TimeTrigger out into its own file.
class TimerTrigger(Trigger.Trigger):
    """A MonkeyHouse Timer Trigger.

    A timer trigger goes into a triggered state when the time matches the
    trigger's template.  The template has a method that provides a datetime
    object for the next time >= to the current time that matches the template
    -- that's really all that's needed.  Each time the trigger is armed, it
    provides a new datetime object.

    The idea, here, is that a MonkeyHouse Rule will fire (i.e., execute its
    firing action) when its firing trigger transitions to the triggered state
    and will de-fire (i.e., execute its de-firing action) when its defiring
    trigger transitions to the triggered state.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(TimerTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'TimerTrigger ctor'
        self.__time = data['time']
        # TODO: executive's register_timer_handler(self).


    def arm(self):
        """Tells the trigger to be ready to trigger."""
        # TODO: Re-calculates the next time that this trigger is valid and
        #   calls the executive's register_timer_handler(self).
        pass

    def on_timeout(self, time):
        """Triggers the trigger."""
        # TODO: If on_timeout changes the state of the TimerTrigger, it
        #   Logs and calls the parent's on_trigger_change method.
        pass

if __name__ == '__main__':
    pass
