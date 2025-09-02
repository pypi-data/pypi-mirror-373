# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

class DeviceDriver(object):
    """abstract device driver definition
    """
    def __init__(self, *args, **kwargs):
        self.deviceName = args[0]

    def get_type(self):
        """get device type
        """
        raise NotImplementedError

    def get_udid(self):
        """get unique device id
        """
        raise NotImplementedError

    def get_name(self):
        """get device name
        """
        raise NotImplementedError

    def get_os_version(self):
        """get device os_version
        """
        raise NotImplementedError

    def get_screen_rect(self):
        """get device screen rectangle
        """
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError

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