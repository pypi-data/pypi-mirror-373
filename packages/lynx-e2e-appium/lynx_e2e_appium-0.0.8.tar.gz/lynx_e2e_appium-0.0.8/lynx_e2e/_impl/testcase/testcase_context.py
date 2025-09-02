# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from ..utils import ThreadGroupLocal


def current_testcase():
    """current testcase

    :return: current running testcase instance
    :rtype: TestCase
    """
    return getattr(ThreadGroupLocal(), 'testcase', None)


def current_test_result():
    """current test_result

    :return: current running testcase's test_result
    :rtype: TestResultBase
    """
    return getattr(ThreadGroupLocal(), 'test_result', None)


def current_testcase_local():
    """crrernt testcase local scope

    :return: thread group local scope instance
    :rtype: ThreadGroupLocal
    """

    return ThreadGroupLocal()
