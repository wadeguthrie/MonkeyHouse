#! /usr/bin/python

import datetime
import json
import os


class Log(object):
    (TRIGGER_ACTIVATE, RULE_FIRE, HARDWARE_COMMUNICATION,
        REMOTE_NODE_COMMUNICATION, TARGRT_INPUT, USER_INPUT, ERROR,
        STATE) = range(8)
    (ERROR, WARNING, INFO) = range(3)
    __type_str = {TRIGGER_ACTIVATE: 'trigger_activate',
                  RULE_FIRE: 'rule_fire',
                  HARDWARE_COMMUNICATION: 'hardware_communication',
                  REMOTE_NODE_COMMUNICATION: 'remote_node_communication',
                  TARGRT_INPUT: 'target_input',
                  USER_INPUT: 'user_input',
                  STATE: 'state'}
    __severity_str = {ERROR: 'error',
                      WARNING: 'warning',
                      INFO: 'info'}
    __date_format = "%Y-%m-%d %H:%M:%S.%f"
    __FILE_TAILER = '\n]}'

    def __init__(self, executive, path, max_bytes_per_file, max_bytes_total,
                 verbose=False):
        self.executive = executive
        self.log_path = path  # Directory that contains the log files.
        self.max_bytes_per_file = max_bytes_per_file
        self.max_bytes_total = max_bytes_total
        self.verbose = verbose

        self.file = None  # For communication with currently open log file.
        self.bytes_this_file = 0  # Number of bytes in the current log file.
        self.bytes_total = 0  # Number of bytes among all log files.
        self.filenames = []
        self.first_entry = True

    """Context manager for logging."""

    def __enter__(self):
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # Gather the existing logfiles.
        if self.verbose:
            print "__enter__: Pre-existing files in %s:" % self.log_path
        for filename in sorted(os.listdir(self.log_path)):
            filepath = os.path.join(self.log_path, filename)
            self.filenames.append(filepath)
            self.bytes_total += os.stat(filepath).st_size
            if self.verbose:
                print "  %s (%d bytes)" % (filename,
                                           os.stat(filepath).st_size)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if self.file is not None:
            self.__close_log_file()
        if exception_type is not None:
            print 'EXCEPTION type: %r' % exception_type
            print 'EXCEPTION val: %s' % exception_value
            print 'Traceback: %r' % exception_traceback
        return True

    def __open_new_log_file(self, now):
        # File.
        filename = 'mkyhs-log-%04d-%02d%02d-%02d%02d-%02d-%06d' % (
            now.year, now.month, now.day,
            now.hour, now.minute, now.second, now.microsecond)
        filepath = os.path.join(self.log_path, filename)
        self.file = open(filepath, 'w')
        self.bytes_this_file = 0
        self.filenames.append(filepath)

        self.__write_to_file('{\n')  # File header.

        # Initial state.
        state = '"%s": {"time": "%s", "state": %s},\n"entries" : [\n' % (
                self.__type_str[self.STATE],
                datetime.datetime.strftime(now, Log.__date_format),
                json.dumps(self.executive.get_state(), indent=2))
        self.__write_to_file(state)

        self.first_entry = True

    def __close_log_file(self):
        self.__write_to_file(self.__FILE_TAILER)
        self.file.close()
        self.file = None

    def __write_to_file(self, string):
        self.file.write(string)
        self.file.flush()
        self.bytes_this_file += len(string)
        self.bytes_total += len(string)

    def log(self, severity, reason, entry):
        """
        entry (JSON-equivalent  data structure)
        """
        now = datetime.datetime.now()

        # If we don't have an open file, we need to either open the last one
        # (if there's room) or open a new one.
        if self.file is None:
            self.__open_new_log_file(now)

        # Write the log message.
        # strptime() <- string
        # strftime() -> string

        # Build and write the log string.
        outstring = ',\n' if not self.first_entry else ''
        outstring += '{ "time": "%s", "severity": "%s", "%s" : %s }' % (
            datetime.datetime.strftime(now, Log.__date_format),
            self.__severity_str[severity],
            self.__type_str[reason],
            json.dumps(entry))
        self.__write_to_file(outstring)
        self.first_entry = False

        # Close this file if it's full.
        if (self.bytes_this_file + len(self.__FILE_TAILER) >=
                self.max_bytes_per_file):
            self.__close_log_file()

        # Delete the oldest file if doing so will leave enough logging data.
        oldest_bytes = os.stat(self.filenames[0]).st_size
        if (self.bytes_total + len(self.__FILE_TAILER) - oldest_bytes >=
                self.max_bytes_total):
            filepath = self.filenames.pop(0)
            os.remove(filepath)
            self.bytes_total -= oldest_bytes
            if self.verbose:
                print 'Removed %s (%d bytes) to get %d bytes' % (
                    filepath, oldest_bytes, self.bytes_total)

# Main
if __name__ == '__main__':
    pass
