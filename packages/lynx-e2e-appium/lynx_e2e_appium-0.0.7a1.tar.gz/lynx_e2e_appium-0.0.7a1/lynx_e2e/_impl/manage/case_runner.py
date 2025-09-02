# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import argparse
import threading
import traceback

from ..exception import StopRunningCase
from ..manage.loader import TestLoader
from .report import StreamTestReport
from ..device.resource import ResourceManager
from ..utils import ThreadGroupLocal, ThreadGroupScope

runner_usage = 'runtest <test ...> --runner-type <runner-type> [--runner-args "<runner-args>"]'

class ITestCaseRunner(object):
    """interface of test case runner
    """

    def setup(self):
        """setup for runner
        """
        raise NotImplementedError

    def teardown(self):
        """teardown for runner
        """
        raise NotImplementedError

    def load_tests(self, tests):
        """load tests and return a test suite
        """
        raise NotImplementedError

    def run_tests(self, tests):
        """run tests in test suite
        """
        raise NotImplementedError

    def run_single_test(self, test):
        """run a single test case
        """
        raise NotImplementedError


class TestRunnerBase(ITestCaseRunner):
    """base class of test case runner
    """

    def __init__(self, report, filemgr):
        self.__report = report
        self.__filemgr = filemgr

    @property
    def report(self):
        return self.__report

    @property
    def filemgr(self):
        return self.__filemgr

    def setup(self):
        pass

    def teardown(self):
        pass

    def load_tests(self, tests):
        test_loader = TestLoader()
        tests = test_loader.load(tests)
        self.report.handle_filtered_tests(
            test_loader.get_last_filtered_tests())
        self.report.handle_error_tests(test_loader.get_last_errors())
        return tests

    def run_tests(self, tests):
        self.report.begin_report()
        self.setup()
        testcases = self.load_tests(tests)
        self.report.handle_loaded_tests(testcases)
        self.run_cases(testcases)
        self.report.end_report()
        self.teardown()
        return self.report

    def run_cases(self, testcases):
        """run testcases set
        """
        testcase_list = list(testcases.values())
        test_passed = True
        while testcase_list:
            testcase = testcase_list.pop(0)
            test_result = self.run_single_test(testcase)
            self.report.on_test_result(test_result)
            self.check_test_result(test_result, testcase_list)
            if not test_result.passed:
                test_passed = False
        if not test_passed:
            raise RuntimeError('test failed!')

    def check_test_result(self, test_result, testcase_list):
        if not test_result.passed:
            testcase = test_result.testcase
            self._retry_record.setdefault(testcase.test_name, self._retries)
            if self._retry_record[testcase.test_name] > 0:
                retry_cases = TestLoader().load_test_from_class(
                    type(testcase), testcase.driven_data_key)
                testcase_list.append(retry_cases[testcase.test_name])
                self._retry_record[testcase.test_name] -= 1

    def run_single_test(self, test):
        raise NotImplementedError

    @classmethod
    def get_parser(cls):
        """get arguments parser for test runner
        """
        raise NotImplementedError

    @classmethod
    def parse_args(cls, args, report=None, resmgr=None):
        """parse arguments and create a runner

        :param args: arguments to create runner
        :type  args: argparse.Namespace
        """
        raise NotImplementedError


class TestRunnerUnit(object):
    """a test runner unit including case, result, and routines
    """

    def __init__(self, testcase, test_result, routines):
        self._testcase = testcase
        self._test_result = test_result
        self._routines = routines
        self.error = None
        self.stop = False

    @property
    def testcase(self):
        return self._testcase

    @property
    def test_result(self):
        return self._test_result

    @property
    def routines(self):
        return self._routines


class BasicTestRunner(TestRunnerBase):
    """a basic runner running case sequentially
    """

    CLEANUP_TIMEOUT = 300

    def __init__(self, report=None, filemgr=None, retries=0):
        self._lock = None
        self._retries = int(retries)
        self._retry_record = {}
        if report is None:
            report = StreamTestReport()
        super(BasicTestRunner, self).__init__(report, filemgr)

    def get_lock(self):
        if self._lock is None:
            self._lock = threading.Lock()
        return self._lock

    def _thread_run(self, test_unit):
        """execute test routines
        """
        testcase = test_unit.testcase
        test_result = test_unit.test_result
        routines = test_unit.routines
        try:
            while True:
                with self.get_lock():
                    if len(routines) == 0 or test_unit.stop:
                        break
                    routine = routines.pop(0)

                try:
                    if routine == "init_test":
                        resmgr = ResourceManager(testcase)
                        getattr(testcase, routine)(
                            test_result, resmgr, self.filemgr)
                    else:
                        getattr(testcase, routine)()
                        if routine == "post_test":
                            testcase.on_step_end()
                except StopRunningCase:
                    if routine == "pre_test":
                        routines.remove("run_test")
                except:
                    test_result.critical('%s unexpectedly raised' % routine)
                    if routine == "init_test":
                        break
                    if routine == "pre_test":
                        routines.pop(0)
        except:
            test_unit.error = traceback.format_exc()

    def _thread_cleanup(self, test_unit):
        """cleanup for test routine
        """
        testcase = test_unit.testcase
        test_result = test_unit.test_result
        routines = test_unit.routines[:]
        try:
            while True:
                with self.get_lock():
                    if len(routines) == 0:
                        break
                    routine = routines.pop(0)
                    if routine in ['init_test', 'pre_test', 'run_test']:
                        continue

                try:
                    getattr(testcase, routine)()
                except StopRunningCase:
                    pass
                except:
                    test_result.critical('%s unexpectedly raised' % routine)
        except:
            test_unit.error = traceback.format_exc()

    def run_single_test(self, test):
        test_result = self.report.create_test_result(test)
        test_routines = ['init_test', 'pre_test',
                         'run_test', 'post_test', 'clean_test']
        test_unit = TestRunnerUnit(test, test_result, test_routines)

        with ThreadGroupScope('%s:%s' % (test.test_name, id(self))):

            ThreadGroupLocal().testcase = test
            ThreadGroupLocal().test_result = test_result

            test_result.begin_test(test)
            timeout = test.timeout
            test_thread = threading.Thread(target=self._thread_run,
                                           name="test_thread",
                                           args=(test_unit,))
            test_thread.daemon = True
            test_thread.start()
            test_thread.join(timeout)
            if test_thread.is_alive():
                test_unit.stop = True
                cleanup_thread = threading.Thread(target=self._thread_cleanup,
                                                  name="cleanup_thread",
                                                  args=(test_unit,))
                cleanup_thread.daemon = True
                cleanup_thread.start()
                cleanup_thread.join(self.CLEANUP_TIMEOUT)
                if cleanup_thread.is_alive():
                    pass
                else:
                    if test_unit.error:
                        raise RuntimeError(
                            "cleanup thread error: \n%s" % test_unit.error)
            else:
                if test_unit.error:
                    raise RuntimeError(
                        "test thread error: \n%s" % test_unit.error)

            test_result.end_test()
            ThreadGroupLocal().testcase = None
            ThreadGroupLocal().test_result = None
        return test_result

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--retries", type=int, default=0,
                            help="retry count while test case failed")
        return parser

    @classmethod
    def parse_args(cls, args, report=None, filemgr=None):
        args = cls.get_parser().parse_args(args)
        return cls(report=report, filemgr=filemgr, retries=args.retries)