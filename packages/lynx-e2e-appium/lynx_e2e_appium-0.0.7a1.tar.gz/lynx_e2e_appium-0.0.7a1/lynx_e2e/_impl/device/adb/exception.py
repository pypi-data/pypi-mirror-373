# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.


class AdbCommandError(Exception):
    """Exec adb command failed.
    """
    pass

class AdbTimeoutError(RuntimeError):
    """Exec adb command failed.
    """
    pass

class DeviceSysError(RuntimeError):
    '''
    Device sys error
    '''
    _error_code = 10110
    _error_desc = "Device System Error"

class DeviceScreenshotException(Exception):
    """
    """
    pass