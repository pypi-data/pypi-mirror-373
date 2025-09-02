# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from functools import wraps


class LynxNotInitialized(Exception):
    """LynxView is not initialized or initializes fail.
    """
    pass


class LynxNotFoundException(Exception):
    """LynxView Element not found
    """
    pass


class LynxCDPTimeoutException(Exception):
    """CDP Response timeout
    """
    pass


class LynxNoSessionIdException(Exception):
    """Can not get session id
    """
    pass


class LynxConnectServerException(Exception):
    """Can not connect lynx devtool server
    """
    pass

class ManagementException(Exception):
    """Case management meets error
    """
    pass

class StopRunningCase(Exception):
    """stop a running case
    """
    pass

class RetryLimitExceeded(Exception):
    """maximum retry limit exceeded error
    """
    pass

class InvalidationException(Exception):
    """User's input is not legal
    """
    pass

class UIAssertionFailure(Exception):
    """UI Assertion Failure
    """
    pass

class MultiCandidateException(Exception):
    """UI Assertion Failure
    """
    pass

class UnSupportException(Exception):
    """
    """
    pass

def try_except_raise(arg):
    """decorator to try...except and raise error
    """

    def _try_except_raise(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print('%s: %s' % (arg, str(e)))
                raise RuntimeError('%s: %s' % (arg, str(e)))

        return wrapper

    return _try_except_raise


def try_except(arg):
    """decorator to try...except without raise error
    """

    def _try_except(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print('%s: %s' % (arg, str(e)))

        return wrapper

    return _try_except
