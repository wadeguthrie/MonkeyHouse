#! /usr/bin/python

import json
import os
import shutil
import unittest

import Executive
import Log

class LogTestCase(unittest.TestCase):
    HEADER_BYTES = 125
    ENTRY_BYTES = 91
    ENTRIES_PER_FILE = 3
    MAX_BYTES_FILE = (HEADER_BYTES +                      # For header.
                      (ENTRIES_PER_FILE * ENTRY_BYTES) +  # For entries.
                      (ENTRIES_PER_FILE - 1)) # For commas between entries.
    MAX_BYTES_TOTAL = MAX_BYTES_FILE * 6
    LOG_PATH = "TestLog"
    COUNTER_START = 10  # Hack: all entries will be same size since counter
                        # is always 2 digits.

    def __init__(self, *args, **kwargs):
        self.counter = self.COUNTER_START
        super(LogTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def __engine(self,
                 clean_start,
                 entry_count,
                 start_verification_at,
                 expected_file_count):
        executive = Executive.Executive()
        beyond_max_entry = self.counter + entry_count

        if clean_start and os.path.exists(self.LOG_PATH):
            # print "deleting %s" % self.LOG_PATH
            shutil.rmtree(self.LOG_PATH)  # Start by deleting the previous log
        with Log.Log(executive = executive,
                     path = self.LOG_PATH,
                     max_bytes_per_file = LogTestCase.MAX_BYTES_FILE,
                     max_bytes_total = LogTestCase.MAX_BYTES_TOTAL,
                     verbose=False) as log:
            while self.counter < beyond_max_entry:
                log.log(Log.Log.INFO, Log.Log.USER_INPUT, {"value" :
                                                           self.counter})
                self.counter += 1

        # Verify by reading the data back from the files.

        assert len(os.listdir(self.LOG_PATH)) == expected_file_count
        entries = []
        for filename in sorted(os.listdir(self.LOG_PATH)):
            filepath = os.path.join(self.LOG_PATH, filename)
            with file(filepath, 'r') as f:
                whole_file = f.read()
                data = json.loads(whole_file)
                for entry in data['entries']:
                    entries.append(entry['user_input']['value'])


        # Make sure we read all the entries we wrote.
        # TODO: doesn't deal with previous entries
        print "entries=%d, s.b. count=%d - start=%d = %d" % (len(entries),
                self.counter, start_verification_at, (self.counter -
                    start_verification_at))
        assert len(entries) == self.counter - start_verification_at

        # Make sure we read the specific entries we wrote (in the same order).
        for entry in entries:
            assert entry == start_verification_at
            start_verification_at += 1

    def test_log(self):
        print "\n-- test_log_empty_dir --"
        # 7 entries: 3 3 1=(216)
        self.__engine(clean_start = True,
                      entry_count = (self.ENTRIES_PER_FILE * 2) + 1,
                      start_verification_at = self.COUNTER_START,
                      expected_file_count = 3)

        # +3 entries = 11 entries: 3 3 1 3
        print "\n-- test_log_add_to_file --"
        self.__engine(clean_start = False,
                      entry_count = 3,
                      start_verification_at = self.COUNTER_START,
                      expected_file_count = 4)

        # +5 entries = 16 entries: 3 3 H3 3 3 2
        #    print "\n-- test_log_new_file_on_first_log --"
        #    self.__engine(clean_start = False,
        #                  entry_count = 5,
        #                  start_verification_at = self.COUNTER_START,
        #                  expected_file_count = 6)

        # +6 entries = 22 entries: x 3 H3 3 3 H3 3 2
        #    print "\n-- test_log_wrap_and_delete_file --"
        #    self.__engine(clean_start = False,
        #                  entry_count = 6,
        #                  start_verification_at = self.COUNTER_START + 3,
        #                  expected_file_count = 7)

if __name__ == '__main__':
    unittest.main() # runs all tests
