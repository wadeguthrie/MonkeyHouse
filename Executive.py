#! /usr/bin/python

"""
The Executive is the engine that runs MonkeyHouse.  Its a 'select' loop that
waits for events or timeouts.  When those occur, the Executive delivers the
events to the objects waiting for them.  It also manages a Message queue,
accepting Messages and delivering them.
"""

import datetime

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
        now = datetime.datetime.now()
        timeout_seconds = 0 if timeout <= now else (timeout - now).seconds()
        self._register_timer_handler(timeout_seconds, (parameter,
                                                       timer_handler))

    def _register_timer_handler(self, seconds, param_handler):
        # TODO: Adds timer_handler, in sorted order of their timeouts but
        # after any existing triggers with the same timeout, to the
        # timer_queue.  The parameter is for the registrant to provide data
        # to be handed back when the timer goes off.  Among other things,
        # this can provide data to differentiate two different timers handled
        # by the same interface.
        pass

# Main
if __name__ == '__main__':
    pass
