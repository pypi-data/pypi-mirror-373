# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import re

from ...api.exception import LynxNotFoundException

class AndroidDeviceDriverMixin(object):
    
    def get_activity_process_name(self, activity_name):
        '''
        从当前activity_stack中获取 activity进程信息
        :param activity_name:
        :return:
        '''
        p = re.compile(r'^\s+ACTIVITY (.*)/(.*) (.*) (.*)$')
        result = self.shell_command("dumpsys activity top | grep 'ACTIVITY'")
        result = result.replace('\r', '')
        activities = []
        for line in result.split('\n')[1:]:
            activity_ret = p.match(line)
            if activity_ret:
                current_process_name = activity_ret.group(1)
                current_activity_name = activity_ret.group(2)
                activities.append(current_activity_name)
                if current_activity_name == activity_name:
                    return current_process_name
        
        msg = f"can not found activity {activity_name} process name in activities {activities}"
        raise LynxNotFoundException(msg)

    def get_app_version(self, package_name):
        p = re.compile(r'^\s+versionName=(.*)$')
        result = self.shell_command("dumpsys activity top | grep 'ACTIVITY'")
        result = result.replace('\r', '')
        for line in result.split('\n')[1:]:
            version_ret = p.match(line)
            if version_ret:
                return version_ret.group(1)

        msg = f"can not get app version for package {package_name}"
        raise LynxNotFoundException(msg)

    def get_current_process(self):
        """get current process / package name
        :return: package name
        :rtype: str
        """
        current_process = self._adb.get_current_process()
        return current_process