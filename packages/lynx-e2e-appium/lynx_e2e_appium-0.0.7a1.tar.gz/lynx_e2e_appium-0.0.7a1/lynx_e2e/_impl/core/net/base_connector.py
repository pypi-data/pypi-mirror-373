# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from abc import ABC, abstractmethod

from ..logger import cdp_logger


class BaseConnector(ABC):
    def __init__(self):
        self.close_callbacks = []
        self.receiver = None
        self.room_id = None
        self.socket_url = None
        self.sender_id = None
        self.device_id = None

    def on_error(self, ws, error):
        cdp_logger.exception(error)
        print("### socket on_error ###")
        print(error)

    def on_close(self, ws):
        cdp_logger.warning('Socket closed')
        for callback in self.close_callbacks:
            try:
                if callable(callback):
                    callback()
            except Exception as e:
                print('Error in on_close handling callback: %s' % e)
        print("### socket on_closed ###")

    @abstractmethod
    def connect(self, socket_url, room_id, usb_server_port, device, receiver, close_callbacks):
        pass

    @abstractmethod
    def socket_send(self, data_obj):
        pass

    @abstractmethod
    def disconnect(self):
        pass
