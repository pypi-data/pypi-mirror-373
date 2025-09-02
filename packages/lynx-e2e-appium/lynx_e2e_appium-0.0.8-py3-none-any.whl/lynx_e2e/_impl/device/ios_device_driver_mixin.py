# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import json
import subprocess


class iOSDeviceDriverMixin(object):
    
    def _run_shell_cmd(self, cmd: list) -> str:
        """
        Execute a shell command and return its output
        Raises RuntimeError if command execution fails
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed ({' '.join(cmd)}): {e.stderr.strip()}")
        except Exception as e:
            raise RuntimeError(f"Command execution error ({' '.join(cmd)}): {str(e)}")

    def is_simulator_by_udid(self, device_id: str) -> bool:
        """
        Check if the given device ID (UDID) belongs to an iOS simulator using Xcode's simctl
        Raises RuntimeError for any execution or parsing errors
        
        :param device_id: The UDID to check
        :return: True if the UDID belongs to a simulator, False otherwise
        """
        # Get all simulators in JSON format
        sim_udid_cmd = ["xcrun", "simctl", "list", "devices", "--json"]
        sim_json = self._run_shell_cmd(sim_udid_cmd)
        
        if not sim_json:
            raise RuntimeError("No output from simulator list command")
        
        # Parse JSON response to extract simulator UDIDs
        try:
            sim_data = json.loads(sim_json)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse simulator list JSON: {str(e)}")
        
        # Check each device group for matching UDID
        for device_group in sim_data.get("devices", {}).values():
            for device in device_group:
                if device.get("udid") == device_id:
                    print(f"Identified as iOS simulator (Name: {device.get('name')}, State: {device.get('state')})")
                    return True
        
        return False
