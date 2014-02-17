#! /usr/bin/python


class Executive(object):
    """
    In its current form, this class exists only to support testing of Logging.
    """
    (INITIALIZING, OPERATING, SUSPENDED_OPERATION) = range(3)
    __state_str = {INITIALIZING: 'initializing',
                   OPERATING: 'operating',
                   SUSPENDED_OPERATION: 'suspended_operation'}

    def __init__(self):
        self.state = self.INITIALIZING
        self.__targets = []
        self.__bridges = []

    def get_state(self):
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
