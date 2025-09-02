# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import json
import six
import sys
import logging
import threading
import traceback

from datetime import datetime

from .exception import TraceableException
from ..testcase import testcase_context


class EnumMeta(type):

    def __new__(cls, name, bases, attrs):
        new_type = type.__new__(cls, name, bases, attrs)
        value_map = {}
        key_map = {}
        setattr(new_type, "_value_map", value_map)
        setattr(new_type, "_key_map", key_map)
        for key in dir(new_type):
            if not key.startswith("_"):
                value = getattr(new_type, key)
                value_map[value] = key
                key_map[key] = new_type(value)
                setattr(new_type, key, key_map[key])
        return new_type

class EnumBase(six.with_metaclass(EnumMeta)):

    def __init__(self, value):
        cls = type(self)
        if value in cls._value_map:
            self.value = value
            self.name = cls._value_map[value]
        else:
            if value in cls._key_map:
                self.value = self._key_map[value].value
                self.name = value
            else:
                raise ValueError(
                    "value=%s not found in keys or values of %s" % (value, cls))

    def __repr__(self):
        return "<%s name=%s, value=%s>" % (type(self).__name__, self.name, self.value)

    def __eq__(self, other):
        if isinstance(other, EnumBase):
            return self.value == other.value
        elif type(other) == type(self.value):
            return self.value == other
        else:
            raise TypeError("invalid other=%s to compare to" % other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, EnumBase):
            return self.value > other.value
        elif type(other) == type(self.value):
            return self.value > other
        else:
            raise TypeError("invalid other=%s to compare to" % other)

    def __ge__(self, other):
        if isinstance(other, EnumBase):
            return self.value >= other.value
        elif type(other) == type(self.value):
            return self.value >= other
        else:
            raise TypeError("invalid other=%s to compare to" % other)

    def __lt__(self, other):
        if isinstance(other, EnumBase):
            return self.value < other.value
        elif type(other) == type(self.value):
            return self.value < other
        else:
            raise TypeError("invalid other=%s to compare to" % other)

    def __le__(self, other):
        if isinstance(other, EnumBase):
            return self.value <= other.value
        elif type(other) == type(self.value):
            return self.value <= other
        else:
            raise TypeError("invalid other=%s to compare to" % other)

    def __hash__(self):
        return self.value


class EnumLogLevel(EnumBase):
    """enum log level
    """
    DEBUG = 10
    INFO = 20
    ENVIRONMENT = 21
    RESOURCE = 22

    WARNING = 30
    ERROR = 40
    ASSERT = 41
    APPCRASH = 42
    CRITICAL = 60
    TESTTIMEOUT = 61


class LogRecord(object):
    """a log record detail
    """

    def __init__(self, stack=None, attachments={}, exception=None, extra_info=None):
        self.stack = stack
        self.attachments = {}
        for key, value in attachments.items():
            if isinstance(key, (str, int, float)):
                self.attachments[key] = value
            else:
                self.attachments[str(key)] = value
        self.exception = exception
        if extra_info is not None:
            if not isinstance(extra_info, dict):
                raise TypeError(
                    "extra_info of LogRecord must be dict instead of %s." % extra_info)
        self.extra_info = extra_info


