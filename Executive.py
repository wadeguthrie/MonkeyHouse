#! /usr/bin/python

class Executive(object):
  (INITIALIZING, OPERATING, SUSPENDED_OPERATION) = range(3)
  __state_str = {INITIALIZING: 'INITIALIZING',
                 OPERATING: 'OPERATING',
                 SUSPENDED_OPERATION: 'SUSPENDED_OPERATION'}

  def __init__(self):
    self.state = self.INITIALIZING
    self.__targets = []
    self.__bridges = []

  def get_state(self):
    state = {
      "STATE" : self.__state_str[self.state],
      "TARGETS" : []
    }
    #for targets in self.__targets:
      #self.state["TARGETS"].append({target.name : target.get_state()})
    #for bridge in self.__bridges:
      #self.state["TARGETS"].append({target.name : target.get_state()})

    return state

# Main
if __name__ == '__main__':
  pass
