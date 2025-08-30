import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import uuid
import time
import os
import datetime
import traceback
from collections import OrderedDict
from dataclasses import dataclass, field

try:
    from termcolor import colored
except ModuleNotFoundError:
    pass

#
# logging levels
#

CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

_levelToName = logging._levelToName

_nameToLevel = logging._nameToLevel


def get_level(level):
    """
    Get information about a logging level

    :param level: (str|int) the integer or string representation of a logging level
    :return: this function will return a tuple of (int, str) representing the level passed in
    """

    try:
        level_int = _nameToLevel[level]
        return level_int, level
    except KeyError:
        pass

    try:
        level_nm = _levelToName[level]
        return level, level_nm

    except KeyError:
        raise KeyError(f'Level not found: {level}')


def level_value(level):
    """
    Convenience function to return integer value of a logging level

    :param level: (str|int) the integer or string representation of a logging level
    :return: (int) value of logging level
    """
    return get_level(level)[0]


def level_name(level):
    """
    Convenience function to return name of a logging level

    :param level: (str|int) the integer or string representation of a logging level
    :return: (str) name of logging level
    """
    return get_level(level)[1]


def get_level_color(level):
    """
    Return the name of the color for a given logging level, used for printing colorized log entries to a console

    :param level: (str|int) the integer or string representation of a logging level
    :return: (str)
    """
    level_int = get_level(level)[0]

    if level_int < INFO:
        return 'white'
    if level_int < WARNING:
        return 'green'
    if level_int < ERROR:
        return 'yellow'

    return 'red'


#
# logging subclasses
#

class KwogFormatter(logging.Formatter):
    """A subclass of logging.Formatter to be used with a log handler"""

    def format(self, record):

        # rewrite as literal, leave like this for quick testing OrderedDict
        source = OrderedDict()
        source['time'] = datetime.datetime.fromtimestamp(record.created)
        source['log'] = record.module
        source['level'] = record.levelname
        source['path'] = record.pathname
        source['func'] = record.funcName
        source['lineno'] = record.lineno

        entry = OrderedDict()
        entry['msg'] = record.msg
        entry.update(record.args['entry'])

        if record.exc_info:
            exc = OrderedDict()
            exc['class'] = KwogEntry._escape_value(record.exc_info[0].__name__)
            exc['msg'] = KwogEntry._escape_value(str(record.exc_info[1]))
            exc['traceback'] = KwogEntry._format_value(traceback.format_tb(record.exc_info[2]))

        else:
            exc = None

        return str(KwogEntry(record.args['context'], source, entry, exc))


