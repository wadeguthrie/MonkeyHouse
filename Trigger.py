#! /usr/bin/python

"""
Implements Trigger base class for MonkeyHouse.
"""

import re

import Log
import MessageHandlerInterface

# TODO: code-up 'arm' and test it
# TODO: Then: Include the message test in the user's guide
# TODO: After: Draw-up arrays in the incoming message
# TODO: Later: Test leading '\'

class Trigger(object): # MessageHandlerInterface):
    """
    MonkeyHouse Trigger base class.
    """

    (FIRING, DEFIRING, FIRING_DEFIRING) = range(3)

    __trigger_type_str = {FIRING: 'firing',
                          DEFIRING: 'defiring',
                          FIRING_DEFIRING: 'firing_defiring'}

    def __init__(self, data, executive, parent, trigger_type):
        """
            data (dict) - this is a JSON-equivalent data structure.
            executive (Executive)
            parent (Trigger or Rule) - Trigger or Rule that contains this
                object.
            trigger_type (enum {FIRING, DEFIRING, FIRING_DEFIRING}).

        """
        print 'Trigger ctor'
        self.__name = data['name']
        self.__executive = executive
        self.__parent = parent
        self.__triggered = False
        self.__trigger_type = trigger_type

    def arm(self):
        """Tells the trigger to be ready to trigger."""
        pass

    def is_triggered(self):
        """Returns True if the Trigger has been triggered."""
        return self.__triggered

    def on_message(self, message):
        """Handles incoming Message from MonkeyHouse."""
        # TODO: operation: arm
        # TODO: operation: trigger
        pass

    def _set_trigger(self, triggered):
        """Triggers or de-triggers a MonkeyHouse Trigger."""
        if self.__triggered != triggered:
            self.__triggered = triggered
            self.__parent.on_trigger_change(self.__trigger_type,
                                            self.__triggered)
            self.__executive.log.log(Log.Log.INFO,
                                     Log.Log.TRIGGER,
                                     {'type': 'trigger',
                                      'name': self.__name,
                                      'trigger': 'activated' if triggered else
                                        'deactivated',
                                      'trigger-type': self.__trigger_type_str[
                                          self.__trigger_type]})

if __name__ == '__main__':
    pass
