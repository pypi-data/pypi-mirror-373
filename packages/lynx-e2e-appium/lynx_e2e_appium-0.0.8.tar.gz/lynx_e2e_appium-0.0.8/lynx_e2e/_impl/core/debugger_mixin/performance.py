# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import base64


class LynxDebuggerPerformance(object):

    def start_trace(self, session_id=-1):
        req_id = self.sender.send_cdp_data(session_id=session_id, method='Tracing.start', params={
            "streamCompression": "none",
            "streamFormat": "json",
            "traceConfig": {},
            "transferMode": "ReturnAsStream"})
        return self.receiver.wait_for_custom_id(req_id)

    def end_trace(self, session_id=-1):
        """
        return stream_id for trace file
        after sending end, app will return a Tracing.tracingComplete with stream id
        """
        self.sender.send_cdp_data(session_id=session_id, method='Tracing.end', params={})
        stream_id = self.receiver.wait_for_cdp_method("Tracing.tracingComplete")['stream']
        return stream_id

    def io_read(self, stream_id, shard=1024 * 32 * 3, session_id=-1, output_file=None):
        """
        read file by stream id
        """
        if output_file is None:
            raise RuntimeError("io_read need a output file")
        content = ''
        while True:
            req_id = self.sender.send_cdp_data(session_id=session_id, method='IO.read',
                                               params={'handle': stream_id, 'size': shard, })
            result = self.receiver.wait_for_custom_id(req_id)
            content += result['data']
            eof = result['eof']
            if eof:
                with open(output_file, 'wb') as f:
                    f.write(base64.b64decode(content.encode("utf8")))
                return output_file

    def get_lynx_perf(self, session_id):
        self.sender.send_cdp_data(session_id=session_id, method='Performance.enable', params={})
        req_id = self.sender.send_cdp_data(session_id=session_id, method='Performance.getMetrics', params={})
        data = self.receiver.wait_for_custom_id(req_id)
        self.sender.send_cdp_data(session_id=session_id, method='Performance.disable', params={})
        return data

    def get_lynx_timing_perf(self, session_id):
        self.sender.send_cdp_data(session_id=session_id, method='Performance.enable', params={})
        req_id = self.sender.send_cdp_data(session_id=session_id, method='Performance.getAllTimingInfo', params={})
        data = self.receiver.wait_for_custom_id(req_id)
        self.sender.send_cdp_data(session_id=session_id, method='Performance.disable', params={})
        return data

    def set_global_switch(self, key, value):
        self.sender.send_global_switch(key, value)