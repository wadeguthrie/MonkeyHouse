#! /usr/bin/python

import json
import mock
import os
import shutil
import unittest

import Executive
import Log
import Trigger


class ParentFake(object):
    def on_trigger_change(self, firing, triggered):
        pass  # TODO: this should be a mock

class TriggerTestCase(unittest.TestCase):

    """Tests the MonkeyHouse |Trigger|."""

    def __init__(self, *args, **kwargs):
        """ Initializes the test.

        Just initializes the counter that will be used to mark the entries for
        debugging.

        """
        super(TriggerTestCase, self).__init__(*args, **kwargs)


    def testMessageTrigger(self):
        print '\n----- testMessageTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {"from": "groucho", "to": "harpo"}
        }

        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()

        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Simple match with one irrelevant element should activate.
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'what': 'IRRELEVANT-VALUE'})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # A bad match should deactivate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'groucho',
                            'to': 'BAD-VALUE',
                            'what': 'IRRELEVANT-VALUE'})
        assert not trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

        # Missing element ('to') should not trigger.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'groucho',
                            'what': 'IRRELEVANT-VALUE'})
        assert not trigger.is_triggered()
        assert log.log.call_count == 0
        assert parent.on_trigger_change.call_count == 0

        # Another simple match should activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'what': 'IRRELEVANT-VALUE'})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # Another missing element ('to') should not activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'groucho',
                            'what': 'IRRELEVEANT-VALUE'}) # Missing 'to'.
        assert trigger.is_triggered()
        assert log.log.call_count == 0
        assert parent.on_trigger_change.call_count == 0


    def testMessageTriggerNone(self):
        print '\n----- testMessageTriggerNone -----'
        # Tests '[]' as an expression of 'None'.
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {'from': 'groucho', 'what': [], 'to': 'harpo'}
        }
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Element 'what' does not exist, should activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo'})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # Element 'what' does exist but shouldn't, should deactivate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'what': 'ever'})
        assert not trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

        # Another activation, this time with an irrelevant value.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'groucho',
                            'to': 'harpo',
                            'foo': 'IRRELEVANT-VALUE'})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)


    def testMessageTriggerNumeric(self):
        print '\n----- testMessageTriggerNumeric -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {"from": "groucho",
                       "foo": ">3"}
        }
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Greater than 3; should ACTIVATE.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 4})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # Less than 3; should DE-activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 1})
        assert not trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

        # Equal to 3; should de-activate EXCEPT no trigger change -- should DO
        # NOTHING.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 3})
        assert not trigger.is_triggered()
        assert log.log.call_count == 0
        assert parent.on_trigger_change.call_count == 0

        # Greater than 3; should ACTIVATE.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 4})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # Less than 3; should DE-activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 1})
        assert not trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

    def testMessageTriggerArray(self):
        print '\n----- testMessageTriggerArray -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {'from': 'groucho',
                       'foo': ['<3', '==7', '>12']}
        }
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # <3, should ACTiVATE.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 1})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # Between 3 and 7; should DE-activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 4})
        assert not trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

        # == 7; should ACTIVATE
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 7})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # Between 7 and 12; should DE-activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 10})
        assert not trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

        # >12; should ACTIVATE.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({"from": "groucho", "foo": 15})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

    def testMessageTriggerDict(self):
        print '\n----- testMessageTriggerDict -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {'from': 'the_switch',
                       'announce_state': {'value': 'on'}}
        }
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        # Value ON; Should ACTIVATE.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'on'}})
        assert trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        # Set State (not Announce); Should do nothing.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'the_switch',
                            'set_state': {'value': 'on'}})
        assert trigger.is_triggered()
        assert log.log.call_count == 0
        assert parent.on_trigger_change.call_count == 0

        # Value OFF; Should DE-activate.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'off'}})
        assert not trigger.is_triggered()
        assert log.log.call_count == 1
        parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

        # Not from 'the-switch'; Should do nothing.
        parent.on_trigger_change.reset_mock()
        log.log.reset_mock()
        trigger.on_message({'from': 'another_switch',
                            'announce_state': {'value': 'on'}})
        assert not trigger.is_triggered()
        assert log.log.call_count == 0
        assert parent.on_trigger_change.call_count == 0


    def testTimerTrigger(self):
        print '\n----- testTimerTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'timer', 
          'time': 3 # TODO
        }
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)

    def testElapsedTimeTrigger(self):
        print '\n----- testElapsedTimeTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'elapsed-time', 
          'time': 3 # TODO
        }
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING_DEFIRING)

    def testAndTrigger(self):
        print '\n----- testAndTrigger -----'
        data = { 'name': 'foo', 'type': 'and'}
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)

    def testOrTrigger(self):
        print '\n----- testOrTrigger -----'
        data = { 'name': 'foo', 'type': 'or'}
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.DEFIRING)

    def testNotTrigger(self):
        print '\n----- testNotTrigger -----'
        data = { 'name': 'foo', 'type': 'not'}
        log = Log.Log(path="BogusPath",
                      max_bytes_per_file=0,
                      max_bytes_total=0,
                      verbose=False)
        log.log = mock.MagicMock()
        executive = Executive.Executive(log)
        parent = ParentFake()
        parent.on_trigger_change = mock.MagicMock()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)

    # TODO: invalid trigger

if __name__ == '__main__':
    unittest.main()  # runs all tests
