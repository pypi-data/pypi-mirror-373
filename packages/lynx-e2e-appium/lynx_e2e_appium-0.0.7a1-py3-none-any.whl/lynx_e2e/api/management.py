# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import importlib
from .config import settings

DEFAULT_MANAGEMENT_PATH = 'lynx_e2e._impl.manage.management'

def create_class():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    manage_class = None
    manage_module = None
    try:
        manage_module = importlib.import_module(f"{driver_path}.management")
    except ModuleNotFoundError:
        manage_module = importlib.import_module(DEFAULT_MANAGEMENT_PATH)
        
    manage_class = getattr(manage_module, 'ManagementTools')
    return manage_class

class ManagementTools(create_class()):
    """UI testcase base
    """
    pass
