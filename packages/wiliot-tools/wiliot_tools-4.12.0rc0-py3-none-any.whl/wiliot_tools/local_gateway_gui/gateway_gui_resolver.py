"""
Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""

import logging
import threading
from queue import Queue
from wiliot_core import set_logger, DataType, Packet
from wiliot_tools.resolver_tool.resolve_packets import ResolvePackets, TagStatus
try:
    from wiliot_core import DecryptedPacket
except ImportError:
    pass  # DecryptedPacket is not available in this context, handle gracefully


class ResolverProcess(ResolvePackets):
    def __init__(self, owner_id, env, need_to_resolve_q, resolved_q, stop_event, base_url):
        logger_path, self.logger = set_logger('ResolverProcess', 'resolver_process', 'resolver')
        self.resolved_q = resolved_q

        super().__init__(tags_in_test=[], owner_id=owner_id, env=env, resolve_q=need_to_resolve_q,
                         set_tags_status_df=self.add_to_resolved_q, stop_event_trig=stop_event,
                         logger_name=self.logger.name, gui_type='ttk', do_parallel_request=True,base_url=base_url)

    def check_tag_status(self, ex_id):
        return TagStatus.INSIDE_TEST

    def add_to_resolved_q(self, element):
        self.resolved_q.put(element, block=False)


class GwGuiResolver(object):
    def __init__(self, logger_name, owner_id, base_url):
        self.logger = logging.getLogger(logger_name)
        stop_event = threading.Event()
        need_to_resolve_q = Queue(maxsize=100)
        resolved_q = Queue(maxsize=100)
        is_connected = False
        resolve_process_handler = None
        resolve_process = None
        try:
            resolve_process = ResolverProcess(owner_id=owner_id, env='prod',
                                              need_to_resolve_q=need_to_resolve_q,
                                              resolved_q=resolved_q,
                                              stop_event=stop_event,
                                              base_url=base_url)
            is_connected = True
        except Exception as e:
            self.logger.warning(f'Could not start the external id resolver due to: {e}')

        if is_connected:
            resolve_process_handler = threading.Thread(target=resolve_process.run)
            resolve_process_handler.start()

        self.external_id_mapping = {}
        self.resolve_process_handler = resolve_process_handler
        self.stop_event = stop_event
        self.need_to_resolve_q = need_to_resolve_q
        self.resolved_q = resolved_q
        self.connected = is_connected

    def stop(self):
        if not self.connected:
            return True

        self.stop_event.set()
        self.resolve_process_handler.join(5)
        if self.resolve_process_handler.is_alive():
            self.logger.warning('could not stop the resolver process')
            return False
        self.connected = False
        self.logger.info('resolver process was stopped')
        return True

    def is_connected(self):
        return self.connected

    def get_external_id_mapping(self):
        self.update_external_id_mapping()
        return self.external_id_mapping

    def resolve_external_id(self, tag_id, packet_list=None, payload=None):
        if not self.connected:
            return ''

        self.update_external_id_mapping()

        if tag_id in self.external_id_mapping.keys():
            return self.external_id_mapping[tag_id]
        
        if payload is None:
            if packet_list is None or len(packet_list) == 0:
                self.logger.warning(f'No packet list or payload provided for tag {tag_id}, cannot resolve')
                return ''
            payload = packet_list.__getitem__(0).get_payload()
        
        if self.need_to_resolve_q.full():
            self.logger.warning(f'resolve queue is full dropping: {tag_id}')
        else:
            self.need_to_resolve_q.put({'tag': tag_id, 'payload': payload}, block=False)
            self.external_id_mapping[tag_id] = 'resolving'
        return 'resolving'

    def is_resolving(self):
        return not self.need_to_resolve_q.empty()

    def update_external_id_mapping(self):
        if not self.resolved_q.empty():
            n_new_ids = self.resolved_q.qsize()
            for _ in range(n_new_ids):
                try:
                    resolved = self.resolved_q.get(block=False)
                    self.external_id_mapping[resolved['adv_address'][0]] = resolved['external_id'][0]
                except Exception as e:
                    self.logger.warning(f'could not pull elements from resolver queue due to: {e}')
                    return
    
    def resolve_data(self, data_in, data_type: DataType, decrypted_mode=False):
        if not self.connected:
            return

        if data_type == DataType.TAG_COLLECTION or data_type == DataType.DECODED_TAG_COLLECTION:
            for tag_id, packet_list in data_in.items():
                if tag_id and tag_id not in self.external_id_mapping:
                    self.resolve_external_id(tag_id, packet_list)
        elif data_type == DataType.DECODED or data_type == DataType.PACKET_LIST:
            for packet in data_in:
                tag_id = packet.decoded_data.get('tag_id', '') if decrypted_mode else packet.packet_data.get('adv_address', '')
                if tag_id and tag_id not in self.external_id_mapping:
                    self.resolve_external_id(tag_id, payload=packet.get_payload())
        elif data_type == DataType.RAW:
            for raw_data in data_in:
                packet = Packet(raw_data['raw'], raw_data['time']) if decrypted_mode else DecryptedPacket(raw_data['raw'], raw_data['time'])
                tag_id = packet.decoded_data.get('tag_id', '') if decrypted_mode else packet.packet_data.get('adv_address', '')
                if tag_id and tag_id not in self.external_id_mapping:
                    self.resolve_external_id(tag_id, payload=packet.get_payload())
        else:
            self.logger.warning(f'Unknown data type {data_type} for resolver, skipping resolution')
            return
