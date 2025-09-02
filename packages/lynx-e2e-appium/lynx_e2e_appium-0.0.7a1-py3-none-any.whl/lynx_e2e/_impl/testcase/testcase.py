# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import inspect
import os
import re
import six
import sys
import threading
import traceback
from collections import OrderedDict

from ..exception import StopRunningCase
from ..manage.test_result import EnumLogLevel, LogRecord
from ..testcase.retry import Retry
from ..utils import ThreadGroupLocal


def get_module_path(cls):
    if cls.__module__ == '__main__':
        from ..config import settings
        cls_path = sys.modules[cls.__module__].__file__
        rel_path = os.path.relpath(cls_path, settings.PROJECT_ROOT)
        rel_path = rel_path.replace(os.path.sep, ".")
        mod_name = rel_path.rsplit(".", 1)[0]
        type_name = mod_name + "." + cls.__name__
    else:
        type_name = cls.__module__ + '.' + cls.__name__
    return type_name

def get_thread_traceback(thread):
    """get stack of thread

    :param thread: target thread to get stack
    :type thread: Thread
    """
    for thread_id, stack in sys._current_frames().items():
        if thread_id != thread.ident:
            continue
        tb = "Traceback ( thread-%d possibly hold at ):\n" % thread_id
        for filename, lineno, name, line in traceback.extract_stack(stack):
            tb += '  File: "%s", line %d, in %s\n' % (filename, lineno, name)
            if line:
                tb += "    %s\n" % (line.strip())
        return tb
    else:
        raise RuntimeError("thread not found")

def get_last_frame_stack(func_name):
    frame = inspect.currentframe()
    outer_frames = inspect.getouterframes(frame)
    if len(outer_frames) <= 2:
        return "frame not enough to get stack"
    keyword = "." + func_name
    for outer_frame in outer_frames[2:]:
        code_line = outer_frame[4][0]
        if code_line.find(keyword) >= 0:
            break
    stack = "".join(traceback.format_stack(outer_frame[0]))
    return stack

class _AssertRaiseContext(object):

    def __init__(self, testcase, except_classes, raise_stop=True):
        self.testcase = testcase
        self.except_classes = except_classes
        class_names = map(lambda x: x.__name__, except_classes)
        class_names = ", ".join(class_names)
        if len(except_classes) > 1:
            self._except_class_names = "(%s)" % class_names
        else:
            self._except_class_names = class_names
        self.exception = None
        self.raise_stop = raise_stop

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type is None:
            if self.raise_stop:
                stack = get_last_frame_stack("assert_raise_")
            else:
                stack = get_last_frame_stack("soft_assert_raise_")
            message = "expected %s not raised" % self._except_class_names
            self.testcase.test_result.log_record(EnumLogLevel.ASSERT,
                                                 message,
                                                 LogRecord(stack=stack))
        else:
            matched = False
            for cls in self.except_classes:
                if issubclass(exc_type, cls):
                    matched = True
                    break
            if matched:
                self.exception = exc_val
                return True
            else:
                stack = "".join(traceback.format_tb(tb))
                cls_name = exc_val.__class__.__name__
                stack += "%s: %s" % (cls_name, exc_val)
                message = "%s raised instead of %s" % (exc_type.__name__,
                                                       self._except_class_names)
                self.testcase.test_result.log_record(EnumLogLevel.ASSERT,
                                                     message,
                                                     LogRecord(stack=stack))
        if self.raise_stop:
            raise StopRunningCase()
        else:
            return True


