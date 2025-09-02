# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import time
import socket
import signal
import subprocess

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.touch_action import TouchAction

from ..core.rectangle import Rectangle as Rect
from ..core.logger import cdp_logger
from ..device.android_device_driver_mixin import AndroidDeviceDriverMixin
from ..device.ios_device_driver_mixin import iOSDeviceDriverMixin
from ..device.device_driver import DeviceDriver as BaseDeviceDriver
from ..device.adb.adb_client import ADBClient
from ..device.adb.adb import ADB
from ..device.adb.exception import DeviceScreenshotException
from ..exception import LynxNotInitialized
from ..manage.exception import ForwardError


class DeviceDriver(BaseDeviceDriver):
    
    def __init__(self, *args, **kwargs):
        """_summary_
        @params:
        args: [name, host, port]
        name: deviceName
        host: adb host
        port: adb port
        """
        self._webdriver = None
        super(DeviceDriver, self).__init__(*args, **kwargs)

    def set_appium_driver(self, webdriver):
        self._webdriver = webdriver

    def get_webdriver(self) -> WebDriver:
        if self._webdriver is None:
            raise LynxNotInitialized("Appium Driver is not initialized!")
        return self._webdriver

    def get_type(self):
        """get device type
        """
        raise NotImplementedError

    def get_udid(self):
        """get unique device id
        """
        return self.deviceName

    def get_name(self):
        """get device name
        """
        return self.deviceName

    def get_os_version(self):
        """get device os_version
        """
        raise NotImplementedError

    def get_screen_rect(self):
        """get device screen rectangle
        """
        width, height = self.get_webdriver().get_window_size()
        return Rect(0, 0, int(width), int(height))

    def get_ip(self):
        """get device ip
        """
        raise NotImplementedError

    def screenshot(self, dir_path=None, file_name=None, quality=None):
        """get current screen shot

        :param dir_path: target directory to store screen shot file
        :type  dir_path: str
        :param file_name: target file name of screen shot file
        :type  file_name: str
        :param quality: screenshot quality, from 0 to 100, None to let driver decide
        :type  quality: int
        """
        if not dir_path:
            dir_path = os.getcwd()
        if not file_name:
            file_name = "screenshot_%s.jpg" % int(time.time() * 1000)
        tmp_path = os.path.join(dir_path, file_name)
        ret = self.webdriver.get_screenshot_as_file(tmp_path)
        if not ret:
            raise DeviceScreenshotException("Screenshot error!")

    def shell_command(self, cmdline, **kwargs):
        """execute a shell command

        :param cmdline: target command line to be executed
        :type  cmdline: str or list
        :param kwargs: keyword arguments for details
        :type  kwargs: dict
        """
        raise NotImplementedError

    def is_app_installed(self, app_id):
        """is app installed

        :param app_id: app unique id, package_name for Android, bundle_id for iOS, etc.
        :type  app_id: str
        """
        raise NotImplementedError

    def start_forward(self, server_port, device_port_or_sock, forward_type="tcp"):
        """forward a device port or sock to a server port which could be visited through
        server host ip

        :param server_port: the server port to expect to forward to
        :type  server_port: int
        :param device_port_or_sock: the device port or socket to be forwarded
        :type  device_port_or_sock: int or str
        :param forward_type: forward type only for android (tcp or localabstract)
        :type  forward_type: str
        :return : forwarded server port (may not be server_port)
        :rtype  : int
        """
        raise NotImplementedError

    def stop_forward(self, server_port):
        """remove the forward to server_port

        :param server_port: a forward server_port
        :type  server_port: int
        :return : remove success or fail
        :rtype  : bool
        """
        raise NotImplementedError

    def start_reverse(self, device_port_or_sock, server_port, server_ip="", reverse_type="tcp"):
        """reverse a server address to device port or socket
        """
        raise NotImplementedError

    def remove_reverse(self, device_port_or_sock):
        """remove a reverse to device port or sock
        """
        raise NotImplementedError

    def start_app(self, app_spec):
        """start app

        :param app_spec: specification of app
        :type  app_spec: dict
        """
        raise NotImplementedError

    def stop_app(self, app):
        """stop app

        :param app: app instance
        :type  app: uibase.app.AppBase
        """
        raise NotImplementedError

    def press_back(self, count=1, interval=0.1):
        """press back button
        """
        raise NotImplementedError

    def click(self, x, y):
        """click coordinate at (x, y) on screen

        :param x: x coordinate
        :type  x: float
        :param y: y coordinate
        :type  y: float
        """
        action = TouchAction(driver=self.get_webdriver())
        action.tap(x=round(x), y=round(y)).perform()

    def long_click(self, x, y, duration=1):
        """long click coordinate at (x, y) on screen

        :param x: x coordinate
        :type  x: float
        :param y: y coordinate
        :type  y: float
        :param duration: long click duration
        :type  duration: float
        """
        raise NotImplementedError

    def drag(self, from_x, from_y, to_x, to_y, duration=None, press_duration=None):
        """drag from coordinate (from_x, from_y) to (to_x, to_y)

        :param from_x: x coordinate
        :type  from_x: float
        :param from_y: y coordinate
        :type  from_y: float
        :param duration: drag procedure duration
        :type  duration: float
        :param press_duration: press duration at (from_x, from_y) before draging
        :type  press_duration: float
        """
        raise NotImplementedError

    def send_keys(self, keys):
        """send keys input to device

        :param keys: keys or text to be sent to device
        :type  keys: str
        """
        raise NotImplementedError

    def get_current_process(self):
        """get current foreground running process
        """
        raise NotImplementedError

    def unlock(self):
        """unlock the device
        """
        raise NotImplementedError

    # Android Only
    def get_current_activity(self, package_name=None):
        """get current activity, Android only
        """
        raise NotImplementedError

    def send_key(self, key):
        """Pass a keyword to the system, such as BACK
        """
        raise NotImplementedError


