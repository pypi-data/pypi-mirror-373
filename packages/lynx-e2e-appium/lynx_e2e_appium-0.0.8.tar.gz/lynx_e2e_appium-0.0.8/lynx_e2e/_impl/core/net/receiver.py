# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import ujson
import asyncio
from queue import Queue

from ..logger import cdp_logger
from ...exception import LynxCDPTimeoutException


WAIT_TIME = 60

class Receiver:
    def __init__(self, sender):
        self.sender = sender
        self.message_queue = Queue()
        self._event_listeners = {}
        self._customized_listeners = {}
        self._cdp_method_listeners = {}
        self._add_build_in_listener()

    def _add_build_in_listener(self):
        def event_initialize(data):
            self.sender.sender_id = data['data']
            self.sender.socket_send({'event': 'Register', 'data': {'id': self.sender.sender_id, 'type': 'Driver'}})

        self.add_event_listener('Initialize', callback=event_initialize)

        def event_room_joined(data):
            if 'info' in data['data']:
                self.sender.device_id = data['data']['id']
            self.message_queue.put((data, None))

        self.add_event_listener('RoomJoined', callback=event_room_joined)

    def add_event_listener(self, event, callback):
        self._event_listeners[event] = callback

    def remove_event_listener(self, event):
        self._event_listeners.pop(event)

    def add_customized_listener(self, type_str, callback):
        self._customized_listeners[type_str] = callback

    def remove_customized_listener(self, type_str):
        self._customized_listeners.pop(type_str)

    def add_cdp_method_listener(self, method, callback):
        self._cdp_method_listeners[method] = callback

    def remove_cdp_method_listener(self, method):
        if method in self._cdp_method_listeners:
            self._cdp_method_listeners.pop(method)

    def on_message(self, message):
        obj = ujson.loads(message)
        if 'error' in obj:
            cdp_logger.info("Receive: %s " % message)
            return
        if 'event' in obj and obj['event'] in self._event_listeners:
            cdp_logger.info("Callback event listener: %s " % message)
            self._event_listeners[obj['event']](obj)
        elif 'event' in obj and obj['event'] == 'Customized':
            type_str = obj['data']['type']
            if type_str in self._customized_listeners:
                self._customized_listeners[type_str](obj['data']['data'])
            elif type_str == 'CDP' or type_str == 'App':
                data_obj = obj['data']['data']
                message_str = data_obj['message']
                message_obj = ujson.loads(message_str)
                if message_obj is None or type(message_obj) is not dict:
                    return
                method_name = message_obj["method"] if "method" in message_obj else ''
                if method_name in self._cdp_method_listeners:
                    cdp_logger.info("Callback cdp method listener: %s " % message_str)
                    callback = self._cdp_method_listeners[method_name]
                    if callable(callback):
                        callback(data_obj, message_obj)
                    else:
                        cdp_logger.warning(f"callback is not callable: {callback}")
                else:
                    self.message_queue.put((message_obj, data_obj))
            else:
                self.message_queue.put((obj['data'], None))
        else:
            self.message_queue.put((obj, None))

    def wait_for_event(self, event, timeout=WAIT_TIME, discard=True):
        if not discard:
            async def check_event():
                while True:
                    message_list = list(self.message_queue.queue)
                    for [message, _] in message_list:
                        if 'event' in message and message['event'] == event:
                            return message
            result = asyncio.run(self._monitor_function_timeout_async(check_event, timeout))
            return result
        else:
            while True:
                try:
                    message, data_obj = self.message_queue.get(timeout=timeout)
                except LynxCDPTimeoutException as e:
                    cdp_logger.exception('wait_for_event %s timeout' % event)
                    raise e
                except Exception as e:
                    cdp_logger.exception('wait_for_event %s exception %s' % (event, e))
                    raise e
                if 'event' in message and message['event'] == event:
                    return message

    def wait_for_custom_id(self, id, timeout=WAIT_TIME, raw=False, discard=True):
        if not discard:
            async def check_custom_id(id, raw):
                while True:
                    message_list = list(self.message_queue.queue)
                    for [message, _] in message_list:
                        if 'id' in message and message['id'] == id:
                            if raw:
                                return data_obj
                            if 'result' in message:
                                return message['result']
            result = asyncio.run(self._monitor_function_timeout_async(check_custom_id, timeout))
            return result
        else:
            while True:
                try:
                    message, data_obj = self.message_queue.get(timeout=timeout)
                except Exception as e:
                    cdp_logger.exception('wait_for_custom_id %s timeout' % str(id))
                    raise LynxCDPTimeoutException('wait_for_custom_id %s timeout' % str(id))
                if 'id' in message and message['id'] == id:
                    if raw:
                        return data_obj
                    if 'result' in message:
                        return message['result']

    def wait_for_cdp_method(self, method, timeout=WAIT_TIME, raw=False, discard=True):
        if not discard:
            async def check_cdp_method():
                while True:
                    message_list = list(self.message_queue.queue)
                    for [message, _] in message_list:
                        if 'method' in message and message['method'] == method:
                            if raw:
                                return data_obj
                            return message['params'] if 'params' in message else None
            result = asyncio.run(self._monitor_function_timeout_async(check_cdp_method, timeout))
            return result
        else:
            while True:
                try:
                    message, data_obj = self.message_queue.get(timeout=timeout)
                except Exception as e:
                    cdp_logger.exception('wait_for_cdp_method %s timeout' % method)
                    raise LynxCDPTimeoutException('wait_for_cdp_method %s timeout' % method)

                if 'method' in message and message['method'] == method:
                    if raw:
                        return data_obj
                    return message['params'] if 'params' in message else None

    def wait_for_type_data(self, type_name, timeout=WAIT_TIME, discard=True):
        if not discard:
            async def check_type_data():
                while True:
                    message_list = list(self.message_queue.queue)
                    for [message, _] in message_list:
                        if 'type' in message and message['type'] == type_name:
                            return message['data'] if 'data' in message else None
            result = asyncio.run(self._monitor_function_timeout_async(check_type_data, timeout))
            return result
        else:
            while True:
                try:
                    data_obj, _ = self.message_queue.get(timeout=timeout)
                except Exception as e:
                    cdp_logger.exception('wait_for_type_data %s timeout' % type_name)
                    raise LynxCDPTimeoutException('wait_for_type_data %s timeout' % type_name)

                if 'type' in data_obj and data_obj['type'] == type_name:
                    return data_obj['data'] if 'data' in data_obj else None

    async def _monitor_function_timeout_async(self, func, timeout=WAIT_TIME):
        """
        异步监控函数执行是否超时

        参数:
        func: 要执行的异步函数
        args: 函数的参数（元组形式）
        kwargs: 函数的参数（字典形式）
        timeout_seconds: 超时时间（秒）
        """
        task = asyncio.create_task(func())
        try:
            await asyncio.wait_for(task, timeout=timeout)
            return task.result()
        except asyncio.TimeoutError as e:
            task.cancel()
            raise e
        except Exception as e:
            raise e
