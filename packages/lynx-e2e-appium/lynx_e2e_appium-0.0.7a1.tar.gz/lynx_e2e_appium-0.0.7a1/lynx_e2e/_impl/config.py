# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import importlib
import os
import traceback

from .core.logger import cdp_logger
from .exception import LynxNotFoundException

_DEFAULT_SETTINSG_MODULE = "settings"
_DEFAULT_EXTRA_SETTINSG_MODULE = "settings_ex"

class _Settings(object):
    """settings container
    """

    def __init__(self):
        self.__keys = set()
        self.__sealed = True
        self.__loaded = False

    def _load(self):
        """loading settings from basic settings and user settings
        """
        settings_mod = self._get_project_settings_module()
        installed_libs = getattr(settings_mod, "INSTALLED_LIBS", [])

        settings_ex_mod = self._get_settings_ex_module()
        if settings_ex_mod:
            installed_libs = getattr(
                settings_ex_mod, "INSTALLED_LIBS", installed_libs)

        for lib in installed_libs:
            mod_settings = "%s.settings" % lib
            try:
                mod = importlib.import_module(mod_settings)
            except:
                stack = traceback.format_exc()
                cdp_logger.warn("[WARN]load library settings module \"%s\" failed:\n%s" % (
                    mod_settings, stack))
            else:
                self._load_setting_from_module(mod)

        self._load_setting_from_module(settings_mod)
        self._load_setting_from_module(settings_ex_mod)

    def _load_setting_from_module(self, module):
        """loading settings from a single module
        """
        for name in dir(module):
            if name.startswith('__'):
                continue
            if name.islower():
                continue
            self.__keys.add(name)
            setattr(self, name, getattr(module, name))

    def _get_project_settings_module(self):
        """get settings module from project
        """
        user_settings = os.environ.get("SETTINGS_MODULE", None)
        if user_settings:
            mod = importlib.import_module(user_settings)
        else:
            mod = importlib.import_module(_DEFAULT_SETTINSG_MODULE)
        return mod

    def _get_settings_ex_module(self):
        """get extra settings module
        """
        mod = None
        extra_settings = os.environ.get("EXTRA_SETTINGS_MODULE", None)
        if extra_settings:
            mod = importlib.import_module(extra_settings)
        else:
            try:
                mod = importlib.import_module(_DEFAULT_EXTRA_SETTINSG_MODULE)
            except ImportError:
                pass
        return mod

    def get(self, name, *default_value):
        """get a setting item
        """
        if len(default_value) > 1:
            raise TypeError("get expected at most 3 arguments, got %s" % (
                len(default_value) + 2))
        if default_value:
            return getattr(self, name, default_value[0])
        else:
            return getattr(self, name)

    def __ensure_loaded(self):
        if not self.__loaded:
            try:
                self.__sealed = False
                self._load()
            finally:
                self.__sealed = True
            self.__loaded = True

    def __setattr__(self, name, value):
        if not name.startswith('_Settings__') and self.__sealed:
            raise RuntimeError(
                "Dynamically modifying settings \"%s\" is not allowed" % name)
        super(_Settings, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self.__keys:
            self.__keys.remove(name)
        return super(_Settings, self).__delattr__(name)

    def __getattribute__(self, name):
        try:
            return super(_Settings, self).__getattribute__(name)
        except AttributeError:
            self.__ensure_loaded()
            try:
                return super(_Settings, self).__getattribute__(name)
            except AttributeError:
                raise LynxNotFoundException("settings key=\'%s\' not found" % name)

    def __iter__(self):
        self.__ensure_loaded()
        return self.__keys.__iter__()

    def __contains__(self, key):
        self.__ensure_loaded()
        return key in self.__keys

settings = _Settings()
