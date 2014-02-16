#! /usr/bin/python

import json
import os
import shutil
import unittest

import Executive
import Log

class LogTestCase(unittest.TestCase):
    HEADER_BYTES = 113
    ENTRY_BYTES = 75
    MAX_BYTES_FILE = HEADER_BYTES + 3 * ENTRY_BYTES
    MAX_BYTES_TOTAL = MAX_BYTES_FILE * 6
    LOG_PATH = "TestLog"

    def __init__(self, *args, **kwargs):
        self.counter = 10  # Hack: all entries will be same size since counter
                           # is always 2 digits.
        super(LogTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # TODO: size file=header+3 entries; total_max = 6 files = 18 entries
    # TODO: rmdir, += 8 entries =  8 entries: 3 3 2
    # TODO:        += 4 entries = 12 entries: 3 3 H3 3
    # TODO:        += 5 entries = 17 entries: 3 3 H3 3 3 2
    # TODO:        += 6 entries = 23 entries: x 3 H3 3 3 H3 3 2

    def test_log_empty_dir(self): # ALL tests must start with 'test'
        executive = Executive.Executive()
        counter_start = self.counter
        entries = 8
        beyond_max_entry = counter_start + entries

        if os.path.exists(self.LOG_PATH):
            shutil.rmtree(self.LOG_PATH)  # Start by deleting the previous log
        with Log.Log(executive = executive,
                     path = self.LOG_PATH,
                     max_bytes_per_file = LogTestCase.MAX_BYTES_FILE,
                     max_bytes_total = LogTestCase.MAX_BYTES_TOTAL) as log:
            while self.counter < beyond_max_entry:
                log.log(Log.Log.INFO, Log.Log.USER_INPUT, {"value" :
                                                           self.counter})
                self.counter += 1

        # Verify

        assert len(os.listdir(self.LOG_PATH)) == 3
        entries = []
        for filename in os.listdir(self.LOG_PATH):
            filepath = os.path.join(self.LOG_PATH, filename)
            print "\n-- %s --" % filepath
            with file(filepath, 'r') as f:
                stuff = f.read()
                print "%r" % json.loads(stuff)

if __name__ == '__main__':
    unittest.main() # runs all tests
