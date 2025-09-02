
# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from io import BytesIO
import os
import time
import six
import select
import socket
import struct
import logging
import ipaddress
import traceback
import threading

from .exception import AdbCommandError, AdbTimeoutError
from ...testcase.retry import Retry

wait_adb_timeout = 0
adb_recv_timeout = 20
sync_data_max = 64 * 1024

def utf8_encode(s):
    if not isinstance(s, bytes):
        s = s.encode('utf8')
    return s

def is_ipv6_address(addr):
    try:
        ipaddress.IPv6Address(addr)
        return True
    except ipaddress.AddressValueError:
        return False
def smart_create_socket(host):
    if is_ipv6_address(host):
        return socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def is_adb_server_opened(host='localhost', port=5037, bind=False, times=5):
    method = _is_adb_server_opened_by_bind if bind else _is_adb_server_opened_by_connect
    for _ in Retry(limit=times, interval=0.1, raise_error=False):
        if method(host, port):
            return True
    else:
        return False


is_adb_server_opend = is_adb_server_opened


def wait_adb_server_opened(host='localhost', port=5037, bind=False, timeout=10, raise_err=True):
    if not isinstance(timeout, int) or timeout <= 10:
        timeout = 10
    method = _is_adb_server_opened_by_bind if bind else _is_adb_server_opened_by_connect
    should_check_server_stable = False
    for _ in Retry(timeout=timeout, interval=2, raise_error=False):
        if not method(host, port):
            should_check_server_stable = True
            continue
        if should_check_server_stable:
            should_check_server_stable = False
            time.sleep(1)
            continue
        return True

    if raise_err:
        raise AdbCommandError("adb server {}:{} not running".format(host, port))
    return False


def _is_adb_server_opened_by_connect(host='localhost', port=5037):
    sock = smart_create_socket(host)
    try:
        sock.settimeout(3)
        sock.connect((host, port))
        return True
    except socket.error:
        return False
    finally:
        sock.close()


def _is_adb_server_opened_by_bind(host='localhost', port=5037):
    '''Check if ADB Server is running
    '''
    sock = smart_create_socket(host)
    try:
        sock.bind((host, port))
        return False
    except:
        return True
    finally:
        sock.close()

class Pipe(object):
    '''Simulate the implementation of memory pipeline.
    '''

    def __init__(self):
        self._buffer = BytesIO()
        self._max_buffer_size = 1024 * 1024
        self._lock = threading.Lock()
        self._pos = 0
        self._write_buffer = b''
        self._running = True

    def close(self):
        if self._running:
            self._running = False

    def write(self, s):
        self._write_buffer += s
        pos = self._write_buffer.rfind(b'\n')
        if pos <= 0:
            return
        s = self._write_buffer[:pos]
        self._write_buffer = self._write_buffer[pos:]
        with self._lock:
            self._buffer.seek(0, 2)
            self._buffer.write(s)

    def readline(self):
        wait = False
        while self._running:
            if wait:
                time.sleep(0.1)
            with self._lock:
                self._buffer.seek(self._pos)
                ret = self._buffer.readline()
                if len(ret) == 0:
                    wait = True
                    continue
                else:
                    self._pos = self._buffer.tell()
                    self._buffer.seek(0, 2)
                    buffer_size = self._buffer.tell()
                    if buffer_size >= self._max_buffer_size:
                        self._buffer.seek(self._pos)
                        buffer = self._buffer.read()
                        self._buffer.close()
                        self._buffer = BytesIO()
                        self._buffer.write(buffer)
                        self._pos = 0
                    return ret
        return b''

    def read(self):
        '''Read all the data in the pipeline.
        '''
        with self._lock:
            self._buffer.seek(self._pos)
            result = self._buffer.read()
            if self._write_buffer:
                result += self._write_buffer
            return result


