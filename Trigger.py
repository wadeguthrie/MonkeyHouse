#! /usr/bin/python

import re

import MessageHandlerInterface


class TriggerFactory(object):
    __factory = {
            'message': lambda d, e, p, t: MessageTrigger(d, e, p, t),
            'timer': lambda d, e, p, t: TimerTrigger(d, e, p, t),
            'elapsed-time': lambda d, e, p, t: ElapsedTimeTrigger(d, e, p, t),
            'and': lambda d, e, p, t: AndTrigger(d, e, p, t),
            'or': lambda d, e, p, t: OrTrigger(d, e, p, t),
            'not': lambda d, e, p, t: NotTrigger(d, e, p, t),
            }
    @staticmethod
    def NewTrigger(data, executive, parent, trigger_type):
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
        pass

    def is_triggered(self):
        return self.__triggered

    def on_message(self, message):
        # TODO: operation: arm
        # TODO: operation: trigger
        pass

    def _set_trigger(self, triggered):
        if self.__triggered != triggered:
            self.__triggered = triggered
            self.__parent.on_trigger_change(self.__trigger_type,
                                            self.__triggered)
            #self.__executive.log()  # TODO: format of the log

# For matching messages

# TODO: unittest: each of the operators and an illegal operator
class TemplateFactory(object):
    re_le = re.compile(r'<=(.*)')
    re_lt = re.compile(r'<(.*)')
    re_ge = re.compile(r'>=(.*)')
    re_gt = re.compile(r'>(.*)')
    re_eq = re.compile(r'==(.*)')
    # TODO: remove a leading '\'
    @staticmethod
    def NewTemplate(template):
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

        match = TemplateFactory.re_le.match(template)
        if match:
            return LessThanOrEqual(match.group(1))

        match = TemplateFactory.re_lt.match(template)
        if match:
            return LessThan(match.group(1))

        match = TemplateFactory.re_ge.match(template)
        if match:
            return GreaterThanOrEqual(match.group(1))

        match = TemplateFactory.re_gt.match(template)
        if match:
            return GreaterThan(match.group(1))

        match = TemplateFactory.re_eq.match(template)
        if match:
            return Equals(match.group(1))

        return Equals(template)

class Template(object):
    def matches(self, value):
        return False

    @staticmethod
    def _value(string):
        try:
            f = float(string)
            return f
        except ValueError:
            pass

        try:
            i = int(string)
            return i
        except ValueError:
            return string

class LessThan(Template):
    def __init__(self, operand):
        self.__operand = operand

    def matches(self, value):
        print 'LT: value=%r template=%r' % (value, self.__operand)
        # TODO: should I check for a decimal point?
        if Template._value(value) < Template._value(self.__operand):
            print 'LT: YES'
            return MessageTrigger.MATCHES
        print 'LT: NO'
        return MessageTrigger.DOESNT_MATCH


class LessThanOrEqual(Template):
    def __init__(self, operand):
        self.__operand = operand

    def matches(self, value):
        print 'LE: value=%r template=%r' % (value, self.__operand)
        if Template._value(value) <= Template._value(self.__operand):
            print 'LE: YES'
            return MessageTrigger.MATCHES
        print 'LE: NO'
        return MessageTrigger.DOESNT_MATCH


class GreaterThan(Template):
    def __init__(self, operand):
        self.__operand = operand

    def matches(self, value):
        print 'GT: value=%r template=%r' % (value, self.__operand)
        if Template._value(value) > Template._value(self.__operand):
            print 'GT: YES'
            return MessageTrigger.MATCHES
        print 'GT: NO'
        return MessageTrigger.DOESNT_MATCH


class GreaterThanOrEqual(Template):
    def __init__(self, operand):
        self.__operand = operand

    def matches(self, value):
        print 'GE: value=%r template=%r' % (value, self.__operand)
        if Template._value(value) >= Template._value(self.__operand):
            print 'GE: YES'
            return MessageTrigger.MATCHES
        print 'GE: NO'
        return MessageTrigger.DOESNT_MATCH


class Equals(Template):
    def __init__(self, operand):
        self.__operand = operand

    def matches(self, value):
        print 'Equals: value=%r template=%r' % (value, self.__operand)
        if Template._value(value) == Template._value(self.__operand):
            print 'EQ: YES'
            return MessageTrigger.MATCHES
        print 'EQ: NO'
        return MessageTrigger.DOESNT_MATCH


class ArrayTemplate(Template):
    def __init__(self, template):
        self.__templates = []
        for element in template:
            self.__templates.append(TemplateFactory.NewTemplate(element))

    # If any template matches, this template matches
    def matches(self, value):
        print "Array: value=%r, template=%r" % (value, self.__templates)
        for template in self.__templates:
            if template.matches(value) == MessageTrigger.MATCHES:
                print 'ARRAY[%r]: YES' % template
                return MessageTrigger.MATCHES
        print 'ARRAY: NO'
        return MessageTrigger.DOESNT_MATCH


