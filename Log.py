#! /usr/bin/python

import datetime
import json
import os


class Log(object):

    """ Logs statements for MonkeyHouse.

    Keeps the log as a collection of files in a circular list.  Old files are
    deleted to keep the total amount of data under a specified limit.  The
    current file is the recipient of log entries until the current file gets
    to a particular size; at this point, the current file is closed and a new
    file is opened.  All this happens under the hood, though; the user only
    needs to open the log (in a 'with' statement) and call |log|.

    The Log is setup as a context manager so that leaving the context manager
    block, for whatever reason, will close the logfile nicely.  The usage is
    something like the following:

        executive = Executive()  # MonkeyHouse Executive.

        with Log.Log(path='LogDirectory',
                     max_bytes_per_file=20 * 1024 * 1024,
                     max_bytes_total=1024 * 1024 * 1024,
                     verbose=False) as log:

            # The whole program being logged is inside here.
            log.set_executive(executive)

            log.log(Log.Log.INFO,
                    Log.Log.USER_INPUT,
                    {"value": self.counter})

    """
    # Severity values for calls to |log|.
    (ERROR, WARNING, INFO) = range(3)

    # Reason values for calls to |log|.
    (TRIGGER, RULE_FIRE, HARDWARE_COMMUNICATION,
        REMOTE_NODE_COMMUNICATION, TARGRT_INPUT, USER_INPUT, ERROR,
        STATE, OTHER) = range(9)

    __severity_str = {ERROR: 'error',
                      WARNING: 'warning',
                      INFO: 'info'}
    __type_str = {TRIGGER: 'trigger',
                  RULE_FIRE: 'rule_fire',
                  HARDWARE_COMMUNICATION: 'hardware_communication',
                  REMOTE_NODE_COMMUNICATION: 'remote_node_communication',
                  TARGRT_INPUT: 'target_input',
                  USER_INPUT: 'user_input',
                  STATE: 'state',
                  OTHER: 'other'}
    __date_format = "%Y-%m-%d %H:%M:%S.%f"
    __FILE_TAILER = '\n]}'

    # Constructor and context manager methods.

    def __init__(self, path, max_bytes_per_file, max_bytes_total,
                 verbose=False):
        """ Initialize the Log.

            path (string) - Directory to hold the log files.
            max_bytes_per_file (int) - Close the log file of this size and
                open a new one.
            max bytes_total (int) - Start deleting files when we go above
                this.
            verbose (bool) - True generates additional output.

        """

        self.__executive = None
        self.log_path = path  # Directory that contains the log files.
        self.max_bytes_per_file = max_bytes_per_file
        self.max_bytes_total = max_bytes_total
        self.verbose = verbose

        self.file = None  # For communication with currently open log file.
        self.bytes_this_file = 0  # Number of bytes in the current log file.
        self.bytes_total = 0  # Number of bytes among all log files.
        self.filenames = []
        self.first_entry = True

    def __enter__(self):
        """ Launches the context manager.

        Gathers information on any existing logfiles.  Doesn't open a logfile
        (don't do that until the first thing is logged).

        """
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
        """ Leaves the context manager.

        Writes tailer (so that the log contains a complete and proper JSON
        object) and closes any open logfile.

        Parameters are prescribed by the Python specification and they
        represent a Python exception.

        """
        if self.file is not None:
            self.__close_log_file()
        if exception_type is not None:
            print 'EXCEPTION type: %r' % exception_type
            print 'EXCEPTION val: %s' % exception_value
            print 'Traceback: %r' % exception_traceback
        return True

    # Public methods.

    def log(self, severity, reason, entry):
        """ Writes an entry to the log file.  Does bookkeeping.

        Opens a logfile if none is open.  Builds a JSON-compatible string with
        the entry, the time, and the severity of the message.  Writes the
        string to the file, and does necessary bookkeeping.  Closes the log
        file if it's too big.  Deletes the oldest logfile in the series if we
        can do this and still have enough data saved.

            severity (enum) - INFO, WARNING, or ERROR (found as an enum in the
                definition of the |Log| class.
            reason (enum) - classification of the message (found as an enum in
                the definition of the |Log| class.
            entry (JSON-equivalent  data structure) - the thing to write to
                the logfile.  This is a JSON structure in order to make it
                trivial to log MonkeyHouse |Message| objects (in particular,
                |set_state| messages) and to enable MonkeyHouse to read and
                parse a logfile in order to play it back.  Unstructured
                entries can be use a structure like this:
                    log.log(Log.Log.INFO, Log.Log.OTHER,
                            {'string': 'whatever you want'})

        Use this as follows:

            log.log(Log.Log.ERROR, Log.Log.ERROR, {'string': 'whatever'})

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

    def set_executive(self, executive):
        """ Sets the executive for the log.

            executive (Executive) - Used to retrieve current status.

        """
        self.__executive = executive

    # Private methods.

    def __open_new_log_file(self, now):
        """ Opens a new log file.

        Names the file (based on the current time -- makes sorting pretty
        easy).  Gets the current state, in a JSON-equivalent data structure,
        from the executive and writes it to the file.

        now (datetime) - The current time; used for naming the new file.

        """
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
                json.dumps(self.__executive.get_state(), indent=2))
        self.__write_to_file(state)

        self.first_entry = True

    def __close_log_file(self):
        """ Writes the tailer to and closes the log file."""
        self.__write_to_file(self.__FILE_TAILER)
        self.file.close()
        self.file = None

    def __write_to_file(self, string):
        """Writes to the log file and keeps track of statistics.

        string (string) - The string to write to the file.

        """
        self.file.write(string)
        self.file.flush()
        self.bytes_this_file += len(string)
        self.bytes_total += len(string)

# Main
if __name__ == '__main__':
    pass
