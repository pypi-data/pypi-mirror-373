# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import base64
import json
import ujson


class LynxTestBench(object):
    def __init__(self):
        self.current_replay_file = None

    def io_read_testbench(self, stream_id, shard=1024 * 32 * 3, session_id=-1, output_file=None):
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
                decode_str = base64.b64decode(content.encode("utf8"))
                json_file = ujson.loads(decode_str)
                with open(output_file, 'w') as f:
                    f.write(json.dumps(json_file, ensure_ascii=False, indent=2))
                return output_file

    def start_replay(self, session_id=-1):
        req_id = self.sender.send_cdp_data(session_id=session_id, method='Replay.start', params={
            "streamCompression": "none",
            "streamFormat": "json",
            "transferMode": "ReturnAsStream"})
        self.receiver.wait_for_custom_id(req_id)

    def end_replay(self):
        """
        return stream_id for dump file
        after sending end, app will return a Replay.end with stream id
        """
        stream_id = self.receiver.wait_for_cdp_method("Replay.end")['stream']
        return stream_id
