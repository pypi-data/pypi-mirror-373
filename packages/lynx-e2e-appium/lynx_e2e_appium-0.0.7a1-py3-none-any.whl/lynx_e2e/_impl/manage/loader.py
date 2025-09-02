# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import fnmatch
import importlib
import pkgutil
import traceback

from ..testcase.testcase import TestCase


class TestSuite(object):
    """test suite
    """

    def __init__(self, tests, owners=[],
                 included_patterns=[], excluded_patterns=[],
                 included_tags=[], excluded_tags=[]):
        self.tests = tests
        self.owners = owners
        self.included_patterns = included_patterns
        self.excluded_patterns = excluded_patterns
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags

    def filter_tests(self, tests):
        matched_tests = {}
        filtered_tests = {}
        for test_name, test in tests.items():
            if self.owners and not test.owner in self.owners:
                reason = "test's owner=%s was not included in owners:%s" % (
                    test.owner, self.owners)
                filtered_tests[test_name] = reason
                continue

            if self.included_patterns:
                for pattern in self.included_patterns:
                    if fnmatch.fnmatch(test_name, pattern):
                        break
                else:
                    reason = "test name was not included in patterns:%s" % self.included_patterns
                    filtered_tests[test_name] = reason
                    continue

            skipped = False
            if self.excluded_patterns:
                for pattern in self.excluded_patterns:
                    if fnmatch.fnmatch(test_name, pattern):
                        skipped = True
                        reason = "test name matched excluded pattern: %s" % pattern
                        filtered_tests[test_name] = reason
                        break
            if skipped:
                continue

            if self.included_tags:
                for tag in self.included_tags:
                    if tag in test.tags:
                        break
                else:
                    reason = "test tags=%s was not in included tags:%s" % (test.tags,
                                                                           self.included_tags)
                    filtered_tests[test_name] = reason
                    continue

            skipped = False
            if self.excluded_tags:
                for tag in self.excluded_tags:
                    if tag in test.tags:
                        skipped = True
                        reason = "test's tags=%s matched excluded tag: %s" % (
                            test.tags, tag)
                        filtered_tests[test_name] = reason
                        break
            if skipped:
                continue

            matched_tests[test_name] = test
        return matched_tests, filtered_tests


class TestLoader(object):
    """test case loader
    """

    def __init__(self):
        self._errors = {}
        self._filtered_tests = {}

    def get_last_errors(self):
        """return errors of last loading

        :return: module names and corresponding stacks
        :rtype: dict
        """
        return self._errors

    def get_last_filtered_tests(self):
        """return filtered tests of last loading
        """
        return self._filtered_tests

    def load(self, tests):
        """load a potential test set

        :param tests: test set indicator
        :type tests: string/list/type

        :return: test cases list
        :rtype: list<TestCase>
        """
        if not isinstance(tests, list):
            tests = [tests]

        self._errors = {}
        self._filtered_tests = {}
        testcases = {}
        for test in tests:
            if isinstance(test, str):
                testcases.update(self.load_test_from_string(test))
            elif isinstance(test, TestSuite):
                testcases.update(self.load_test_from_suite(test))
            elif isinstance(test, type) and issubclass(test, TestCase):
                testcases.update(self.load_test_from_class(test))
            elif isinstance(test, TestCase):
                if not self._is_testcase_class(type(test)):
                    raise ValueError("invalid test case: %s" % test)
                testcases[test.test_name] = test
        return testcases

    def _is_testcase_class(self, cls):
        """whether a class is a TestCase class

        :return: True or False
        :rtype: bool
        """
        if not issubclass(cls, TestCase) or cls == TestCase:
            return False

        if getattr(cls, "run_test") == TestCase.run_test:
            return False
        return True

    def _filter_bad_class(self, cls):
        test_name = "%s.%s" % (cls.__module__, cls.__name__)
        if not issubclass(cls, TestCase):
            raise TypeError("%s is not a valid test case class" % test_name)
        elif cls != TestCase:
            reason = "%s is recognized as a base TestCase" % test_name
            self._filtered_tests[test_name] = reason

    def load_test_from_string(self, test_name):
        """load test from a string

        :param test_name: test name or test module
        :type test_name: str
        :return: testcase set 
        :rtype: dict
        """
        sub_test_names = test_name.split()
        tests = {}
        for sub_test_name in sub_test_names:
            tests.update(self._load_test_from_string(sub_test_name))
        return tests

    def _load_test_from_string(self, test_name):
        """load test from a string indicates a single test set
        """
        parts = test_name.split('.')
        module = None
        stack = None
        temp_parts = parts[:]
        while temp_parts:
            try:
                module_name = '.'.join(temp_parts)
                module = importlib.import_module(module_name)
                break
            except:
                del temp_parts[-1]
                stack = traceback.format_exc()
        if temp_parts == parts:
            return self.load_test_from_module(module)
        elif temp_parts and temp_parts == parts[:-1]:
            test_name_parts = parts[-1].split("/")
            if len(test_name_parts) == 1:
                test_class_name = test_name_parts[0]
                driven_data_key = None
            else:
                test_class_name = test_name_parts[0]
                driven_data_key = test_name_parts[1]
            if hasattr(module, test_class_name):
                cls = getattr(module, test_class_name)
                if self._is_testcase_class(cls):
                    return self.load_test_from_class(cls, driven_data_key)
                else:
                    self._filter_bad_class(cls)
            else:
                if hasattr(module, "__path__"):
                    error = stack
                else:
                    error = "module %s has no attribute named: %s" % (
                        module_name, test_class_name)
                self._errors[test_name] = error
        else:
            self._errors[test_name] = stack
        return {}

    def load_test_from_class(self, cls, driven_data_key=None):
        """load test from a specified class and driven data key

        :param cls: test case class
        :type  cls: type
        :return: test case dict
        :rtype: dict
        """
        if not self._is_testcase_class(cls):
            self._filter_bad_class(cls)
            return {}

        try:
            return self._load_test_from_class(cls, driven_data_key)
        except:
            traceback.print_exc()
            return {}

    def _load_test_from_class(self, cls, driven_data_key=None):
        tests = {}
        test = cls()
        print(f"_load_test_from_class cls: {test}")
        tests[test.test_name] = test
        return tests

    def load_test_from_module(self, module):
        tests = {}
        if hasattr(module, "__path__"):
            for _, module_name, is_pkg in pkgutil.walk_packages(module.__path__, module.__name__ + '.',
                                                                onerror=self._walk_package_error):
                if is_pkg:
                    continue
                try:
                    sub_module = importlib.import_module(module_name, module)
                    tests.update(self.load_test_from_module(sub_module))
                except:
                    self._errors[module_name] = traceback.format_exc()
        else:
            for key in dir(module):
                value = getattr(module, key)
                if isinstance(value, type):
                    if self._is_testcase_class(value):
                        tests.update(self.load_test_from_class(value))
                    elif issubclass(value, TestCase) and value != TestCase:
                        test_name = value.__name__
                        reason = "%s is recognized as a base TestCase" % test_name
                        self._filtered_tests[test_name] = reason
        return tests

    def _walk_package_error(self, module_name):
        """on walking package error
        """
        self._errors[module_name] = traceback.format_exc()

    def load_test_from_suite(self, test_suite):
        tests = self.load(test_suite.tests)
        matched_tests, self._filtered_tests = test_suite.filter_tests(tests)
        return matched_tests