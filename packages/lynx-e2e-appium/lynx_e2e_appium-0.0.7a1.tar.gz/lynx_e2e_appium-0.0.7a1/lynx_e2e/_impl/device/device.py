# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import importlib
import traceback
import logging

from .device_driver import DeviceDriver
from ...api.config import settings
from ...api.exception import LynxNotFoundException


def dict_deep_update(source, dest):
    for key, value in source.items():
        if key in dest and isinstance(value, dict):
            dict_deep_update(value, dest[key])
        else:
            dest[key] = value

class Device(object):
    
    def __init__(self, device_driver):
        self._driver = device_driver
        self._testcase = None
        self._forward_ports = set()
        self._reverse_ports = set()

    def __str__(self):
        return "<Device [%s]%s>" % (self.udid, self.name)

    @property
    def type(self):
        return self._driver.get_type()

    @property
    def udid(self):
        """unique device id
        """
        return self._driver.get_udid()

    @property
    def name(self):
        """device name
        """
        return self._driver.get_name()

    @property
    def os_version(self):
        """os version
        """
        return self._driver.get_os_version()

    @property
    def ip(self):
        """
        :return: devcie ip
        :rtype: uibase.common.Rectangle
        """
        return self._driver.get_ip()

    @property
    def screen_rect(self):
        """screen size

        :return: screen size rectangle
        :rtype: uibase.common.Rectangle
        """
        result = self._driver.get_screen_rect()
        return result

    @property
    def device_driver(self) -> DeviceDriver:
        return self._driver

    @property
    def adb(self):
        return self.device_driver._adb

    def screenshot(self, path=None, quality=None):
        """get current screen shot

        :param path: target path to store screen shot file
        :type  path: str
        :param quality: screenshot quality, from 0 to 100, None to let driver decide
        :type  quality: int
        """
        if path:
            path = os.path.abspath(path)
            if os.path.isdir(path):
                dir_name = path
                file_name = None
            else:
                parent_dir = os.path.dirname(path)
                if os.path.isdir(parent_dir):
                    dir_name, file_name = os.path.split(path)
                else:
                    raise ValueError(
                        "path %s and its parent were not found" % path)
        else:
            dir_name, file_name = os.getcwd(), None

        try:
            return self._driver.screenshot(dir_name, file_name, quality)
        except TypeError:
            return self._driver.screenshot(dir_name, file_name)

    def shell_command(self, cmdline, **kwargs):
        """execute a command line

        :param cmdline: target command line to be executed
        :type  cmdline: str or list
        :param kwargs: keyword arguments for details
        :type  kwargs: dict
        """
        return self._driver.shell_command(cmdline, **kwargs)

    def is_app_installed(self, app_id):
        """is app installed

        :param app_id: app unique id, package_name for Android, bundle_id for iOS, etc.
        :type  app_id: str
        """
        return self._driver.is_app_installed(app_id)

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
        forward_port = self._driver.start_forward(
            server_port, device_port_or_sock, forward_type)
        self._forward_ports.add(forward_port)
        return forward_port

    def stop_forward(self, server_port):
        """remove the forward to server_port

        :param server_port: a forward server_port
        :type  server_port: int
        :return : remove success or fail
        :rtype  : bool
        """
        return self._driver.stop_forward(server_port)

    def stop_forwards(self):
        if self._forward_ports:
            for port in self._forward_ports:
                try:
                    self.stop_forward(port)
                except Exception as e:
                    logging.warning("remove forward error: %s" % str(e))
                    traceback.print_exc()
            self._forward_ports.clear()

    def start_reverse(self, device_port_or_sock, server_port, server_ip="", reverse_type="tcp"):
        """reverse a server address to device port or socket
        """
        reverse_port = self._driver.start_reverse(
            device_port_or_sock, server_port, server_ip, reverse_type)
        self._reverse_ports.add(reverse_port)
        return reverse_port

    def remove_reverse(self, device_port_or_sock):
        """remove the reverse to device_port_or_sock
        """
        return self._driver.remove_reverse(device_port_or_sock)

    def remove_reverses(self):
        """remove all reverses
        """
        if self._reverse_ports:
            for d_or_s in self._reverse_ports:
                try:
                    self.remove_reverse(d_or_s)
                except Exception as e:
                    logging.warning("remove reverse error: %s" % str(e))
            self._reverse_ports.clear()

    def start_app(self, app, overwrites={}):
        """start app

        :param app: app instance
        :type  app: uibase.app.AppBase
        :param overwrites: overwrites for app_spec
        :type  overwrites: dict
        """
        if isinstance(app, dict):
            return self._driver.start_app(app)

        try:
            app_spec = app.get_app_spec().copy()
            dict_deep_update(overwrites, app_spec)
            return self._driver.start_app(app_spec)
        finally:
            pass

    def stop_app(self, app):
        """stop app

        :param app: app instance
        :type  app: uibase.app.AppBase
        """
        app.pre_stop()
        try:
            return self._driver.stop_app(app)
        finally:
            app.post_stop()

    def press_back(self, count=1, interval=0.1):
        """press back button

        :param count: press back times, default one
        :type  count: int
        :param interval: press back interval, default 0.1s
        :type  interval: float
        """
        try:
            return self._driver.press_back(count=count, interval=interval)
        except TypeError:
            # TODO remove after all driver updated
            return self._driver.press_back()

    def click(self, x, y):
        """click coordinate at (x, y) on screen

        :param x: x coordinate
        :type  x: float
        :param y: y coordinate
        :type  y: float
        """
        return self._driver.click(x, y)

    def long_click(self, x, y, duration=1):
        """long click coordinate at (x, y) on screen

        :param x: x coordinate
        :type  x: float
        :param y: y coordinate
        :type  y: float
        :param duration: long click duration
        :type  duration: float
        """
        return self._driver.long_click(x, y, duration=duration)

    def drag(self, from_x, from_y, to_x, to_y, duration=None, press_duration=None):
        """drag from coordinate (from_x, from_y) to (to_x, to_y)

        :param from_x: start x coordinate
        :type  from_x: float
        :param from_y: start y coordinate
        :type  from_y: float
        :param to_x: end x coordinate
        :type  to_x: float
        :param to_y: end y coordinate
        :type  to_y: float
        :param duration: drag procedure duration
        :type  duration: float
        :param press_duration: press duration at (from_x, from_y) before dragging
        :type  press_duration: float
        """
        return self._driver.drag(from_x, from_y, to_x, to_y,
                                 duration=duration,
                                 press_duration=press_duration)

    def send_keys(self, keys):
        """send keys input to device

        :param keys: keys or text to be sent to device
        :type  keys: str
        """
        return self._driver.send_keys(keys)

    def get_current_process(self):
        """get current foreground running process
        """
        return self._driver.get_current_process()

    def unlock(self):
        return self._driver.unlock()

    # Android Only
    def get_current_activity(self, package_name=None):
        """get current foreground running activity
        """
        return self._driver.get_current_activity(package_name=package_name)

    def send_key(self, key):
        return self._driver.send_key(key)

    def get_app_version(self, package_name):
        return self._driver.get_app_version(package_name)

