# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import threading
import ujson


class Sender:
    def __init__(self, connector):
        self._global_request_id = 1
        self._mutex = threading.Lock()
        self._connector = connector

    def register_listener(self, receiver):
        def event_initialize(data):
            self._connector.sender_id = data['data']
            self.socket_send({'event': 'Register', 'data': {'id': self._sender_id(), 'type': 'Driver'}})

        receiver.add_event_listener('Initialize', callback=event_initialize)

        def event_room_joined(data):
            self._connector.device_id = data['data']['id']
            receiver.message_queue.put((data, None))

        receiver.add_event_listener('RoomJoined', callback=event_room_joined)

    def _sender_id(self):
        return self._connector.sender_id

    def _device_id(self):
        return self._connector.device_id

    def get_new_request_id(self):
        self._mutex.acquire()
        self._global_request_id = self._global_request_id + 1
        new_request_id = self._global_request_id
        self._mutex.release()
        return new_request_id

    def send_cdp_data(self, session_id=None, method=None, params=None, session=None):
        request_id = self.get_new_request_id()
        message_obj = {
            'id': request_id,
            'method': method,
            'params': params
        }
        if session is not None:
            message_obj['sessionId'] = session
        self.socket_send({
            'event': 'Customized',
            'data': {
                'type': 'CDP',
                'sender': self._sender_id(),
                'data': {
                    'client_id': self._device_id(),
                    'session_id': session_id,
                    'message': ujson.dumps(message_obj)
                }
            }
        })
        return request_id

    def send_app_data(self, method=None, params=None):
        request_id = self.get_new_request_id()
        message_obj = {
            'id': request_id,
            'method': method,
            'params': params
        }
        self.socket_send({
            'event': 'Customized',
            'data': {
                'type': 'App',
                'sender': self._sender_id(),
                'data': {
                    'client_id': self._device_id(),
                    'session_id': -1,
                    'message': message_obj
                }
            }
        })
        return request_id

    def send_custom_data(self, type_name=None, data=None):
        real_data = {
            'client_id': self._device_id(),
        }
        real_data.update(data)
        self.socket_send({
            'event': 'Customized',
            'data': {
                'type': type_name,
                'sender': self._sender_id(),
                'data': real_data
            }
        })
        return None

    def send_global_switch(self, key, value):
        request_id = self.get_new_request_id()
        message_obj = {
            'global_key': key,
            'global_value': value
        }
        self.socket_send({
            'event': 'Customized',
            'data': {
                'type': 'SetGlobalSwitch',
                'data': {
                    'client_id': self._device_id(),
                    'session_id': -1,
                    'message': message_obj,
                },
                'sender': self._sender_id(),
          },
        })
        return request_id

    def open_lynx_container(self, url=None):
        self.socket_send({
            'event': 'Customized',
            'data': {
                'type': 'OpenCard',
                'sender': self._sender_id(),
                'data': {
                    'type': 'url',
                    'url': url
                }
            }
        })
        return None

    def socket_send(self, data_obj):
        self._connector.socket_send(data_obj)
