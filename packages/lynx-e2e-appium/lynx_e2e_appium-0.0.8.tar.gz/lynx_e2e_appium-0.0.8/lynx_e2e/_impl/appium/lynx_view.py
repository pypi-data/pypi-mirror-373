# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from appium.webdriver.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy

from .lynx_element import LynxElement
from ..core.logger import cdp_logger
from ..core.rectangle import Rectangle
from ..core.lynx_view_mixin import LynxViewMixin
from ..core.upath import UPath
from ..exception import LynxNotFoundException


class LynxView(LynxViewMixin, WebElement):
    
    def __init__(self, element: WebElement, app, path=None, root=None):
        self._web_element = element
        self._app = app
        self.view_spec = {}
        LynxViewMixin.__init__(self, path, root)
        self._parent = element._parent
        self._id = element._parent

    def get_by_class(self, class_name, index=None):
        path = UPath(predicates=[{"name": "class", "value": class_name, "operator": "=="}])
        lynx_element = LynxElement(None, path=path, root=self, container_view=self)
        return lynx_element

    @property
    def app(self):
        return self._app

    def get_by_test_tag(self, test_tag, index=None):
        elements = self._web_element.find_elements(AppiumBy.XPATH, f"//*[@view-tag='{test_tag}']")
        path = UPath(predicates=[{"name": "lynx-test-tag", "value": test_tag, "operator": "=="}], index=index)
        if len(elements) == 0:
            return LynxElement(None, path=path, root=self, container_view=self)
        if index is not None and len(elements) <= index:
            raise LynxNotFoundException(f"There are only {len(elements)} elements with test_tag {test_tag}.\
                                    The element at {index} cannot be obtained.")
        if index is not None:
            return LynxElement(elements[index], path=path, root=self, container_view=self)
        else:
            index = 0
            cdp_logger.warning("multiple elements founded with test_tag [%s]" % test_tag)
            return LynxElement(elements[0], path=path, root=self, container_view=self)

    def get_by_text(self, text, index=None):
        path = UPath(predicates=[{"name": "text", "value": text, "operator": "=="}])
        lynx_element = LynxElement(None, path=path, root=self, container_view=self)
        return lynx_element

    def get_by_name(self, name, index=None):
        elements = self._web_element.find_elements(AppiumBy.XPATH, f"//*[@name='{name}']")
        path = UPath(predicates=[{"name": "name", "value": name, "operator": "=="}], index=index)
        if len(elements) == 0:
            return LynxElement(None, path=path, root=self, container_view=self)
        if index is not None and len(elements) <= index:
            raise LynxNotFoundException(f"There are only {len(elements)} elements with name {name}.\
                                    The element at {index} cannot be obtained.")
        if index is not None:
            return LynxElement(elements[index], path=path, root=self, container_view=self)
        else:
            index = 0
            return LynxElement(elements[0], path=path, root=self, container_view=self)

    def get_by_bindtap(self, bindtap_name, index=None):
        raise NotImplementedError("get_by_bindtap method is not implemented for Appium.")

    def get_by_type(self, type, index=None):
        raise NotImplementedError("get_by_type method is not implemented for Appium.")

    def get_by_placeholder(self, placeholder, index=None):
        elements = self._web_element.find_elements(AppiumBy.XPATH, f"//*[@text='{placeholder}']")
        path = UPath(predicates=[{"name": "placeholder", "value": placeholder, "operator": "=="}], index=index)
        if len(elements) == 0:
            return LynxElement(None, path=path, root=self, container_view=self)
        if index is not None and len(elements) <= index:
            raise LynxNotFoundException(f"There are only {len(elements)} elements with placeholder {placeholder}.\
                                    The element at {index} cannot be obtained.")
        if index is not None:
            return LynxElement(elements[index], path=path, root=self, container_view=self)
        else:
            index = 0
            return (LynxElement(elements[0], path=path, root=self, container_view=self))

    @property
    def rect(self):
        size = self._web_element.size
        location = self._web_element.location
        return Rectangle(location["x"], location["y"], size["width"], size["height"])

    def get_view_driver(self):
        return self._app.get_lynx_driver(self)
