# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import time
import warnings

from .debugger import LynxDebugger
from .logger import cdp_logger
from .lynx_driver import LynxDriver
from ..exception import LynxCDPTimeoutException

class App(object):
    
    def __init__(self, device, app_spec):
        self._device = device
        self._app_spec = app_spec
        self._package_name = None
    
    def restart(self, **kwargs):
        """ Restart app without clearing data.
        """
        overwrites_spec = {'clear_data': False, 'kill_process': True, 'grant_all_permissions': False,
                           'before_launch_app': None}
        overwrites_spec.update(kwargs)
        self._device.start_app(self, overwrites_spec)

    @property
    def package_name(self):
        '''
        Get the package name. First, try to obtain package_name. 
        If it doesn't exist, obtain an installed one from package_names.
        '''
        package_name = self._app_spec.get('package_name', None)
        if not package_name:
            package_names = self._app_spec.get("package_names", [])
            for p_i in package_names:
                if self._device.is_app_installed(p_i):
                    package_name = p_i
                    self._app_spec["package_name"] = p_i
                    break
        return package_name

    @package_name.setter
    def package_name(self, package_name):
        self._package_name = package_name

    def get_app_spec(self):
        return self._app_spec

    def get_device(self):
        return self._device

    def get_controller(self, tag, index=0):
        '''
        In the current page, find the corresponding node according to the specified tag and index.
        
        Params:
            tag (str): The tag of the node to be found.
            index (int): The index of the target node in node list which ard found by tag.

        Returns:
            The node found by tag and index.
        '''
        raise NotImplementedError("The get_controller method in the app is not implemented. Please implement this method in app.py.")

    def get_lynxview(self, tag, lynxview_type):
        '''
        In the current page, find the corresponding lynxview root node according to the specified tag.
        
        Params:
            tag (str): The tag of the node to be found.

        Returns:
            The lynxview root node found by tag and index.
        '''
        raise NotImplementedError("The get_lynxview method in the app is not implemented. Please implement this method in app.py.")

    def get_red_box(self):
        '''
        In the current page, find the redbox node.

        Returns:
            return the redbox node if it exists, else return None.
        '''
        raise NotImplementedError("The get_red_box method in the app is not implemented. Please implement this method in app.py.")

    def get_by_label(self, label_name, index=None):
        '''
        In the current page, find the target node by label attribute.

        Returns:
            return the node match the query condition.
        '''
        raise NotImplementedError("The get_by_label method in the app is not implemented. Please implement this method in app.py.")

    def get_by_tag(self, tag_name, index=None):
        '''
        In the current page, find the target node by tag attribute.

        Returns:
            return the node match the query condition.
        '''
        raise NotImplementedError("The get_by_tag method in the app is not implemented. Please implement this method in app.py.")

    def get_lynx_driver(self, lynxview):
        if self.lynxDebug is None:
            cdp_logger.warning("[Lynx E2E]:lynxDebug is not initialized, it need launch connect_app_to_lynx_server")
            self.connect_app_to_lynx_server(over_usb=True)
        return LynxDriver(lynxview, lynx_debugger=self.lynxDebug, **lynxview.view_spec)

    def open_card(self, url):
        if url == '':
            return
        self.open_lynx_container(url)

