# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import importlib
from .config import settings

DEFAULT_TESTCASE_PATH = 'lynx_e2e._impl.testcase.testcase'

def create_class():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    platform = os.environ.get('platform')
    testcase_class = None
    try:
        testcase_module = importlib.import_module(f"{driver_path}.testcase")
    except ModuleNotFoundError:
        testcase_module = importlib.import_module(DEFAULT_TESTCASE_PATH)
        
    if platform.lower() == 'android':
        testcase_class = getattr(testcase_module, 'AndroidTestBase')
    elif platform.lower() == 'ios':
        testcase_class = getattr(testcase_module, 'iOSTestBase')
    return testcase_class

class TestCase(create_class()):
    """UI testcase base
    """
    pass
