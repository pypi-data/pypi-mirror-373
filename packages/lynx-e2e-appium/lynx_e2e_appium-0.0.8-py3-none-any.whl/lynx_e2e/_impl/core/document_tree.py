# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import base64
import json
import queue
import ujson
import weakref
from zlib import decompress

from .rectangle import Rectangle
from .logger import cdp_logger


class LynxRect:
    """ lynx rect with Rectangle and is_absolute bool
    """

    def __init__(self, rect, is_absolute=False):
        self.value = rect
        self.is_absolute = is_absolute

    def get_absolute_rect(self, container_rect, inner_visual_rect):
        container_width = container_rect.width
        container_height = container_rect.height
        left_offset = container_rect.left
        top_offset = container_rect.top
        width_scale = container_width / inner_visual_rect.width
        height_scale = container_height / inner_visual_rect.height
        if self.is_absolute:
            rect = Rectangle(self.value.left * width_scale,
                             self.value.top * height_scale,
                             self.value.width * width_scale,
                             self.value.height * height_scale)
        else:
            rect = Rectangle(left_offset + self.value.left * width_scale,
                             top_offset + self.value.top * height_scale,
                             self.value.width * width_scale,
                             self.value.height * height_scale)
        return rect

    def get_rated_rect(self, container_rect, inner_visual_rect):
        container_width = container_rect.width
        container_height = container_rect.height
        left_offset = container_rect.left
        top_offset = container_rect.top
        width_scale = container_width / inner_visual_rect.width
        height_scale = container_height / inner_visual_rect.height
        if self.is_absolute:
            rect = Rectangle((self.value.left - left_offset / width_scale) / inner_visual_rect.width,
                             (self.value.top - top_offset / height_scale) / inner_visual_rect.height,
                             self.value.width / inner_visual_rect.width,
                             self.value.height / inner_visual_rect.height)
        else:
            rect = Rectangle(self.value.left / inner_visual_rect.width,
                             self.value.top / inner_visual_rect.height,
                             self.value.width / inner_visual_rect.width,
                             self.value.height / inner_visual_rect.height)
        return rect

    def get_relative_rect(self, container_rect, inner_visual_rect):
        container_width = container_rect.width
        container_height = container_rect.height
        left_offset = container_rect.left
        top_offset = container_rect.top
        width_scale = container_width / inner_visual_rect.width
        height_scale = container_height / inner_visual_rect.height
        if self.is_absolute:
            rect = Rectangle((self.value.left - left_offset / width_scale),
                             (self.value.top - top_offset / height_scale),
                             self.value.width,
                             self.value.height)
        else:
            rect = Rectangle(self.value.left,
                             self.value.top,
                             self.value.width,
                             self.value.height)
        return rect


class LynxNode:
    """lynx document tree node
    """

    def __init__(self, debugger, session_id):
        self.children = []
        self.id = None
        self.parent_id = None
        self.name = None
        self.value = None
        self.attributes = {}
        self.rect = None
        self.debugger = debugger
        self.session_id = session_id

    def get_box_model(self) -> LynxRect:
        box_model = self.debugger.get_box_model(self.session_id, self.id)
        if 'error' in box_model:
            return None
        rect = Rectangle(box_model['model']["padding"][0],
                         box_model['model']["padding"][1],
                         box_model['model']["padding"][2] - box_model['model']["padding"][0],
                         box_model['model']["padding"][5] - box_model['model']["padding"][1], )
        is_absolute = True
        lynx_rect = LynxRect(rect, is_absolute)
        self.rect = lynx_rect
        return lynx_rect

    @staticmethod
    def split_attr_to_dict(src_attributes) -> dict:
        """convert attributes str to dict for future mod
        """
        result = {}
        if len(src_attributes) > 0:
            attr_key = src_attributes[::2]
            attr_value = src_attributes[1::2]
            for i in range(len(attr_key)):
                result[attr_key[i]] = attr_value[i]
        return result

    def convert_node_to_src_dict(self) -> dict:
        """convert node object to original JSON dict for elem_info
        """
        elem_info = {
            "nodeId": self.id,
            "nodeName": self.name,
            "attribute": self.attributes,
            "nodeValue": self.value,
            "children": []
        }
        for child in self.children:
            elem_info["children"].append(child.convert_node_to_src_dict())
        if self.parent_id:
            elem_info["parentId"] = self.parent_id

        return elem_info

    def print_node_tree(self):
        """
        for debug use, print current LynxNode tree
        """

        def dfs_print(node):
            """
            print the node/root tree by dfs recursive
            """
            print("{ ", end="")
            print("nodeId:", node.id, end=",")
            print("localName:", node.name, end=",")

            print("attributes: {", end="")
            if len(node.attributes) > 0:
                for key in node.attributes.keys():
                    print(key, ":", node.attributes[key], end=",")
            print("}, ", end="")
            for child in node.children:
                dfs_print(child)
            print("}, ", end="")

        dfs_print(self)
        print("\n")


