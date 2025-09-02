# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import re
import subprocess
import threading

from ...api.config import settings
from .exception import ResourceNoMatchedError
from .device import get_device_class, get_device_driver_class

class DeviceHandler(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._resource_records = {}
        self._session_map = {}
        self._providers = {}

    def create_session(self, testcase):
        session = testcase.test_name
        self._session_map[session] = {"case": testcase,
                                      "resources": {}}
        return session

    def destroy_session(self, session):
        with self._lock:
            session_data = self._session_map.pop(session)
            for _, lock in session_data["resources"].items():
                lock.release()

    def acquire(self, session, conditions={}):
        if isinstance(conditions, dict):
            conds = [conditions]
        else:
            conds = conditions
        matched_resources = []
        for cond in conds:
            resources = self.query(cond)
            for resource in resources:
                with self._lock:
                    self._resource_records[resource] = session
                matched_resources.append(resource)
                break
        return matched_resources

    def release(self, resource):
        pass

    def get_lock_name(self, resource):
        return resource.udid

    def get_acquired_resources(self, session):
        resource_info = self._session_map[session]["resources"]
        return list(resource_info.keys())

    def _get_devices(self):
        platform = os.environ.get('platform', "android")
        if platform.lower() == 'android':
            return self._get_android_devices()
        elif platform.lower() == 'ios':
            return self._get_ios_devices()
        else:
            raise ValueError("platform=%s is not supported" % platform)

    def _get_android_devices(self):
        from lynx_e2e._impl.device.adb.adb_client import ADBClient
        host, port = settings.ANDROID_ADB_SERVER
        adb_client = ADBClient(host, port)
        if host == "127.0.0.1" and port == 5037 and not adb_client.is_adb_server_opend():
            from lynx_e2e._impl.device.adb.adb import LocalAdbServer
            LocalAdbServer.start()

        devices = []
        device_names = adb_client.list_device()
        if not device_names:
            return devices
        for name in device_names:
            device_driver_class = get_device_driver_class()
            device_class = get_device_class()
            devices.append(device_class(device_driver_class(name, host, port)))
        return devices

    def _get_ios_devices(self):
        devices = []
        device_list = self._list_ios_devices()
        simulator_list = self._list_booted_ios_simulators()
        if simulator_list:
            device_list.extend(simulator_list)
        if not device_list:
            return devices
        for device in device_list:
            device_driver_class = get_device_driver_class()
            device_class = get_device_class()
            devices.append(device_class(device_driver_class(device["device_id"])))
        return devices

    def _list_ios_devices(self):
        def get_connected_devices():
            sp_result = subprocess.run(["system_profiler", "SPUSBDataType"], capture_output=True, text=True)
            connected_devices_info = []
            device_info = {}
            found_device = False
            for line in sp_result.stdout.splitlines():
                if "iPhone" in line or "iPad" in line or "iPod" in line:
                    found_device = True
                    device_info = {}
                if found_device:
                    if "Serial Number:" in line:
                        device_info["serial_number"] = line.split(":")[1].strip()
                        connected_devices_info.append(device_info.copy())
                        found_device = False
            return connected_devices_info
        pattern = r'(.*?)\s*\((.*?)\)\s*\((.*?)\)'
        connected_devices_info = get_connected_devices()
        xctrace_result = subprocess.check_output(["xcrun", "xctrace", "list", "devices"], timeout=60, text=True)
        devices_list = xctrace_result.splitlines()
        connected_devices = []
        for line in devices_list:
            for device_info in connected_devices_info:
                device_id_prefix = device_info["serial_number"][:8]
                if device_id_prefix in line:
                    matches = re.search(pattern, line)
                    if matches:
                        device_name = matches.group(1)
                        version = matches.group(2)
                        device_id = matches.group(3)
                        connected_devices.append({"device_name": device_name, "device_id": device_id, "version": version})
        return connected_devices

    def _list_booted_ios_simulators(self):
        result = subprocess.run(
            ["xcrun", "simctl", "list", "devices", "booted"],
            capture_output=True,
            text=True,
            timeout=60
        )

        booted_simulators = []
        pattern = r'^(.*?)\s*\(([0-9A-F-]+)\)\s*\(Booted\)'

        for line in result.stdout.splitlines():
            match = re.match(pattern, line.strip())
            if match:
                device_name = match.group(1)
                device_id = match.group(2)
                version = "unknown"
                booted_simulators.append({
                    "device_name": device_name,
                    "device_id": device_id,
                    "version": version,
                    "state": "booted"
                })

        return booted_simulators

    def query(self, conditions={}):
        devices = []
        temp_devices = self._get_devices()
        for temp_device in temp_devices:
            for key, value in conditions.items():
                v = getattr(temp_device, key)
                if key == "tags":
                    value = set(value)
                    if not value.issubset(v):
                        break
                elif v != value:
                    break
            else:
                devices.append(temp_device)
        return devices

    def on_acquire(self, resource):
        resource.device_driver.on_acquired()

    def on_release(self, resource):
        resource.device_driver.on_release()

    def release(self, resource):
        """release a device resource

        :param resource: a device
        :type  resource: uibase.device.Device
        """
        resource.stop_forwards()
        resource.remove_reverses()


class ResourceManager(object):
    """resource manager
    """

    def __init__(self, testcase):
        self.testcase = testcase
        self.resource_handlers = {}
        self._session_map = {}
        self.resource_handlers["device"] = DeviceHandler()

    def acquire(self, res_type, conditions={}, auto_clean=True):
        """acquire a resource

        :param res_type: resource type
        :type  res_type:str
        :param conditions: single condition or condition list
        :type  conditions: dict or list<dict>
        :return: resources: single resource or resource list in corresponds to conditions type
        :rtype: any or list<any>
        """
        if res_type not in self.resource_handlers:
            raise ValueError("res_type=%s is not supported" % res_type)
        handler = self.resource_handlers[res_type]
        if res_type not in self._session_map:
            self._session_map[res_type] = handler.create_session(self.testcase)
        session = self._session_map[res_type]
        resources = handler.acquire(session, conditions)
        if isinstance(resources, dict):
            resources = [resources]
        for resource in resources:
            if auto_clean:
                msg = "auto release[%s]:%s" % (res_type, resource)
                self.testcase.add_cleanup(msg,
                                          self.release,
                                          res_type,
                                          resource)
        if isinstance(conditions, dict):
            if isinstance(resources, list):
                if len(resources) > 0:
                    return resources[0]
                else:
                    raise ResourceNoMatchedError(
                            "no resource matched in: %s" % resources)
            else:
                return resources
        else:
            return resources

    def release(self, res_type, resource):
        """acquire a resource

        :param res_type: resource type
        :type  res_type:str
        :param resource: resouce object
        :type  resource: any
        """
        if res_type not in self.resource_handlers:
            raise ValueError("res_type=%s is not supported" % res_type)
        handler = self.resource_handlers[res_type]
        handler.release(resource)

    def query(self, res_type, conditions={}):
        """query resource list

        :param res_type: resource type
        :type  res_type:str
        :param conditions: conditions
        :type  conditions: dict
        """
        if res_type not in self.resource_handlers:
            raise ValueError("res_type=%s is not supported" % res_type)
        handler = self.resource_handlers[res_type]
        resources = handler.query(conditions)
        return resources

    def release_all(self):
        """destroy all sessions and release all resources
        """
        for res_type, session in self._session_map.items():
            handler = self.resource_handlers[res_type]
            handler.destroy_session(session)
        self._session_map.clear()

    def get_acquired_resources(self, res_type):
        if res_type not in self.resource_handlers:
            raise ValueError("res_type=%s is not supported" % res_type)
        handler = self.resource_handlers[res_type]
        if res_type in self._session_map:
            return handler.get_acquired_resources(self._session_map[res_type])
        else:
            return []
