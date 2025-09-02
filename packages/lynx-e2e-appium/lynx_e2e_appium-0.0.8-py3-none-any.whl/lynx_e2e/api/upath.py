# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import importlib
from ..api.config import settings

DEFAULT_UPATH_PATH = 'lynx_e2e._impl.core.upath'

def get_class(class_name: str):
    driver_path = settings.get('E2E_DRIVER_PATH', None)
    upath_module = None
    try:
        upath_module = importlib.import_module(f"{driver_path}.upath")
    except ModuleNotFoundError:
        upath_module = importlib.import_module(DEFAULT_UPATH_PATH)

    return getattr(upath_module, class_name)

class BasicPredicate(get_class('BasicPredicate')):
    pass

class StringPredicate(get_class('StringPredicate')):
    pass

class BooleanPredicate(get_class('BooleanPredicate')):
    pass

class ListPredicate(get_class('ListPredicate')):
    pass

class UPath(get_class('UPath')):
    pass

id_ = BasicPredicate("id")
text_ = StringPredicate("text")
name_ = StringPredicate("name")
type_ = StringPredicate("type")
visible_ = BooleanPredicate("visible")
enabled_ = BooleanPredicate("enabled")
clickable_ = BooleanPredicate("clickable")
class_ = ListPredicate("class")

placeholder_ = StringPredicate("placeholder")

# iOS only
label_ = StringPredicate("label")

# Android only
tag_ = StringPredicate("tag")

# Lynx specific
bindtap_ = StringPredicate("bindtap")
idSelector_ = StringPredicate("idSelector")
lynx_test_tag_ = StringPredicate("lynx-test-tag")
mode_ = StringPredicate("mode")