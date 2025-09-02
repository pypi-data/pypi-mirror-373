# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.


class TraceableException(Exception):
    """exception that could trace origin
    """

    def __init__(self, *args, **kwargs):
        self.error_origin = kwargs.pop("error_origin", None)
        super(TraceableException, self).__init__(*args, **kwargs)

class ForwardError(Exception):
    """forward error
    """
    pass
