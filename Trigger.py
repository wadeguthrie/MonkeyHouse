#! /usr/bin/python

import MessageHandlerInterface


class Trigger(MessageHandlerInterface):
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
        self.__name  # TODO read out of 'data'
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

# Main
if __name__ == '__main__':
    pass
