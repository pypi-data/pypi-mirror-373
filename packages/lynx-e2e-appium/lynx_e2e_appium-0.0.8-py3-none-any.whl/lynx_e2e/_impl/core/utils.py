# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

def version_cmp(ver1, ver2):
    """ comparing version
        rt 1, -1, 0
    """
    if ver1 == ver2:
        return 0
    ver1 = ver1.split('.')
    ver2 = ver2.split('.')
    i = 0
    while True:
        if i >= len(ver1) and i >= len(ver2):
            return 0
        if i >= len(ver1) and i < len(ver2):
            return -1
        if i >= len(ver2) and i < len(ver1):
            return 1
        if ver1[i].isdigit() and ver2[i].isdigit():
            c1 = int(ver1[i])
            c2 = int(ver2[i])
            if c1 > c2:
                return 1
            elif c1 < c2:
                return -1
        elif ver1[i].isdigit():
            return 1
        elif ver2[i].isdigit():
            return -1
        else:
            return 0
        i += 1

def str_to_bool(s: str, true_values=None, false_values=None) -> bool:
    """
    Convert a string to a boolean value.

    :param s: The string to convert
    :param true_values: Custom set of strings considered as True.
                        Defaults to {'true', '1', 'yes', 'y', 't'}
    :param false_values: Custom set of strings considered as False.
                         Defaults to {'false', '0', 'no', 'n', 'f'}
    :return: Boolean value corresponding to the input string
    :raises ValueError: If the string cannot be converted to a boolean
    """
    if true_values is None:
        true_values = {'true', '1', 'yes'}
    if false_values is None:
        false_values = {'false', '0', 'no'}

    if not s:
        raise ValueError("Empty string cannot be converted to a boolean")

    lower_s = s.lower()

    if lower_s in true_values:
        return True
    elif lower_s in false_values:
        return False
    else:
        raise ValueError(
            f"Cannot convert string '{s}' to a boolean. "
            f"Valid values include: {sorted(true_values | false_values)}"
        )
