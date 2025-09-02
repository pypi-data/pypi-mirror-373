# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import time
from ..exception import RetryLimitExceeded


class _RetryItem(object):
    """retry item
    """

    def __init__(self, iteration, timestamps=None):
        self.__iteration = iteration
        self.__ts = timestamps

    @property
    def iteration(self):
        return self.__iteration

    @property
    def ts(self):
        return self.__ts

    def __str__(self):
        return "<%s iter=%s, ts=%s>" % (self.__class__.__name__, self.__iteration, self.__ts)


class _RetryWithTimeout(object):
    """retry mechanism with timeout
    """

    def __init__(self, timeout=60, interval=5, message="", raise_error=True):
        self.interval = interval
        self.timeout = timeout
        self.message = message
        self.raise_error = raise_error
        self.__start_time = None
        self.__count = 0

    def __iter__(self):
        return self

    def next(self):
        if self.__start_time == None:
            self.__count += 1
            self.__start_time = time.time()
            return _RetryItem(self.__count, self.__start_time)
        else:
            time.sleep(self.interval)
            ts = time.time()
            if ts - self.__start_time < self.timeout:
                self.__count += 1
                return _RetryItem(self.__count, ts)
            else:
                if self.raise_error:
                    raise RetryLimitExceeded(
                        "%s[times=%s interval=%s]" % (self.message,
                                                      self.__count,
                                                      self.interval))
                else:
                    raise StopIteration

    __next__ = next


class _RetryWithCount(object):
    """retry mechanism with count
    """

    def __init__(self, limit=3, interval=None, message="", raise_error=True):
        self.limit = limit
        self.raise_error = raise_error
        self.interval = interval
        self.message = message
        self.__count = 0

    def __iter__(self):
        return self

    def next(self):
        self.__count += 1
        if self.__count <= self.limit:
            if self.__count != 1 and self.interval:
                time.sleep(self.interval)
            return _RetryItem(self.__count, time.time())
        if self.raise_error:
            raise RetryLimitExceeded(
                "%s[times=%s interval=%ss]" % (self.message,
                                               self.limit,
                                               self.interval))
        else:
            raise StopIteration

    __next__ = next


class Retry(object):
    """retry mechanism with timeout or limit
    """

    def __init__(self, timeout=10, limit=None, interval=0.5, message="", raise_error=True):
        if limit:
            self._retry = _RetryWithCount(
                limit=limit, interval=interval, message=message, raise_error=raise_error)
        else:
            self._retry = _RetryWithTimeout(
                timeout=timeout, interval=interval, message=message, raise_error=raise_error)

    def __iter__(self):
        return self._retry.__iter__()

    def call(self, callee, *args, **kwargs):
        if not hasattr(callee, "__call__"):
            raise ValueError("callee=%s is not a callable object" % callee)
        for _ in self:
            r = callee(*args, **kwargs)
            if r:
                return r