class KwogAdapter(logging.LoggerAdapter):
    """A subclass of logging.LoggerAdapter to be used with a log handler

    This adapter is designed to add contextual logging data via key value pairs to each entry over the lifetime of this
    object.

    """

    def __init__(self, logger, **context):
        """
        Initialize the adapter with a logger and context data

        :param logger: The logger to be used (typical returned by logging.getLogger)
        :param context: key word arguments to be added as context data to each entry logged by this object
        """

        self.logger = logger
        self.context = context
        self.timers = {}

    def generate_id(self, field_name='uuid'):
        """
        Generate a unique id to be added to the context logger. It uses the built in uuid.uuid3 method as passes in
        the current unix epoch time and pid of the current running process to guarantee uniqueness on the machine
        running this logger

        :param field_name: the unique id will be added to the loggers context namespace with this name
        :return: (str) string representation of generated uuid
        """
        _id = str(uuid.uuid3(uuid.uuid4(), f'{time.time()}-{os.getpid()}'))
        self.context[field_name] = _id
        return _id

    def process(self, msg, args, kwargs):
        try:
            exc_info = kwargs['exc_info']
            del kwargs['exc_info']
        except KeyError:
            exc_info = None

        args = [{'context': self.context, 'entry': kwargs}]

        return msg, args, {'exc_info': exc_info}

    def log(self, level, msg, *args, **kwargs):
        """
        Write a log entry with a dynamically supplied level

        :param level: (int) logging level to be used
        :param msg: (str) this string will be logged on the entry as the value for the msg key
        :param args: to be passed to underlying logging method (KwogAdapter.logger._log)
        :param kwargs: key word data to be passed to log entry
        :return: None
        """

        if self.isEnabledFor(level):
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(level, msg, *args, **kwargs)

    def log_exc(self, level, msg, *args, **kwargs):
        """
        Write a log entry with a dynamically supplied level and pass exc_info=True to underlying logger to capture
        exception and traceback information.

        :param level: (int) logging level to be used
        :param msg: (str) this string will be logged on the entry as the value for the msg key
        :param args: to be passed to underlying logging method (KwogAdapter.logger._log)
        :param kwargs: key word data to be passed to log entry
        :return: None
        """
        if self.isEnabledFor(level):
            msg, args, kwargs = self.process(msg, args, kwargs)
            kwargs['exc_info'] = True
            self.logger._log(level, msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        """
        Write a log entry with DEBUG logging level

        :param msg: (str) this string will be logged on the entry as the value for the msg key
        :param args: to be passed to underlying logging method (KwogAdapter.logger._log)
        :param kwargs: key word data to be passed to log entry
        :return: None
        """
        if self.isEnabledFor(DEBUG):
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(DEBUG, msg, *args, **kwargs)
    
    def debug_exc(self, msg, *args, **kwargs):
        """
        Write a log entry with DEBUG logging level and pass exc_info=True to underlying logger to capture
        exception and traceback information.

        :param msg: (str) this string will be logged on the entry as the value for the msg key
        :param args: to be passed to underlying logging method (KwogAdapter.logger._log)
        :param kwargs: key word data to be passed to log entry
        :return: None
        """
        if self.isEnabledFor(DEBUG):
            msg, args, kwargs = self.process(msg, args, kwargs)
            kwargs['exc_info'] = True
            self.logger._log(DEBUG, msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug except use log level INFO
        """
        if self.isEnabledFor(INFO):
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(INFO, msg, *args, **kwargs)
    
    def info_exc(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug_exc except use log level INFO
        """
        if self.isEnabledFor(INFO):
            msg, args, kwargs = self.process(msg, args, kwargs)
            kwargs['exc_info'] = True
            self.logger._log(INFO, msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug except use log level WARNING
        """
        if self.isEnabledFor(WARNING):
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(WARNING, msg, *args, **kwargs)
    
    def warning_exc(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug_exc except use log level WARNING
        """
        if self.isEnabledFor(WARNING):
            msg, args, kwargs = self.process(msg, args, kwargs)
            kwargs['exc_info'] = True
            self.logger._log(WARNING, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.warning_exc
        """
        if self.isEnabledFor(WARNING):
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(WARNING, msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug except use log level ERROR
        """
        if self.isEnabledFor(ERROR):
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(ERROR, msg, *args, **kwargs)
    
    def error_exc(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug_exc except use log level ERROR
        """
        if self.isEnabledFor(ERROR):
            msg, args, kwargs = self.process(msg, args, kwargs)
            kwargs['exc_info'] = True
            self.logger._log(ERROR, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug except use log level CRITICAL
        """
        if self.isEnabledFor(CRITICAL):
            msg, args, kwargs = self.process(msg, args, kwargs)
            self.logger._log(CRITICAL, msg, *args, **kwargs)

    def critical_exc(self, msg, *args, **kwargs):
        """
        Same documentation as KwogAdapter.debug_exc except use log level CRITICAL
        """
        if self.isEnabledFor(CRITICAL):
            msg, args, kwargs = self.process(msg, args, kwargs)
            kwargs['exc_info'] = True
            self.logger._log(CRITICAL, msg, *args, **kwargs)

    def timer_start(self, name, **kwargs):
        """
        Start an instance of KwogTimer and add to this object's timers dict using <name> as the key
        and then write an INFO level log entry with the name of the timer and its start time on the entry using
        keys timer_name and start_time respectively as additional keywords

        :param name:(str)
        :param kwargs: keywords to be passed to log entry
        :return: None
        """
        self.timers[name] = KwogTimer(name)
        kwargs.update(dict(self.timers[name]))
        del kwargs['elapsed_time']
        del kwargs['end_time']

        if self.isEnabledFor(INFO):
            msg, args, kwargs = self.process('TIMER_STARTED', [], kwargs)
            self.logger._log(INFO, msg, *args, **kwargs)

    def timer_stop(self, name, **kwargs):
        """
        Stop the <name> instance of KwogTimer on this object and then write an INFO level log entry with the name of the
        timer, its start time, elapsed time and end time on the entry using keys timer_name, start_time, elapsed_time
        and end_time respectively as additional keywords

        :param name:(str)
        :param kwargs: keywords to be passed to log entry
        :return: None
        """
        try:
            self.timers[name].stop()
            kwargs.update(dict(self.timers[name]))
        except KeyError:
            raise ValueError(f'No timer named: {name}')

        if self.isEnabledFor(INFO):
            msg, args, kwargs = self.process('TIMER_STOPPED', [], kwargs)
            self.logger._log(INFO, msg, *args, **kwargs)

    def timer_checkpoint(self, name, **kwargs):
        """
        Get the time elapsed for <name> instance of KwogTimer on this object and then write an INFO level log entry with
        the name of the timer, its start time and elapsed time on the entry using keys timer_name, start_time,
        and elapsed_time respectively as additional keywords

        :param name:(str)
        :param kwargs: keywords to be passed to log entry
        :return: None
        """
        try:
            kwargs.update(dict(self.timers[name]))
            del kwargs['end_time']
        except KeyError:
            raise ValueError(f'No timer named: {name}')

        if self.isEnabledFor(INFO):
            msg, args, kwargs = self.process('TIMER_CHECKPOINT', [], kwargs)
            self.logger._log(INFO, msg, *args, **kwargs)


#
# initialize logger convenience functions
#

def rotate_by_size(name, path, level=DEBUG, max_bytes=5242880, backups=5, **context):
    """
    Initialize an instance of KwogAdapter using built in RotatingFileHandler configured to rotate file by size

    :param name: The name of the logger to be fetched with logging.getLogger
    :param path: path to the log file
    :param level: the logging level to instantiate the logger with
    :param max_bytes: rotate the log file after it has reached this size
    :param backups: keep at most this many backup log files
    :param context: key word arguments to provide context data when instantiating KwogAdapter
    :return: KwogAdapter
    """
    fh = RotatingFileHandler(path, maxBytes=max_bytes, backupCount=backups)
    f = KwogFormatter()
    fh.setFormatter(f)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    return KwogAdapter(logger, **context)


def rotate_by_time(name, path, level=DEBUG, when='midnight', interval=1, utc=False, at_time=None, backups=5, **context):
    """
    Initialize an instance of KwogAdapter using built in TimedRotatingFileHandler configured to rotate file by size

    :param name: The name of the logger to be fetched with logging.getLogger
    :param path: path to the log file
    :param level: the logging level to instantiate the logger with
    :param when: when to rotate the file, see built in logging.handlers.TimedRotatingFileHandler for more info
    :param interval: interval to rotate the file, see built in logging.handlers.TimedRotatingFileHandler for more info
    :param utc: if True use UTC time to determine when to rotate, else use local time
    :param at_time: time to rotate the log file, see built in logging.handlers.TimedRotatingFileHandler for more info
    :param backups: keep at most this many backup log files
    :param context: key word arguments to provide context data when instantiating KwogAdapter
    :return: KwogAdapter
    """
    fh = TimedRotatingFileHandler(path, when=when, interval=interval, backupCount=backups, utc=utc, atTime=at_time)
    f = KwogFormatter()
    fh.setFormatter(f)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    return KwogAdapter(logger, **context)


def new(name, unique_id=None, extend=None, **context):
    """
    Return a new instance of logger [name] with new context [context]. Optionally add a unique id by passing
    a fieldname to unique_id or an instance of a KwogAdapter to extend to extend the context provided to this instance

    :param name: (str) the name of the logger to get
    :param unique_id: (str) if provided use .generate_id() to add an id to this logger using this as the field name
    :param extend: (KwogAdapter) if provided update **context with context from this logger
    :param context: additional kwargs to add to the new logger instance's context

    :return:KwogAdapter
    """
    if extend is not None:
        # retain key order with parent keys before new context
        context = {**extend.context, **context}

    logger = KwogAdapter(logging.getLogger(name), **context)
    if unique_id is not None:
        logger.generate_id(unique_id)

    return logger


#
# Kwogger classes
#


class KwogEntry:
    """
    The KwogEntry class has four "namespaces" for storing key/value data in each log entry. The values can be of
    any type but only None, bool, int, float and str and preserved when serializing to the log file and parsing
    afterword. Any other value will be cast to a string with str before serializing.

    namespaces:
        context
            the kwargs attached to the logging adapter, this data is added to each log entry over the
            lifetime of the KwogAdapter object to correlate ane search multiple entries
        source
            information about the log entry such as timestamp, level, module and line number
        entry
            The first string argument to the logging call (info, error_exc, etc) is places in this namespace under
            field name 'msg'. All other kwargs from that call are set here. Order is preserved with OrderedDict
        exception
            When handling and exception this contains three fields, the 'class' name of the exception,
            the exception's 'msg' and 'traceback'

    When serialized before writing the namespaces are abbreviated to c, s, e and exc respectively.

    example:

        [written to log file as a single line, using breaks here for readability]

        s.time="2021-01-05 23:28:23.253117"
        s.log="test_kwogger" s.level="WARNING" s.path="./test_kwogger.py" s.func="my_func_name" s.lineno=44

        e.msg="TEST_EXCEPTION"  e.field1=None e.field2=True e.field3=1 e.field4=1.5 e.field5="hello"
        e.other_type="<module 'os' from 'os.py'>"

        exc.class="TypeError"
        exc.msg="unsupported operand type(s) for +: 'int' and 'str'"
        exc.traceback="[ ... truncated ... ]"

        c.is_unit_test=True c.test_id="70ea8059-f6c5-3f52-855b-15531e2824d4"
    """

    def __init__(self, context=None, source=None, entry=None, exc=None, raw=None):
        """
        :param context: (None|dict) key value pairs for data in this namespace or None
        :param source: (None|dict) key value pairs for data in this namespace or None
        :param entry: (None|dict) key value pairs for data in this namespace or None
        :param exc: (None|dict) key value pairs for data in this namespace or None
        :param raw: (str) the original line as read from file
        """
        self.context, self.source, self.entry, self.exc, self.raw, = context, source, entry, exc, raw

    def __repr__(self):
        return f'<KwogEntry | {self.level_name} | exception={self.handling_exception}>'

    def __str__(self):
        return self.format('log_file')

    def __iter__(self):
        namespaces = [('context', self.context), ('source', self.source), ('entry', self.entry), ('exc', self.exc)]
        for name, group in namespaces:
            try:
                for key, value in group.items():
                    yield '.'.join([name, key]), value
            except AttributeError:
                pass

    #
    # formatting
    #

    @classmethod
    def _format_value(cls, value):
        if value is None:
            return 'None'

        if isinstance(value, (bool, float, int)):
            return str(value)

        return '"' + cls._escape_value(str(value)) + '"'

    def _format_namespace(self, parent, dictionary):
        for key, value in dictionary.items():
            # this is written to only go one level into lists/dicts, this is a logging library not a datastore
            # sub lists/dicts will be converted to a string

            yield '{}.{}={}'.format(parent, key, self._format_value(value))

    @staticmethod
    def _string_trunc(string):
        length = 50
        if len(string) > length:
            return string[0:15] + ' ... ' + string[-35:]
        else:
            return string

    @staticmethod
    def _escape_value(value):
        return value.replace('"', '""').replace('\n', '')

    #
    # formatters
    #

    def _formatter_log_file(self):
        """
        For serializing this entry and then writing to a log file

        :return: (str)
        """
        items = list(self._format_namespace('s', self.source))
        items.extend(list(self._format_namespace('c', self.context)))
        items.extend(list(self._format_namespace('e', self.entry)))
        if self.exc:
            items.extend(list(self._format_namespace('exc', self.exc)))

        return ' '.join(items)

    def _formatter_cli(self):
        """
        For printing this entry to a console with color

        :return: (str)
        """

        #
        # format source line
        #

        string = f's: {self.source["time"]} {self.level_name} {self.source["log"]}'
        string += f' {self._string_trunc(self.source["path"])} func: {self.source["func"]} line: {self.source["lineno"]}'

        #
        # format context
        #

        if self.context:
            string += f'\nc: '
            if self.context != {}:
                for key, value in self.context.items():
                    string += f'{key}={value}\t'

        #
        # format entry
        #

        if self.entry:
            string += f'\ne: '
            for key, value in self.entry.items():
                string += f'{key}={value}\t'

        #
        # format exception
        #

        if self.exc:
            string += f'\nexc: {self.exc["class"]}: {self.exc["msg"]}\ntraceback:\n'
            tb = self.exc['traceback'][3:-3].split('\\n')
            tb[0] = tb[0].strip()
            for line in tb:
                string += '\t' + line.replace("', '  ", '') + '\n'

        # return
        try:
            return colored(string + '\n', get_level_color(self.level_name))
        except NameError:
            return string + '\n'

    #
    # properties
    #

    @property
    def level(self):
        """
        :return: (int) the numerical value of the entry's log level
        """
        return level_value(self.source['level'])

    @property
    def level_name(self):
        """
        :return: (str) the name of the entry's log level
        """
        return self.source['level']

    @property
    def handling_exception(self):
        """
        :return: (bool) whether or not this entry is handling and exception
        """
        return self.exc != {}

    #
    # interface methods
    #

    @classmethod
    def parse(cls, line):
        """
        Parse a line from a log file and return an entry of this class

        :param line: (str) the line as read from the log file (with or without trailing line break)
        :return: (KwogEntry)
        """
        p = KwogParser(line)
        return cls(p.data.get('c', {}), p.data.get('s', {}), p.data.get('e', {}), p.data.get('exc', {}), line)

    def format(self, formatter):
        """
        Format a string from the data on this object

        :param formatter: (str) the name of the formatter,
            must reference a method on this object with naming convention "_formatter_{formatter}"

            built in formatters:
                'log_file' for serializing to a log file
                'cli' for printing to a console with colors

        :return: (str)
        """
        try:
            _method = getattr(self, f'_formatter_{formatter}')

        except AttributeError:
            raise ValueError(f'No formatter named: {formatter}')

        return _method()


@dataclass
class KwogTimer:
    """
    Simple class for timing a task
    """
    name: str
    start_time: float = field(default_factory=time.time)
    end_time: float = None

    def elapsed_time(self):
        """
        :return: (float) the time elapsed from 'start_time' to 'end_time', or time.time() if still running
        """
        try:
            return self.end_time - self.start_time
        except TypeError:
            return time.time() - self.start_time

    def stop(self):
        """
        stop the timer (set the end_time on the object)
        :return: (None)
        """
        self.end_time = time.time()

    def __iter__(self):
        yield 'timer_name', self.name
        yield 'start_time', self.start_time
        yield 'elapsed_time', self.elapsed_time()
        if self.end_time != 0:
            yield 'end_time', self.end_time


#
# parse and file io
#


class KwoggerParseError(Exception):
    pass


class KwogParser:
    """
    Parse data from a KwogEntry serialized to a string with KwogEntry._formatter_log_file (default when writing to
    a log file) and set each namespace on self.data. Parsing is done during instantiation.

    example:
    self.data = {'s': {...}, 'e': {...}, 'c': {...}, 'exc': {...}}
    """

    def __init__(self, line):
        """

        :param line:
        """
        self.line = line.strip()
        self.pairs = []
        self.data = {}
        self.index = 0

        # parse input
        self._parse_pairs()
        self._format_pairs()

    def __str__(self):
        return str(self.data)

    def _parse_pairs(self):
        last_break = 0
        in_string = False
        escaping = False
        for index, char in enumerate(self.line):

            if escaping and char in ['\n', ' ', '']:
                escaping = False
                in_string = False
                self.pairs.append(self.line[last_break:index])
                last_break = index + 1

            elif escaping and char == '"':
                escaping = False

            elif escaping:
                escaping = False
                in_string = False

            elif char == ' ' and not in_string:
                self.pairs.append(self.line[last_break:index])
                last_break = index + 1

            elif char == '"' and not in_string:
                in_string = True

            elif char == '"' and in_string:
                escaping = True

        if escaping:
            in_string = False

        if in_string:
            raise KwoggerParseError('Could not find end of string')

        self.pairs.append(self.line[last_break:])

    def _format_pairs(self):
        for pair in self.pairs:

            try:
                key, value = pair.split('=', 1)
            except ValueError:
                raise KwoggerParseError(f'Could not parse key/value from: "{pair}"')

            parsed_value = self._format_value(value)

            ns = key.split('.')

            if len(ns) == 1:
                self.data[key] = parsed_value

            if len(ns) == 2:
                try:
                    self.data[ns[0]][ns[1]] = parsed_value
                except KeyError:
                    self.data[ns[0]] = {ns[1]: parsed_value}

    @staticmethod
    def _format_value(value):

        if value == 'None':
            return None

        if value == 'True':
            return True

        if value == 'False':
            return False

        if str(value).find('.') != -1:
            try:
                float_value = float(value)
                return float_value
            except ValueError:
                pass

        try:
            int_value = int(value)
            return int_value
        except ValueError:
            pass

        if value[0:1] == '"' and value[-1:] == '"':
            return value[1:-1].replace('""', '"')

        return str(value)


class KwogFile:
    """
    Utility for parsing and tailing a log file.

    """

    def __init__(self, path, level=DEBUG, seek='head'):
        """
        :param path: (str) the path to the log file
        :param level: (int) ignore entries below this log level
        :param seek: (str, 'head'|'tail', default=head) seek to the head of tail of a file when instantiating
        """
        self.path = path
        self.level = level
        self._file = open(path, 'r')

        if seek == 'head':
            self.seek_head()
        elif seek == 'tail':
            self.seek_tail()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            entry = self.parse_line()
            try:
                if entry.level >= self.level:
                    return entry
            except AttributeError:
                raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #
    # file handler
    #

    def seek_head(self):
        """
        Seek to the head of the file

        :return: None
        """
        self._file.seek(0)

    def seek_tail(self):
        """
        Seek to the tail of the file

        :return:
        """
        self._file.seek(0, os.SEEK_END)

    def close(self):
        """
        Close the file handle

        :return: None
        """
        self._file.close()

    #
    # interface methods
    #

    def follow(self):
        """
        Parse and yield remaining lines from current position in file to EOF and then follow file like unix 'tail -f' cmd

        :yields: (KwogEntry)
        """
        try:
            for line in self:
                yield line

            while True:
                line = self._file.readline()

                if line:
                    entry = KwogEntry.parse(line)
                    if entry.level >= self.level:
                        yield entry

        except KeyboardInterrupt:
            pass

    def parse_line(self):
        """
        Get next line in file using readline and return parsed KwogEntry

        :return: (KwogEntry)
        """
        line = self._file.readline()
        if line:
            return KwogEntry.parse(line)


