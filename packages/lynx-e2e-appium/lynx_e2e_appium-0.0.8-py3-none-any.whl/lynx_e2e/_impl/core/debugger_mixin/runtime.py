# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import json
from ..logger import cdp_logger

class LynxDebuggerRuntime(object):

    def __init__(self):
        self._error_message_list = []
        self._enable_redbox_record = False

    def eval(self, expression, session_id):
        req_id = self.sender.send_cdp_data(session_id=session_id, method='Runtime.evaluate', params={
            "expression": expression
        })
        return self.receiver.wait_for_custom_id(req_id)

    def set_global_switch(self, key, value):
        self.sender.send_global_switch(key, value)

    def _error_event_listener(self, _, message_obj):
        if self._enable_redbox_record:
            cdp_logger.info(f"Receive lynx_error_event: {message_obj}")
            error_dict = json.loads(message_obj['params']['error'])
            error_message = error_dict['error']
            self._error_message_list.append(error_message)

    def clear_error_message(self):
        self._error_message_list = []

    def set_redbox_record(self, enable: bool):
        self._enable_redbox_record = enable
        if enable:
            self.receiver.add_cdp_method_listener("lynx_error_event", self._error_event_listener)
        else:
            self.receiver.remove_cdp_method_listener("lynx_error_event")

    def get_redbox_messages(self) -> list:
        if len(self._error_message_list) > 0:
            return self._error_message_list
        else:
            cdp_logger.warning(f"No redbox error")
            return []