def get_device_class():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    platform = os.environ.get('platform')
    device_class = None
    try:
        device_module = importlib.import_module(f"{driver_path}.device")
        if platform.lower() == 'android':
            device_class = getattr(device_module, 'AndroidDevice')
        elif platform.lower() == 'ios':
            device_class = getattr(device_module, 'iOSDevice')
        return device_class
    except ModuleNotFoundError:
        device_module = importlib.import_module("lynx_e2e._impl.device.device")
        device_class = getattr(device_module, 'Device')
        return device_class
    except AttributeError:
        traceback.print_exc()
        raise LynxNotFoundException(f"device is not found in {driver_path}.device!")

def get_device_driver_class():
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    platform = os.environ.get('platform')
    driver_class = None
    try:
        driver_module = importlib.import_module(f"{driver_path}.device_driver")
        if platform.lower() == 'android':
            driver_class = getattr(driver_module, 'AndroidDeviceDriver')
        elif platform.lower() == 'ios':
            driver_class = getattr(driver_module, 'iOSDeviceDriver')
        else:
            raise ValueError(f"platform {platform} is not supported!")
        return driver_class
    except ModuleNotFoundError:
        raise LynxNotFoundException(f"{driver_path}.device_driver is not found!")
    except AttributeError:
        raise LynxNotFoundException(f"DeviceDriver is not found in {driver_path}.device_driver!")