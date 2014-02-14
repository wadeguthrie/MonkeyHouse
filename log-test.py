#! /usr/bin/python

import unittest

import Executive
import Log

class LogTestCase(unittest.TestCase):
  def setUp(self):
    #if not EventTestCase.log:
    #  EventTestCase.log = Logger.Logger.Instance()
    #  EventTestCase.log.Init('_test.log', True)  # Only Init once per run.
    pass

  def tearDown(self):
    #self._log.Print(Logger.Type.ERROR,
    #                'Date: %s doesn\'t match a valid date format', date)
    # optional
    pass

  def test_makeevent(self): # ALL tests must start with 'test'
    executive = Executive.Executive()
    log = Log.Log(executive = executive,
                  path = "TestLog",
                  max_bytes_per_file  = 20 * 1024 * 1024,
                  max_bytes_total = 1024 * 1024 * 1024)
    log.log(Log.Log.INFO, Log.Log.USER_INPUT, {"name" : "foo"})
    assert True

if __name__ == '__main__':
    unittest.main() # runs all tests
