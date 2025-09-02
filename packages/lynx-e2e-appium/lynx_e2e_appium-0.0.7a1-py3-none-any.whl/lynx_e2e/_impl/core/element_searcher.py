# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import queue
import re

from .document_tree import LynxNode


def matches(a, b):
    return re.match(b, a) is not None


operators_map = {
    "==": lambda x, y: x == y,
    "!=": lambda x, y: x != y,
    "~=": matches,
    ">": lambda x, y: x > y,
    ">=": lambda x, y: x >= y,
    "<": lambda x, y: x < y,
    "<=": lambda x, y: x <= y,
}


class ElementSearcher:
    """lynx UI Element Searcher
    """

    def __init__(self, lynx_driver):
        self._lynx_driver = lynx_driver

    def _find_target_root_node(self, body_tree_root, node_id=None, local_name=None) -> LynxNode:
        return self._lynx_driver.get_document_tree().find_target_node(body_tree_root, node_id, local_name)

    def find_single_lynx_element_id_by_path(self, target_root, upath_list):
        def find_node_in_path(node, upath_item) -> list:
            index = upath_item['index'] if 'index' in upath_item else None
            depth = upath_item['depth'] if 'depth' in upath_item else None
            predicate_list = path_item["predicates"] if 'predicates' else None
            if predicate_list is None:
                if index is None or len(node.children) > index:
                    return node.children[index: index + 1]
            # bfs search
            q = queue.Queue()
            q.put((node, 0))
            nodes = []
            while not q.empty():
                node, d = q.get()
                if self.check_predicate(predicate_list, node) and d > 0:
                    nodes.append(node)
                    if index is None or len(nodes) > index:
                        return node
                if node.children is not None and len(node.children) > 0 and (depth is None or d < depth):
                    for child_node in node.children:
                        q.put((child_node, d + 1))
            return None

        if len(upath_list) == 0:
            return target_root
        current_node = target_root
        for path_item in upath_list:
            father_node = current_node
            current_node = find_node_in_path(father_node, path_item)
            """double check with a new document tree in case update node error
            which should be fixed in Lynx 2.1 and later
            """
            if current_node is None:
                if self._lynx_driver:
                    self._lynx_driver._document_tree = None
                    self._lynx_driver.get_document_tree()
                    current_node = find_node_in_path(father_node, path_item)
                if current_node is None:
                    break
        return [] if current_node is None else [current_node.id]

    def find_lynx_element_ids_by_path(self, target_root, upath_list):
        def find_node_in_path(node, upath_item) -> list:
            index = upath_item['index'] if 'index' in upath_item else None
            depth = upath_item['depth'] if 'depth' in upath_item else None
            predicate_list = path_item["predicates"] if 'predicates' else None
            if predicate_list is None:
                if index is None or len(node.children) > index:
                    return node.children[index: index + 1]
            q = queue.Queue()
            q.put((node, 0))
            nodes = []
            while not q.empty():
                node, d = q.get()
                if self.check_predicate(predicate_list, node) and d > 0:
                    nodes.append(node)
                if node.children is not None and len(node.children) > 0 and (depth is None or d < depth):
                    for child_node in node.children:
                        q.put((child_node, d + 1))
            if index is None:
                return nodes
            elif len(nodes) > index:
                return [nodes[index]]
            else:
                return []

        if len(upath_list) == 0:
            return target_root
        results = [target_root]
        for path_item in upath_list:
            roots = results
            results = []
            for root in roots:
                father_node = root
                new_results = find_node_in_path(father_node, path_item)
                if new_results is not None:
                    results = results + new_results
        elem_ids = [result.id for result in results]
        return elem_ids

    """Check if current node meets predicate_list condition or not
    """
    def check_predicate(self, predicate_list, _node):
        def sub_attr_match(attr_dict, key, val, op):
            if operators_map[op](attr_dict[target_key], val):
                return True
            for sub_attr in attr_dict[key].split():
                if operators_map[op](sub_attr, val):
                    return True
            return False

        if predicate_list is None or len(predicate_list) == 0:
            return True
        target_key = None
        for predicate in predicate_list:
            target_key = 'text' if predicate['name'] == 'label' else predicate['name']
            target_value = predicate['value']
            op = predicate['operator']
            if target_key in ['name', 'type']:
                if operators_map[op](_node.name, target_value.upper()) or \
                        operators_map[op](_node.name, target_value):
                    continue
                else:
                    return False
            if len(_node.attributes) == 0 or target_key not in _node.attributes:
                return False
            if type(target_value) is list:
                for sub_value in target_value:
                    if not sub_attr_match(_node.attributes, target_key, sub_value['value'], sub_value['operator']):
                        return False
            else:
                if not sub_attr_match(_node.attributes, target_key, target_value, op):
                    return False
        return True