class TestResultBase(object):
    """test result base
    """

    def __init__(self):
        self.__lock = None
        self.__steps_passed = []
        self.__curr_step = 0
        self.__failed_step_msg = None
        self.__accept_result = False
        self.__testcase = None
        self.__start_time = None
        self.__end_time = None
        self.__pre_step_msg = None
        self.__error_level = EnumLogLevel.INFO
        self.__error_type = None
        self.__failed_info = ""
        self.__failed_stack = ""
        self.__error_origin = None
        self.__tags = []

    @property
    def testcase(self):
        """corresponding test case of this result
        """
        return self.__testcase

    @property
    def passed(self):
        """test result

        :returns: True or False
        """
        return all(self.__steps_passed)

    @property
    def failed_reason(self):
        """failed reason

        :returns: str
        """
        return self.__error_level.name

    @property
    def failed_step(self):
        """failed step, starting with index=1

        :returns: int
        """
        return self.__curr_step

    @property
    def failed_step_msg(self):
        """failed step message

        :returns: str
        """
        return self.__failed_step_msg

    @property
    def failed_type(self):
        if self.__error_type is None:
            return self.failed_reason
        else:
            return self.__error_type.__name__

    @property
    def failed_info(self):
        """failed information

        :returns: str
        """
        return self.__failed_info

    @property
    def failed_stack(self):
        """failed stack

        :returns: stack of failure
        :rtype: str
        """
        return self.__failed_stack

    @property
    def error_origin(self):
        """failed error origin func

        :returns: str
        """
        return self.__error_origin

    @property
    def start_time(self):
        """begin time of test case

        :returns: float
        """
        return self.__start_time

    @property
    def end_time(self):
        """end time of test case

        :returns: float
        """
        return self.__end_time

    @property
    def tags(self):
        return self.__tags

    def add_tag(self, tag):
        """explicitly add test result tag
        """
        if not isinstance(tag, six.string_types):
            raise ValueError("%s is not a string" % tag)
        self.__tags.append(tag)

    def get_lock(self):
        if self.__lock is None:
            self.__lock = threading.RLock()
        return self.__lock

    def begin_test(self, test):
        """begin to run test

        :param test: test case
        :type test: TestCase
        """
        with self.get_lock():
            if self.__accept_result:
                raise RuntimeError("begin test should only be invoked once")
            self.__accept_result = True
            self.__start_time = datetime.now()
            self.handle_test_begin(test)
            self.begin_step("Test begins")
            self.__testcase = test

    def end_test(self):
        """end of running test
        """
        if not self.get_lock():
            raise RuntimeError("test already ended")
        with self.get_lock():
            if not self.__accept_result:
                raise RuntimeError("test not began")
            self.handle_step_end(self.__steps_passed[self.__curr_step - 1])
            self.__end_time = datetime.now()
            self.handle_test_end()
            self.__accept_result = False
        self.__lock = None

    def begin_step(self, step_msg):
        """begin a step

        :param step_msg: step message
        :type step_msg: str
        """
        with self.get_lock():
            if not self.__accept_result:
                raise RuntimeError("test not began or already ended")
            step_start_time = datetime.now()
            if len(self.__steps_passed) > 0:
                self.handle_step_end(self.__steps_passed[self.__curr_step - 1])
            self.__steps_passed.append(True)
            self.__curr_step += 1
            self.handle_step_begin(step_msg)
            self.__pre_step_msg = step_msg

    def handle_error_record(self, level, msg, record, override_level):
        self.__steps_passed[self.__curr_step - 1] = False
        if self.__error_level < EnumLogLevel.ERROR or override_level:
            self.__error_level = level
            self.__failed_step_msg = self.__pre_step_msg
            if record.extra_info:
                self.__error_origin = record.extra_info.get("error_origin")
            if record.exception:
                self.__error_type = type(record.exception)
                self.__failed_info = str(record.exception)
                if isinstance(record.exception, TraceableException):
                    self.__error_origin = record.exception.error_origin
            else:
                self.__failed_info = msg
                
            if record.stack:
                self.__failed_stack = record.stack

    def log_record(self, level, msg, record=None, override_level=False):
        """log a record

        :param level: log level
        :type level: EnumLogLevel
        :param msg: message
        :type msg: str
        :param record: log record detail
        :type record: LogRecord
        :param override_level: if True and level >= 40, error level would be overridden
        :type override_level: bool
        """
        if not isinstance(msg, six.string_types):
            msg = str(msg)
        records = [record]
        if level >= EnumLogLevel.ERROR:
            if record is None:
                raise ValueError(
                    "error level greater than ERROR must specify a LogRecord")
            self.handle_error_record(level, msg, record, override_level)
            extra_record = self._get_failure_record_safe()
            if extra_record is not None:
                records.append(extra_record)

        records = [x for x in records if x is not None]
        with self.get_lock():
            if not self.__accept_result:
                return
            self.handle_log_records(level, msg, records)

    def _get_failure_record_safe(self, timeout=300):
        """using a thread to get failure record
        """
        def _run(outputs, errors):
            try:
                outputs.append(testcase_context.current_testcase().get_failure_record())
            except:
                exc_info = sys.exc_info()
                errors.append(LogRecord(stack=traceback.format_exc(),
                                        exception=exc_info[1]))

        errors = []
        outputs = []
        t = threading.Thread(target=_run, args=(outputs, errors))
        t.daemon = True
        t.start()
        t.join(timeout)
        return outputs[0] if len(outputs) > 0 else None

    def debug(self, msg, record=None):
        self.log_record(EnumLogLevel.DEBUG, msg, record)

    def info(self, msg, record=None):
        self.log_record(EnumLogLevel.INFO, msg, record)

    def warning(self, msg, record=None):
        self.log_record(EnumLogLevel.WARNING, msg, record)

    def error(self, msg, record=None):
        self.log_record(EnumLogLevel.ERROR, msg, record)

    def critical(self, msg, record=None):
        if record is None:
            exc_info = sys.exc_info()
            record = LogRecord(stack=traceback.format_exc(),
                               exception=exc_info[1])
        self.log_record(EnumLogLevel.CRITICAL, msg, record)

    def handle_test_begin(self, test):
        """handle test begin

        :param test: test case
        :type test: TestCase
        """
        pass

    def handle_test_end(self):
        """handle test end
        """
        pass

    def handle_step_begin(self, msg):
        """handle a test step beginning

        :param msg: step message
        :type msg: str
        """
        pass

    def handle_step_end(self, passed):
        """andle a test step ending

        :param passed: step passed
        :type passed: boolean
        """
        pass

    def handle_log_records(self, level, msg, records):
        """handle a log with records

        :param level: log level
        :type level: EnumLogLevel
        :param msg: log message
        :type msg: str
        :param records: log record details
        :type records: list<LogRecord>
        """
        pass