class DictTemplate(Template):
    def __init__(self, template):
        self.__template = {}
        for key in template:
            self.__template[key] = TemplateFactory.NewTemplate(template[key])

    def matches(self, value):
        print "Dict: value=%r, template=%r" % (value, self.__template)
        pending_none = None  # A message with a key that matches 'None' isn't
                             # a deactivated trigger until all other keys
                             # match.
        for key in self.__template:
            print '>>> Check %r' % key
            if self.__template[key] is None:
                print 'Dict: None'
                if key in value:
                    pending_none = key
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
            print 'DICT[%r=None]: NO' % key
            return MessageTrigger.DOESNT_MATCH
        print 'Dict: YES'
        return MessageTrigger.MATCHES


# TODO: unittest: 'template' not in data
class MessageTrigger(Trigger):
    (MATCHES, DOESNT_MATCH, DOESNT_APPLY) = range(3)
    matches_str = {MATCHES: 'matches',
                   DOESNT_MATCH: 'does not match',
                   DOESNT_APPLY: 'does not apply'}

    def __init__(self, data, executive, parent, trigger_type):
        super(MessageTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'MessageTrigger ctor'
        self.__template = TemplateFactory.NewTemplate(data['template'])

    def on_message(self, message):
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
class TimerTrigger(Trigger):
    def __init__(self, data, executive, parent, trigger_type):
        super(TimerTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'TimerTrigger ctor'
        self.__time = data['time']
        # TODO: executive's register_timer_handler(self).

    def arm(self):
        # TODO: Re-calculates the next time that this trigger is valid and
        #   calls the executive's register_timer_handler(self).
        pass

    def on_timeout(self, time):
        # TODO: If on_timeout changes the state of the TimerTrigger, it
        #   Logs and calls the parent's on_trigger_change method.
        pass


class ElapsedTimeTrigger(Trigger):
    def __init__(self, data, executive, parent, trigger_type):
        super(ElapsedTimeTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'ElapsedTimeTrigger ctor'
        self.__time = data['time']
        # TODO: executive's register_timer_handler(self).

    def arm(self):
        # TODO: Adds time to the current time and calls the Executive's
        #   register_timer_handler method.
        pass

    def on_timeout(self, time):
        # TODO: If on_timeout changes the state of the ElapsedTimeTrigger,
        #   it logs and calls the parent's on_trigger_change method.
        pass


class AndTrigger(Trigger):
    def __init__(self, data, executive, parent, trigger_type):
        super(AndTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'AndTrigger ctor'
        # TODO: "sub-triggers" : [ <trigger>, <trigger>, ... <trigger> ] # or just one trigger for "operation":"not"
        # TODO: instantiate sub-triggers(FIRING_DEFIRING)

    def arm(self):
        # Calls constituent Trigger's arm methods.
        pass

    def on_trigger_change(self, firing, triggered):
        # TODO: called by their constituent Triggers.  The Trigger will call
        #   is_triggered on its constituent Triggers, determine whether or
        #   not this Trigger is triggered, save the current state of the
        #   Trigger, and if there's a state change, log and call the
        #   on_trigger_change(is_triggered()) method of its parent (whether
        #   it's parent is a Trigger or a Rule).  Active Triggers call
        #   parent's on_trigger_change.
        pass


class OrTrigger(Trigger):
    def __init__(self, data, executive, parent, trigger_type):
        super(OrTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'OrTrigger ctor'
        # TODO: "sub-triggers" : [ <trigger>, <trigger>, ... <trigger> ] # or just one trigger for "operation":"not"
        # TODO: instantiate sub-triggers(FIRING_DEFIRING)

    def arm(self):
        # Calls constituent Trigger's arm methods.
        pass

    def on_trigger_change(self, firing, triggered):
        # TODO: called by their constituent Triggers.  The Trigger will call
        #   is_triggered on its constituent Triggers, determine whether or
        #   not this Trigger is triggered, save the current state of the
        #   Trigger, and if there's a state change, log and call the
        #   on_trigger_change(is_triggered()) method of its parent (whether
        #   it's parent is a Trigger or a Rule).  Active Triggers call
        #   parent's on_trigger_change.
        pass


class NotTrigger(Trigger):
    def __init__(self, data, executive, parent, trigger_type):
        super(NotTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'NotTrigger ctor'
        # TODO: "sub-triggers" : [ <trigger>, <trigger>, ... <trigger> ] # or just one trigger for "operation":"not"
        # TODO: instantiate sub-triggers(FIRING_DEFIRING)

    def arm(self):
        # Calls constituent Trigger's arm methods.
        pass

    def on_trigger_change(self, firing, triggered):
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
