# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import re

operators_map = {
    "==": lambda x, y: x == y,
    "!=": lambda x, y: x != y,
    "~=": lambda x, y: ~x == y,
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
}


class Expression(object):
    """expression
    """

    def __init__(self, left, op, right):
        self.left = left
        if op not in operators_map.keys():
            raise ValueError("op=%s is invalid" % op)
        self.op = op
        self.right = right

    def dumps(self):
        return {
            "name": self.left,
            "operator": self.op,
            "value": self.right
        }


class ListItemExpression(Expression):
    """list item expression
    """

    def dumps(self):
        return {
            "name": self.left,
            "value": {"operator": self.op, "value": self.right}
        }


class UPath(list):
    """UI path tool
    """

    def __init__(self, *args, **kwargs):
        """construct a UPath

        :param args: positional predicate expressions
        :type  args: list<Expression>
        :param kwargs: keyword arguments since python2 forbids standalone keyword argument
        :type  kwargs: dict
        """
        super(UPath, self).__init__()
        depth = kwargs.pop("depth", None)
        index = kwargs.pop("index", None)
        predicates = kwargs.pop("predicates", [])
        if index and not isinstance(index, int):
            raise ValueError("index=%s didn't match int" % index)
        if kwargs:
            raise ValueError(
                "unsupported keyword arguments for UPath: %s" % kwargs)
        if depth is not None:
            if not isinstance(depth, int):
                raise ValueError("depth=%s didn't match int" % depth)
            if depth == 0:
                raise ValueError(
                    "depth must be None or integer not equal to 0")
            if depth < 0:
                if (index is not None or len(args) > 0):
                    raise ValueError(
                        "index and predicate shall not be specified when depth < 0")
            else:
                if len(args) == 0 and index is None:
                    raise ValueError(
                        "index or predicate must be specified when depth > 0")

        keys = set()
        list_predicates = {}
        for item in args:
            if not isinstance(item, Expression):
                raise TypeError("upath item=%s didn't match Predicate" % item)
            elif isinstance(item, ListItemExpression):
                list_item = item.dumps()
                name = list_item["name"]
                if name not in list_predicates:
                    list_predicates[name] = {
                        "name": name, "operator": "==", "value": []}
                list_predicates[name]["value"].append(list_item["value"])
            else:
                if item.left in keys:
                    raise ValueError(
                        "predicate with name `%s` was specified twice" % item.left)
                keys.add(item.left)
                predicates.append(item.dumps())
        for predicate in list_predicates.values():
            predicates.append(predicate)
        self.append({"predicates": predicates, "depth": depth, "index": index})

    def __truediv__(self, other):
        if not isinstance(other, (UPath, int)):
            raise TypeError("other=%r didn't match UPath or int" % other)
        if isinstance(other, int):
            other = UPath(index=other, depth=None)
        elif other[0]["depth"] is None:
            other[0]["depth"] = 5
        new_path = UPath()
        new_path[:] = self[:]
        new_path.extend(other)
        return new_path

    __div__ = __truediv__

    def __add__(self, other):
        if not isinstance(other, UPath):
            raise TypeError("other=%r didn't match UPath type" % other)
        new_path = UPath()
        new_path[:] = self[:]
        new_path.extend(other)
        return new_path

    def _combine_predicate(self, name, operator, value):
        if operator == "~=":
            name = "~" + name
            operator = "=="
        if isinstance(value, str):
            value = value.replace("\"", "\\\"")
            value = value.replace("\n", "\\n")
            value = "\"" + value + "\""
        elif value is True:
            value = "True"
        elif value is False:
            value = "False"
        return name + " " + operator + " " + str(value)

    def _upath_item_to_string(self, upath_item, is_first):
        result = "UPath("
        components = []
        for predicate in upath_item["predicates"]:
            name = predicate["name"].replace("-", "_") + "_"
            op = predicate["operator"]
            value = predicate["value"]

            if isinstance(value, (list, tuple)):
                for item in value:
                    op = item["operator"]
                    val = item["value"]
                    components.append(self._combine_predicate(name, op, val))
            else:
                components.append(self._combine_predicate(name, op, value))
        result += ", ".join(components)
        count = len(components)
        if upath_item["index"] is not None:
            if not upath_item["predicates"] and not is_first and upath_item["depth"] is None:
                return str(upath_item["index"])
            if count > 0:
                result += ", "
            result += "index=%s" % upath_item["index"]
            count += 1
        if upath_item["depth"] is not None:
            if count > 0:
                result += ", "
            result += "depth=%s" % upath_item["depth"]
        result += ")"
        return result

    def __str__(self):
        upath_str = ""
        for i, upath_item in enumerate(self):
            if i != 0:
                upath_str += " / "
            upath_str += self._upath_item_to_string(upath_item, i == 0)
        return upath_str

    __repr__ = __str__


class Predicate(object):
    """predicate using to find control
    """

    def __init__(self, name, op=None):
        self.name = name
        self.op = op

    def _ensure_string(self, x):
        if not isinstance(x, str):
            raise ValueError("x=%r didn't match string" % x)

    def _ensure_basic(self, x):
        if not isinstance(x, (int, float, str, list, tuple, dict, set, bool)):
            raise ValueError("x=%r didn't match basic python type" % x)

    def _ensure_bool(self, x):
        if x not in [True, False]:
            raise ValueError("x=%r didn't match bool" % x)

    def _ensure_regex(self, s):
        try:
            re.compile(s)
        except re.error:
            raise ValueError("s=%r is not a valid regular expression" % s)

    def __gt__(self, other):
        raise TypeError("> operation is not supported for %s" % type(self))

    def __ge__(self, other):
        raise TypeError(">= operation is not supported for %s" % type(self))

    def __lt__(self, other):
        raise TypeError("< operation is not supported for %s" % type(self))

    def __le__(self, other):
        raise TypeError("<= operation is not supported for %s" % type(self))


class BasicPredicate(Predicate):
    """basic predicate
    """

    def __eq__(self, other):
        self._ensure_basic(other)
        if self.op == "~=":
            self._ensure_string(other)
            self._ensure_regex(other)
            return Expression(self.name, self.op, other)
        else:
            return Expression(self.name, "==", other)

    def __ne__(self, other):
        self._ensure_basic(other)
        return Expression(self.name, "!=", other)

    def __invert__(self):
        return type(self)(self.name, "~=")


class StringPredicate(Predicate):

    def __eq__(self, other):
        self._ensure_string(other)
        if self.op == "~=":
            self._ensure_regex(other)
            return Expression(self.name, self.op, other)
        else:
            return Expression(self.name, "==", other)

    def __ne__(self, other):
        self._ensure_string(other)
        return Expression(self.name, "!=", other)

    def __invert__(self):
        return type(self)(self.name, "~=")


class BooleanPredicate(Predicate):

    def __eq__(self, other):
        self._ensure_bool(other)
        return Expression(self.name, "==", other)

    def __ne__(self, other):
        self._ensure_bool(other)
        return Expression(self.name, "!=", other)

class ListPredicate(BasicPredicate):
    """list value predicate
    """

    def __eq__(self, other):
        self._ensure_basic(other)
        if self.op == "~=":
            self._ensure_string(other)
            self._ensure_regex(other)
            return ListItemExpression(self.name, self.op, other)
        else:
            return ListItemExpression(self.name, "==", other)

    def __ne__(self, other):
        self._ensure_basic(other)
        return ListItemExpression(self.name, "!=", other)

    def __invert__(self):
        return type(self)(self.name, "~=")
