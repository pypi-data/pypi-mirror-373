# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

from .lynx_element_mixin import LynxElementMixin

class LynxViewMixin(LynxElementMixin):
    """new LynxView, lynxview = NewLynxView(app=test.app, url=url))
    """

    def get_session_id(self):
        return self.get_lynx_driver().get_session_id()

    def document_tree(self):
        return self.get_lynx_driver().get_src_document_tree()

    def local_document_tree(self):
        return self.get_lynx_driver().get_document_tree()

    def get_lynx_timing_perf(self):
        """
        get performance timing info of lynx_view, which is more detail than get_lynx__perf API
        Returns:
            A dict mapping names and values of lynx_view performance timing info.
        """
        return self.get_lynx_driver().get_lynx_timing_perf()

    def get_console_log(self):
        return self.get_lynx_driver().get_console_log()

    def get_lynx_perf(self):
        """
        get performance data of lynxview
        Returns:
            A dict mapping names and values of lynxview performance parameters. Time is in 'ms' and size is in 'byte'.
            Example:
               [{"name":"source_js_size","value":10626.0},
               {"name":"tasm_binary_decode","value":2.0},
               {"name":"first_page_layout","value":22.0},
               {"name":"diff_root_create","value":1.0},
               {"name":"layout","value":4.0},
               {"name":"tasm_finish_load_template","value":8.0},
               {"name":"tasm_end_decode_finish_load_template","value":6.0},
               {"name":"js_finish_load_core","value":56.0},
               {"name":"js_runtime_type","value":2.0},
               {"name":"js_finish_load_app","value":11.0},
               {"name":"tti","value":65.0},
               {"name":"corejs_size","value":286462.0},
               {"name":"js_and_tasm_all_ready","value":68.0}].
            Description:
               {
                'source_js_size': size of template.js,
                'tasm_binary_decode': binary decoding time,
                'first_page_layout': first page layout time,
                'diff_root_create': first diff root time,
                'layout': layout time,
                'tasm_finish_load_template': template loading time,
                'tasm_end_decode_finish_load_template': time from end of decode to completing loading template,
                'js_finish_load_core': core.js loading time,
                'js_runtime_type': type of js runtime/engine,
                'js_finish_load_app': app loading time,
                'tti': time to interactive,
                'corejs_size': size of core.js,
                'js_and_tasm_all_ready': core.js + app.js loading time
                }
        """
        return self.get_lynx_driver().get_lynx_perf()

    def screenshot(self, image_path):
        """get current screen shot by lynx self

        :param image_path: target directory to store screen shot file
        :type  image_path: str
        """
        self.get_lynx_driver().screenshot(image_path, self.rect)
        return image_path

    def get_lynx_driver(self):
        if self._lynx_driver is None:
            self._lynx_driver = self._app.get_lynx_driver(self)
        return self._lynx_driver

    def get_lynx_view_id(self):
        return self.id