# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import time
import ujson

from ..logger import cdp_logger


WAIT_TIME = 60

class LynxDebuggerScreenCast(object):

    def page_start_screencast(self, width, height, session_id):
        req_id = self.sender.send_cdp_data(session_id=session_id, method='Page.startScreencast', params={
            "format": "jpeg",
            "maxHeight": height,
            "maxWidth": width,
            "quality": 100})
        return self.receiver.wait_for_custom_id(req_id)

    def page_stop_screencast(self, session_id):
        self.sender.send_cdp_data(session_id=session_id, method='Page.stopScreencast', params={})

    def screencast_frame(self, session_id):
        req_id = self.sender.send_cdp_data(session_id=session_id, method='Page.enable')
        self.receiver.wait_for_custom_id(req_id)

        res = self.page_start_screencast(9999, 9999, session_id)
        start_time = time.time()
        while time.time() - start_time < WAIT_TIME:
            try:
                data = self.receiver.wait_for_cdp_method('Page.screencastFrame', timeout=12, raw=True)
            except Exception as e:
                print("Wait for Page.screencastFrame timeout, Retry screen_shoot! Error: %s" % str(e))
                cdp_logger.info("Wait for Page.screencastFrame timeout, Retry screen_shoot! Error: %s" % str(e))
                self.page_stop_screencast(session_id)
                self.page_start_screencast(9999, 9999, session_id)
                continue
            if data['session_id'] == session_id:
                self.page_stop_screencast(session_id)
                data = ujson.loads(data['message'])
                data = data['params'] if 'params' in data else None
                return data
            else:
                print("get other frame, session id " + str(data['sessionId']))
        raise RuntimeError("can not get screencast in 60s!!")