class TestCaseType(type):
    """test case metaclass
    """
    __methods__ = ["__init__"]

    def __new__(cls, name, bases, attrs):
        super_new = super(TestCaseType, cls).__new__
        parents = [b for b in bases if isinstance(b, TestCaseType)]

        if not parents:
            return super_new(cls, name, bases, attrs)

        base_tags_set = set()
        if "tags" in attrs:
            tags = attrs.pop("tags")
            if isinstance(tags, str):
                tags = [tags]
            tags_set = set(tags)
        else:
            tags_set = set()
        for b in bases:
            if hasattr(b, "tags"):
                base_tags_set |= b.tags
        if "__module__" in attrs:
            mod = sys.modules[attrs["__module__"]]
            if hasattr(mod, "__tags__"):
                mod_tags = mod.__tags__
                if isinstance(mod_tags, str):
                    mod_tags = [mod_tags]
                base_tags_set |= set(mod_tags)
        tags_set |= base_tags_set
        attrs["tags"] = tags_set
        attrs["base_tags"] = base_tags_set
        attrs["__data_driven__"] = None
        return super_new(cls, name, bases, attrs)


class TestCase(six.with_metaclass(TestCaseType)):
    """test case base class
    """
    owner = None
    timeout = None
    tags = set()
    TIME_UNIT_MAP = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    __methods__ = ["init_test", "clean_test"]
    ATTRIBUTES_ALLOWED = ["device_conditions", "enable_op_ui_scene"]
    device_conditions = [{}]
    enable_op_ui_scene = False

    def __init__(self, driven_data_key=None, driven_data=None, attrs={}):
        """construct function

        :param driven_data_key: driven data key
        :type  driven_data_key: str
        :param driven_data: driven data
        :type  driven_data: object
        :param attrs: attributes for current case to be overwritten
        :type  attrs: dict
        """
        self.__driven_data_key = driven_data_key
        self.__driven_data = driven_data
        self.__test_result = None
        self.__resmgr = None
        self.__filemgr = None
        self.__test_doc = None
        self.__cleanups = OrderedDict()
        self.__cleanup_index = 0
        self.__last_step_id = None
        self.__step_handlers = []

        if attrs:
            invalid_attrs = []
            for k, v in attrs.items():
                if k not in type(self).get_allowed_attrs():
                    invalid_attrs.append(k)
                    continue

                if k == "__doc__":
                    self.__test_doc = v
                elif k == "tags":
                    if isinstance(v, str):
                        v = [v]
                    self.tags = self.base_tags | set(v)
                else:
                    setattr(self, k, v)
            if invalid_attrs:
                raise ValueError("attribute(s) not supported: %s" %
                                 ", ".join(invalid_attrs))

        if isinstance(self.timeout, str):
            unit = self.timeout[-1]
            timeout = float(self.timeout[:-1]) * self.TIME_UNIT_MAP[unit]
            self.timeout = timeout

    @classmethod
    def get_allowed_attrs(cls):
        attrs = set()
        for temp_cls in cls.mro():
            for item in getattr(temp_cls, "ATTRIBUTES_ALLOWED", []):
                attrs.add(item)
        return attrs

    @property
    def driven_data_key(self):
        return self.__driven_data_key

    @property
    def driven_data(self):
        return self.__driven_data

    @property
    def test_result(self):
        """test result for current case
        """
        if not self.__test_result:
            raise RuntimeError("%s.init_test must be invoked first" % self)
        return self.__test_result

    @property
    def test_class_name(self):
        """return full test class name with module path

        :rtype: str
        """
        return get_module_path(type(self))

    @property
    def test_name(self):
        """return unique test case name

        :rtype: str
        """
        if self.driven_data_key is not None:
            return '%s/%s' % (self.test_class_name, self.driven_data_key)
        else:
            return self.test_class_name

    @property
    def short_test_name(self):
        return self.test_name.split(".")[-1]

    @property
    def test_doc(self):
        """description of test case

        :rtype: str
        """
        if not self.__test_doc:
            class_doc = self.__class__.__doc__
            class_doc = re.sub(r'^\s*', '', class_doc)
            class_doc = re.sub(r'\s*$', '', class_doc)
            self.__test_doc = class_doc
        return self.__test_doc

    @property
    def resmgr(self):
        return self.__resmgr

    @property
    def filemgr(self):
        return self.__filemgr

    def acquire(self, res_type, conditions={}, auto_clean=True):
        """acquire specified resource type with conditions

        :param res_type: resource type
        :type  res_type: str
        :param conditions: single condition or condition list
        :type  conditions: dict or list<dict>
        :param auto_clean: if True, resource will be released automatically
        :type  auto_clean: bool
        :return: single resource or resource list in correspond to conditions type
        :rtype: any or list<any>
        """
        return self.resmgr.acquire(res_type,
                                   conditions=conditions,
                                   auto_clean=auto_clean)

    def init_test(self, test_result, resmgr, filemgr):
        """initializing test

        :param test_result: test result for test case
        :type test_result: TestResult
        """
        self.__test_result = test_result
        self.__resmgr = resmgr
        self.__filemgr = filemgr
        setattr(ThreadGroupLocal(), "last_ui_meta", None)

    def acquire_device(self, conditions=None):
        """get first matched device

        :param conditions: conditions to match device, key can be: type, udid and so on.
        :type  conditions: dict
        """
        if conditions is None:
            conditions = self.device_conditions
            if isinstance(conditions, list) and len(conditions) == 1:
                conditions = conditions[0]
        devices = self.resmgr.acquire("device", conditions=conditions)

        return devices

    def _record_screenshots(self, devices):
        """take a screenshot for all devices if testcase passed 
        """
        if not self.test_result.passed:
            return
        for device in devices:
            self.take_screenshot(device)

    def take_screenshot(self, device, file_path=None, msg=None, quality=None):
        """explicitly take screenshot for a device

        :param device: target device instance
        :type  device: uibase.device.Device
        :param file_path: target screenshot file path, can be None
        :type  file_path: str
        :param msg: msg to be displayed
        :type  msg: str
        :param quality: screenshot quality, from 0 to 100, None to let driver decide
        :type  quality: int
        :return: screenshot file path
        :rtype: str
        """
        try:
            screenshot = device.screenshot(file_path, quality=quality)
            attachments = {"%s" % device.udid: screenshot}
            stack = None
            msg = msg or "screenshot"
            level = EnumLogLevel.INFO
        except:
            screenshot = None
            attachments = {}
            stack = traceback.format_exc()
            msg = "screenshot for %s failed" % device.udid
            level = EnumLogLevel.WARNING
        self.log_record(msg, level=level, attachments=attachments, stack=stack)
        return screenshot

    def get_failure_record(self):
        """failure data when case failed

        :return: log record for failure details
        :rtype: LogRecord
        """
        devices = self.resmgr.get_acquired_resources("device")
        attachments = {}
        for device in devices:
            udid = device.udid
            try:
                screenshot = device.screenshot()
            except:
                stack = traceback.format_exc()
                self.test_result.log_record(EnumLogLevel.WARNING,
                                            "screenshot for %s failed" % udid,
                                            LogRecord(stack=stack))
            else:
                attachments["%s" % udid] = screenshot
        return LogRecord(attachments=attachments)

    def pre_test(self):
        """prepare actions for test case
        """
        pass

    def run_test(self):
        """actions for test case
        """
        raise NotImplementedError(
            "You need overwrite `run_test` method at %s" % type(self))

    def post_test(self):
        """post actions for test case
        """
        pass

    def clean_test(self):
        """clean up actions for test case
        """
        cleanups = list(self.__cleanups.values())[:]
        self.__cleanups.clear()
        for cleanup in reversed(cleanups):
            ctx, timeout, msg, func, args, kwargs = cleanup
            self._do_cleanup(ctx, timeout, msg, func, args, kwargs)

    def _do_cleanup(self, ctx, timeout, msg, func, args, kwargs):
        def _wrapper_func(errors, ctx, func, args, kwargs):
            try:
                with ctx:
                    func(*args, **kwargs)
            except:
                errors.append(traceback.format_exc())

        self.log_info(msg)
        error_list = []
        thd = threading.Thread(target=_wrapper_func, args=(
            error_list, ctx, func, args, kwargs))
        thd.daemon = True
        thd.start()
        thd.join(timeout)
        if thd.is_alive():
            error = "cleanup %s didn't finish in %ss" % (func, timeout)
            stack = get_thread_traceback(thd)
            self.log_record(error, EnumLogLevel.CRITICAL, stack=stack)
        elif error_list:
            error = "cleanup %s failed" % func
            self.log_record(error, EnumLogLevel.CRITICAL, stack=error_list[0])

    def add_cleanup_with_ctx(self, ctx, timeout, msg, func, *args, **kwargs):
        """add a cleanup action with context for current test case

        :param ctx: a context object to execute func
        :type  ctx: Context
        :param timeout: timeout for cleanup procedure
        :type  timeout: float
        :param msg: indication message when executing cleanup
        :type  msg: str
        :param func: function to be executed
        :type  func: callable
        :param args: positional arguments for func
        :type  args: tuple
        :param kwargs: keyword arguments for func
        :type  kwargs: dict
        """
        index = self.__cleanup_index
        self.__cleanups[index] = (ctx, timeout, msg, func, args, kwargs)
        self.__cleanup_index += 1
        return index

    def add_cleanup(self, msg, func, *args, **kwargs):
        """add a cleanup action for current test case, action should be done in 60s

        :param msg: indication message when executing cleanup
        :type  msg: str
        :param func: function to be executed
        :type  func: callable
        :param args: positional arguments for func
        :type  args: tuple
        :param kwargs: keyword arguments for func
        :type  kwargs: dict
        """
        class NullContext(object):

            def __enter__(self):
                pass

            def __exit__(self, *args):
                pass

        return self.add_cleanup_with_ctx(NullContext(), 60, msg, func, *args, **kwargs)

    def remove_cleanup(self, index):
        if index not in self.__cleanups:
            raise ValueError("invalid cleanup index: %s" % index)
        del self.__cleanups[index]

    def start_step(self, step_msg, step_id=None):
        """begin a step

        :param step_msg: step message
        :type step_msg: str
        :param step_id: step id to identify this step
        :type  step_id: str
        """
        self.on_step_end()
        self.test_result.begin_step(step_msg)
        self.__last_step_id = step_id or step_msg
        self.on_step_begin()

    def on_step_begin(self):
        for step_handler in self.__step_handlers:
            step_handler.on_step_begin(self)

    def on_step_end(self):
        if self.__last_step_id:
            try:
                for step_handler in self.__step_handlers:
                    step_handler.on_step_end(self)
            except StopRunningCase:
                pass
            except:
                self.test_result.critical('end step raised')
            finally:
                self.__last_step_id = None

    def log_info(self, msg):
        """output a message of INFO level into test result

        :param msg: message to output
        :type msg: str
        """
        self.test_result.info(msg)

    def log_debug(self, msg):
        """output a message of DEBUG level into test result

        :param msg: message to output
        :type msg: str
        """
        self.test_result.debug(msg)

    def log_record(self, msg, level=None,
                   stack=None, attachments={},
                   exception=None, override_level=False,
                   extra_info=None):
        """lower level logging method for more functionalities

        :param msg: text message to output
        :type  msg: str
        :param level: record level
        :type  level: core.logger.EnumLogLevel
        :param stack: code stack to display, eg: trackback.format_exc()
        :type  stack: str
        :param attachments: a dictionary of name:file_path pairs
        :type  attachments: dict
        :param exception: exception instance to output
        :type  exception: Exception
        :param override_level: whether to override current error level, default is False
        :type  override_level: bool
        """
        if level is None:
            level = EnumLogLevel.INFO
        if exception is not None:
            if not isinstance(exception, Exception):
                raise ValueError(
                    "exception=%s is not a instance of Exception" % exception)
        record = LogRecord(stack=stack,
                           attachments=attachments,
                           exception=exception,
                           extra_info=extra_info)
        self.test_result.log_record(level,
                                    msg,
                                    record=record,
                                    override_level=override_level)

    def _log_failed(self, message, expr, func_name):
        """format assert failed message and output

        :param message: failed message
        :type  message: str
        :param expr: expression string
        :type  expr: str
        :param func_name: function name for stack tracking
        :type  func_name: str
        """
        stack = get_last_frame_stack(func_name)
        if expr:
            message = "[%s]%s" % (message, expr.split("\n")[0])
        stack += expr
        self.test_result.log_record(
            EnumLogLevel.ASSERT, message, LogRecord(stack=stack))

    def assert_(self, message, expression):
        """test assertion, if failed, test case would fail and stop execution

        :param message: indication message when assertion failed
        :type  message: str
        :param expression: an expression results in a boolean value
        :type  expression: bool
        """
        if not expression:
            self._log_failed(message, "", "assert_")
            raise StopRunningCase()

    def soft_assert_(self, message, expression):
        """test assertion, if failed, test case would fail but execution will resume

        :param message: indication message when assertion failed
        :type  message: str
        :param expression: an expression results in a boolean value
        :type  expression: bool
        """
        if not expression:
            self._log_failed(message, "", "soft_assert_")
            return False
        return True

    def _check_raise_params(self, except_class, func, *args, **kwargs):
        if func is None and any([args, kwargs]):
            raise ValueError(
                "unexpected params while func not specified: %s %s" % (str(args), kwargs))
        if isinstance(except_class, (list, tuple)):
            except_classes = except_class
        else:
            except_classes = [except_class]
        for cls in except_classes:
            if not issubclass(cls, Exception):
                raise ValueError("%r is not a subclass of Exception" % cls)
        return except_classes

    def soft_assert_raise_(self, except_class, func=None, *args, **kwargs):
        """soft assert there will be an exception raised, can be used as context

        :param except_class: expected exception class
        :type  except_class: type
        :param func: function that will be invoked to raise an exception
        :type  func: callable
        :param args: positional arguments to be passed to func
        :type  args: tuple
        :param kwargs: keyword arguments to be passed to func
        :type  kwargs: dict
        """
        except_classes = self._check_raise_params(
            except_class, func, *args, **kwargs)
        ctx = _AssertRaiseContext(self, except_classes, raise_stop=False)
        if func is None:
            return ctx
        with ctx:
            func(*args, **kwargs)

    def assert_raise_(self, except_class, func=None, *args, **kwargs):
        """soft assert there will be an exception raised, can be used as context

        :param except_class: expected exception class
        :type  except_class: type
        :param func: function that will be invoked to raise an exception
        :type  func: callable
        :param args: positional arguments to be passed to func
        :type  args: tuple
        :param kwargs: keyword arguments to be passed to func
        :type  kwargs: dict
        """
        except_classes = self._check_raise_params(
            except_class, func, *args, **kwargs)
        ctx = _AssertRaiseContext(self, except_classes, raise_stop=True)
        if func is None:
            return ctx
        with ctx:
            func(*args, **kwargs)

    def soft_wait_for_equal(self, message, obj, prop_name, expected, timeout=10, interval=0.5):
        """wait for a specified value and execution would resume anyway

        :param message: indication message when timed out
        :type  message: str
        :param obj: object to be inspected
        :type  obj: any
        :param prop_name: property name of obj
        :type  prop_name: str
        :param expected: expected value of property
        :type  expected: any
        :param timeout: the maximum seconds to wait
        :type  timeout: float or int
        :param interval: interval between retries
        :type interval: float
        """
        for retry_item in Retry(timeout=timeout, interval=interval, raise_error=False):
            actual = getattr(obj, prop_name)
            if actual == expected:
                return True
        else:
            msg = "%s\n  expected:%s\n  acutal:%s\n" % (
                message, expected, actual)
            msg += "  retried %s times in %ss" % (
                retry_item.iteration, timeout)
            self._log_failed(msg, "", "wait_for_equal")
            return False

    def wait_for_equal(self, message, obj, prop_name, expected, timeout=10, interval=0.5):
        """wait for a specified value and execution would stop if failed

        :param message: indication message when timed out
        :type  message: str
        :param obj: object to be inspected
        :type  obj: any
        :param prop_name: property name of obj
        :type  prop_name: str
        :param expected: expected value of property
        :type  expected: any
        :param timeout: the maximum seconds to wait
        :type  timeout: float or int
        :param interval: interval between retries
        :type  interval: float
        """
        if not self.soft_wait_for_equal(message, obj, prop_name, expected, timeout, interval):
            raise StopRunningCase()

    def soft_wait_for_match(self, message, obj, prop_name, expected, timeout=10, interval=0.5):
        """wait for a string to match a regular expression and execution would resume anyway

        :param message: indication message when timed out
        :type  message: str
        :param obj: object to be inspected
        :type  obj: any
        :param prop_name: property name of obj
        :type  prop_name: str
        :param expected: regular expression for match
        :type  expected: str
        :param timeout: the maximum seconds to wait
        :type  timeout: float or int
        :param interval: interval between retries
        :type  interval: float
        """
        for retry_item in Retry(timeout=timeout, interval=interval, raise_error=False):
            actual = getattr(obj, prop_name)
            if re.match(expected, actual, re.I):
                return True
        else:
            msg = "%s\n  regex:%s\n  acutal:%s\n" % (message, expected, actual)
            msg += "  retried %s times in %ss" % (
                retry_item.iteration, timeout)
            self._log_failed(msg, "", "wait_for_match")
            return False

    def wait_for_match(self, message, obj, prop_name, expected, timeout=10, interval=0.5):
        """wait for a string to match a regular expression and execution would stop if failed

        :param message: indication message when timed out
        :type  message: str
        :param obj: object to be inspected
        :type  obj: any
        :param prop_name: property name of obj
        :type  prop_name: str
        :param expected: regular expression for match
        :type  expected: str
        :param timeout: the maximum seconds to wait
        :type  timeout: float or int
        :param interval: interval between retries
        :type  interval: float
        """
        if not self.soft_wait_for_match(message, obj, prop_name, expected, timeout, interval):
            raise StopRunningCase()

    def debug_run(self):
        """local debug
        """
        from ..manage.case_runner import BasicTestRunner
        from ..manage.report import StreamTestReport
        tests = self
        report = StreamTestReport(output_summary=False)
        runner = BasicTestRunner(report)
        runner.run_tests(tests)
        return runner.report


class AndroidTestBase(TestCase):
    """UI testcase base
    """
    __methods__ = ["init_test", "clean_test"]
    ATTRIBUTES_ALLOWED = ["device_conditions", "enable_op_ui_scene"]
    device_conditions = [{}]
    enable_op_ui_scene = False

    def acquire_device(self, conditions={}):
        if "type" not in conditions:
            conditions["type"] = "Android"
        return TestCase.acquire_device(self, conditions=conditions)

    def take_screen_shot(self, device):
        '''
        :param app_or_device: AndroidApp类或AndroidDevice实例
        :type app_or_device:  AndroidApp or AndroidDevice
        '''
        return self.take_screenshot(device)

    def get_crash_files(self):
        if hasattr(self, "crash_files") and self.crash_files:
            return self.crash_files
        return None

    def get_logcat_files(self):
        if hasattr(self, "logcat_files") and self.logcat_files:
            return self.logcat_files
        return None


class iOSTestBase(TestCase):
    def acquire_device(self, conditions={}):
        if "type" not in conditions:
            conditions["type"] = "iOS"
        return TestCase.acquire_device(self, conditions=conditions)

    def take_screen_shot(self, device):
        return self.take_screenshot(device)
