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
            TARGRT_INPUT: 'targrt_input',
            USER_INPUT: 'user_input',
            STATE: 'state'}
    __severity_str = {ERROR: 'error',
            WARNING: 'warning',
            INFO: 'info'}
    __date_format = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, executive, path, max_bytes_per_file, max_bytes_total):
        self.log_path = path # describes the directory that contains the log files.
        self.file = None # file descriptor used to communicate with the currently open log file.
        self.bytes_this_file = 0 # count of the number of bytes written to the current log file.
        self.total_bytes = 0 # count of the number of bytes written to the current log file.
        self.max_bytes_total = max_bytes_total # number of bytes distributed across the logfiles that causes the oldest logfile to be deleted.
        self.executive = executive # Needed to get system state.
        self.max_bytes_per_file = max_bytes_per_file
        self.filenames = []
        self.first_entry = True

    """Context manager for logging."""

    def __enter__(self):
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # Gather the existing logfiles.
        lastpath = None
        lastsize = 0
        for filename in sorted(os.listdir(self.log_path)):
            filepath = os.path.join(self.log_path, filename)
            self.filenames.append(filepath)
            stat = os.stat(filepath)
            self.total_bytes += stat.st_size
            lastpath = filepath
            lastsize = stat.st_size

        # Open either the most recent one or a new one.
        if lastpath is None or lastsize >= self.max_bytes_per_file:
            self.__open_new_log_file()
        else:
            self.bytes_this_file = lastsize
            try:
                self.file = open(lastpath, 'a')
            except:
                self.__exit__(*sys.exc_info())
            else:
                self.__save_state()
        return self

    def __exit__ (self, exception_type, exception_value, exception_traceback):
        if self.file is not None:
            self.__close_log_file()
        if exception_type is not None:
            print 'EXCEPTION type: %r' % exception_type
            print 'EXCEPTION val: %s' % exception_value
            print 'Traceback: %r' % exception_traceback
        return True

    def __save_state(self, now=None):
        if now is None:
            now = datetime.datetime.now()
        state = self.executive.get_state()
        outstring = '"%s": {"time": "%s", "state": %s},\n"entries" : [\n' % (
                self.__type_str[self.STATE],
                datetime.datetime.strftime(now, Log.__date_format),
                json.dumps(state, indent=2))
        self.first_entry = True
        self.file.write(outstring)
        self.bytes_this_file += len(outstring)
        self.total_bytes += len(outstring)

    def __open_new_log_file(self):
        now = datetime.datetime.now()
        filename = 'mkyhs-log-%04d-%02d%02d-%02d%02d-%02d-%06d' % (
                now.year, now.month, now.day, now.hour, now.minute, now.second,
                now.microsecond)
        filepath = os.path.join(self.log_path, filename)
        self.filenames.append(filepath)
        try:
            self.file = open(filepath, 'w')
        except:
            self.__exit__(*sys.exc_info())
        else:
            self.bytes_this_file = 2
            self.file.write('{\n')
            self.__save_state(now)

    def __close_log_file(self):
        self.file.write(']}')
        self.file.close()
        self.file = None

    def log(self, severity, reason, entry):
        """
        entry (JSON-equivalent  data structure)
        """
        print "LOGGING"
        # strptime() <- string
        # strftime() -> string
        # ("%Y-%m-%d %H:%M:%S.%f")

        # TODO: what to do about severity
        now = datetime.datetime.now()
        outstring = ',' if not self.first_entry else ''
        outstring += '{ "time": "%s", "%s" : %s }\n' % (
            datetime.datetime.strftime(now, Log.__date_format),
            self.__type_str[reason],
            json.dumps(entry))
        self.file.write(outstring)
        self.file.flush()
        self.first_entry = False

        self.bytes_this_file += len(outstring)
        self.total_bytes += len(outstring)
        if self.bytes_this_file > self.max_bytes_per_file:
            self.__close_log_file()
            self.__open_new_log_file()

        # TODO: do this in a loop
        stat = os.stat(self.filenames[0])
        oldest_bytes = stat.st_size

        # Delete the oldest file if we can delete it and still stay over the
        # max.
        if self.total_bytes - oldest_bytes > self.max_bytes_total:
            filepath = self.filenames.pop(0)
            os.remove(filepath)

# Main
if __name__ == '__main__':
    pass
