# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import importlib
from .config import settings

DEFAULT_TESTRESULT_PATH = 'lynx_e2e._impl.manage.test_result'

def create_testresult_module():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    result_module = None
    try:
        result_module = importlib.import_module(f"{driver_path}.logger")
    except ModuleNotFoundError:
        result_module = importlib.import_module(DEFAULT_TESTRESULT_PATH)

    return result_module

def create_level_class():
    result_module = create_testresult_module()
    return getattr(result_module, 'EnumLogLevel')

def create_record_class():
    result_module = create_testresult_module()
    return getattr(result_module, 'LogRecord')


class EnumLogLevel(create_level_class()):
    pass

class LogRecord(create_record_class()):
    pass