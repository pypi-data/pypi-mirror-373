# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import json
import time
import ujson

from .debugger_mixin.dom import LynxDebuggerDom
from .debugger_mixin.performance import LynxDebuggerPerformance
from .debugger_mixin.runtime import LynxDebuggerRuntime
from .debugger_mixin.screencast import LynxDebuggerScreenCast
from .debugger_mixin.testbench import LynxTestBench
from .document_tree import DocumentTreeDelegate
from .logger import console_logger, cdp_logger
from .net.receiver import Receiver
from .net.sender import Sender
from .net.usb_connector import USBConnector
from ..exception import LynxCDPTimeoutException, LynxNoSessionIdException


def save_to_console_file(session_id, message_obj):
    if 'params' not in message_obj or 'args' not in message_obj['params']:
        return
    log_args = message_obj['params']['args']
    log_level = message_obj['params']['type']
    log_content = ''

    def get_content(log_item):
        type_str = log_item['type']
        if type_str == 'string':
            return log_item['value']
        elif type_str == 'number':
            if 'description' in log_item:
                return log_item['description']
            if 'value' in log_item:
                return log_item['value']
        elif type_str == 'object':
            if 'preview' in log_item and 'className' in log_item and log_item['className'] == 'Object':
                return process_object(log_item['preview'])
            if 'preview' in log_item and 'className' in log_item and log_item['className'] == 'Array':
                return process_array(log_item['preview'])
            if 'value' in log_item:
                return log_item['value']
        return ''

    def process_object(preview):
        properties_dict = {}
        for properties_item in preview['properties']:
            name = properties_item['name']
            properties_dict[name] = get_content(properties_item)
        return ujson.dumps(properties_dict)

    def process_array(preview):
        properties_array = []
        for properties_item in preview['properties']:
            properties_array.append(get_content(properties_item))
        return ujson.dumps(properties_array)

    for item in log_args:
        log_content += get_content(item) + ' '

    console_logger.write("%s:%s:%s" % (session_id, log_level, log_content))

session_list = []

class LynxDebugger(LynxDebuggerPerformance, LynxDebuggerScreenCast,
                   LynxDebuggerDom, LynxTestBench, LynxDebuggerRuntime):

    def __init__(self, device=None, usb_server_port=None, callbacks=[]):
        super(LynxDebugger, self).__init__()
        LynxDebuggerRuntime.__init__(self)
        self.sdkVersion = ''
        self.connector = None
        self.sender = None
        self.receiver = None
        self.start_connect(device=device, usb_server_port=usb_server_port, callbacks=callbacks)
        self.sender.send_custom_data('ListSession', {})

    def start_connect(self, device=None, usb_server_port=None, callbacks=[]):
        self.connector = USBConnector()
        self.sender = Sender(self.connector)
        self.receiver = Receiver(self.sender)
        self.sender.register_listener(self.receiver)
        self.register_listener(self.receiver)
        res = self.connector.connect(usb_server_port=usb_server_port,
                                     device=device,
                                     receiver=self.receiver,
                                     close_callbacks=callbacks)
        if 'sdkVersion' in res['data']['info'].keys():
            self.sdkVersion = res['data']['info']['sdkVersion']

    def register_listener(self, receiver: Receiver):
        def type_session_list(data):
            cdp_logger.warning("[SessionList] Receive SessionList: %s " % json.dumps(data))
            global session_list
            session_list = data
            self.enable_session_log()
            self.enable_session_dom_compression()

        receiver.add_customized_listener('SessionList', callback=type_session_list)

        def method_console_api(data_obj, message_obj):
            cdp_logger.info("Receive: %s " % ujson.dumps(message_obj))
            try:
                save_to_console_file(data_obj['session_id'], message_obj)
            except Exception as e:
                print("save log failed! %s" % str(e))
                cdp_logger.info("save log failed! %s" % str(e))

        receiver.add_cdp_method_listener('Runtime.consoleAPICalled', callback=method_console_api)
        DocumentTreeDelegate.add_method_callback(receiver)

    def enable_session_log(self):
        for session in session_list:
            self.sender.send_cdp_data(session["session_id"], "Debugger.enable", {
                "maxScriptsCacheSize": 100000000
            })
            self.sender.send_cdp_data(session["session_id"], "Runtime.enable", {})

    def enable_session_dom_compression(self):
        """enable dom.getDocument compression status
        """
        for session in session_list:
            self.sender.send_cdp_data(session["session_id"], "DOM.enable", {
                "useCompression": True
            })

    def disconnect(self):
        if self.connector is not None:
            self.connector.disconnect()

    def check_devtool_connected(self):
        try:
            self.sender.socket_send(params={"event": "Ping"})
            self.receiver.wait_for_event("Pong", timeout=3)
            return True
        except LynxCDPTimeoutException:
            return False

    def wait_for_session(self, url_keyword, max_try=4):
        """
        default wait 1 + 1 + 2 + 4 = 8s
        """
        count = 0
        time_list_second = [1, 1, 2, 4]
        while True:
            try:
                self.get_session_id(url_keyword)
                return
            except LynxNoSessionIdException as e:
                if count < max_try:
                    time.sleep(time_list_second[count])
                    count += 1
                else:
                    raise RuntimeError("timeout, can not get the session for %s" % url_keyword)

    def get_session_id(self, url=None):
        query_count = 3
        while query_count > 0:
            if len(session_list) > 0:
                max_session_id = -1
                for session_item in session_list:
                    if session_item['session_id'] > max_session_id:
                        max_session_id = session_item['session_id']
                return max_session_id
            time.sleep(2)
            query_count = query_count - 1

        raise LynxNoSessionIdException(ujson.dumps(session_list))

    def get_session_list(self):
        return session_list

    def get_console_log(self, session_id=None):
        if console_logger.get_log_file():
            with open(console_logger.get_log_file(), 'r') as reader:
                log_content = reader.read()
            session_console_list = []
            for log_item in log_content.split('\n'):
                log_fragment = log_item.split(':', 1)
                if len(log_fragment) < 2:
                    continue
                if session_id is not None and str(session_id) != log_fragment[0]:
                    continue
                session_console_list.append(log_fragment[1])
            return session_console_list
        else:
            return []

    def open_lynx_container(self, url=None):
        return self.sender.open_lynx_container(url)

    def _set_custom_id_wait_time(self, wait_time):
        self.receiver._custom_id_wait_time = wait_time
