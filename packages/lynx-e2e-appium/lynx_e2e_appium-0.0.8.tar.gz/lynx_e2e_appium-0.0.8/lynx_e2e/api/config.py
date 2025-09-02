# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import importlib
from .._impl.config import settings as default_settings
from .exception import LynxNotFoundException

DEFAULT_CONFIG_PATH = "lynx_e2e._impl.config"

class _Factory(object):
    
    def __init__(self):
        driver_path = default_settings.get('E2E_DRIVER_PATH', None)
        self._settings = None
        settings_module = None
        if driver_path is not None:
            try:
                settings_module = importlib.import_module(f"{driver_path}.config")
            except ModuleNotFoundError:
                settings_module = importlib.import_module(DEFAULT_CONFIG_PATH)

            try:
                self._settings = getattr(settings_module, 'settings')
            except AttributeError:
                raise LynxNotFoundException(f"settings is not found in {driver_path}!")

    def get_settings(self):
        if self._settings is None:
            raise LynxNotFoundException(f"settings.E2E_DRIVER_PATH is necessary!")
        return self._settings

settings = _Factory().get_settings()