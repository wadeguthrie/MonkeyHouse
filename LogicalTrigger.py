#! /usr/bin/python

"""
Implements Logical Triggers for MonkeyHouse.
"""

import re

import Log
import Trigger
import TriggerFactory

class LogicalTrigger(Trigger.Trigger):
    """
    Base class for logical triggers.  Handles instantiation of sub-triggers
    and passing 'arm' down the ladder.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(LogicalTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        self._triggers = []
        if 'sub-triggers' in data:
            for trigger in data['sub-triggers']:
                self._triggers.append(
                        TriggerFactory.TriggerFactory.new_trigger(
                            trigger, executive, self,
                            Trigger.Trigger.FIRING_DEFIRING))
        if 'sub-trigger' in data:
            self._triggers.append(TriggerFactory.TriggerFactory.new_trigger(
                data['sub-trigger'], executive, self,
                Trigger.Trigger.FIRING_DEFIRING))

    def arm(self):
        """Tells the trigger to be ready to trigger."""
        for trigger in self._triggers:
            trigger.arm()

class AndTrigger(LogicalTrigger):
    """
    This trigger goes into the triggered state if _all_ of it's constituent
    triggers are in the triggered state.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(AndTrigger, self).__init__(data, executive, parent,
                                         trigger_type)
        print 'AndTrigger ctor'
        if len(self._triggers) < 2:
            raise ValueError('"And" trigger needs at least 2 sub-triggers: %r'
                    % data)

    def on_trigger_change(self, firing, triggered):
        """Called by a constituent trigger when _that_ trigger changes state.

        When called, this trigger will check with its constituent triggers to
        determine whether this trigger should change state.
        """
        for trigger in self._triggers:
            if self._triggered == trigger.is_triggered():
                return # _this_ trigger didn't change

        self._set_trigger(not self._triggered)

class OrTrigger(LogicalTrigger):
    """
    This is a MonkeyHouse Trigger that goes into the triggered state if _any_
    of its constituent triggers goes into the triggered state.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(OrTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'OrTrigger ctor'
        if len(self._triggers) < 2:
            raise ValueError('"Or" trigger needs at least 2 sub-triggers: %r'
                    % data)

    def on_trigger_change(self, firing, triggered):
        """Called by a constituent trigger when _that_ trigger changes state.

        When called, this trigger will check with its constituent triggers to
        determine whether this trigger should change state.
        """
        for trigger in self._triggers:
            if self._triggered != trigger.is_triggered():
                self._set_trigger(not self._triggered)
                break  # Only change once

class NotTrigger(LogicalTrigger):
    """
    This is a MonkeyHouse Trigger that goes into the triggered state if its
    constituent trigger goes into the non-triggered state.  This really only
    makes sense for a constituent trigger that's a MessageTrigger.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(NotTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'NotTrigger ctor'
        if len(self._triggers) != 1:
            raise ValueError('"Not" trigger needs exactly one sub-trigger: %r'
                    % data)

    def on_trigger_change(self, firing, triggered):
        """Called by a constituent trigger when _that_ trigger changes state.
        """
        if self._triggered == self._triggers[0].is_triggered():
            self._set_trigger(not self._triggered)

if __name__ == '__main__':
    pass
