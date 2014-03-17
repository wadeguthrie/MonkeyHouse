#! /usr/bin/python

"""
Implements Logical Triggers for MonkeyHouse.
"""

import re

import Log
import Trigger

class AndTrigger(Trigger.Trigger):
    """
    This trigger goes into the triggered state if _all_ of it's constituent
    triggers are in the triggered state.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(AndTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'AndTrigger ctor'
        # TODO: "sub-triggers" : [ <trigger>, <trigger>, ... <trigger> ]
        # or just one trigger for "operation":"not"
        # TODO: instantiate sub-triggers(FIRING_DEFIRING)

    def arm(self):
        """Tells the trigger to be ready to trigger."""
        # Calls constituent Trigger's arm methods.
        pass

    def on_trigger_change(self, firing, triggered):
        """Called by a constituent trigger when _that_ trigger changes state.

        When called, this trigger will check with its constituent triggers to
        determine whether this trigger should change state.
        """
        # TODO: called by their constituent Triggers.  The Trigger will call
        #   is_triggered on its constituent Triggers, determine whether or
        #   not this Trigger is triggered, save the current state of the
        #   Trigger, and if there's a state change, log and call the
        #   on_trigger_change(is_triggered()) method of its parent (whether
        #   it's parent is a Trigger or a Rule).  Active Triggers call
        #   parent's on_trigger_change.
        pass


class OrTrigger(Trigger.Trigger):
    """
    This is a MonkeyHouse Trigger that goes into the triggered state if _any_
    of its constituent triggers goes into the triggered state.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(OrTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'OrTrigger ctor'
        # TODO: "sub-triggers" : [ <trigger>, <trigger>, ... <trigger> ]
        # or just one trigger for "operation":"not"
        # TODO: instantiate sub-triggers(FIRING_DEFIRING)

    def arm(self):
        """Tells the trigger to be ready to trigger."""
        # Calls constituent Trigger's arm methods.
        pass

    def on_trigger_change(self, firing, triggered):
        """Called by a constituent trigger when _that_ trigger changes state.
        """
        # TODO: called by their constituent Triggers.  The Trigger will call
        #   is_triggered on its constituent Triggers, determine whether or
        #   not this Trigger is triggered, save the current state of the
        #   Trigger, and if there's a state change, log and call the
        #   on_trigger_change(is_triggered()) method of its parent (whether
        #   it's parent is a Trigger or a Rule).  Active Triggers call
        #   parent's on_trigger_change.
        pass


class NotTrigger(Trigger.Trigger):
    """
    This is a MonkeyHouse Trigger that goes into the triggered state if its
    constituent trigger goes into the non-triggered state.  This really only
    makes sense for a constituent trigger that's a MessageTrigger.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(NotTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'NotTrigger ctor'
        # TODO: "sub-triggers" : [ <trigger>, <trigger>, ... <trigger> ]
        # or just one trigger for "operation":"not"
        # TODO: instantiate sub-triggers(FIRING_DEFIRING)

    def arm(self):
        """Tells the trigger to be ready to trigger."""
        # Calls constituent Trigger's arm methods.
        pass

    def on_trigger_change(self, firing, triggered):
        """Called by a constituent trigger when _that_ trigger changes state.
        """
        # TODO: called by their constituent Triggers.  The Trigger will call
        #   is_triggered on its constituent Triggers, determine whether or
        #   not this Trigger is triggered, save the current state of the
        #   Trigger, and if there's a state change, log and call the
        #   on_trigger_change(is_triggered()) method of its parent (whether
        #   it's parent is a Trigger or a Rule).  Active Triggers call
        #   parent's on_trigger_change.
        pass

if __name__ == '__main__':
    pass
