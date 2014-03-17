#! /usr/bin/python

"""
Implements Message Triggers for MonkeyHouse.
"""

import re

import Log
import LogicalTrigger
import MessageHandlerInterface
import MessageTrigger
import TimerTrigger

# TODO: code-up 'arm' and test it
# TODO: Then: Include the message test in the user's guide
# TODO: After: Draw-up arrays in the incoming message
# TODO: Later: Test leading '\'

class TriggerFactory(object):
    """Builds MonkeyHouse Triggers of the type described in text input."""
    __factory = {
            'message': lambda d, e, p, t: MessageTrigger.MessageTrigger(d,
                                                                        e,
                                                                        p,
                                                                        t),
            'timer': lambda d, e, p, t: TimerTrigger.TimerTrigger(d, e, p, t),
            'and': lambda d, e, p, t: LogicalTrigger.AndTrigger(d, e, p, t),
            'or': lambda d, e, p, t: LogicalTrigger.OrTrigger(d, e, p, t),
            'not': lambda d, e, p, t: LogicalTrigger.NotTrigger(d, e, p, t),
            }
    @staticmethod
    def new_trigger(data, executive, parent, trigger_type):
        """Returns a Trigger of the appropriate type.

        Param:
            executive - Executive object
            parent - Trigger or Rule object
            trigger_type - string object

        Returns: Trigger.
        """
        if 'type' not in data:
            raise ValueError('No "type" in data')
        elif data['type'] in TriggerFactory.__factory:
            return TriggerFactory.__factory[data['type']](data,
                                                          executive,
                                                          parent,
                                                          trigger_type)
        else:
            raise ValueError('Trigger type "%s" not supported' % data['type'])


if __name__ == '__main__':
    pass
