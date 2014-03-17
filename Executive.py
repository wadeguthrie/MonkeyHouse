#! /usr/bin/python

"""
The Executive is the engine that runs MonkeyHouse.  Its a 'select' loop that
waits for events or timeouts.  When those occur, the Executive delivers the
events to the objects waiting for them.  It also manages a Message queue,
accepting Messages and delivering them.
"""

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

# Main
if __name__ == '__main__':
    pass
