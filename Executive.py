#! /usr/bin/python

"""
The Executive is the engine that runs MonkeyHouse.  Its a 'select' loop that
waits for events or timeouts.  When those occur, the Executive delivers the
events to the objects waiting for them.  It also manages a Message queue,
accepting Messages and delivering them.
"""

#import datetime

class Executive(object):
    """
    In its current form, this class exists only to support testing of Logging.
    """
    (INITIALIZING, OPERATING, SUSPENDED_OPERATION) = range(3)
    __state_str = {INITIALIZING: 'initializing',
                   OPERATING: 'operating',
                   SUSPENDED_OPERATION: 'suspended_operation'}

    def __init__(self, log):
        self.state = self.INITIALIZING
        self.__targets = []
        self.__bridges = []
        self.__timers = []
        self.log = log

    def get_state(self):
        """Returns the state of the MonkeyHouse Executive."""
        state = {
            "state": self.__state_str[self.state],
            "targets": []
        }
        #for targets in self.__targets:
            #self.state["TARGETS"].append({target.name : target.get_state()})
        #for bridge in self.__bridges:
            #self.state["TARGETS"].append({target.name : target.get_state()})

        return state

    def register_timer_handler(self, timer_handler, parameter, timeout):
        """Adds a timer (and timeout) to __timers

        Params:
            - timer_handler - TimerHandlerInterface (or, really, anything with
                an |on_timeout| method.  Called when now >= |timeout|
            - parameter - anything -- passed back to timer_handler on timeout
            - timeout - datetime object describing when |timer_handler| should
                be called.
        """
        # Insert, sorted, into the list of timers
        for i in range(len(self.__timers)):
            if timeout < self.__timers[i][0]:  # TODO: name indecis
                self.__timers.insert(i, (timeout, timer_handler, parameter))
                return
        # If it didn't fit before any existing timers, add at the end
        self.__timers.insert(len(self.__timers),
                            (timeout, timer_handler, parameter))

# Main
if __name__ == '__main__':
    pass
