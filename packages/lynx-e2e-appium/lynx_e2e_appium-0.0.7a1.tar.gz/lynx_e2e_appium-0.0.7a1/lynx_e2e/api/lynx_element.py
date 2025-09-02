# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import importlib
from .exception import LynxNotFoundException
from .config import settings


def create_class():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    lynxelement_module = None
    try:
        lynxelement_module = importlib.import_module(f"{driver_path}.lynx_element")
    except ModuleNotFoundError:
        raise LynxNotFoundException(f"{driver_path}.lynx_element is not found!")

    return getattr(lynxelement_module, 'LynxElement')
class LynxElement(create_class()):
    """lynx element
        """
    pass