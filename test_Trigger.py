#! /usr/bin/python

import json
import mock
import os
import shutil
import unittest

import Executive
import Log
import Trigger
import TriggerFactory

# TODO: Include the message test in the user's guide
# TODO: test invalid triggers
# TODO: should an unarmed trigger save and announce its last state when armed?

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
        trigger.arm(True)
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
        trigger = TriggerFactory.TriggerFactory.new_trigger(
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
        trigger = TriggerFactory.TriggerFactory.new_trigger(
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
        trigger = TriggerFactory.TriggerFactory.new_trigger(
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
        trigger = TriggerFactory.TriggerFactory.new_trigger(
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
        trigger = TriggerFactory.TriggerFactory.new_trigger(
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
          'time': 'Wednesday 12:00:00'
        }
        trigger = TriggerFactory.TriggerFactory.new_trigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

    def testAndTrigger(self):
        print '\n----- testAndTrigger -----'
        data = {'name': 'foo',
                'type': 'and',
                'sub-triggers': [{'name': 'flip-1', 
                                  'type': 'message',
                                  'template': {'from': 'switch-1',
                                               'announce_state':{
                                                   'value': 'on'}}
                                 },
                                 {'name': 'flip-2', 
                                  'type': 'message',
                                  'template': {'from': 'switch-2',
                                               'announce_state': {
                                                   'value': 'on'}}
                                 }
                                ]
                }
        trigger = TriggerFactory.TriggerFactory.new_trigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()
        sub_1_trigger = trigger._triggers[0]
        sub_2_trigger = trigger._triggers[1]

        print '\n== flip-1 -> on, parent -> (unchanged) =='
        self.__setup_test(trigger)
        sub_1_trigger.on_message({'from': 'switch-1',
                                  'announce_state': {'value': 'on'}})

        assert sub_1_trigger.is_triggered()
        assert not sub_2_trigger.is_triggered()
        assert not trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== flip-2 -> on, parent-> on =='
        self.__setup_test(trigger)
        sub_2_trigger.on_message({'from': 'switch-2',
                                  'announce_state': {'value': 'on'}})

        assert sub_1_trigger.is_triggered()
        assert sub_2_trigger.is_triggered()
        assert trigger.is_triggered()
        assert self.__log.log.call_count == 2
        assert self.__parent.on_trigger_change.call_count == 1

        print '\n== flip-2 -> off, parent -> off =='
        self.__setup_test(trigger)
        sub_2_trigger.on_message({'from': 'switch-2',
                                  'announce_state': {'value': 'off'}})

        assert sub_1_trigger.is_triggered()
        assert not sub_2_trigger.is_triggered()
        assert not trigger.is_triggered()
        assert self.__log.log.call_count == 2
        assert self.__parent.on_trigger_change.call_count == 1

        print '\n== flip-1 -> off, parent -> (unchanged) =='
        self.__setup_test(trigger)
        sub_1_trigger.on_message({'from': 'switch-1',
                                  'announce_state': {'value': 'off'}})

        assert not sub_1_trigger.is_triggered()
        assert not sub_2_trigger.is_triggered()
        assert not trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

    def testOrTrigger(self):
        print '\n----- testOrTrigger -----'
        data = {'name': 'parent',
                'type': 'or',
                'sub-triggers': [{'name': 'flip-1', 
                                  'type': 'message',
                                  'template': {'from': 'switch-1',
                                               'announce_state':{
                                                   'value': 'on'}}
                                 },
                                 {'name': 'flip-2', 
                                  'type': 'message',
                                  'template': {'from': 'switch-2',
                                               'announce_state': {
                                                   'value': 'on'}}
                                 }
                                ]
                }
        trigger = TriggerFactory.TriggerFactory.new_trigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()
        sub_1_trigger = trigger._triggers[0]
        sub_2_trigger = trigger._triggers[1]

        print '\n== flip-1 -> on, parent -> on =='
        self.__setup_test(trigger)
        sub_1_trigger.on_message({'from': 'switch-1',
                                  'announce_state': {'value': 'on'}})

        assert sub_1_trigger.is_triggered()
        assert not sub_2_trigger.is_triggered()
        assert trigger.is_triggered()
        assert self.__log.log.call_count == 2
        assert self.__parent.on_trigger_change.call_count == 1

        print '\n== flip-2 -> on, parent (no change) =='
        self.__setup_test(trigger)
        sub_2_trigger.on_message({'from': 'switch-2',
                                  'announce_state': {'value': 'on'}})

        assert sub_1_trigger.is_triggered()
        assert sub_2_trigger.is_triggered()
        assert trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== flip-2 -> off, parent -> (no change) =='
        self.__setup_test(trigger)
        sub_2_trigger.on_message({'from': 'switch-2',
                                  'announce_state': {'value': 'off'}})

        assert sub_1_trigger.is_triggered()
        assert not sub_2_trigger.is_triggered()
        assert trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== flip-1 -> off, parent -> off =='
        self.__setup_test(trigger)
        sub_1_trigger.on_message({'from': 'switch-1',
                                  'announce_state': {'value': 'off'}})

        assert not sub_1_trigger.is_triggered()
        assert not sub_2_trigger.is_triggered()
        assert not trigger.is_triggered()
        assert self.__log.log.call_count == 2
        assert self.__parent.on_trigger_change.call_count == 1


    def testNotTrigger(self):
        print '\n----- testNotTrigger -----'
        data = { 'name': 'parent',
                 'type': 'not',
                 'sub-trigger': {'name': 'child', 
                                 'type': 'message',
                                 'template': {'from': 'the_switch',
                                              'announce_state': {
                                                  'value': 'on'}}
                                }
                }
        not_trigger = TriggerFactory.TriggerFactory.new_trigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        sub_trigger = not_trigger._triggers[0]
        assert not not_trigger.is_triggered()

        print '\n== sub: not->triggered, trigger: not->not =='
        self.__setup_test(not_trigger)
        sub_trigger.on_message({'from': 'the_switch',
                                'announce_state': {'value': 'on'}})

        assert sub_trigger.is_triggered()
        assert not not_trigger.is_triggered()
        assert self.__log.log.call_count == 1   # One state changed
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== sub: triggered->not, trigger: not->triggered =='
        self.__setup_test(not_trigger)
        sub_trigger.on_message({'from': 'the_switch',
                                'announce_state': {'value': 'off'}})

        assert not sub_trigger.is_triggered()
        assert not_trigger.is_triggered()
        assert self.__log.log.call_count == 2   # Both states changed
        self.__parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, True)

        print '\n== sub: not->triggered, trigger: triggered->not =='
        self.__setup_test(not_trigger)
        sub_trigger.on_message({'from': 'the_switch',
                                'announce_state': {'value': 'on'}})

        assert sub_trigger.is_triggered()
        assert not not_trigger.is_triggered()
        assert self.__log.log.call_count == 2   # Both states changed
        self.__parent.on_trigger_change.assert_called_once_with(
                Trigger.Trigger.FIRING, False)

    def testArm(self):
        print '\n----- testArm -----'
        data = { 'name': 'parent',
                 'type': 'message',
                 'template': {'from': 'the_switch',
                              'announce_state': { 'value': 'on'}}
                }
        trigger = TriggerFactory.TriggerFactory.new_trigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        print '\n== armed, triggered, announce =='
        self.__setup_test(trigger)
        trigger.arm(True)
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'on'}})
        self.__assert_activate(trigger)

        print '\n== dis-armed, de-triggered, no-announce  =='
        self.__setup_test(trigger)
        trigger.arm(False)
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'off'}})
        assert not trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== dis-armed, triggered, no-announce =='
        self.__setup_test(trigger)
        trigger.arm(False)
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'on'}})
        assert trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== armed, de-triggered, announce =='
        self.__setup_test(trigger)
        trigger.arm(True)
        trigger.on_message({'from': 'the_switch',
                            'announce_state': {'value': 'off'}})
        self.__assert_deactivate(trigger)

    def testZMessageArm(self):
        print '\n----- testMessageArm -----'
        data = { 'name': 'parent',
                 'type': 'message',
                 'template': {'from': 'the_switch',
                              'announce_state': { 'value': 'on'}}
                }
        trigger = TriggerFactory.TriggerFactory.new_trigger(
                data, self.__executive, self.__parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()

        print '\n== armed, triggered, announce =='
        self.__setup_test(trigger)
        trigger.on_message({'from': 'exec', 'operation': {'arm': 'yes'}})
        trigger.on_message({'from': 'exec', 'operation': {'trigger': 'yes'}})
        self.__assert_activate(trigger)

        print '\n== dis-armed, de-triggered, no-announce  =='
        self.__setup_test(trigger)
        trigger.on_message({'from': 'exec', 'operation': {'arm': 'no'}})
        trigger.on_message({'from': 'exec', 'operation': {'trigger': 'no'}})
        assert not trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== dis-armed, triggered, no-announce =='
        self.__setup_test(trigger)
        trigger.on_message({'from': 'exec', 'operation': {'arm': 'no'}})
        trigger.on_message({'from': 'exec', 'operation': {'trigger': 'yes'}})
        assert trigger.is_triggered()
        assert self.__log.log.call_count == 1
        assert self.__parent.on_trigger_change.call_count == 0

        print '\n== armed, de-triggered, announce =='
        self.__setup_test(trigger)
        trigger.on_message({'from': 'exec', 'operation': {'arm': 'yes'}})
        trigger.on_message({'from': 'exec', 'operation': {'trigger': 'no'}})
        self.__assert_deactivate(trigger)

if __name__ == '__main__':
    unittest.main()  # runs all tests
