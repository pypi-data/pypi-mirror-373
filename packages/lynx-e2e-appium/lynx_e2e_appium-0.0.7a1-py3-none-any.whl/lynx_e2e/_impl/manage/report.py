# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import argparse
import json
import sys
from datetime import datetime

from . import test_result
from .test_result import EnumLogLevel

report_usage = 'runtest <test ...> --report-type <report-type> [--report-args "<report-args>"]'

def get_installed_distributions(paths=None):
    import pkg_resources
    from pip._internal.utils.compat import stdlib_pkgs
    if paths:
        working_set = pkg_resources.WorkingSet(paths)
    else:
        working_set = pkg_resources.working_set
    items = []
    for d in working_set:
        if d.key not in stdlib_pkgs:
            items.append(d)
    return items

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

class ITestReport(object):
    """interface for test report
    """

    def begin_report(self):
        """begin of report
        """
        raise NotImplementedError

    def end_report(self):
        """end of report
        """
        raise NotImplementedError

    def on_test_result(self, test, test_result):
        """callback for a test result

        :param test: test case
        :type test: TestCase
        :param test_result: test result
        :type test_result: TestResult
        """
        raise NotImplementedError

    def is_passed(self):
        """is all test cases passed?

        :return: boolean
        """
        raise NotImplementedError

    def is_case_passed(self, testcase):
        """is test case passed

        :return: boolean
        """
        raise NotImplementedError

    def handle_loaded_tests(self, tests):
        """handle successfully loaded tests

        :param tests: test list
        :type  tests: dict<str:TestCase>
        """
        raise NotImplementedError

    def handle_filtered_tests(self, filtered_tests):
        """handle filtered tests

        :param filtered_tests: filtered test list
        :type  filtered_tests: dict<str:str>
        """
        raise NotImplementedError

    def handle_error_tests(self, error_tests):
        """handle error tests

        :param error_tests: error test list
        :type  error_tests: dict<str:str>
        """
        raise NotImplementedError

    def log_test_target(self, test_target):
        """log test target

        :param test_target: information of target
        :type test_target: dict
        """
        raise NotImplementedError

    def log_resource(self, resouce_type, resource):
        """log resource usage

        :param resouce_type: resource type
        :type resouce_type: str
        :param resource: resource object
        :type resource: dict
        """
        raise NotImplementedError

    def create_test_result(self, test):
        """create a test result for test

        :param test: test case
        :type  test: TestCase
        """
        raise NotImplementedError

    def log_record(self, level, msg, record):
        """log a single record

        :param level: log level
        :type  level: test_result.EnumLogLevel
        :param msg: message
        :type msg: str
        :param record: record
        :type record: dict
        """
        raise NotImplementedError

    def info(self, msg, record):
        """log a INFO level message

        :param msg: message
        :type msg: str
        :param record: record
        :type record: dict
        """
        raise NotImplementedError

    def warn(self, msg, record={}):
        """log a WARN level message

        :param msg: message
        :type msg: str
        :param record: record
        :type record: dict
        """
        raise NotImplementedError

    warning = warn

    def debug(self, msg, record={}):
        """log a DEBUG level message

        :param msg: message
        :type msg: str
        :param record: record
        :type record: dict
        """
        raise NotImplementedError

    def error(self, msg, record={}):
        """log a ERROR level message

        :param msg: message
        :type msg: str
        :param record: record
        :type record: dict
        """
        raise NotImplementedError

    def critical(self, msg, record={}):
        """log a CRITICAL level message

        :param msg: message
        :type msg: str
        :param record: record
        :type record: dict
        """
        raise NotImplementedError

    @classmethod
    def get_parser(cls):
        """get argument parser

        :return: argument parser
        :rtype: argparse.ArgumentParser
        """
        raise NotImplementedError

    @classmethod
    def parse_args(cls, args_string):
        """construct a report instance from arguments string

        :return: report instance
        :rtype: cls
        """
        raise NotImplementedError


