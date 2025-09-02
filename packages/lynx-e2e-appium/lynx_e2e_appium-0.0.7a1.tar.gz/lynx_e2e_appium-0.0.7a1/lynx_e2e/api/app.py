# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import importlib
from .config import settings
from .exception import LynxNotFoundException

def create_app_class():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    platform = os.environ.get('platform')
    app_class = None
    try:
        app_module = importlib.import_module(f"{driver_path}.app")
    except ModuleNotFoundError:
        raise LynxNotFoundException(f"{driver_path}.app is not found!")
        
    if platform.lower() == 'android':
        app_class = getattr(app_module, 'AndroidApp')
    elif platform.lower() == 'ios':
        app_class = getattr(app_module, 'iOSApp')
    else:
        raise LynxNotFoundException(f"platform {platform} is not supported!")
    return app_class

class LynxApp(create_app_class()):
    """app base
    """
    pass