class LynxAppMixin:
    def __init__(self, *args, **kwargs):
        self.lynxDebug = None
        self._testcase = None

    def connect_app_to_lynx_server(self, usb_server_port=None):
        if self.lynxDebug:
            self.disconnect()
            time.sleep(3)
        for usb_server_port in range(8901, 8921):
            try:
                time.sleep(1)
                self.init_lynx_debug(usb_server_port)
                break
            except ConnectionError as e:
                cdp_logger.exception("[Lynx-E2E] port %s is not accessable, try another! %s" % (usb_server_port, str(e)))
                continue
        self.set_global_switch('enable_devtool', True)
        self.set_global_switch('enable_automation', True)

    def init_lynx_debug(self, usb_server_port=None):
        self.lynxDebug = LynxDebugger(device=self.get_device(), usb_server_port=usb_server_port)

    def eval(self, expression):
        return self.lynxDebug.eval(expression)

    def get_console_log(self):
        return self.lynxDebug.get_console_log()

    def wait_for_session(self, name):
        warnings.warn("wait_for_session is a deprecated function.",
                      category=DeprecationWarning,
                      stacklevel=2)
        time.sleep(2)

    def start_trace(self):
        return self.lynxDebug.start_trace()

    def end_trace(self):
        return self.lynxDebug.end_trace()

    def io_read(self, stream_id, shard=1024 * 32 * 3, output_file='trace.pftrace'):
        return self.lynxDebug.io_read(stream_id, output_file=output_file)

    def open_lynx_container(self, url):
        return self.lynxDebug.open_lynx_container(url)

    def get_room(self):
        return self.lynxDebug.get_room()

    def get_socket_url(self):
        return self.lynxDebug.get_socket_url()

    def get_lynx_sdk_version(self):
        return self.lynxDebug.sdkVersion

    def get_session_id(self, url=None):
        return self.lynxDebug.get_session_id(url)

    def get_session_list(self):
        return self.lynxDebug.get_session_list()

    def disconnect(self):
        if self.lynxDebug:
            cdp_logger.warning("[Lynx-E2E] close connection")
            self.lynxDebug.disconnect()
            self.lynxDebug = None

    def start_replay(self):
        self.lynxDebug.start_replay()

    def io_read_testbench(self, stream_id, output_file=None):
        return self.lynxDebug.io_read_testbench(stream_id, output_file=output_file)

    def end_replay(self):
        return self.lynxDebug.end_replay()

    def enable_debug_mode(self):
        self.set_global_switch('enable_debug_mode', True)

    def send_custom_data(self, type_name: str = None, data: dict = None):
        """
        Send custom data to devtool
        Args:
            type_name: type name for custom data.
            data: dict
        """
        return self.lynxDebug.sender.send_custom_data(type_name, data)

    def send_cdp_data(self, session_id: int = None, method: str = None, params: dict = None,
                      session: str = None) -> int:
        """
        Send data to devtool
        Args:
            session_id: The session to send for.
            method: Specify method name.
            params: The params in data.
            session: for lepus.

        Returns:
            return id to wait for response.
        """
        return self.lynxDebug.sender.send_cdp_data(session_id, method, params, session)

    def send_app_data(self, method: str = None, params: dict = None) -> int:
        """
        Send data to host app
        Args:
            method: specify method name.
            params: params data, pass {} if empty

         Returns:
             return id to wait for response.
        """
        return self.lynxDebug.sender.send_app_data(method, params)

    def wait_for_cdp_id(self, req_id: int, timeout: int = 5, raw: bool = False) -> dict:
        """
        Wait result for id, and block thread.
        Args:
            req_id: The id return by send_cdp_data.
            timeout: Raise LynxCDPTimeoutException after timeout.
            raw: raw data.
        Returns:
            return message['result'].
        """
        try:
            result = self.lynxDebug.receiver.wait_for_custom_id(req_id, timeout, raw)
            return result
        except LynxCDPTimeoutException as e:
            extra_message = "[extra_info] {'session_list': %s, 'session_id': %s}" % (self.lynxDebug.get_session_list(), self.lynxDebug.get_session_id())
            e.args = e.args + (extra_message,)
            raise e

    def wait_for_cdp_method(self, method: str, timeout: int = 5, raw: bool = False) -> dict:
        """
        Wait result for method name, and block thread.
        Args:
            method: The method name you want to wait.
            timeout: Raise LynxCDPTimeoutException after timeout.
            raw: raw data.
        Returns:
            return message['params'].
        """
        try:
            result = self.lynxDebug.receiver.wait_for_cdp_method(method, timeout, raw)
            return result
        except LynxCDPTimeoutException as e:
            extra_message = "[extra_info] {'session_list': %s, 'session_id': %s}" % (self.lynxDebug.get_session_list(), self.lynxDebug.get_session_id())
            e.args = e.args + (extra_message,)
            raise e

    def wait_for_type_data(self, type_name: str, timeout: int = 5):
        """
        Wait result for type name, and block thread.
        Args:
            type_name: The type name you want to wait.
            timeout: Raise LynxCDPTimeoutException after timeout.
        Returns:
            return response['data']['data'].
        """
        try:
            result = self.lynxDebug.receiver.wait_for_type_data(type_name, timeout)
            return result
        except LynxCDPTimeoutException as e:
            extra_message = "[extra_info] {'session_list': %s, 'session_id': %s}" % (self.lynxDebug.get_session_list(), self.lynxDebug.get_session_id())
            e.args = e.args + (extra_message,)
            raise e

    def register_event_listener(self, event_name: str, callback: callable):
        """
        Register event listener.
        Args:
            event_name: The event name you want to listen.
            callback: The callback function.
        """
        self.lynxDebug.receiver.add_event_listener(event_name, callback)

    def unregister_event_listener(self, event_name: str):
        """
        Unregister event listener.
        Args:
            event_name: The event name you want to stop listen.
        """
        self.lynxDebug.receiver.remove_event_listener(event_name)

    def register_customized_listener(self, event_name: str, callback: callable):
        """
        Register event listener.
        Args:
            event_name: The event name you want to listen.
            callback: The callback function.
        """
        self.lynxDebug.receiver.add_customized_listener(event_name, callback)

    def unregister_customized_listener(self, event_name: str):
        """
        Unregister event listener.
        Args:
            event_name: The event name you want to stop listen.
        """
        self.lynxDebug.receiver.remove_customized_listener(event_name)

    def register_cdp_method_listener(self, method: str, callback: callable):
        """
        Register cdp method listener.
        Args:
            method: The cdp method name you want to listen.
            callback: The callback function.
        """
        self.lynxDebug.receiver.add_cdp_method_listener(method, callback)

    def unregister_cdp_method_listener(self, method: str):
        """
        Unregister cdp method listener.
        Args:
            method: The cdp method you want to stop listen.
        """
        self.lynxDebug.receiver.remove_cdp_method_listener(method)

    def get_redbox_messages(self) -> list:
        return self.lynxDebug.get_redbox_messages()

    def clear_error_message(self):
        self.lynxDebug.clear_error_message()

    def set_global_switch(self, key, value):
        return self.lynxDebug.set_global_switch(key, value)

    def set_redbox_record_switch(self, enable: bool):
        self.set_global_switch('enable_perf_metrics', enable)
        self.lynxDebug.set_redbox_record(enable)

    def set_testcase(self, testcase):
        self._testcase = testcase
