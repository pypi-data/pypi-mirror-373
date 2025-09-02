# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import sys
import importlib
import threading
import traceback

def get_attribute_from_string(object_path):
    parts = object_path.split(".")
    parts_len = len(parts)
    mod = None
    import_error = None
    for index in range(parts_len):
        mod_path = ".".join(parts[:index + 1])
        try:
            mod = importlib.import_module(mod_path)
        except ImportError as e:
            import_error = e
            break
    value = mod
    for new_index in range(index, parts_len):
        try:
            value = getattr(value, parts[new_index])
        except AttributeError:
            if new_index + 1 == parts_len:
                msg = "%s has no attribute named \"%s\"" % (
                    value, parts[new_index])
                raise AttributeError(msg)
            else:
                raise import_error
    return value

def dict_deep_update(source, dest):
    for key, value in source.items():
        if key in dest and isinstance(value, dict):
            dict_deep_update(value, dest[key])
        else:
            dest[key] = value

class ThreadGroupLocal(object):
    """local storage for thread group
    equivalent to threading.local() if not used with ThreadGroupScope;
    thread and sub-threads share a common local storage if used with ThreadGroupScope.
    """

    def __init__(self):
        curr_thread = threading.current_thread()
        if hasattr(curr_thread, 'test_group'):
            self.__data = curr_thread.test_local
        else:
            if not hasattr(curr_thread, 'test_local_outofscope'):
                curr_thread.test_local_outofscope = {}
            self.__data = curr_thread.test_local_outofscope

    def __setattr__(self, name, value):
        if name.startswith('_ThreadGroupLocal__'):
            super(ThreadGroupLocal, self).__setattr__(name, value)
        else:
            self.__data[name] = value

    def __getattr__(self, name):
        if name.startswith('_ThreadGroupLocal__'):
            return super(ThreadGroupLocal, self).__getattr__(name)
        else:
            try:
                return self.__data[name]
            except KeyError:
                raise AttributeError(
                    "'ThreadGroupLocal' object has no attribute '%s'" % (name))


class ThreadGroupScope(object):
    """thread group scope, parent thread and child threads share a common scope, eg:

        def _thread_proc():
            ThreadGroupLocal().counter +=1

        with ThreadGroupScope("test_group"):
            ThreadGroupLocal().counter = 0
            t = threading.Thread(target=_thread_proc)
            t.start()
            t.join()
            t = threading.Thread(target=_thread_proc)
            t.start()
            t.join()
            assert ThreadGroupLocal().counter == 2

    """

    def __init__(self, name):
        """init

        :param name: globally unique scope name
        :type name: string
        """
        self._name = name

    def __enter__(self):
        curr_thread = threading.current_thread()
        curr_thread.test_local = {}
        curr_thread.test_group = self._name

    def __exit__(self, *exc_info):
        del threading.current_thread().test_local
        del threading.current_thread().test_group

    @staticmethod
    def current_scope():
        """return current scope storage
        """
        curr_thread = threading.current_thread()
        if hasattr(curr_thread, 'test_group'):
            return curr_thread.test_group

def get_thread_traceback(thread):
    """get stack of thread

    :param thread: target thread to get stack
    :type thread: Thread
    """
    for thread_id, stack in sys._current_frames().items():
        if thread_id != thread.ident:
            continue
        tb = "Traceback ( thread-%d possibly hold at ):\n" % thread_id
        for filename, lineno, name, line in traceback.extract_stack(stack):
            tb += '  File: "%s", line %d, in %s\n' % (filename, lineno, name)
            if line:
                tb += "    %s\n" % (line.strip())
        return tb
    else:
        raise RuntimeError("thread not found")
