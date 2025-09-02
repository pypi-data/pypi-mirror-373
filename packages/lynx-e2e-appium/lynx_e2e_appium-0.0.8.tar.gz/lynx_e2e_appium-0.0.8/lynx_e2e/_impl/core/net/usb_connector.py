# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import socket
import struct
import threading
import time
import ujson

from .base_connector import BaseConnector
from ..logger import cdp_logger


class USBConnector(BaseConnector):
    forward_dict = {}

    def __init__(self):
        super().__init__()
        self.sender_id = 152
        self.device_id = self.sender_id
        self.sock_port = 6100
        self.usb_socket = None
        self.buffer = None
        self.device = None
        self.device_port = None
        self.initial_msg = {"event": "Initialize", "data": self.sender_id}

    def recv_usb_run_forever(self):
        while True:
            try:
                buf = self.usb_socket.recv(1024)
            except OSError as e:
                cdp_logger.info(f'usb connect meets OSError {e} usb disconnect')
                self.on_close(self.usb_socket)
                return
            self.recv_usb_msg(buf)

    def connect(self, usb_server_port, device, receiver, close_callbacks):
        self.receiver = receiver
        self.close_callbacks = close_callbacks
        device_port = usb_server_port if usb_server_port else 8901
        self.device = device
        self.device_port = device_port
        self.device = device
        self.device_port = device_port
        platform = device.type
        cdp_logger.warning("Connect Lynx server starting, %s forward to %s" % (platform, device_port))
        res = None
        if platform == 'Android':
            self.connect_android(device, device_port)
        else:
            res = self.connect_ios(device, device_port)
        sock_thread = threading.Thread(target=self.recv_usb_run_forever, args=())
        sock_thread.setDaemon(True)
        sock_thread.start()
        if platform == 'Android':
            res = self.receiver.wait_for_event("Register", timeout=5)
        cdp_logger.warning("Successfully registered and connected to lynx server over usb socket. Registered info: %s"
                        % res)
        return res

    def disconnect(self):
        if self.usb_socket is not None:
            self.usb_socket.close()
        if self.device is not None:
            self.device.device_driver.stop_forward(self.sock_port)
            self.device.device_driver.get_webdriver().quit()

    def connect_android(self, device, device_port):
        sock_ip = device.adb.device_host
        self.sock_port = device.start_forward(self.sock_port, device_port)
        self.usb_socket = socket.socket()
        try:
            cdp_logger.info('Initial a socket connection on: %s, %s' % (sock_ip, self.sock_port))
            self.usb_socket.connect((sock_ip, self.sock_port))
        except socket.error:
            cdp_logger.warning('fail to setup socket connection')
        cdp_logger.info('Send initialize message: %s' % self.initial_msg)
        self.socket_send(self.initial_msg)
        return None

    def connect_ios(self, device, device_port):
        if hasattr(device.device_driver.__class__, "get_server_ip") and \
            callable(getattr(device.device_driver.__class__, "get_server_ip")):
            sock_ip = device.device_driver.get_server_ip()
        else:
            sock_ip = device.device_driver.get_ip()
        is_simulator = device.device_driver.is_simulator_by_udid(device.udid)
        if is_simulator:
            self.sock_port = device_port
            self.forward_dict[device_port] = self.sock_port
        else:
            if device_port in self.forward_dict.keys():
                self.sock_port = self.forward_dict[device_port]
            else:
                self.sock_port = device.start_forward(self.sock_port, device_port)
                self.forward_dict[device_port] = self.sock_port
        cdp_logger.warning('Initial a socket connection on: %s, %s' % (sock_ip, self.sock_port))
        query_count = 3
        data = None
        while query_count > 0:
            time.sleep(3)
            self.usb_socket = socket.socket()
            self.usb_socket.connect((sock_ip, self.sock_port))
            cdp_logger.warning('Try to socket.connect: %s, %s' % (sock_ip, self.sock_port))
            self.socket_send(self.initial_msg)
            data = self.usb_socket.recv(1024)
            if len(data) > 0:
                break
            query_count -= 1
            cdp_logger.warning('Received no register data, sleep 3 more seconds.')
        else:
            cdp_logger.warning('Failed to setup socket connection')
        msg = str(data[20:].decode('utf-8'))
        self.receiver.on_message(msg)
        res = self.receiver.wait_for_event("Register", timeout=5)
        return res

    def socket_send(self, data_obj):
        data_str = ujson.dumps(data_obj)
        cdp_logger.warning("Socket send: %s" % data_str)
        enc = data_str.encode('utf-8')
        packed_header = struct.pack("! I I I I", 1, 101, 0, len(enc) + 4)
        packed_message = struct.pack("! I {0}s".format(len(enc)), len(enc), enc)
        packet = packed_header + packed_message
        try:
            self.usb_socket.send(packet)
        except OSError as e:
            cdp_logger.exception(f'usb connect meets OSError {e}!')
            raise e

    def recv_usb_msg(self, buf):
        """ receive usb socket data following peertalk standard,
        data example:
        b'\x00\x00\x00\x00\x00\x00\x00e\x00\x00\x00\x00\x00\x00\x01\x94\x00\x00\x01\x80{\n
        "data" : {\n    ' \ b'  "id" : 152,\n      "info" : {\n         "App" : "LynxPlayground",\n
        "AppVersion" : ' \ b'"1.0.0",\n         "deviceModel" : "OnePlus LE2120",\n         "manufacturer" :
        "OnePlus",' \ b'\n         "model" : "LE2120",\n         "network" : "WIFI",\n         "osVersion" :
        "11",' \ b'\n         "sdkVersion" : "0.0.1"\n      },\n      "type" : "runtime"\n   },\n   "event"
        : ' \ b'"Register"\n}\n '
        """
        header_length = 20
        if self.buffer is None:
            self.buffer = buf
        else:
            self.buffer += buf
        while True:
            if len(self.buffer) < header_length:
                return
            header = struct.unpack_from("! I I I I I", self.buffer)
            packet_size = header[4] + header_length
            if len(self.buffer) < packet_size:
                return
            msg = str(self.buffer[header_length:packet_size].decode('utf-8'))
            try:
                self.receiver.on_message(msg)
            except Exception as e:
                cdp_logger.exception(f'Error in on_message handling msg: {msg}')
            self.buffer = self.buffer[packet_size:]
