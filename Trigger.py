#! /usr/bin/python

"""
Implements Triggers for MonkeyHouse.
"""

import re

import Log
import MessageHandlerInterface

# TODO: code-up 'arm' and test it
# TODO: Then: Include the message test in the user's guide
# TODO: After: Draw-up arrays in the incoming message
# TODO: Later: Test leading '\'

class TriggerFactory(object):
    """Builds MonkeyHouse Triggers of the type described in text input."""
    __factory = {
            'message': lambda d, e, p, t: MessageTrigger(d, e, p, t),
            'timer': lambda d, e, p, t: TimerTrigger(d, e, p, t),
            'and': lambda d, e, p, t: AndTrigger(d, e, p, t),
            'or': lambda d, e, p, t: OrTrigger(d, e, p, t),
            'not': lambda d, e, p, t: NotTrigger(d, e, p, t),
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
            data (array) - this is a JSON-equivalent data structure.
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

# For matching messages

class MessageTemplateFactory(object):
    """Creates Message templates.

    A MessageTemplate is an object that contains a partial MonkeyHouse Message
    (which is a JSON-equivalent data structure) and code to determine whether
    another Message matches the partial Message stored.  The rules are defined
    by the MonkeyHouse Design Specification.
    """
    re_slash = re.compile(r'\\(.*)')
    re_le = re.compile(r'<=(.*)')
    re_lt = re.compile(r'<(.*)')
    re_ge = re.compile(r'>=(.*)')
    re_gt = re.compile(r'>(.*)')
    re_eq = re.compile(r'==(.*)')

    @staticmethod
    def new_template(template):
        """Creates a MessageTemplate of the appropriate type.

        Params:
            - template - string that contains JSON text describing a
                MessageTemplate.
        Returns: a MessageTemplate
        """
        # This will probably never happen as there's no way to express 'None'
        # in the JSON.  Instead, we'll get there via an empty array.
        if template is None:
            return None

        if isinstance(template, dict):
            return DictTemplate(template)

        if isinstance(template, list):
            if len(template) == 0:
                return None
            return ArrayTemplate(template)

        if not isinstance(template, str):
            return Equals(template)

        # Allow leading slash to quote [<>=] chars.
        match = MessageTemplateFactory.re_slash.match(template)
        if match:
            return Equals(match.group(1))

        match = MessageTemplateFactory.re_le.match(template)
        if match:
            return LessThanOrEqual(match.group(1))

        match = MessageTemplateFactory.re_lt.match(template)
        if match:
            return LessThan(match.group(1))

        match = MessageTemplateFactory.re_ge.match(template)
        if match:
            return GreaterThanOrEqual(match.group(1))

        match = MessageTemplateFactory.re_gt.match(template)
        if match:
            return GreaterThan(match.group(1))

        match = MessageTemplateFactory.re_eq.match(template)
        if match:
            return Equals(match.group(1))

        return Equals(template)

class MessageTemplate(object):
    """
    Base class for MonkeyHouse Message templates.

    A MessageTemplate is an object that contains a partial MonkeyHouse Message
    (which is a JSON-equivalent data structure) and code to determine whether
    another Message matches the partial Message stored.  The rules are defined
    by the MonkeyHouse Design Specification.
    """

    def matches(self, value):
        """Returns True if |value| matches the template.

        Base class returns False - derived classes need to implement this.
        """
        return False

    @staticmethod
    def _value(string):
        """
        Returns a numberic value for |string|, if possible.
        
        Figures out what kind of thing |string| represents (a float, an int,
        or just a string) and returns that.
        """
        try:
            float_value = float(string)
            return float_value
        except ValueError:
            pass

        try:
            int_value = int(string)
            return int_value
        except ValueError:
            return string

class LessThan(MessageTemplate):
    """Checks if a Message element's value is < the template's."""
    def __init__(self, operand):
        super(LessThan, self).__init__()
        self.__operand = operand

    def matches(self, value):
        """Checks value of |value| (string) vs. the template's |__operand|."""
        print 'LT: value=%r template=%r' % (value, self.__operand)
        if MessageTemplate._value(value) < MessageTemplate._value(
                self.__operand):
            print 'LT: YES'
            return MessageTrigger.MATCHES
        print 'LT: NO'
        return MessageTrigger.DOESNT_MATCH


class LessThanOrEqual(MessageTemplate):
    """Checks if a Message element's value is <= the template's."""
    def __init__(self, operand):
        super(LessThanOrEqual, self).__init__()
        self.__operand = operand

    def matches(self, value):
        """Checks value of |value| (string) vs. the template's |__operand|."""
        print 'LE: value=%r template=%r' % (value, self.__operand)
        if MessageTemplate._value(value) <= MessageTemplate._value(
                self.__operand):
            print 'LE: YES'
            return MessageTrigger.MATCHES
        print 'LE: NO'
        return MessageTrigger.DOESNT_MATCH


class GreaterThan(MessageTemplate):
    """Checks if a Message element's value is > the template's."""
    def __init__(self, operand):
        super(GreaterThan, self).__init__()
        self.__operand = operand

    def matches(self, value):
        """Checks value of |value| (string) vs. the template's |__operand|."""
        print 'GT: value=%r template=%r' % (value, self.__operand)
        if MessageTemplate._value(value) > MessageTemplate._value(
                self.__operand):
            print 'GT: YES'
            return MessageTrigger.MATCHES
        print 'GT: NO'
        return MessageTrigger.DOESNT_MATCH


class GreaterThanOrEqual(MessageTemplate):
    """Checks if a Message element's value is >= the template's."""
    def __init__(self, operand):
        super(GreaterThanOrEqual, self).__init__()
        self.__operand = operand

    def matches(self, value):
        """Checks value of |value| (string) vs. the template's |__operand|."""
        print 'GE: value=%r template=%r' % (value, self.__operand)
        if MessageTemplate._value(value) >= MessageTemplate._value(
                self.__operand):
            print 'GE: YES'
            return MessageTrigger.MATCHES
        print 'GE: NO'
        return MessageTrigger.DOESNT_MATCH


class Equals(MessageTemplate):
    """Checks if a Message element's value is == the template's."""
    def __init__(self, operand):
        super(Equals, self).__init__()
        self.__operand = operand

    def matches(self, value):
        """Checks value of |value| (string) vs. the template's |__operand|."""
        print 'Equals: value=%r template=%r' % (value, self.__operand)
        if MessageTemplate._value(value) == MessageTemplate._value(
                self.__operand):
            print 'EQ: YES'
            return MessageTrigger.MATCHES
        print 'EQ: NO'
        return MessageTrigger.DOESNT_MATCH


class ArrayTemplate(MessageTemplate):
    """Checks if a Message element's array matches the template's."""
    def __init__(self, template):
        super(ArrayTemplate, self).__init__()
        self.__templates = []
        for element in template:
            self.__templates.append(
                    MessageTemplateFactory.new_template(element))

    def matches(self, value):
        """Checks value of |value| (string) vs. the template's |__templates|.

        The __templates array contains an array of values (any of which
        might, actually, be a <, <=, ==, >=, or > template).  If _any_ of
        these match |value|, the template matches.  For instance, if
        __templates is [3, 5, 12], then the value 3 or the value 5 would
        match but the value 4 would not.

        NOTE: MonkeyHouse Messages don't contain arrays so the semantics of
        this class work just fine (otherwise, it would have been expected to
        match one array against another).
        """
        print "Array: value=%r, template=%r" % (value, self.__templates)
        for template in self.__templates:
            if template.matches(value) == MessageTrigger.MATCHES:
                print 'ARRAY[%r]: YES' % template
                return MessageTrigger.MATCHES
        print 'ARRAY: NO'
        return MessageTrigger.DOESNT_MATCH


class DictTemplate(MessageTemplate):
    """Checks if a Message element's dict matches the template's."""
    def __init__(self, template):
        super(DictTemplate, self).__init__()
        self.__template = {}
        for key in template:
            self.__template[key] = MessageTemplateFactory.new_template(
                    template[key])

    def matches(self, value):
        """Checks value of |value| (string) vs. the template's |__operand|.

        This checks to see if an incoming dict (in |value|) matches the dict
        in the object's __template.  The template contains a dict of templates
        so the match is done piece-wise -- each element of |value| is checked
        against the corresponding template in dict.
        """
        print "Dict: value=%r, template=%r" % (value, self.__template)
        pending_none = None  # A message with a key that matches 'None' isn't
                             # a deactivated trigger until all other keys
                             # match.
        key = None
        for key in self.__template:
            print '>>> Check %r' % key
            if self.__template[key] is None:
                print 'Dict: None'
                if key in value:
                    pending_none = key
                continue
            if key not in value:
                # Message is not applicable, return without altering the
                # trigger.
                print 'Dict: %r: does not apply' % key
                return MessageTrigger.DOESNT_APPLY
            match = self.__template[key].matches(value[key])
            print 'Dict: match is "%s"' % MessageTrigger.matches_str[match]
            if match == MessageTrigger.DOESNT_MATCH:
                print 'DICT[%r]: NO' % key
                return MessageTrigger.DOESNT_MATCH
            if match == MessageTrigger.DOESNT_APPLY:
                print 'Dict: %r: does not apply (2)' % key
                return MessageTrigger.DOESNT_APPLY

        if pending_none is not None:
            if key is None:
                print 'Empty template'
            else:
                print 'DICT[%r=None]: NO' % key
            return MessageTrigger.DOESNT_MATCH
        print 'Dict: YES'
        return MessageTrigger.MATCHES


# TODO: unittest: 'template' not in data
class MessageTrigger(Trigger):
    """A MonkeyHouse Message Trigger.

    A message trigger goes into a triggered state when a Message matches the
    trigger's template and goes into a non-triggered state when a Message does
    not match (though it's possible that the incoming message does not apply
    -- see the MonkeyHouse design specification for details).

    The idea, here, is that a MonkeyHouse Rule will fire (i.e., execute its
    firing action) when its firing trigger transitions to the triggered state
    and will de-fire (i.e., execute its de-firing action) when its defiring
    trigger transitions to the triggered state.
    """
    (MATCHES, DOESNT_MATCH, DOESNT_APPLY) = range(3)
    matches_str = {MATCHES: 'matches',
                   DOESNT_MATCH: 'does not match',
                   DOESNT_APPLY: 'does not apply'}

    def __init__(self, data, executive, parent, trigger_type):
        super(MessageTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'MessageTrigger ctor'
        self.__template = MessageTemplateFactory.new_template(
                data['template'])

    def on_message(self, message):
        """Handles incoming messages for the MessageTrigger.

        This handles messages directed specifically to the Trigger (like 'arm'
        or 'trigger' -- these messages will have a 'to' value matching the
        name of the trigger) or, if the message is not directed at the
        trigger, will see if the message matches the trigger's message
        template in such a way to transition to the triggered or non-triggered
        state.

        Params:
            - message - a JSON-equivalent data structure -- a MonkeyHouse
                Message (see the MonkeyHouse design specification for details)
        Returns: nothing.
        """
        print '===== on_message(%r) =====' % message
        match = self.__template.matches(message)
        if match == MessageTrigger.MATCHES:
            self._set_trigger(triggered=True)
        elif match == MessageTrigger.DOESNT_MATCH:
            self._set_trigger(triggered=False)
        return


# TODO: time template looks like: [anchor][+increment] where 'anchor' is a
# time/date with, possibly, items missing and 'increment' is a number and a
# time element (e.g., week, months, minutes -- note singular and plural).  The
# anchor is the initial time for the trigger and the increment is added for
# subsequent times.  Without the increment, just match the next missing value
# in 'anchor'.  Without 'anchor', the initial time is 'Now+increment'.  An
# empty string means 'Now'.  Note, 'elapsed time' is no longer necessary.
# TODO: move TimeTrigger out into its own file.
class TimerTrigger(Trigger):
    """A MonkeyHouse Timer Trigger.

    A timer trigger goes into a triggered state when the time matches the
    trigger's template.  The template has a method that provides a datetime
    object for the next time >= to the current time that matches the template
    -- that's really all that's needed.  Each time the trigger is armed, it
    provides a new datetime object.

    The idea, here, is that a MonkeyHouse Rule will fire (i.e., execute its
    firing action) when its firing trigger transitions to the triggered state
    and will de-fire (i.e., execute its de-firing action) when its defiring
    trigger transitions to the triggered state.
    """
    def __init__(self, data, executive, parent, trigger_type):
        super(TimerTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'TimerTrigger ctor'
        self.__time = data['time']
        # TODO: executive's register_timer_handler(self).


    def arm(self):
        """Tells the trigger to be ready to trigger."""
        # TODO: Re-calculates the next time that this trigger is valid and
        #   calls the executive's register_timer_handler(self).
        pass

    def on_timeout(self, time):
        """Triggers the trigger."""
        # TODO: If on_timeout changes the state of the TimerTrigger, it
        #   Logs and calls the parent's on_trigger_change method.
        pass


class AndTrigger(Trigger):
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


class OrTrigger(Trigger):
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


class NotTrigger(Trigger):
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


# Main
if __name__ == '__main__':
    pass
