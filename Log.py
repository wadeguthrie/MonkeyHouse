#! /usr/bin/python

import datetime
import errno
import json
import os
import sys

import Executive

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

    def __init__(self, executive, path, max_bytes_per_file, max_bytes_total):
        self.log_path = path # Directory that contains the log files.
        self.file = None # For communication with currently open log file.
        self.bytes_this_file = 0 # Number of bytes in the current log file.
        self.total_bytes = 0 # Number of bytes among all log files.
        self.max_bytes_total = max_bytes_total
        self.executive = executive
        self.max_bytes_per_file = max_bytes_per_file
        self.filenames = []
        self.first_entry = True

    """Context manager for logging."""

    def __enter__(self):
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # Gather the existing logfiles.
        for filename in sorted(os.listdir(self.log_path)):
            filepath = os.path.join(self.log_path, filename)
            self.filenames.append(filepath)
            stat = os.stat(filepath)
            self.total_bytes += stat.st_size
        return self

    def __exit__ (self, exception_type, exception_value, exception_traceback):
        if self.file is not None:
            self.__close_log_file()
        if exception_type is not None:
            print 'EXCEPTION type: %r' % exception_type
            print 'EXCEPTION val: %s' % exception_value
            print 'Traceback: %r' % exception_traceback
        return True

    def __get_state(self, now):
        state = self.executive.get_state()
        outstring = '"%s": {"time": "%s", "state": %s},\n"entries" : [\n' % (
                self.__type_str[self.STATE],
                datetime.datetime.strftime(now, Log.__date_format),
                json.dumps(state, indent=2))
        self.first_entry = True  # TODO: do I need this?
        return outstring

    def __open_new_log_file(self, now):
        filename = 'mkyhs-log-%04d-%02d%02d-%02d%02d-%02d-%06d' % (
                now.year, now.month, now.day,
                now.hour, now.minute, now.second, now.microsecond)
        filepath = os.path.join(self.log_path, filename)
        self.filenames.append(filepath)
        try:
            self.file = open(filepath, 'w')
        except:
            self.__exit__(*sys.exc_info())
        else:
            file_header = '{\n'
            self.bytes_this_file = len(file_header) + len(self.__FILE_TAILER) 
            self.file.write(file_header)

    def __close_log_file(self):
        self.file.write(self.__FILE_TAILER)
        self.file.close()
        self.file = None

    def log(self, severity, reason, entry):
        """
        entry (JSON-equivalent  data structure)
        """
        now = datetime.datetime.now()

        # If we don't have an open file, we need to either open the last one
        # (if there's room) or open a new one.
        if self.file is None:
            state_string = self.__get_state(now)

            # Is there an existing logfile with room for more logging?
            lastsize = None
            lastpath = None
            if self.filenames:
                lastpath = self.filenames[-1]
                lastsize = os.stat(lastpath).st_size
                if lastsize + len(state_string) >= self.max_bytes_per_file:
                    lastpath = None

            if lastpath:
                self.bytes_this_file = lastsize
                self.file = open(lastpath, 'a')
            else:
                self.__open_new_log_file(now)

            self.file.write(state_string)
            self.bytes_this_file += len(state_string)
            self.total_bytes += len(state_string)

        # Write the log message.
        # strptime() <- string
        # strftime() -> string
        # ("%Y-%m-%d %H:%M:%S.%f")

        outstring = ',\n' if not self.first_entry else ''
        outstring += '{ "time": "%s", "severity": "%s", "%s" : %s }' % (
            datetime.datetime.strftime(now, Log.__date_format),
            self.__severity_str[severity],
            self.__type_str[reason],
            json.dumps(entry))
        self.file.write(outstring)
        self.file.flush()
        self.first_entry = False

        self.bytes_this_file += len(outstring)
        self.total_bytes += len(outstring)

        if self.bytes_this_file >= self.max_bytes_per_file:
            self.__close_log_file()

        # Delete the oldest file if doing so will leave enough logging data.

        oldest_bytes = os.stat(self.filenames[0]).st_size
        if self.total_bytes - oldest_bytes > self.max_bytes_total:
            filepath = self.filenames.pop(0)
            os.remove(filepath)
            self.total_bytes -= oldest_bytes

# Main
if __name__ == '__main__':
    pass
