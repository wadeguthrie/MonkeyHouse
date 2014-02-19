#! /usr/bin/python

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

    # TODO: trigger this manually
    def on_message(self, message):
        pass


class MessageTrigger(Trigger):
    def __init__(self, data, executive, parent, trigger_type):
        super(MessageTrigger, self).__init__(data, executive, parent,
                                             trigger_type)
        print 'MessageTrigger ctor'
        self.__template = data['template']

    def on_message(self, message):
        # TODO: This method matches the method against template (described,
        # below) to determine whether the incoming Message triggers,
        # de-triggers, or does nothing. If on_message changes the state of
        # the MessageTrigger, it logs and calls the parent's
        # on_trigger_change method.

        # If:
        # a field exists in the template but is set to None, the message
        #   must not have the field,
        # a field exists in the template and has a value, the message must
        #   match the value -- the value may be preceded by '=', '<', or '>'
        #   to indicate that the template matches if the incoming message's
        #   field is equal to, less than, or greater than the indicated value,
        # a field exists in the template and has an array as its value, the
        #   message may match any of the values in the array,
        # a field does not exist in the template, the message matches.
        pass


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
