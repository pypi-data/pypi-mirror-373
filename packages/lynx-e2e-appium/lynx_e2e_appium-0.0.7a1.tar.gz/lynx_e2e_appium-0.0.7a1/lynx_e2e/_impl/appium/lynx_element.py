
# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from appium.webdriver.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy

from ..core.upath import UPath
from ..core.lynx_element_mixin import LynxElementMixin
from ..exception import LynxNotFoundException, UnSupportException


class LynxElement(LynxElementMixin, WebElement):
    
    def __init__(self, element: WebElement, path=None, root=None, container_view=None):
        self._web_element = element
        self.view_spec = {}
        LynxElementMixin.__init__(self, path, root)
        if element != None:
            self._parent = element._parent
            self._id = element._id
        self.container_view = container_view

    def click(self, offset_x=0, offset_y=0):
        x, y = self.rect.center
        x = x + offset_x
        y = y + offset_y
        self._device.click(x, y)

    def get_by_class(self, class_name, index=None):
        if not self._web_element:
            raise UnSupportException("Get child elements from current element is not supported.")
        elements = self._web_element.find_elements(AppiumBy.CLASS_NAME, class_name)
        if len(elements) == 0:
            raise LynxNotFoundException(f"Can't find element with class_name {class_name}")
        if index is None:
            index = 0
        if len(elements) <= index:
            raise LynxNotFoundException(f"There are only {len(elements)} elements with class_name {class_name}.\
                                    The element at {index} cannot be obtained.")
        path = UPath(predicates=[{"name": "class", "value": class_name, "operator": "=="}], index=index)
        return LynxElement(elements[index], path=path, root=self, container_view=self.container_view)

    def get_by_test_tag(self, test_tag, index=None):
        elements = self._web_element.find_elements(AppiumBy.XPATH, f"//*[@view-tag='{test_tag}']")
        path = UPath(predicates=[{"name": "lynx-test-tag", "value": test_tag, "operator": "=="}], index=index)
        if len(elements) == 0:
            return LynxElement(None, path=path, root=self, container_view=self)
        if len(elements) <= index:
            raise LynxNotFoundException(f"There are only {len(elements)} elements with test_tag {test_tag}.\
                                    The element at {index} cannot be obtained.")
        return LynxElement(elements[0], path=path, root=self, container_view=self)

    def get_by_text(self, text, index=None):
        if not self._web_element:
            raise UnSupportException("Get child elements from current element is not supported.")
        elements = self._web_element.find_elements(AppiumBy.XPATH, f"//*[contains(@text, '{text}')]")
        if len(elements) == 0:
            raise LynxNotFoundException(f"Can't find element with text {text}")
        if index is None:
            index = 0
        if len(elements) <= index:
            raise LynxNotFoundException(f"There are only {len(elements)} elements with text {text}.\
                                    The element at {index} cannot be obtained.")
        path = UPath(predicates=[{"name": "text", "value": text, "operator": "=="}], index=index)
        return LynxElement(elements[index], path=path, root=self, container_view=self.container_view)

    def get_by_name(self, name, index=None):
        if not self._web_element:
            raise UnSupportException("Get child elements from current element is not supported.")
        elements = self._web_element.find_elements(AppiumBy.XPATH, f"//*[contains(@name, '{name}')]")
        if len(elements) == 0:
            raise LynxNotFoundException(f"Can't find element with name {name}")
        if index is None:
            index = 0
        if len(elements) <= index:
            raise LynxNotFoundException(f"There are only {len(elements)} elements with name {name}.\
                                    The element at {index} cannot be obtained.")
        path = UPath(predicates=[{"name": "name", "value": name, "operator": "=="}], index=index)
        return LynxElement(elements[index], path=path, root=self, container_view=self.container_view)

    def get_by_bindtap(self, bindtap_name, index=None):
        raise NotImplementedError("get_by_bindtap method is not implemented for Appium.")

    def get_by_type(self, type, index=None):
        raise NotImplementedError("get_by_type method is not implemented for Appium.")

    def get_by_placeholder(self, placeholder, index=None):
        raise NotImplementedError("get_by_placeholder method is not implemented for Appium.")
