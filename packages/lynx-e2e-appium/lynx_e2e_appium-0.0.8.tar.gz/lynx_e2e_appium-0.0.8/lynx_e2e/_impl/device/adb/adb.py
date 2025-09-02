# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys
import logging
import threading
import subprocess

from ...device.adb.adb_client import ADBClient, is_adb_server_opened
from ...device.adb.exception import AdbCommandError


wait_device_timeout = 20

class EnumRootState(object):
    Unknown = 0
    NonRoot = 1
    AdbdRoot = 2
    SuRoot = 3


class ADB(object):
    armeabi = 'armeabi'
    x86 = 'x86'

    connect_timeout = 300

    def __init__(self, device_name, host='127.0.0.1', port=5037, adb_client=None):
        self._adb_client = adb_client if adb_client else ADBClient(host, port)
        self._device_name = device_name
        self._root_state = EnumRootState.Unknown

        self._need_quote = None
        self._log_filter_thread_list = []
        self._shell_prefix = None
        self._logcat_callbacks = []
        self._newline = None
        self._su_prefix = "su -c"
        self._package_activity_map = {}
        self.__forward_ports = set()
        self._device_spec = {}

    @property
    def device_host(self):
        return self._adb_client._server_host

    @property
    def device_name(self):
        return self._device_name

    def adb_command(self, cmd, *args, **kwargs):
        retry_count = 3
        if 'retry_count' in kwargs:
            retry_count = kwargs.pop('retry_count')
        timeout = 20
        if 'timeout' in kwargs:
            timeout = kwargs.pop('timeout')
        sync = True
        if 'sync' in kwargs:
            sync = kwargs.pop('sync')

        binary_output = kwargs.get('binary_output', False)

        for times in range(retry_count):
            if not threading.current_thread().ident in self._log_filter_thread_list:
                logging.debug('adb %s:%s %s %s' % (
                    self.device_host, self.device_name, cmd, ' '.join(args)))
                pass
            try:
                result = self._adb_client.call(cmd, self._device_name, *args, sync=sync, retry_count=1,
                                               timeout=timeout)
            except Exception as e:
                logging.error('Exec adb %s failed: %s' % (cmd, e))
                if times == retry_count - 1:
                    raise e
                else:
                    continue

            if not isinstance(result, tuple):
                return result
            out, err = result
            if err:
                if "device not found" in err or 'device offline' in err:
                    self._adb_client.wait_for_device(self.device_name, timeout=wait_device_timeout)
                    return self.adb_command(cmd, *args, **kwargs)
                return err
            if isinstance(out, (bytes, str)) and not binary_output:
                out = out.strip()
            return out

    def shell_command(self, cmd_line, **kwds):
        if isinstance(cmd_line, bytes):
            cmd_line = cmd_line.decode('utf8')

        if not self._newline:
            result = self.adb_command('shell', 'echo "1\n2"')
            if b'\r\n' in result:
                self._newline = b'\r\n'
            else:
                self._newline = b'\n'

        binary_output = kwds.get('binary_output', False)

        def _handle_result(result):
            if not isinstance(result, (bytes, str)):
                return result
            if binary_output:
                return result
            if self._newline != b'\n' and isinstance(result, bytes):
                result = result.replace(self._newline, b'\n')

            if isinstance(result, bytes):
                try:
                    result = result.decode('utf8')
                except UnicodeDecodeError:
                    logging.debug("decode error,origin result :\n{}".format(repr(result)))
                    return result.decode("utf8", "replace")

            if self._shell_prefix != None and self._shell_prefix > 0:
                result = '\n'.join(result.split('\n')[self._shell_prefix:])
            if result.startswith('WARNING: linker:'):
                lines = result.split('\n')
                idx = 1
                while idx < len(lines):
                    if not lines[idx].startswith('WARNING: linker:'):
                        break
                    idx += 1
                return '\n'.join(lines[idx:]).strip()
            else:
                return result

        return _handle_result(self.adb_command('shell', '%s' % cmd_line, **kwds))

    def forward(self, local_port, remote, forward_type='tcp'):
        '''port forward
        '''
        while 1:
            ret = self.adb_command('forward', 'tcp:%d' % local_port, '%s:%s' % (forward_type, remote))
            if not 'cannot bind' in ret:
                self.__forward_ports.add(local_port)
                return local_port
            local_port += 1

    def list_forward(self):
        '''
        :return: dict {"local":"remote"}
        '''
        return self.adb_command('forward', '--list')

    def stop_forward(self, local_port):
        return 'not found' not in self.adb_command('forward', '--remove', 'tcp:%d' % local_port)

    def start_activity(self, activity_name='', action='', type='', data_uri='', category='', extra={}, wait=True):
        if activity_name:
            if "$" in activity_name:
                activity_name = "\'{}\'".format(activity_name)
            activity_name = '-n %s ' % activity_name
        if action:
            action = '-a %s ' % action
        if type:
            type = '-t %s ' % type
        if data_uri:
            data_uri = '-d "%s" ' % data_uri
        if category:
            category = '-c "%s" ' % category
        extra_str = self._build_intent_extra_string(extra)
        W = u''
        if wait:
            W = '-W'
        command = 'am start %s %s -S %s%s%s%s%s' % (
            W, activity_name, action, category, type, data_uri, extra_str)
        if command[-1] == ' ':
            command = command[:-1]
        result = self.shell_command(command, timeout=15, retry_count=3)

        ret_dict = {}
        for line in result.split('\n')[1:]:
            if ': ' in line:
                key, value = line.split(': ')
                ret_dict[key] = value
        if 'Error' in ret_dict:
            raise AdbCommandError(ret_dict['Error'])
        return ret_dict

    def _build_intent_extra_string(self, extra):
        extra_str = ''
        for key in extra:
            p_type = ''
            value = extra[key]
            if isinstance(value, bytes):
                value = value.decode('utf8')

            if value in ['true', 'false']:
                p_type = 'z'
            elif isinstance(value, bool):
                p_type = "z"
                value = 'true' if value is True else 'false'
            elif isinstance(value, int):
                if self._is_int(value):
                    p_type = 'i'
                else:
                    p_type = 'l'
            elif isinstance(value, float):
                p_type = 'f'
            elif value.startswith('file://'):
                p_type = 'u'
            param = '-e%s %s %s ' % (p_type, key,
                                     ('"%s"' % value) if not p_type else value)
            if p_type:
                param = u'-' + param
            extra_str += param
        if len(extra_str) > 0:
            extra_str = extra_str[:-1]
        return extra_str

    def _is_int(num):
        return (num <= 2147483647 and num >= -2147483648)

    def get_current_process(self):
        cmd = "dumpsys window windows | grep mCurrentFocus"
        if self.sdk_version() >= 29:
            cmd = 'dumpsys window displays | grep -E "mCurrentFocus|mStableFullscreen"'
        response = self.shell_command(cmd)
        p = re.compile(r'Window{(.*:)?( .*: )?(\w+)( .*)? u(\d+) (.*)}')
        ret = p.search(response)
        return ret.group(6).split('/')[0]

    def get_property(self, prop):
        '''get device property
        '''
        return self.shell_command('getprop %s' % prop)

    def sdk_version(self):
        '''get sdk version
        '''
        try:
            return int(self.get_property("ro.build.version.sdk"))
        except ValueError as e:
            err_msg = "" if not e.args else e.args[0]
            raise AdbCommandError(err_msg)

_adb_path = None

def get_adb_path():
    global _adb_path
    if _adb_path is None:
        if sys.platform == 'win32':
            sep = ';'
            file_name = 'adb.exe'
        else:
            sep = ':'
            file_name = 'adb'
        for root in os.environ.get('PATH').split(sep):
            adb_path = os.path.join(root, file_name)
            if os.path.exists(adb_path):
                return adb_path

        raise RuntimeError("Can not find local adb, is it installed?")
    return _adb_path

class LocalAdbServer(object):

    @staticmethod
    def stop():
        subprocess.call([get_adb_path(), 'kill-server'])

    @staticmethod
    def start(server_port=5037):
        if is_adb_server_opened("127.0.0.1", server_port):
            return False
        subprocess.call([get_adb_path(), 'start-server'])
        return True

    @staticmethod
    def connect_device(name):
        proc = subprocess.Popen(
            [get_adb_path(), 'connect', name], stdout=subprocess.PIPE)
        result = proc.stdout.read()
        if result.find('unable to connect to') >= 0:
            print(result, file=sys.stderr)
            return False
        return True

if __name__ == '__main__':
    pass
