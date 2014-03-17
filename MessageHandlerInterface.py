#! /usr/bin/python


class MessageHandlerInterface(object):
    """Base class for, well, MessageHandlers."""

    def on_message(self, message):
        """Method to handle MonkeyHouse Messages.

        Param:
            - message - dict structured like a MonkeyHouse Message.
        Returns: Nothing.
        """
        pass

if __name__ == '__main__':
    pass