class ADBPopen(object):
    class StdinPipe(object):
        '''
        '''

        def __init__(self, sock):
            self._sock = sock

        def write(self, s):
            self._sock.send(s)

        def flush(self):
            pass

    def __init__(self, connect, timeout=None):
        self._sock = connect._sock
        self._stdin = self.StdinPipe(self._sock)
        self._stdout = Pipe()
        self._stderr = Pipe()
        self._running = True
        self._timeout = timeout
        if not isinstance(self._timeout, int) or self._timeout <= 0:
            self._timeout = 0xFFFFFFFF
        self._event = threading.Event()
        self._thread = threading.Thread(
            target=self._work_thread, args=(), name=self.__class__.__name__)
        self._thread.setDaemon(True)
        self._thread.start()
        self._work_thread_error = None
        self._work_thread_error_traceback = None

    @property
    def stdin(self):
        return self._stdin

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    @property
    def pid(self):
        return self._thread.ident

    def _work_thread(self):
        time0 = time.time()
        try:
            while self._running and time.time() - time0 < self._timeout:
                infds, _, _ = select.select([self._sock, ], [], [], 1)
                if len(infds) > 0:
                    buff = self._sock.recv(4096)
                    if len(buff) == 0:
                        self._running = False
                        self._event.set()
                        return
                    self._stdout.write(buff)
        except Exception as e:
            self._work_thread_error = e
            self._work_thread_error_traceback = traceback.format_exc()
            logging.warning("ADBPopen work thread error: %s, traceback: %s" % (self._work_thread_error, self._work_thread_error_traceback))
            self._event.set()
            return
        finally:
            self._stdout.close()
            self._sock.close()
            self._sock = None

    def poll(self):
        if self._thread.is_alive():
            return None
        else:
            return 0

    def terminate(self):
        self._running = False
        time.sleep(1)

    def communicate(self):
        '''
        '''
        while True:
            if self._event.wait(0.001) is True or self.poll() == 0:
                if self._running:
                    if self._work_thread_error:
                        logging.warning("ADBPopen work thread error: %s, traceback: %s" % (self._work_thread_error, self._work_thread_error_traceback))
                        raise self._work_thread_error
                    else:
                        logging.debug(
                            "command execute timeout event state {} , work thread state {}".format(self._event.is_set(),
                                                                                                self.poll()))
                        raise Exception('AdbCommandTimeout! execute timeout about {}s'.format(self._timeout))
                return self.stdout.read(), self.stderr.read()

