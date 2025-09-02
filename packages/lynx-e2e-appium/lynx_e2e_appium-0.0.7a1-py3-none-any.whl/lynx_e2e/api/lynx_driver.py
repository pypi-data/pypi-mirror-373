# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import importlib
from .config import settings

DEFAULT_TESTCASE_PATH = 'lynx_e2e._impl.base.lynx_driver'

def create_class():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    driver_module = None
    try:
        driver_module = importlib.import_module(f"{driver_path}.lynx_driver")
    except ModuleNotFoundError:
        driver_module = importlib.import_module(DEFAULT_TESTCASE_PATH)

    return getattr(driver_module, 'LynxDriver')

class LynxDriver(create_class()):
    """UI testcase base
    """
    pass
