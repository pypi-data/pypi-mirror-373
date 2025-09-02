# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import time

from .logger import cdp_logger
from ..exception import MultiCandidateException, LynxNotFoundException
from ..testcase.retry import Retry

class LynxElementMixin:

    def __init__(self, path=None, root=None, timeout=10, **kwargs):
        self._lynx_driver = None
        self._path = path
        self._root = root
        self._timeout = timeout
        self._device = self.app.get_device()
        self._node_id = None

    def get_lynx_driver(self):
        if self._lynx_driver is None:
            self._lynx_driver = self.container_view.get_lynx_driver()
        return self._lynx_driver

    @property
    def root(self):
        return self._root

    @property
    def app(self):
        if self._root:
            return self._root.app
        return None

    @property
    def text(self):
        """get element's text
        """
        return self.get_lynx_driver().get_text(self.id)

    @text.setter
    def text(self, value):
        """set element's text
        """
        self.get_lynx_driver().set_text(self.id, value)

    @property
    def rect(self):
        inner_rect = self.get_lynx_driver().inner_get_rect(self.id)
        elem_rect = self.get_lynx_driver().scale_rect(inner_rect)
        return elem_rect

    def input(self, text, interval=None):
        """activate element and input text to it

        :param text: target text to be input
        :type  text: str
        :param interval: interval between click and send_keys
        :type  interval: float
        """
        for _ in Retry(limit=5, interval=1, raise_error=False):
            self.click()
            if self.get_lynx_driver().has_keyboard():
                break
        if interval is not None:
            time.sleep(interval)
        self.send_keys(text)

    def get_attribute(self, key):
        return self.get_lynx_driver().get_attribute(self.id, key)

    def get_property(self, name):
        return self.get_attribute(name)

    @property
    def attributes(self):
        return self.get_lynx_driver().get_attributes(self.id)

    @property
    def id(self):
        if not self._node_id:
            self._find_id()
        return self._node_id

    def _find_id(self):
        ambiguous_count = 3
        for item in Retry(timeout=self._timeout, raise_error=False):
            ids = self.get_lynx_driver().get_element_ids(self._path, self.root)
            if not isinstance(ids, (list, tuple)):
                raise TypeError(
                    "ids=%s didn't match list or tuple" % str(ids))
            if len(ids) > 1:
                if ambiguous_count > 0:
                    cdp_logger.info(
                        "retry to get id because %s elements found" % len(ids))
                    ambiguous_count -= 1
                    continue
                error = "path=%r, root=%s got %s matched UIElements:\n" % (self._path,
                                                                           self.root,
                                                                           len(ids))
                visible_elem_ids = []
                elems_string = ""
                for elem_id in ids:
                    elem_info = self.get_lynx_driver().get_element_info(elem_id)
                    if elem_info.get("visible", False):
                        visible_elem_ids.append(elem_id)
                    elems_string += "\n%s" % elem_info
                if len(visible_elem_ids) == 1:
                    cdp_logger.info(
                        "pick the only one visible elem: %s" % elems_string)
                    self._node_id = visible_elem_ids[0]
                    return
                else:
                    raise MultiCandidateException(error + elems_string)
            if len(ids) == 1:
                self._node_id = ids[0]
                return
        error = "path=%r, root=%s not found in %ss for %s times" % (self._path,
                                                                        self.root,
                                                                        self._timeout,
                                                                        item.iteration)
        raise LynxNotFoundException(error)

    def long_click(self, offset_x=0, offset_y=0, duration=1):
        x, y = self.rect.center
        x = x + offset_x
        y = y + offset_y
        self._device.long_click(x, y, duration)

    def drag(self, to_x, to_y, offset_x=0, offset_y=0, duration=None, press_duration=None):
        visible_rect = self.ensure_visible(offset_x, offset_y)
        from_x, from_y = self.get_abs_coordinate(
            visible_rect, offset_x, offset_y)
        self.get_lynx_driver().drag(self.get_lynx_view_id(), from_x, from_y, to_x, to_y, duration, press_duration)

    def scroll(self, distance_x=0, distance_y=0, coefficient_x=None, coefficient_y=None):
        rect = self.rect
        rect = rect & self.get_lynx_driver().get_visual_rect()
        mid_x, mid_y = rect.center
        x1 = mid_x + distance_x / 2
        x2 = mid_x - distance_x / 2
        y1 = mid_y + distance_y / 2
        y2 = mid_y - distance_y / 2
        self.get_lynx_driver().drag(self.get_lynx_view_id(), x1, y1, x2, y2)

    def get_lynx_view_id(self):
        return self.container_view.id

    @property
    def visible(self):
        """first we need check visible attribute of UIElement and then rect
        """
        return self.driver.is_visible(self.id)

    @property
    def existing(self):
        try:
            self._find_id()
        except LynxNotFoundException:
            return False
        return True

    def wait_for_existing(self, timeout=20, interval=0.5, raise_error=True):
        for _ in Retry(timeout=timeout, interval=interval, raise_error=False):
            if self.existing:
                return True
        else:
            if raise_error is False:
                return False
            err_msg = "elem=%s did not exist in %ss" % (self._path, timeout)
            raise LynxNotFoundException(err_msg, error_origin="wait_for_existing")

    def ensure_visible(self, offset_x=0, offset_y=0):
        for _ in Retry(limit=3, message="get visible rect for %s failed" % self):
            visible_rect = self._ensure_visible(offset_x, offset_y)
            if visible_rect is not None:
                break
        return visible_rect

    def _scroll_to_center(self, x, y, origin):
        """scroll to scrollable root center
        """
        distance_x = (x - origin[0]) * 0.5
        distance_y = (y - origin[1]) * 0.5
        self.root.scroll(distance_x, distance_y)

    def _ensure_visible(self, offset_x, offset_y):
        """ensure current UI element is visible
        """
        rect = self.wait_for_ui_stable()
        visual_rect = self.get_lynx_driver().get_visual_rect()
        x, y = self.get_abs_coordinate(rect, offset_x, offset_y)
        if self.visible and (x, y) in visual_rect:
            visible_rect = self.rect & visual_rect
            return visible_rect

        if rect in visual_rect and (x, y) in visual_rect:
            visible_rect = self.handle_invisible_element(rect)
            if visible_rect is not None:
                return visible_rect
        return self._scroll_to_visible(offset_x, offset_y, rect, visual_rect)

    def _scroll_to_visible(self, offset_x, offset_y, elem_rect, visual_rect):
        x, y = self.get_abs_coordinate(elem_rect, offset_x, offset_y)
        scroll_rect = self.root.rect & visual_rect
        if scroll_rect is None:
            root_offset_x, root_offset_y = self.root.get_offset_coordinate(
                abs_x=x, abs_y=y)
            new_scroll_rect = self.root.ensure_visible(
                root_offset_x, root_offset_y)
            scroll_rect = new_scroll_rect & visual_rect
        quartern_width = min(scroll_rect.width, visual_rect.width) / 4
        quartern_height = min(scroll_rect.height, visual_rect.height) / 4
        scroll_origin = None
        rect_records = [elem_rect]
        while True:
            if x < visual_rect.left or x > visual_rect.right:
                x_delta = x - scroll_rect.center[0]
                distance_x = quartern_width * (x_delta / abs(x_delta))
                scroll_origin_x = scroll_rect.center[0]
            else:
                x_delta = 0
                distance_x = 0
                scroll_origin_x = scroll_rect.center[0]
            if y < visual_rect.top or y > visual_rect.bottom:
                y_delta = y - scroll_rect.center[1]
                distance_y = quartern_height * (y_delta / abs(y_delta))
                scroll_origin_y = scroll_rect.center[1]
            else:
                y_delta = 0
                distance_y = 0
                scroll_origin_y = scroll_rect.center[1]
            if scroll_origin is None:
                scroll_origin = (scroll_origin_x, scroll_origin_y)

            need_scrolling = True
            if abs(distance_x) > 0 or abs(distance_y) > 0:
                self.root.scroll(distance_x, distance_y)
            else:
                need_scrolling = False
                self._scroll_to_center(x, y, scroll_origin)
            new_rect = self.rect
            rect_records.append(new_rect)
            new_x, new_y = self.get_abs_coordinate(new_rect,
                                                   offset_x,
                                                   offset_y)

            if self.visible and new_rect.center in visual_rect:
                if need_scrolling:
                    self._scroll_to_center(new_x,
                                           new_y,
                                           scroll_origin)
                    new_rect = self.rect
                return new_rect & visual_rect

            x = new_x
            y = new_y
            visual_rect = self.get_lynx_driver().get_visual_rect()

    def get_abs_coordinate(self, rect, offset_x=0, offset_y=0, ratio_x=None, ratio_y=None):
        """get absolute coordinate for rect

        :param rect: target rectangle
        :type  rect: uibase.common.Rectangle
        :param offset_x: offset for x coordinate
        :type  offset_x: float
        :param offset_y: offset for y coordinate
        :type  offset_y: float
        :param ratio_x: offset ratio for x coordinate, equivalent with: offset_x = rect.width * ratio_x
        :type  ratio_x: float
        :param ratio_y: offset ratio for y coordinate, equivalent with: offset_y = rect.height * ratio_y
        :type  ratio_y: float
        """
        center = rect.center
        x = center[0] + offset_x
        y = center[1] + offset_y
        if ratio_x is not None:
            x = center[0] + rect.width * ratio_x
        if ratio_y is not None:
            y = center[1] + rect.height * ratio_y
        return x, y

    def get_offset_coordinate(self, abs_x=None, abs_y=None, ratio_x=None, ratio_y=None):
        """get offset coordinate for element

        :param abs_x: absolute x coordinate
        :type  abs_x: float
        :param abs_y: absolute y coordinate
        :type  abs_y: float
        :param ratio_x: absolute x ratio coordinate, from 0~1
        :type  ratio_x: float
        :param ratio_y: absolute y ratio coordinate, from 0~1
        :type  ratio_y: float
        """
        if abs_x is not None and ratio_x is not None:
            raise ValueError(
                "abs_x=%s and ratio_x=%s can't be specified simultaneously" % (abs_x, ratio_x))
        if abs_y is not None and ratio_y is not None:
            raise ValueError(
                "abs_x=%s and ratio_x=%s can't be specified simultaneously" % (abs_x, ratio_x))
        rect = self.rect
        offset_x = 0
        if abs_x:
            offset_x = abs_x - 0.5 * rect.width
        if ratio_x:
            offset_x = (ratio_x - 0.5) * rect.width
        offset_y = 0
        if abs_y:
            offset_y = abs_y - 0.5 * rect.height
        if ratio_y:
            offset_y = (ratio_y - 0.5) * rect.height
        return offset_x, offset_y

    def screenshot(self, image_path):
        """get current screen shot by lynx self

        :param image_path: target directory to store screen shot file
        :type  image_path: str
        """
        self.get_lynx_driver().screenshot(image_path, self.rect)
        return image_path

    def send_keys(self, keys):
        raise NotImplementedError("send_keys method should be implemented in LynxElement.")

    def find_elements(self, search_params: dict)->list:
        """Find the target node among the child nodes of the current Element.

        Args:
            search_params (dict): The attribute keyword to be searched for and the corresponding value of the keyword,
            which is format like: {"tag": "lynxview", "lynx-test-tag": "scroll-view"}
        
        Returns:
            list: The target node list, where each element is a LynxElement.
        """
        if not hasattr(self, "get_elements"):
            raise NotImplementedError("LynxElement should implement the get_elements method.")
        elements = self.get_elements(search_params)
        if len(elements) > 0:
            if not isinstance(elements[0], LynxElementMixin):
                raise TypeError("elements=%s should inherit from the LynxElementMixin class." % elements)
        else:
            raise LynxNotFoundException("No element found with the search_params: %s" % search_params)
        return elements

    def get_by_test_tag(self, test_tag, index=None):
        search_params = {}
        if index is None:
            search_params = {"lynx-test-tag": test_tag}
        else:
            search_params = {"lynx-test-tag": test_tag, "index": index}
        return self.find_elements(search_params)

    def get_by_bindtap(self, bindtap_name, index=None):
        search_params = {}
        if index is None:
            search_params = {"bindtap": bindtap_name}
        else:
            search_params = {"bindtap": bindtap_name, "index": index}
        return self.find_elements(search_params)

    def get_by_class(self, class_name, index=None):
        search_params = {}
        if index is None:
            search_params = {"class": class_name}
        else:
            search_params = {"class": class_name, "index": index}
        return self.find_elements(search_params)

    def get_by_text(self, text, index=None):
        search_params = {}
        if index is None:
            search_params = {"text": text}
        else:
            search_params = {"text": text, "index": index}
        return self.find_elements(search_params)

    def get_by_name(self, name, index=None):
        search_params = {}
        if index is None:
            search_params = {"name": name}
        else:
            search_params = {"name": name, "index": index}
        return self.find_elements(search_params)

    def get_by_type(self, type, index=None):
        search_params = {}
        if index is None:
            search_params = {"type": type}
        else:
            search_params = {"type": type, "index": index}
        return self.find_elements(search_params)

    def get_by_placeholder(self, placeholder, index=None):
        search_params = {}
        if index is None:
            search_params = {"placeholder": placeholder}
        else:
            search_params = {"placeholder": placeholder, "index": index}
        return self.find_elements(search_params)
