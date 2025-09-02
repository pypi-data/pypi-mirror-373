# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import time

from appium import webdriver
from appium.options.common.base import AppiumOptions
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

from .lynx_element import LynxElement
from .lynx_view import LynxView
from ..core.app import App as E2EBaseApp, LynxAppMixin
from ..core.logger import cdp_logger
from ..core.lynx_driver import LynxDriver
from ..core.upath import UPath
from ..core.utils import str_to_bool
from ..exception import LynxNotFoundException


DEFAULT_APPIUM_SERVER_HOST = "127.0.0.1"
DEFAULT_APPIUM_SERVER_PORT = 4723
DEFAULT_IS_HEADELESS = "false"


class CommonApp(E2EBaseApp):
    def __init__(self, *args, **kwargs):
        self._device = args[0]
        self._server_host = os.environ.get('server_host', DEFAULT_APPIUM_SERVER_HOST)
        self._server_port = os.environ.get('server_port', DEFAULT_APPIUM_SERVER_PORT)
        if 'app_spec' not in kwargs:
            raise ValueError("app_spec is required in app init!")
        options = self._transform_app_spec(kwargs['app_spec'])
        self._appium_driver = webdriver.Remote(f"{self._server_host}:{self._server_port}", options=options)
        E2EBaseApp.__init__(self, device=args[0], app_spec=kwargs['app_spec'])
        self._device.set_appium_driver(self._appium_driver)
        time.sleep(5)

    def _transform_app_spec(self, app_spec):
        """transform app_spec to desired_capabilities for appium
        app_spec = {
            "package_name": "com.lynx.example",  # For Android only
            "init_device": True,  # whether to wake up device
            "process_name": "",  # main process name of app
            "start_activity": "",  # leave it empty to be detected automatically
            "grant_all_permissions": True,  # grant all permissions before starting app
            "clear_data": True,  # pm clear app data
            "kill_process": True,  # whether to kill previously started app
            "bundle_id": "com.lynx.example", # For iOS only
        }

        Args:
            app_spec (_type_): _description_
        """
        raise NotImplementedError()

    def get_controller(self, tag, index=0):
        """Find specific view by tag in current window

        Args:
            tag (str): search condition
            index (int, optional): search contidion when there are multiple views with the same tag in the window.
        """
        elements = self._appium_driver.find_elements(AppiumBy.XPATH, f"//*[@view-tag='{tag}']")
        if len(elements) == 0:
            raise LynxNotFoundException("Can't find lynxview on current window")
        if len(elements) < index:
            raise LynxNotFoundException(f"In the current window, there are only {len(elements)} elements with tag {tag}.\
                                    The element at {index} cannot be obtained.")
        path = UPath(predicates=[{"name": "lynx-test-tag", "value": tag, "operator": "=="}], index=index)
        return LynxElement(elements[index], path=path, root=None)

    def get_page_root(self):
        raise NotImplementedError()

    def get_lynxview(self, tag, _):
        """Find lynxview by tag in current window

        Args:
            tag (_type_): _description_
            lynxview_type (LynxView): _description_
        """
        elements = self._appium_driver.find_elements(AppiumBy.XPATH, f"//*[@view-tag='{tag}']")
        if len(elements) == 0:
            raise LynxNotFoundException("Can't find lynxview on current window")
        return LynxView(elements[0], app=self, root=self.get_page_root())

    def add_cleanup(self, msg, func, *args, **kwargs):
        """add cleanup action to be done at the end of testcase execution

        :param msg: indication message for cleanup action
        :type  msg: str
        :param func: a callable object to be invoked
        :type  func: function
        :param args: positional arguments to be passed to func
        :type  args: list
        :param kwargs: keyword arguments to be passed to func
        :type  kwargs: dict
        :return index: an index to identify a cleanup action for remove_cleanup
        :rtype index: int
        """
        if self._testcase:
            return self._testcase.add_cleanup(msg, func, *args, **kwargs)
        else:
            cdp_logger.warning(
                "you may need to do explicit cleanup for: [%s]%s" % (msg, func))

    def get_lynx_driver(self, lynxview):
        cdp_logger.warning("[Appium]:start to get_lynx_driver")
        if self.lynxDebug is None:
            cdp_logger.warning("[Appium]:lynxDebug is not initialized, it need launch connect_app_to_lynx_server")
            self.connect_app_to_lynx_server(over_usb=True)
        return LynxDriver(lynxview, lynx_debugger=self.lynxDebug, **lynxview.view_spec)

    def get_pid(self):
        '''get current process id
        '''
        return None