class StreamResult(TestResultBase):
    """output test result to stream
    """

    _seperator1 = "-" * 40 + "\n"
    _seperator2 = "=" * 60 + "\n"

    def __init__(self, stream=None):
        super(StreamResult, self).__init__()
        self._stream = stream or sys.stdout
        encoding = getattr(stream, "encoding", "UTF-8")
        if encoding not in ["UTF-8"] and hasattr(self._stream, "reconfigure"):
            self._stream.reconfigure(encoding="UTF-8")
        self._write = self._stream.write
        self._step_results = []

    def handle_test_begin(self, test):
        self._write("\n")
        self._write(self._seperator2)
        owner = getattr(test, 'owner', None)
        timeout = getattr(test, 'timeout', None)
        begin_msg = "Test name:%s owner:%s timeout:%ss\n" % (
            test.test_name, owner, timeout)
        self._write(begin_msg)
        self._write(self._seperator2)

    def handle_test_end(self):
        self._write(self._seperator2)
        self._write("Start  time: %s\n" %
                    self.start_time.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3])
        self._write("End    time: %s\n" %
                    self.end_time.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3])
        self._write("Time   cost: %.2f\n" %
                    (self.end_time - self.start_time).total_seconds())

        result_map = {True: 'Passed', False: 'Failed'}
        steptxt = ''
        for i, is_passed in enumerate(self._step_results):
            steptxt += "%s:%s " % (i + 1, result_map[is_passed])
        self._write("Step result: %s\n" % steptxt)
        self._write("Test result: %s\n" % self.passed)
        self._write("Test result tags: %s\n" % (", ".join(self.tags)))
        self._write(self._seperator2)
        self._stream = None
        self._write = None

    def handle_step_begin(self, msg):
        if not isinstance(msg, str):
            raise ValueError("msg='%r' didn't match str type" % msg)

        self._write(self._seperator1)
        self._write("Step[%s]: %s\n" % (len(self._step_results) + 1, msg))

    def handle_step_end(self, passed):
        self._step_results.append(passed)

    def handle_log_records(self, level, msg, records):
        now = datetime.now()
        format_time_str = now.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
        self._write("[%s][%s] %s\n" % (format_time_str, level.name, msg))

        for record in records:
            if record.stack:
                self._write("%s\n" % record.stack)
            for name in record.attachments:
                file_path = record.attachments[name]
                self._write("  [Attachment]%s:%s\n" % (name, file_path))
            if record.extra_info:
                for key, value in record.extra_info.items():
                    self._write("%s:%s\n" % (key, json.dumps(value, indent=2, cls=JSONEncoder)))

class JSONEncoder(json.encoder.JSONEncoder):

    def default(self, o):
        obj_type = type(o)
        json_types = [str, int, dict, list, tuple, bool, float, type(None)]
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
        elif obj_type not in json_types:
            return str(o)
        else:
            return o


class TestOutputBase(object):
    """base class of test case output
    """

    def __init__(self, output_file=None):
        if output_file is None:
            self._fd = None
            self._close_fd = False
            self._output_func = logging.info
        else:
            self._fd = open(output_file, "w")
            self._close_fd = True
            self._output_func = lambda x: self._fd.write(x + "\n")

    def output_normal_tests(self, normal_tests):
        raise NotImplementedError

    def output_filtered_tests(self, filtered_tests):
        raise NotImplementedError

    def output_error_tests(self, error_tests):
        raise NotImplementedError

    def end_output(self):
        if self._close_fd:
            self._fd.close()


class StreamTestOutput(TestOutputBase):
    """stream output
    """

    def output_normal_tests(self, normal_tests):
        self._output_func("\n======================")
        self._output_func("%s normal tests:" % len(normal_tests))
        self._output_func("======================")
        for _, test in normal_tests:
            test_info = self.stream_format_test(test)
            self._output_func(test_info)

    def output_filtered_tests(self, filtered_tests):
        self._output_func("\n======================")
        self._output_func("%s filtered tests:" % len(filtered_tests))
        self._output_func("======================")
        for test_name, reason in filtered_tests:
            test_info = test_name + ", reason:" + reason
            self._output_func(test_info)

    def output_error_tests(self, error_tests):
        self._output_func("\n======================")
        self._output_func("%s error tests:" % len(error_tests))
        self._output_func("======================")
        for test_name, error in error_tests:
            test_info = "cannot load test \"%s\"" % test_name + ", error:\n" + error
            self._output_func(test_info)

    def stream_format_test(self, test):
        test_info = "%-12s " % ",".join(test.tags)
        test_info += "timeout=%-5s " % test.timeout
        test_info += "%-10s " % test.owner
        test_info += "%s" % test.test_name
        return test_info