class TestReportBase(ITestReport):
    """base class of test report
    """

    def __init__(self):
        self._test_results = {}
        self._start_time = None
        self._end_time = None
        self._total_run_count = 0
        self._passed_count = 0
        self._dist_list = []

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def test_results(self):
        return self._test_results

    @property
    def total_run_count(self):
        return self._total_run_count

    @property
    def passed_count(self):
        return self._passed_count

    def begin_report(self):
        self._start_time = datetime.now()
        dist_list = get_installed_distributions(None)
        dist_list.sort(key=lambda x: x.project_name.lower())
        for item in dist_list:
            self._dist_list.append([item.project_name, item.version])
        self.on_begin_report()

    def on_begin_report(self):
        raise NotImplementedError

    def end_report(self):
        self._end_time = datetime.now()
        self.on_end_report()

    def on_end_report(self):
        raise NotImplementedError

    def on_test_result(self, test_result):
        test_name = test_result.testcase.test_name
        self._test_results.setdefault(test_name, [])
        self._test_results[test_name].append(test_result)
        self._total_run_count += 1
        case_passed = self.is_case_passed(test_name)
        if case_passed:
            self._passed_count += 1
        self.handle_test_result(test_result, case_passed)

    def handle_test_result(self, test_result, case_passed):
        raise NotImplementedError

    def log_test_target(self, test_target):
        pass

    def log_resource(self, resouce_type, resource):
        pass

    def is_passed(self):
        if len(self.test_results) == 0:
            return False

        for test_name in self.test_results:
            if not self.is_case_passed(test_name):
                return False
        return True

    def is_case_passed(self, test_name):
        case_results = self.test_results[test_name]
        return any(map(lambda x: x.passed is True, case_results))

    def info(self, msg, record=None):
        self.log_record(EnumLogLevel.INFO, msg, record)

    def warn(self, msg, record=None):
        self.log_record(EnumLogLevel.WARNING, msg, record)

    def debug(self, msg, record=None):
        self.log_record(EnumLogLevel.DEBUG, msg, record)

    def error(self, msg, record=None):
        self.log_record(EnumLogLevel.ERROR, msg, record)

    def critical(self, msg, record=None):
        self.log_record(EnumLogLevel.CRITICAL, msg, record)


class StreamTestReport(TestReportBase):
    """test report output to stream
    """

    def __init__(self, stream=None, error_stream=None, output_test_result=True, output_summary=True):
        """

        :param stream: target file descriptor to output
        :type stream: file
        :param output_test_result: whether to output test result content, default is True
        :type output_test_result: boolean
        :param output_summary: whether to output test summary, default is True
        :type output_summary: boolean
        """
        super(StreamTestReport, self).__init__()
        self._stream = stream or sys.stdout
        self._err_stream = error_stream or sys.stderr
        self._write = self._stream.write
        self._write_err = self._err_stream.write
        self._output_test_result = output_test_result
        self._output_summary = output_summary

    def on_begin_report(self):
        self._write("Test runs at:%s.\n" %
                    self.start_time.strftime("%Y-%m-%d %H:%M:%S"))

    def on_end_report(self):
        self._write("Test ends at:%s.\n" %
                    self.end_time.strftime("%Y-%m-%d %H:%M:%S"))

        if self._output_summary:
            self._write("\n" + "=" * 60 + "\n")
            self._write("SUMMARY:\n\n")
            self._write(" Totals: %s\t%0.4fs\n\n" % (self.total_run_count,
                                                     (self.end_time - self.start_time).total_seconds()))

            passed_content = []
            failed_content = []
            for case_results in self.test_results.values():
                for case_result in case_results:
                    time_cost = (case_result.end_time -
                                 case_result.start_time).total_seconds()
                    content = " \t%s\t%0.3fs\n" % (case_result.testcase.test_name,
                                                   time_cost)
                    if case_result.passed:
                        passed_content.append(content)
                    else:
                        failed_content.append(content)

            self._write(" Passed: %s\n" % len(passed_content))
            self._write("".join(passed_content))
            self._write("\n")
            self._write(" Failed: %s\n" % len(failed_content))
            self._write("".join(failed_content))

    def handle_test_result(self, test_result, case_passed):
        testcase = test_result.testcase
        self._write("run test case: %s(pass?:%s)\n" %
                    (testcase.test_name, test_result.passed))

    def log_test_target(self, test_target):
        self._write("[TARGET]:\n  %s\n" % test_target)

    def log_resource(self, resouce_type, resource):
        self._write("[RESOURCE][%s]:%s" % (resouce_type, resource))

    def log_record(self, level, msg, record):
        if not self._output_test_result:
            return
        self._write("[%s]%s\n" % (level.name, msg))
        if record:
            for name, attachment in record.attachments.items():
                self._write("  [ATTACHMENTS]%s: %s" % (name, attachment))
            if record.stack:
                self._write(record["stack"])
            if record.extra_info:
                for key, value in record.extra_info.items():
                    self._write("%s:%s\n" % (key, json.dumps(value, indent=2, cls=JSONEncoder)))

    def handle_loaded_tests(self, tests):
        self._write("totally %s cases loaded." % len(tests))

    def handle_filtered_tests(self, filtered_tests):
        for test_name, reason in filtered_tests.items():
            self._write("[FILTERED]%s: %s\n" % (test_name, reason))

    def handle_error_tests(self, error_tests):
        for test_name, error in error_tests.items():
            self._write("[ERROR]%s: %s\n" % (test_name, error))

    def create_test_result(self, test):
        return test_result.StreamResult(self._stream)

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser(usage=report_usage)
        parser.add_argument("--no-result-content", action="store_true",
                            help="don't output result content of test cases")
        parser.add_argument("--no-summary", action="store_true",
                            help="don't output summary information")
        return parser

    @classmethod
    def parse_args(cls, args):
        args = cls.get_parser().parse_args(args)
        return cls(output_test_result=not args.no_result_content,
                   output_summary=not args.no_summary)
