#! /usr/bin/python

import json
import os
import shutil
import unittest

import Executive  # TODO: Mock
import Trigger

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

    def testMessageTrigger(self):
        print '\n----- testMessageTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'message',
          'template': {"from": "groucho",
                       "to": "harpo"} # TODO
        }
        executive = Executive.Executive()
        parent = ParentFake()
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)
        assert not trigger.is_triggered()
        trigger.on_message({"from": "groucho",
                            "to": "curly"})
        assert not trigger.is_triggered()
        trigger.on_message({"from": "groucho",
                            "to": "harpo"})
        assert trigger.is_triggered()

    def testTimerTrigger(self):
        print '\n----- testTimerTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'timer', 
          'time': 3 # TODO
        }
        executive = Executive.Executive()
        parent = 2 # TODO
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)

    def testElapsedTimeTrigger(self):
        print '\n----- testElapsedTimeTrigger -----'
        data = {
          'name': 'foo', 
          'type': 'elapsed-time', 
          'time': 3 # TODO
        }
        executive = Executive.Executive()
        parent = 2 # TODO
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING_DEFIRING)

    def testAndTrigger(self):
        print '\n----- testAndTrigger -----'
        data = { 'name': 'foo', 'type': 'and'}
        executive = Executive.Executive()
        parent = 2 # TODO
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)

    def testOrTrigger(self):
        print '\n----- testOrTrigger -----'
        data = { 'name': 'foo', 'type': 'or'}
        executive = Executive.Executive()
        parent = 2 # TODO
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.DEFIRING)

    def testNotTrigger(self):
        print '\n----- testNotTrigger -----'
        data = { 'name': 'foo', 'type': 'not'}
        executive = Executive.Executive()
        parent = 2 # TODO
        trigger = Trigger.TriggerFactory.NewTrigger(
                data, executive, parent, Trigger.Trigger.FIRING)

    # TODO: invalid trigger

if __name__ == '__main__':
    unittest.main()  # runs all tests