class _ADBClientConnect(object):

    def __init__(self, server_host='127.0.0.1', server_port=5037):
        self._server_host = server_host
        self._server_port = server_port
        self._connect()

    def _connect(self):
        socket_err = None
        for i in range(3):
            try:
                self._sock = smart_create_socket(self._server_host)
                self._sock.connect((self._server_host, self._server_port))
                return
            except socket.error as e:
                socket_err = e
                if i == 0 and not is_adb_server_opened(self._server_host, self._server_port, times=1):
                    logging.warning("adb server not running , wait for adb server open")
                    wait_adb_server_opened(self._server_host, self._server_port,
                                           timeout=wait_adb_timeout)
                else:
                    logging.warning("connect adb server error , retry after 1s")
                    time.sleep(1)
        if socket_err:
            raise AdbCommandError("connect adb server error {}".format(socket_err))

    def close(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    def check_status(self):
        '''Check the return status.
        Check whether the current communication connection is normal. If there is no response for a long time, it may be abnormal.
        '''
        stat = self.recv(4, adb_recv_timeout)
        if stat == b"OKAY":
            return True
        elif stat == b"FAIL":
            size = int(self.recv(4, adb_recv_timeout), 16)
            val = self.recv(size, adb_recv_timeout)
            self.close()
            raise AdbCommandError(val.decode('utf8'))
        else:
            raise AdbCommandError("Bad response: %r" % (stat,))

    def _send_command(self, cmd, timeout=None):
        if not isinstance(cmd, bytes):
            cmd = cmd.encode('utf8')
        data = b"%04x%s" % (len(cmd), cmd)
        if timeout:
            self._sock.settimeout(timeout)
        self._sock.send(data)
        return self.check_status()

    def send(self, data):
        self._sock.send(data)

    def recv(self, size=None, timeout=None):
        last_timeout = None
        if timeout:
            last_timeout = self._sock.gettimeout()
            self._sock.settimeout(timeout)
        result = b''
        try:
            if size is not None:
                while len(result) < size:
                    data = self._sock.recv(size - len(result))
                    if not data:
                        raise socket.error("device may be offline")
                    result += data
            else:
                data = self._sock.recv(4096)
                while data:
                    result += data
                    data = self._sock.recv(4096)
        except socket.timeout:
            raise AdbCommandError("can not recv data in {}s , may be adb daemon error".format(self._sock.gettimeout()))
        finally:
            if timeout:
                self._sock.settimeout(last_timeout)
        return result

    def send_command(self, cmd, timeout=None):
        self._send_command(cmd, timeout)
        size = int(self._sock.recv(4), 16)
        resp = self._sock.recv(size)
        self.close()
        return resp.decode('utf8')

    def transport(self, device_id):
        self._send_command('host:transport:%s' % device_id)

    def sync_read_mode(self, remote_path):
        remote_path = utf8_encode(remote_path)
        data = b'STAT' + struct.pack(b'I', len(remote_path)) + remote_path
        self._sock.send(data)
        result = self.recv(16, adb_recv_timeout)
        if result[:4] != b'STAT':
            raise AdbCommandError('sync_read_mode error')
        mode, size, time = struct.unpack(b'III', result[4:])
        return mode, size, time

class ADBClient(object):
    instance_dict = {}

    def __init__(self, server_host='127.0.0.1', server_port=5037):
        self._server_host = server_host
        self._server_port = server_port

    def is_adb_server_opend(self):
        return is_adb_server_opened(self._server_host, self._server_port)

    def is_adb_server_opened(self):
        return is_adb_server_opened(self._server_host, self._server_port)

    def list_device(self):
        if not self.is_adb_server_opened():
            if not wait_adb_timeout or \
                not wait_adb_server_opened(self._server_host, self._server_port,
                                           timeout=wait_adb_timeout, raise_err=False):
                return []
        result = self.call('devices', retry_count=3)[0]
        result = result.split('\n')
        device_list = []
        for device in result:
            if len(device) <= 1 or not '\t' in device:
                continue
            device_name, status = device.split('\t')
            if status != 'device':
                continue
            device_list.append(device_name)
        return device_list

    def call(self, cmd, *args, **kwds):
        cmd = cmd.replace('-', '_')
        # if cmd in ['forward', "reverse"] and args[1] in ['--remove', '--list']:
        #     method_prefix = "remove_" if args[1] == "--remove" else "list_"
        #     method_name = method_prefix + cmd
        #     method = getattr(self, method_name)
        #     args = list(args)
        #     args.pop(1)
        # else:
        method = getattr(self, cmd)
        sync = True
        if 'sync' in kwds:
            sync = kwds.pop('sync')
        if 'timeout' in kwds and not cmd in ('shell', 'wait_for_device'):
            kwds.pop('timeout')
        if sync:
            ret = None
            retry_count = kwds.pop('retry_count')
            i = 0
            socket_error_count = 0
            while i < retry_count:
                try:
                    ret = method(*args, **kwds)
                    break
                except socket.error as e:
                    logging.error(u'run %s %s error socket:%s' % (cmd, ' '.join(args), e))
                    socket_error_count += 1
                    if socket_error_count <= 10:
                        i -= 1
                    time.sleep(1)
                except AdbCommandError as e:
                    err_msg = str(e)
                    if "device '{}' not found".format(args[0]) in err_msg:
                        return '', "device not found"
                    elif 'device offline' in err_msg:
                        return '', err_msg
                    elif 'cannot bind' in err_msg:
                        return '', err_msg
                    elif 'listener' in err_msg and "not found" in err_msg:
                        return '', err_msg
                    elif 'Bad response' in err_msg or 'Device or resource busy' in err_msg or 'closed' in err_msg:
                        logging.error('Run %s%s %r' %
                                     (cmd, ' '.join(args), e))
                    else:
                        raise AdbCommandError(u'run %s %s error: %s' %
                                              (cmd, ' '.join(args), err_msg))
                    time.sleep(1)
                    if i >= retry_count - 1:
                        raise e
                except AdbTimeoutError as e:
                    logging.warning('Run cmd timeout %s%s %r' % (cmd, ' '.join(args), e))
                finally:
                    i += 1
            if ret is None:
                raise AdbTimeoutError(u'Run cmd %s %s failed' % (cmd, ' '.join(args)))

            if isinstance(ret, (six.string_types, six.binary_type)):
                return ret, ''
            else:
                return ret
        else:
            c = self._connect()
            c.transport(args[0])
            if cmd == 'shell':
                c._send_command('shell:' + ' '.join(args[1:]))
                pipe = ADBPopen(c)
                return pipe

    def _connect(self):
        return _ADBClientConnect(self._server_host, self._server_port)

    def devices(self):
        '''adb devices
        '''
        c = self._connect()
        result = c.send_command('host:devices')
        return result

    def shell(self, device_id, cmd, **kwds):
        '''adb shell
        '''
        with self._connect() as c:
            c.transport(device_id)
            c._send_command('shell:%s' % cmd)
            result = ADBPopen(c, timeout=kwds['timeout']).communicate()
            with self._connect() as check:
                check.transport(device_id)
            return result

    def pull(self, device_id, src_file, dst_file):
        '''adb pull
        '''
        start = time.time()
        with self._connect() as c:
            c.transport(device_id)
            c._send_command('sync:')
            mode, _, _ = c.sync_read_mode(src_file)
            if mode == 0:
                raise AdbCommandError('remote object %r does not exist' % src_file)

            src_file = utf8_encode(src_file)
            data = b'RECV' + struct.pack(b'I', len(src_file)) + src_file
            c.send(data)
            try:
                f = open(dst_file, 'wb')
            except OSError as e:
                raise AdbCommandError("dst file error: {}".format(e))
            data_size = 0
            while True:
                result = c.recv(8, adb_recv_timeout)
                psize = struct.unpack(b'I', result[4:])[0]

                if result[:4] == b'DONE':
                    break
                elif result[:4] == b'FAIL':
                    raise AdbCommandError(c.recv(psize, adb_recv_timeout))
                elif result[:4] != b'DATA':
                    raise AdbCommandError('pull_file error')

                result = c.recv(psize)
                f.write(result)
                data_size += len(result)

            f.close()
            c.send(b'QUIT' + struct.pack(b'I', 0))
            time_cost = time.time() - start
            if data_size > 0:
                return '%d KB/s (%d bytes in %fs)' % (
                    int(data_size / 1000 / time_cost) if time_cost > 0 else 65535, data_size, time_cost)
            else:
                return ''

    def push(self, device_id, src_file, dst_file):
        '''adb push
        '''
        start = time.time()
        try:
            st = os.stat(src_file)
        except OSError as e:
            if e.errno == 2:
                raise AdbCommandError(
                    "cannot stat '%s': No such file or directory" % src_file)
            else:
                raise e

        with self._connect() as c:
            c.transport(device_id)
            c._send_command('sync:')
            dst_file = utf8_encode(dst_file)
            mode, fsize, ftime = c.sync_read_mode(dst_file)

            s = b'%s,%d' % (dst_file, st.st_mode)
            data = b'SEND' + struct.pack(b'I', len(s)) + s
            c.send(data)
            with open(src_file, 'rb') as fp:
                data = fp.read(sync_data_max)
                data_size = 0
                while data:
                    send_data = b'DATA' + struct.pack(b'I', len(data)) + data
                    c.send(send_data)
                    data_size += len(data)
                    data = fp.read(sync_data_max)

            data = b'DONE' + struct.pack(b'I', int(st.st_mtime))
            c.send(data)
            result = c.recv(8, adb_recv_timeout)
            if result[:4] == b'OKAY':
                time_cost = time.time() - start
                return '%d KB/s (%d bytes in %fs)' % (
                    int(data_size / 1000.0 / time_cost) if time_cost > 0 else 0, data_size, time_cost)
            elif result[:4] == b'FAIL':
                msg_len = struct.unpack(b'I', result[4:])[0]
                error_msg = c.recv(msg_len, adb_recv_timeout)
                raise AdbCommandError(error_msg)
            else:
                raise AdbCommandError('Unexpect data: %r' % result)

    def forward(self, device_id, local, remote):
        '''adb forward
        '''
        with self._connect() as c:
            c._send_command('host-serial:%s:forward:%s;%s' %
                            (device_id, local, remote))
        return ''

    def stop_forward(self, device_id, local):
        '''adb forward --remove
        '''
        with self._connect() as c:
            c._send_command('host-serial:%s:killforward:%s' %
                            (device_id, local))
        return ''

    def list_forward(self, device_id=None):
        forward_map = {}
        c = self._connect()
        ret = c.send_command('host:list-forward')
        for line in ret.split('\n'):
            if line:
                serial, local, remote = line.split()
                if serial not in forward_map:
                    forward_map[serial] = {}
                forward_map[serial][local] = remote
        if device_id:
            return forward_map.get(device_id, {})
        return forward_map

    def list_reverse(self, device_id):
        with self._connect() as c:
            c.transport(device_id)
            ret = c.send_command('reverse:list-forward')
        reverses = {}
        for line in ret.split('\n'):
            if line:
                _, remote, local = line.split()
                reverses[remote] = local
        return reverses

    def reverse(self, device_id, remote, local):
        with self._connect() as c:
            c.transport(device_id)
            c._send_command('reverse:forward:%s;%s' % (remote, local))
            c.check_status()
        return ""

    def remove_reverse(self, device_id, remote):
        '''adb reverse --remove
        '''
        with self._connect() as c:
            c.transport(device_id)
            c._send_command('reverse:killforward:%s' % remote)
            c.check_status()
        return ""

    def get_state(self, device_id):
        if not self.is_adb_server_opend():
            return ""
        c = self._connect()
        try:
            return c.send_command('host-serial:%s:get-state' % (device_id))
        except AdbCommandError as e:
            return ""

    def connect(self, device_id):
        c = self._connect()
        c.send_command('host:connect:%s' % device_id)
        for _ in Retry(timeout=10):
            connected = False
            devices = self.devices().split("\n")
            for device in devices:
                if not device:
                    continue
                parts = device.split()
                if parts[0] == device_id and parts[1] == "device":
                    connected = True
                    break
            if connected:
                break
        return True

    def disconnect(self, device_id):
        c = self._connect()
        result = c.send_command('host:disconnect:%s' % device_id)
        return 'disconnected' in result

    def wait_for_device(self, device_id, **kwds):
        with self._connect() as c:
            c._send_command('host-serial:%s:wait-for-any-device' % (device_id))
            try:
                ADBPopen(c, timeout=kwds['timeout']).communicate()
            except AdbTimeoutError:
                raise AdbCommandError(device_name=device_id, state=self.get_state(device_id))