class AndroidApp(LynxAppMixin, CommonApp):
    def __init__(self, *args, **kwargs):
        LynxAppMixin.__init__(self, *args, **kwargs)
        CommonApp.__init__(self, *args, **kwargs)

    def _transform_app_spec(self, app_spec):
        """transform app_spec to desired_capabilities for appium
        app_spec = {
            "package_name": "com.lynx.example",  # For Android only
            "init_device": True,  # whether to wake up device
            "process_name": "",  # main process name of app
            "start_activity": "",  # leave it empty to be detected automatically
            "grant_all_permissions": True,  # grant all permissions before starting app
            "clear_data": True,  # pm clear app data
            "kill_process": True,  # whether to kill previously started app
            "bundle_id": "com.lynx.example", # For iOS only
        }

        Args:
            app_spec (_type_): _description_
        """
        desired_capabilities = {
            "udid": self._device.udid,
            "deviceName": self._device.udid,
        }
        desired_capabilities["platformName"] = "Android"
        desired_capabilities["automationName"] = "espresso"
        desired_capabilities["espressoBuildConfig"] = '{"kotlin":"1.6.21","additionalAndroidTestDependencies": ' + '["androidx.lifecycle:lifecycle-extensions:2.2.0"]}'
        desired_capabilities["appPackage"] = app_spec.get("package_name", None)
        if 'start_activity' in app_spec and len(app_spec['start_activity']) > 0:
            desired_capabilities['appActivity'] = app_spec.get('start_activity')
        if 'app' in app_spec and len(app_spec['app']) > 0:
            desired_capabilities['app'] = app_spec.get('app')
        desired_capabilities['platformVersion'] = self._device.os_version
        return AppiumOptions().load_capabilities(desired_capabilities)

    def has_keyboard(self):
        focused_edit_text = self._appium_driver.find_elements(AppiumBy.XPATH, "//*[@class='android.widget.EditText' and @focused='true']")
        if focused_edit_text:
            return True
        else:
            return False

    def restart(self, **kwargs):
        self._appium_driver.terminate_app(self._app_spec['package_name'])
        time.sleep(3)
        self._appium_driver.activate_app(self._app_spec['package_name'])

    def get_page_root(self):
        return self._appium_driver.find_element(AppiumBy.CLASS_NAME, 'com.android.internal.policy.DecorView')

    def is_app_crashed(self):
        package_name = self._device.get_current_process()
        return package_name != self.app_spec["package_name"]


class iOSApp(LynxAppMixin, CommonApp):
    def __init__(self, *args, **kwargs):
        LynxAppMixin.__init__(self, *args, **kwargs)
        CommonApp.__init__(self, *args, **kwargs)

    def _transform_app_spec(self, app_spec):
        desired_capabilities = {
            "udid": self._device.udid,
            "deviceName": self._device.udid,
            "platformName": "iOS",
            "automationName": "XCUITest",
            "isHeadless": str_to_bool(os.environ.get("APPIUM_isHeadless", DEFAULT_IS_HEADELESS))
        }
        desired_capabilities |= app_spec
        return XCUITestOptions().load_capabilities(desired_capabilities)

    def restart(self, **kwargs):
        self._appium_driver.terminate_app(self._app_spec['bundleId'])
        time.sleep(3)
        self._appium_driver.activate_app(self._app_spec['bundleId'])

    def get_page_root(self):
        return self._appium_driver.find_elements(AppiumBy.XPATH, "/*")

    def is_app_crashed(self):
        bundle_id = self._device.get_current_process()
        return bundle_id != self.app_spec["bundle_id"]

    def get_lynxview(self, tag, _):
        """Find lynxview by tag in current window

        Args:
            tag (_type_): _description_
            lynxview_type (LynxView): _description_
        """
        elements = self._appium_driver.find_elements(AppiumBy.XPATH, f"//*[@label='{tag}']")
        if len(elements) == 0:
            raise LynxNotFoundException("Can't find lynxview on current window")
        return LynxView(elements[0], app=self, root=self.get_page_root())
