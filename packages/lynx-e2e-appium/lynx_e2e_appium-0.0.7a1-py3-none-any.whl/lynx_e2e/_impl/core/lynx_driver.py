# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import base64
import os

from .debugger import LynxDebugger
from .element_searcher import ElementSearcher
from ..exception import LynxNotFoundException, LynxCDPTimeoutException
from .document_tree import DocumentTree, LynxNode, DocumentTreeDelegate
from .rectangle import Rectangle

from ...api.lynx_view import LynxView


def is_parent_obj(obj, cls):
    for parent in cls.__bases__:
        if isinstance(obj, parent):
            return True
    return False

def is_subclass_obj(obj, cls):
    return isinstance(obj, cls) or any(isinstance(obj, sub_cls) for sub_cls in cls.__subclasses__())

def check_inheritance(obj, cls):
    return is_parent_obj(obj, cls) or is_subclass_obj(obj, cls) or isinstance(obj, cls)

class _LynxElementId(dict):
    def __init__(self, node_id, node_obj):
        self.node_id = node_id
        self.node_obj = node_obj
        super().__init__({
            'node_id': node_id,
            'node_obj': node_obj
        })

class LynxDriver:
    def __init__(self, view, title=None, url=None,
                 description=None, index=0, window_attrs={},
                 lynx_debugger:LynxDebugger = None):
        self._view = view
        self._debugger = lynx_debugger
        self._title = title
        self._url = url
        self._description = description
        self._index = index
        self._tab = None
        self._window_attrs = window_attrs
        self._session_id = None
        self._document_tree = None
        self._element_searcher = ElementSearcher(self)
        self._get_rect_normalization = hasattr(Rectangle, "scale_to_rect")

    def get_session_id(self):
        if self._session_id is None:
            self._session_id = self._debugger.get_session_id()
        return self._session_id

    def _get_target_node(self, ele_id):
        body_obj = self._get_body_tree()
        if check_inheritance(ele_id, LynxView) or ele_id is None:
            target_root = body_obj
        elif isinstance(ele_id, _LynxElementId):
            target_root = self._element_searcher._find_target_root_node(node_id=ele_id.node_id,
                                                                        body_tree_root=body_obj)
        elif isinstance(ele_id, int):
            target_root = self._element_searcher._find_target_root_node(node_id=ele_id, body_tree_root=body_obj)
        else:
            raise ValueError("root_id=%s is not supported" % ele_id)
        return target_root

    def get_children(self, elem_id):
        target_root = self._get_target_node(elem_id)
        return [node.id for node in target_root.children]

    def get_element_ids(self, path, root_id=None):
        """return the first elem_id meet the upath
        """
        try:
            target_root = self._get_target_node(root_id)
            elem_ids = self._element_searcher.find_single_lynx_element_id_by_path(target_root, path)
        except LynxNotFoundException:
            return []
        except LynxCDPTimeoutException:
            return []
        else:
            return elem_ids

    def get_multi_element_ids(self, path, root_id=None):
        """return all elem_ids meet the upath
        """
        try:
            target_root = self._get_target_node(root_id)
            elem_ids = self._element_searcher.find_lynx_element_ids_by_path(target_root, path)
        except LynxNotFoundException:
            return []
        except LynxCDPTimeoutException:
            return []
        else:
            return elem_ids

    def inner_get_rect(self, elem_id):
        """get rect for uibase
        """
        if elem_id is None:
            raise ValueError("elem_id is None")
        if self._get_rect_normalization:
            return self._get_normalized_relative_rect(elem_id)
        return self._get_relative_rect(elem_id)

    def _get_relative_rect(self, node_id):
        return self.get_document_tree().get_relative_rect(node_id, self._view.rect)

    def _get_normalized_relative_rect(self, node_id):
        node_rect = DocumentTree.get_box_model_static(self.get_session_id(), node_id, self._debugger)
        rect = node_rect.get_rated_rect(self._view.rect, self._get_relative_rect(self._get_body_tree().id))
        return rect

    def _get_node_id(self, elem_id):
        return elem_id

    def get_rect(self, elem_id):
        inner_rect = self.inner_get_rect(elem_id)
        elem_rect = self._scale_rect(inner_rect)
        return elem_rect

    def _scale_rect(self, inner_rect):
        return inner_rect.scale_to_rect(self._view.rect)

    def inner_get_visual_rect(self):
        """get container view rect for uibase
        """
        if self._get_rect_normalization:
            return Rectangle(0, 0, 1, 1)
        body_obj = self._get_body_tree()
        return self._get_relative_rect(body_obj.id)

    def get_lynx_perf(self):
        return self._debugger.get_lynx_perf(session_id=self.get_session_id())

    def get_lynx_timing_perf(self):
        return self._debugger.get_lynx_timing_perf(session_id=self.get_session_id())

    def get_console_log(self):
        return self._debugger.get_console_log(session_id=self.get_session_id())

    def _get_box_model(self, node_id):
        return self.get_document_tree().get_box_model(node_id)

    def _get_body_tree(self) -> LynxNode:
        """get document body tree root without document root
        """
        return self.get_document_tree().get_body_tree()

    def is_visible(self, elem_id):
        rect = self.inner_get_rect(elem_id)
        if rect.width * rect.height == 0:
            return False
        container_rect = self.inner_get_visual_rect()
        if container_rect.right < rect.left or container_rect.top > rect.bottom \
            or container_rect.left > rect.right or container_rect.bottom < rect.top:
            return False
        return True

    def scale_rect(self, inner_rect):
        view_rect = self._view.rect
        scaled_left = view_rect.width * inner_rect.left
        scaled_width = view_rect.width * inner_rect.width
        scaled_top = view_rect.height * inner_rect.top
        scaled_height = view_rect.height * inner_rect.height
        left = round(view_rect.left + scaled_left, 2)
        top = round(view_rect.top + scaled_top, 2)
        width = round(scaled_width, 2)
        height = round(scaled_height, 2)
        return Rectangle(left, top, width, height)

    def set_text(self, elem_id, text):
        self.set_attribute(elem_id, "text", text)

    def get_text(self, elem_id):
        body_obj = self._get_body_tree()
        target_node = self._element_searcher._find_target_root_node(body_obj, node_id=self._get_node_id(elem_id), )

        def get_nested_raw_texts(node):
            if node is None:
                return ''
            res = ''
            if node.name in ['RAW-TEXT', 'raw-text'] and 'text' in node.attributes:
                return node.attributes['text']
            for child_node in node.children:
                res = res + get_nested_raw_texts(child_node)
            return res

        if target_node is None:
            return ''
        if target_node.name in ['RAW-TEXT', 'raw-text'] and 'text' in target_node.attributes:
            return target_node.attributes['text']
        elif target_node.name in ['X-INPUT', 'x-input'] and 'value' in target_node.attributes:
            return target_node.attributes['value']
        elif target_node.name in ['TEXT', 'INLINE-TEXT', 'X-TEXT', 'X-INLINE-TEXT', 'text', 'inline-text', 'x-text', 'x-inline-text']:
            return get_nested_raw_texts(target_node)
        return ''

    def get_attribute(self, elem_id, key):
        node_attributes = self.get_attributes(elem_id)
        if key in node_attributes:
            return node_attributes[key]
        else:
            return None

    def set_attribute(self, elem_id, name, value):
        if name == 'x-input':
            self._debugger.set_attributes_as_text(session_id=self.get_session_id(),
                                                  node_id=self._get_node_id(elem_id),
                                                  text="%s=%s" % ('value', value))
        elif name == 'text':
            self._debugger.set_attributes_as_text(session_id=self._get_session_id(),
                                                  node_id=self._get_node_id(elem_id),
                                                  text="%s=%s" % ('text', value))
        else:
            self._debugger.set_attributes_as_text(session_id=self.get_session_id(),
                                                  node_id=self._get_node_id(elem_id),
                                                  text="%s=%s" % (name, value))

    def get_attributes(self, elem_id) -> dict:
        return self.get_document_tree().get_node(elem_id).attributes

    def get_parent(self, elem_id):
        return self.get_document_tree().get_node(elem_id).parent_id

    def node_name(self, elem_id):
        return self.get_document_tree().get_node_name(elem_id)

    def get_ui_tree(self, root_id=None):
        self._debugger._set_custom_id_wait_time(5)
        return [self.get_document_tree().get_ui_tree_with_rect(self._view.rect, root_id=root_id, use_rate=True)]

    def get_document_tree(self) -> DocumentTree:
        """get completed document tree root without document root
            keep singleton, avoid repeat DOM request
        """
        if not self._document_tree:
            self._document_tree = DocumentTree(self.get_src_document_tree(), self._debugger, self.get_session_id())
            DocumentTreeDelegate.document_tree_dict[self.get_session_id()] = self._document_tree
        return self._document_tree

    def get_src_document_tree(self):
        """unique entrance for all to get remote DOM tree
        """
        return self._debugger.get_document(session_id=self.get_session_id())["root"]

    def get_element_info(self, elem_id):
        """convert elem_id dict to json
        """
        return self.get_document_tree().get_elem_info(elem_id)

    def screenshot(self, image_path, rect):
        screen_shot_image_data = self._debugger.screencast_frame(self.get_session_id())
        with open(image_path, 'wb+') as image:
            image.write(base64.b64decode(screen_shot_image_data["data"].encode("utf8")))
        import cv2
        image = cv2.imread(image_path)
        scale = 1
        platform = os.environ.get('platform')
        if platform.lower()  == "ios":
            # device = self._view.app.get_device()
            # screen_rect = device.device_driver.get_screen_rect()
            # screen_resolution = device.device_driver.get_screen_resolution()
            # scale = int(screen_resolution.width / screen_rect.width)
            scale = 3
        crop_img = image[rect.top * scale:(rect.top + rect.height) * scale,
                   rect.left * scale:(rect.left + rect.width) * scale]
        ret = cv2.imwrite(image_path, crop_img)
        return ret