class DocumentTree:
    """local lynx document tree data structure
    """

    def __init__(self, src_document_tree, debugger, session_id):
        """ __init__ method
        Args:
            src_document_tree (dict): source document tree dict from devtool cdp data.
            debugger (LynxDebugger): an lynxdebugger instance passed by driver.
            session_id (int): session_id of lynxview passed by driver

        """
        self.dict = {}
        self.debugger = debugger
        self.session_id = session_id
        self.src_document_tree = src_document_tree
        self.root = self.build_tree(src_document_tree)

    def build_tree(self, src_document_tree) -> LynxNode:
        """
        build a lynxElement tree from Dom.document tree
        """
        return self.dfs(src_document_tree)

    def dfs(self, src_node):
        """
        build a lynxElement tree from Dom.document tree by dfs recursive
        """
        node = LynxNode(self.debugger, self.session_id)
        node.id = src_node["nodeId"]
        node.name = src_node["nodeName"]
        if "attributes" in src_node:
            node.attributes = LynxNode.split_attr_to_dict(src_node["attributes"])
        if "nodeValue" in src_node:
            node.value = src_node["nodeValue"]


        if node.id not in self.dict.keys():
            self.dict[node.id] = node
        if "parentId" in src_node:
            node.parent_id = src_node["parentId"]

        for child in src_node["children"]:
            node.children.append(self.dfs(child))
        if "shadowRoots" in src_node:
            for child in src_node["shadowRoots"]:
                node.children.append(self.dfs(child))

        return node

    def print_tree(self):
        """
        for debug use, print whole document tree
        """
        self.dfs_print(self.root)

    def dfs_print(self, node):
        """
        print the document tree by dfs recursive
        """
        print("{ ", end="")
        print("nodeId:", node.id, end=",")
        print("nodeName:", node.name, end=",")
        for child in node.children:
            self.dfs_print(child)
        print("} ", end="")

    def print_dict(self):
        for key in self.dict.keys():
            print("keyNodeId:", key, "nodeId:", self.dict[key].id, "name:", self.dict[key].name, end=",")

    def get(self, args):
        return self.root.children[0]

    def get_node(self, node_id) -> LynxNode:
        return self.dict.get(node_id)

    def set_node_name(self, node_id, new_name):
        node = self.get_node(node_id)
        node.name = new_name

    def get_node_name(self, node_id):
        node = self.get_node(node_id)
        return node.name

    def set_node_value(self, node_id, value):
        node = self.get_node(node_id)
        node.value = value

    def get_node_value(self, node_id):
        node = self.get_node(node_id)
        return node.value

    def set_attributes(self, node_id, new_attributes):
        node = self.get_node(node_id)
        node.attributes = new_attributes

    def get_attributes(self, node_id):
        node = self.get_node(node_id)
        return node.attributes

    def set_attribute_value(self, node_id, attr_name, attr_value):
        node = self.get_node(node_id)
        node.attributes[attr_name] = attr_value

    def get_attribute_value(self, node_id, attr_name):
        node = self.get_node(node_id)
        return node.attributes[attr_name]

    def remove_attribute(self, node_id, attr_name):
        node = self.get_node(node_id)
        return node.attributes.pop(attr_name, None)

    def child_node_inserted(self, parent_id, src_child_node):
        """
        insert node under parent Node
        """
        if isinstance(src_child_node, dict):
            child_node = self.build_tree(src_child_node)
        parent = self.get_node(parent_id)
        parent.children.append(child_node)
        self.dict[child_node.id] = child_node

    def remove_node(self, node_id, parent_id=None):
        """
        remove node from document tree by "nodeId"
        """
        node = self.get_node(node_id)
        if parent_id is None:
            parent_id = node.parent_id
        parent = self.get_node(parent_id)
        parent.children.remove(node)
        self.dict.pop(node_id, None)

    def get_body_tree(self) -> LynxNode:
        """
        In LynxView DOM, root is "#document" node, "PAGE"(LynxView) is root's 1st child.
        That we call it body tree.
        """
        return self.root.children[0]

    def get_box_model(self, node_id):
        """
        get local_box_model/rect of a node, which is diff from cdp box model format
        """
        node = self.get_node(node_id)
        return node.get_box_model()

    def get_relative_rect(self, node_id, container_rect):
        """
        get relative rect of a node
        """
        lynx_view_rect = self.get_box_model(self.get_body_tree().id).value
        node = self.get_node(node_id)
        node_rect = node.get_box_model()
        return node_rect.get_relative_rect(container_rect, lynx_view_rect)

    def get_node_rect(self, node_id):
        """
        box_model rect from document_tree class
        """
        node = self.get_node(node_id)
        return node.get_box_model()

    def get_elem_info(self, node_id):
        """convert node_info dict to json
        """
        if not self.get_node(node_id):
            return {}
        elem_id_dict = {
            'node_id': node_id,
            'node_obj': self.get_node(node_id).convert_node_to_src_dict()
        }
        return json.dumps(elem_id_dict)

    @staticmethod
    def get_ui_tree_with_rect_general(session_id, container_rect, lynx_debugger, dom_tree=None, use_rate=False):
        return DocumentTree.get_ui_tree_with_rect_static(session_id, container_rect,
                                                         lynx_debugger, dom_tree, True, use_rate)

    @staticmethod
    def get_ui_tree_with_rect_static(session_id, container_rect, lynx_debugger, dom_tree=None, is_ng=False,
                                     use_rate=False):
        if not dom_tree:
            dom_tree = lynx_debugger.get_document_with_box_model(session_id)["root"] if is_ng \
                else lynx_debugger.get_document(session_id)["root"]
        body_tree = dom_tree["children"][0]
        inner_visual_rect = DocumentTree.get_box_model_static(session_id, body_tree["nodeId"], lynx_debugger).value

        class BoxModelWrapper:
            def __init__(self, node_id, req_id, debugger):
                self.node_id = node_id
                self.req_id = req_id
                self.debugger = debugger

            def get_rect(self):
                try:
                    box_model = self.debugger.receiver.wait_for_custom_id(self.req_id, timeout=10)
                except Exception as e:
                    cdp_logger.info("BoxModelWrapper get rect fail with node_id %s and req_id %s" %
                                    (str(self.node_id), str(self.req_id)))
                    return None
                if "error" in box_model:
                    return None
                rect = Rectangle(box_model["model"]["padding"][0],
                                 box_model["model"]["padding"][1],
                                 box_model["model"]["padding"][2] - box_model["model"]["padding"][0],
                                 box_model["model"]["padding"][5] - box_model["model"]["padding"][1])
                is_absolute = True
                lynx_rect = LynxRect(rect, is_absolute)
                return lynx_rect

        def send_multiple_box_model(d_node):
            if d_node['nodeName'] == 'SLOT':
                return None
            d_node['boxModelWrapper'] = BoxModelWrapper(d_node['nodeId'],
                                                        DocumentTree.get_fast_model_static(session_id,
                                                                                           d_node['nodeId'],
                                                                                           lynx_debugger),
                                                        lynx_debugger)
            if d_node['childNodeCount'] > 0:
                for item in d_node['children']:
                    send_multiple_box_model(item)
            if 'shadowRoots' in d_node and len(d_node['shadowRoots']) > 0:
                for item in d_node['shadowRoots']:
                    send_multiple_box_model(item)

        def convert_ui_tree(d_node, u_node=None):
            if d_node['nodeName'] == 'SLOT':
                return None
            if u_node is None:
                u_node = {}
            u_node['elem_id'] = d_node['nodeId']
            elem_info = {}
            u_node['elem_info'] = elem_info
            if 'boxModelWrapper' in d_node:
                node_rect = d_node['boxModelWrapper'].get_rect()
                del d_node['boxModelWrapper']
            else:
                node_rect = DocumentTree.convert_box_model_to_rect_static(d_node) if is_ng \
                    else DocumentTree.get_box_model_static(session_id, d_node['nodeId'], lynx_debugger)
            actual_rect = DocumentTree.get_actual_rect(
                container_rect, inner_visual_rect, node_rect)
            if node_rect and inner_visual_rect.width and inner_visual_rect.height and use_rate:
                rect = node_rect.get_rated_rect(container_rect, inner_visual_rect)
                elem_info['rect'] = rect.to_dict()
            else:
                elem_info['rect'] = actual_rect.to_dict()
            elem_info['controller'] = 'LynxElement'
            elem_info['type'] = d_node['nodeName']
            elem_info['_repr'] = d_node['nodeName']
            elem_info['name'] = d_node['nodeName']
            elem_info['visible'] = DocumentTree.is_visible(actual_rect, container_rect)
            attr_dict = LynxNode.split_attr_to_dict(d_node["attributes"])
            elem_info.update(attr_dict)
            u_node['children'] = []
            if d_node['childNodeCount'] > 0:
                for item in d_node['children']:
                    u_node_item = convert_ui_tree(item)
                    if u_node_item is not None:
                        u_node['children'].append(u_node_item)
            if 'shadowRoots' in d_node and len(d_node['shadowRoots']) > 0:
                for item in d_node['shadowRoots']:
                    u_node_item = convert_ui_tree(item)
                    if u_node_item is not None:
                        u_node['children'].append(u_node_item)
            return u_node

        if not is_ng:
            send_multiple_box_model(body_tree)
        ui_tree = convert_ui_tree(body_tree)
        return ui_tree

    @staticmethod
    def get_fast_model_static(session_id, node_id, lynx_debugger):
        return lynx_debugger.get_box_model(session_id, node_id, sync=False)

    @staticmethod
    def get_box_model_static(session_id, node_id, lynx_debugger):
        box_model = lynx_debugger.get_box_model(session_id, node_id)
        if "error" in box_model:
            return None
        rect = Rectangle(box_model["model"]["padding"][0],
                         box_model["model"]["padding"][1],
                         box_model["model"]["padding"][2] - box_model["model"]["padding"][0],
                         box_model["model"]["padding"][5] - box_model["model"]["padding"][1])
        is_absolute = True
        lynx_rect = LynxRect(rect, is_absolute)
        return lynx_rect

    @staticmethod
    def convert_box_model_to_rect_static(node):
        if "box_model" not in node or node["box_model"] is None or not bool(node["box_model"]):
            return None
        rect = Rectangle(node["box_model"]["padding"][0],
                         node["box_model"]["padding"][1],
                         node["box_model"]["padding"][2] - node["box_model"]["padding"][0],
                         node["box_model"]["padding"][5] - node["box_model"]["padding"][1])
        is_absolute = True
        lynx_rect = LynxRect(rect, is_absolute)
        return lynx_rect

    @staticmethod
    def get_actual_rect(container_rect, inner_visual_rect, node_rect):
        if node_rect is None or node_rect.value is None:
            rect = Rectangle(0, 0, 0, 0)
        elif inner_visual_rect.width and inner_visual_rect.height:
            rect = node_rect.get_absolute_rect(container_rect, inner_visual_rect)
        else:
            rect = node_rect.value
        return rect

    @staticmethod
    def is_visible(actual_rect, inner_visual_rect):
        if actual_rect.width * actual_rect.height == 0:
            return False
        if actual_rect.left < inner_visual_rect.left \
            or (actual_rect.left + actual_rect.width) > (inner_visual_rect.left + inner_visual_rect.width) \
            or actual_rect.height > inner_visual_rect.height \
            or actual_rect.top < inner_visual_rect.top:
            return False
        visible_rect = actual_rect & inner_visual_rect
        return visible_rect is not None

    def get_ui_tree_with_rect(self, view_rect, root_id=None, dom_tree=None, use_rate=False):
        return DocumentTree.get_ui_tree_with_rect_static(self.session_id, view_rect,
                                                         self.debugger, dom_tree, True, use_rate)

    def find_target_node(self, body_tree_root=None, node_id=None, node_name=None) -> LynxNode:
        if body_tree_root is None:
            body_tree_root = self.get_body_tree()
        if node_id is not None:
            return self.get_node(node_id)
        elif node_name is not None:
            q = queue.Queue()
            q.put(body_tree_root)
            while not q.empty():
                node = q.get()
                if node_name is not None and node.name == node_name:
                    return node
                else:
                    for child_node in node.children:
                        q.put(child_node)
        raise ValueError("root_id=%s and node_name=%s is not find" % (node_id, node_name))


