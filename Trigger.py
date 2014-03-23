#! /usr/bin/python

"""
Implements Trigger base class for MonkeyHouse.
"""

import re

import Log
import MessageHandlerInterface

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
        self._name = data['name']
        self.__trigger_type = trigger_type
        self._executive = executive
        self._parent = parent
        self._triggered = False
        self._armed = False

    def arm(self, armed):
        """Tells the trigger to be ready to trigger."""
        print 'Trigger(%s).arm(%s)' % (self._name,
                                       'ARMED' if armed else 'NOT armed')
        self._armed = armed

    def is_triggered(self):
        """Returns True if the Trigger has been triggered."""
        return self._triggered

    def on_message(self, message):
        """Handles incoming Message from MonkeyHouse.

        This, the base class, handles 'arm' and 'trigger' messages sent to the
        Trigger.  The MessageTrigger child class will handle other messages.

        Params:
            - message - dict containing MonkeyHouse message the Trigger is
              handling

        Returns: True if this method successfully handled the message.
        """
        if ('to' in message and message['to'] != '*' and message['to'] !=
                self._name):
            print '  Not directed at us: not \'arm\' or \'trigger\' message'
            return False  # Not directed at this trigger.

        if 'operation' not in message:
            print '  No \'operation\': not \'arm\' or \'trigger\' message'
            return False  # Not our kind of message.

        handled = False
        # NOTE: this allows the 'arm' and 'trigger' to be in the same message.
        if 'arm' in message['operation']:
            armed = True if message['operation']['arm'] == 'yes' else False
            self.arm(armed)
            handled = True

        if 'trigger' in message['operation']:
            triggered = (True if message['operation']['trigger'] == 'yes' else
                False)
            self._set_trigger(triggered)
            handled = True

        return handled

    def _set_trigger(self, triggered):
        print 'Trigger(%s)._set_trigger(%s)' % (
                self._name,
                'Triggered' if triggered else 'NOT Triggered')
        """Triggers or de-triggers a MonkeyHouse Trigger."""
        if self._triggered == triggered:
            print '  Not changing triggered value'
            return

        self._triggered = triggered
        print 'Trigger(%s) now %s' % (
                self._name,
                'Triggered' if self._triggered else 'NOT Triggered')
        self._executive.log.log(Log.Log.INFO,
                                Log.Log.TRIGGER,
                                {'type': 'trigger',
                                 'name': self._name,
                                 'trigger': 'activated' if triggered else
                                    'deactivated',
                                 'trigger-type': self.__trigger_type_str[
                                    self.__trigger_type],
                                 'armed' : 'armed' if self._armed else
                                    'disarmed'})

        # Go ahead and change state if we're not armed but don't report the
        # state change.
        if self._armed:
            print '  Armed, informing parent'
            self._parent.on_trigger_change(self.__trigger_type,
                                           self._triggered)
        else:
            print '  Not armed, not informing parent'

if __name__ == '__main__':
    pass
