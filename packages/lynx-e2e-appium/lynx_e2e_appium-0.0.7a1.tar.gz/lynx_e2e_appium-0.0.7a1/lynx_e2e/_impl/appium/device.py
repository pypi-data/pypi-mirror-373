# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from ..device.device import Device as BaseDevice

class AndroidDevice(BaseDevice):

    def set_appium_driver(self, driver):
        self._driver.set_appium_driver(driver)

class iOSDevice(BaseDevice):

    def set_appium_driver(self, driver):
        self._driver.set_appium_driver(driver)