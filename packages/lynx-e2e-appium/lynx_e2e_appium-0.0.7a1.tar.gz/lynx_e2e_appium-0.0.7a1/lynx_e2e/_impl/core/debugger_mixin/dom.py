# Copyright 2024 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import base64
import time
from zlib import decompress
import ujson


class LynxDebuggerDom(object):
    def get_document(self, session_id):
        req_id = self.sender.send_cdp_data(session_id=session_id, method='DOM.getDocument', params={})
        received_data = self.receiver.wait_for_custom_id(req_id)
        if 'compress' in received_data and received_data['compress']:
            received_data['root'] = ujson.loads(decompress(base64.b64decode(received_data['root'].encode('utf8'))))
        return received_data

    def get_document_with_box_model(self, session_id, is_ng=False):
        """
        Get lynx dom_tree with box_model
        """
        if is_ng:
            document = self.get_document(session_id)
            self._dfs(session_id, document['root'])
            return document
        else:
            req_id = self.sender.send_cdp_data(session_id=session_id, method='DOM.getDocumentWithBoxModel', params={})
            received_data = self.receiver.wait_for_custom_id(req_id)
            if 'compress' in received_data and received_data['compress']:
                received_data['root'] = ujson.loads(decompress(base64.b64decode(received_data['root'].encode('utf8'))))
            return received_data

    """Using depth-first traversal, add the box_model attribute to each node of the document_tree.

    Args:
        session_id: Current devtool session id.
        src_node: The currently processed tree node.
    """
    def _dfs(self, session_id, src_node):
        node_id = src_node['nodeId']
        box_model = self.get_box_model(session_id, node_id)
        if 'model' in box_model:
            src_node['box_model'] = box_model['model']
        else:
            src_node['box_model'] = None
        for child in src_node["children"]:
            self._dfs(session_id, child)

    def get_box_model(self, session_id, node_id, sync=True):
        req_id = self.sender.send_cdp_data(session_id=session_id, method='DOM.getBoxModel', params={'nodeId': node_id})
        if sync:
            return self.receiver.wait_for_custom_id(req_id)
        else:
            return req_id

    def set_attributes_as_text(self, session_id, node_id, text):
        req_id = self.sender.send_cdp_data(session_id=session_id,
                                           method='DOM.setAttributesAsText',
                                           params={'nodeId': node_id, 'text': text})
        return self.receiver.wait_for_custom_id(req_id)

    def click_by_cdp(self, session_id, x, y):
        self.sender.send_cdp_data(session_id=session_id,
                                           method='Input.emulateTouchFromMouseEvent',
                                           params={"type": 'mousePressed',
                                                   "x": x,
                                                   "y": y,
                                                   "button": 'left'
                                               }
                                           )
        time.sleep(1)
        self.sender.send_cdp_data(session_id=session_id,
                                  method='Input.emulateTouchFromMouseEvent',
                                  params={"type": 'mouseReleased',
                                          "x": x,
                                          "y": y,
                                          "button": 'left'
                                          }
                                  )