class AndroidDeviceDriver(AndroidDeviceDriverMixin, DeviceDriver):
    def __init__(self, *args, **kwargs):
        adb_client = ADBClient(args[1], args[2])
        self._adb = ADB(args[0], adb_client=adb_client)
        super().__init__(*args, **kwargs)

    def get_type(self):
        """get device type
        """
        return "Android"

    def get_os_version(self):
        """get device os_version
        """
        command = "getprop ro.build.version.release"
        return self.shell_command(command)

    def shell_command(self, cmdline, **kwargs):
        """execute a shell command

        :param cmdline: target command line to be executed
        :type  cmdline: str or list
        :param kwargs: keyword arguments for details
        :type  kwargs: dict
        """
        if isinstance(cmdline, list):
            cmdline = " ".join(cmdline)
        return self._adb.shell_command(cmdline, **kwargs)

    def start_forward(self, server_port, device_port_or_sock, forward_type="tcp"):
        """forward a device port or sock to a server port which could be visited through
        server host ip

        :param server_port: the server port to expect to forward to
        :type  server_port: int
        :param device_port_or_sock: the device port or socket to be forwarded
        :type  device_port_or_sock: int or str
        :param forward_type: forward type only for android (tcp or localabstract)
        :type  forward_type: str
        :return : forwarded server port (may not be server_port)
        :rtype  : int
        """
        return self._adb.forward(server_port, device_port_or_sock, forward_type)

    def stop_forward(self, server_port):
        """remove the forward to server_port

        :param server_port: a forward server_port
        :type  server_port: int
        :return : remove success or fail
        :rtype  : bool
        """
        return self._adb.stop_forward(server_port)

    def start_app(self, app_spec):
        """start app

        :param app_spec: specification of app
        :type  app_spec: dict
        """
        package_name = app_spec.get("package_name")
        start_activity = app_spec.get("start_activity", None)
        start_params = {"action": "android.intent.action.MAIN",
                        "category": "android.intent.category.LAUNCHER",
                        "wait": False}
        if not start_activity:
            start_activity = self._real_device.get_start_activity(package_name)
            app_spec['start_activity'] = start_activity
            if not start_activity:
                raise RuntimeError("Can not find start activity")
        self._start_activity(
            "%s/%s" % (package_name, start_activity), **start_params)

    def _start_activity(self, activity_name, action='', type='', data_uri='', category='', extra={}, wait=True):
        return self._adb.start_activity(activity_name, action, type, data_uri, category, extra, wait)


class iOSDeviceDriver(iOSDeviceDriverMixin, DeviceDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._forward_dict = {}

    def get_type(self):
        """get device type
        """
        return "iOS"

    def start_forward(self, server_port, device_port_or_sock, forward_type="tcp"):
        """执行 iproxy <local_port> <ios_device_port> 命令
        """
        if server_port is None:
            server_port = self._get_available_server_port()
        forward_process = self.iproxy(server_port, device_port_or_sock)
        self._forward_dict[server_port] = forward_process
        return server_port

    def iproxy(self, port, device_port):
        command = ["iproxy", str(port), str(device_port)]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process

    def _is_reachable(self, port, host="127.0.0.1", timeout=1):
        s = socket.socket()
        s.settimeout(timeout)
        try:
            s.connect((host, port))
        except socket.error:
            pass
        else:
            return True
        finally:
            s.close()
        return False

    def _get_available_server_port(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0))
        local_port = s.getsockname()[1]
        s.close()
        return local_port

    def stop_forward(self, server_port):
        forward_process = self._forward_dict.get(server_port)
        if forward_process is None:
            return
        try:
            forward_process.terminate()
            forward_process.wait(timeout=5)
            if forward_process.returncode is not None and forward_process.returncode!= -signal.SIGTERM:
                cdp_logger.info("remove forward to %s done." % server_port)
                return
            else:
                cdp_logger.warning("remove forward failed!")
        except subprocess.TimeoutExpired:
            cdp_logger.exception("remove forward timeout!")
        except Exception as e:
            cdp_logger.exception("stop_forward failed!")
        finally:
            self._forward_dict.pop(server_port)

    def start_app(self, app_spec):
        pass

    def get_ip(self):
        # get server ip
        return "127.0.0.1"

    def click(self, x, y):
        """click coordinate at (x, y) on screen
        Using TouchAction directly in iOS will result in an error. Therefore, it is changed to using driver.tap().

        :param x: x coordinate
        :type  x: float
        :param y: y coordinate
        :type  y: float
        """
        self.get_webdriver().tap([(round(x), round(y))])

    def get_screen_rect(self):
        """get device screen rectangle
        """
        width, height = self.get_webdriver().get_window_size()
        return Rect(0, 0, width, height)
