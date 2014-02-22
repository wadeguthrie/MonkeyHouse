#! /usr/bin/python

import json
import mock
import os
import shutil
import unittest

import Executive
import Log
import Trigger


# Basis for mocks found below.
class ParentFake(object):
    def on_trigger_change(self, firing, triggered):
        pass

class TriggerTestCase(unittest.TestCase):

    """Tests the MonkeyHouse |Trigger|."""

    def __init__(self, *args, **kwargs):
        """ Initializes the test.

        Just initializes the counter that will be used to mark the entries for
        debugging.

        """
        super(TriggerTestCase, self).__init__(*args, **kwargs)


    def setUp(self):
        self.__log = Log.Log(path="BogusPath",
                             max_bytes_per_file=0,
                             max_bytes_total=0,
                             verbose=False)
        self.__log.log = mock.MagicMock()
        self.__executive = Executive.Executive(self.__log)
        self.__parent = ParentFake()
        self.__parent.on_trigger_change = mock.MagicMock()
        self.__previous_state = None


    def __setup_test(self, trigger):
        self.__log.log.reset_mock()
        self.__parent.on_trigger_change.reset_mock()
        self.__previous_state = trigger.is_triggered()

    def __assert_activate(self, trigger):
        assert trigger.is_triggered()
        assert self.__log.log.call_count == 1
        self.__parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

    def __assert_deactivate(self, trigger):
        assert not trigger.is_triggered()
        assert self.__log.log.call_count == 1
        self.__parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

    def __assert_no_activation_change(self, trigger):
        assert trigger.is_triggered() == self.__previous_state
        assert self.__log.log.call_count == 0
        assert self.__parent.on_trigger_change.call_count == 0

    def testMessageTrigger(self):
        print '\n----- testMessageTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {"from": "groucho", "to": "harpo"}
        }
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Simple match with one irrelevant element should activate.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'what': 'IRRELEVANT-VALUE'})
        self.__assert_activate(trigger)

        # A bad match should deactivate.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'to': 'BAD-VALUE',
                            'what': 'IRRELEVANT-VALUE'})
        self.__assert_deactivate(trigger)

        # A bad match should deactivate EXCEPT, trigger doesn't change.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'to': 'BAD-VALUE',
                            'what': 'IRRELEVANT-VALUE'})
        self.__assert_no_activation_change(trigger)

        # Missing element ('to') should not trigger.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'what': 'IRRELEVANT-VALUE'})
        self.__assert_no_activation_change(trigger)

        # Another simple match should activate.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'what': 'IRRELEVANT-VALUE'})
        self.__assert_activate(trigger)

        # Another missing element ('to') should not activate.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'what': 'IRRELEVEANT-VALUE'}) # Missing 'to'.
        self.__assert_no_activation_change(trigger)


    def testMessageTriggerNone(self):
        print '\n----- testMessageTriggerNone -----'
        # Tests '[]' as an expression of 'None'.
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {'from': 'groucho', 'what': [], 'to': 'harpo'}
        }
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Element 'what' does not exist, should activate.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo'})
        self.__assert_activate(trigger)

        # Element 'what' does exist but shouldn't, should deactivate.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'what': 'ever'})
        self.__assert_deactivate(trigger)

        # Another activation, this time with an irrelevant value.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'foo': 'IRRELEVANT-VALUE'})
        self.__assert_activate(trigger)


    def testMessageTriggerNumeric(self):
        print '\n----- testMessageTriggerNumeric -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {"from": "groucho",
                       "foo": ">3"}
        }
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Greater than 3; should ACTIVATE.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 4})
        self.__assert_activate(trigger)

        # Less than 3; should DE-activate.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 1})
        self.__assert_deactivate(trigger)

        # Equal to 3; should de-activate EXCEPT no trigger change -- should DO
        # NOTHING.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 3})
        self.__assert_no_activation_change(trigger)

        # Greater than 3; should ACTIVATE.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 4})
        self.__assert_activate(trigger)

        # Less than 3; should DE-activate.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 1})
        self.__assert_deactivate(trigger)

    def testMessageTriggerArray(self):
        print '\n----- testMessageTriggerArray -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {'from': 'groucho',
                       'foo': ['<3', '==7', '>12']}
        }
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # <3, should ACTiVATE.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 1})
        self.__assert_activate(trigger)

        # Between 3 and 7; should DE-activate.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 4})
        self.__assert_deactivate(trigger)

        # == 7; should ACTIVATE
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 7})
        self.__assert_activate(trigger)

        # Between 7 and 12; should DE-activate.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 10})
        self.__assert_deactivate(trigger)

        # >12; should ACTIVATE.
        self.__setup_test(trigger)
        trigger.on_message({"from": "groucho", "foo": 15})
        self.__assert_activate(trigger)

    def testMessageTriggerDict(self):
        print '\n----- testMessageTriggerDict -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {'from': 'the_switch',
                       'announce_state': {'value': 'on'}}
        }
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Value ON; Should ACTIVATE.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'on'}})
        self.__assert_activate(trigger)

        # Set State (not Announce); Should do nothing.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'the_switch',
                            'set_state': {'value': 'on'}})
        self.__assert_no_activation_change(trigger)

        # Value OFF; Should DE-activate.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'off'}})
        self.__assert_deactivate(trigger)

        # Not from 'the-switch'; Should do nothing.
        self.__setup_test(trigger)
        trigger.on_message({'from': 'another_switch',
                            'announce_state': {'value': 'on'}})
        self.__assert_no_activation_change(trigger)


    def testTimerTrigger(self):
        print '\n----- testTimerTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'timer', 
          'time': 3 # TODO
        }
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

    def testElapsedTimeTrigger(self):
        print '\n----- testElapsedTimeTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'elapsed-time', 
          'time': 3 # TODO
        }
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

    def testAndTrigger(self):
        print '\n----- testAndTrigger -----'
        data = { 'name': 'foo', 'type': 'and'}
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

    def testOrTrigger(self):
        print '\n----- testOrTrigger -----'
        data = { 'name': 'foo', 'type': 'or'}
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

    def testNotTrigger(self):
        print '\n----- testNotTrigger -----'
        data = { 'name': 'foo', 'type': 'not'}
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

    # TODO: invalid trigger

if __name__ == '__main__':
    unittest.main()  # runs all tests