class DocumentTreeDelegate:
    document_tree_dict = weakref.WeakValueDictionary()

    @staticmethod
    def _child_node_inserted(data_obj, message_obj):
        if 'compress' in message_obj and message_obj['compress']:
            message_obj['params'] = \
                ujson.loads(decompress(base64.b64decode(message_obj["params"].encode('utf8'))))
        child_node = message_obj["params"]["node"]
        parent_id = message_obj["params"]["parentNodeId"]
        session_id =  data_obj['session_id']
        if session_id not in DocumentTreeDelegate.document_tree_dict:
            return
        target_tree = DocumentTreeDelegate.document_tree_dict[session_id]
        if target_tree.find_target_node(node_id=parent_id):
            target_tree.child_node_inserted(parent_id, child_node)

    @staticmethod
    def _child_node_removed(data_obj, message_obj):
        node_id = message_obj["params"]["nodeId"]
        parent_id = message_obj["params"]["parentNodeId"]
        session_id = data_obj['session_id']
        if session_id not in DocumentTreeDelegate.document_tree_dict:
            return
        target_tree = DocumentTreeDelegate.document_tree_dict[session_id]
        if target_tree.find_target_node(node_id=node_id):
            target_tree.remove_node(node_id, parent_id)


    @staticmethod
    def _attribute_modified(data_obj, message_obj):
        attr_name = message_obj["params"]["name"]
        attr_value = message_obj["params"]["value"]
        node_id = message_obj["params"]["nodeId"]
        session_id = data_obj['session_id']
        if session_id not in DocumentTreeDelegate.document_tree_dict:
            return
        target_tree = DocumentTreeDelegate.document_tree_dict[session_id]
        if target_tree.find_target_node(node_id=node_id):
            target_tree.set_attribute_value(node_id, attr_name, attr_value)


    @staticmethod
    def _attribute_removed(data_obj, message_obj):
        attr_name = message_obj["params"]["name"]
        node_id = message_obj["params"]["nodeId"]
        session_id = data_obj['session_id']
        if session_id not in DocumentTreeDelegate.document_tree_dict:
            return
        target_tree = DocumentTreeDelegate.document_tree_dict[session_id]
        if target_tree.find_target_node(node_id=node_id):
            target_tree.remove_attribute(node_id, attr_name)


    @staticmethod
    def add_method_callback(receiver):
        receiver.add_cdp_method_listener('DOM.childNodeInserted', callback=DocumentTreeDelegate._child_node_inserted)
        receiver.add_cdp_method_listener('DOM.childNodeRemoved', callback=DocumentTreeDelegate._child_node_removed)
        receiver.add_cdp_method_listener('DOM.attributeModified', callback=DocumentTreeDelegate._attribute_modified)
        receiver.add_cdp_method_listener('DOM.attributeRemoved', callback=DocumentTreeDelegate._attribute_removed)
        # receiver.add_cdp_method_listener('DOM.documentUpdated', callback=DocumentTreeDelegate._document_updated)
