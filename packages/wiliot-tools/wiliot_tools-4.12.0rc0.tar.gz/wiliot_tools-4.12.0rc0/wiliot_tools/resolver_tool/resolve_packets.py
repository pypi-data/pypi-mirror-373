"""
  Copyright (c) 2016- 2023, Wiliot Ltd. All rights reserved.

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
import time
from queue import Queue
from threading import Event
from multiprocessing.pool import ThreadPool

from wiliot_api import ManufacturingClient, WiliotCloudError
from wiliot_core import GetApiKey
from wiliot_tools.resolver_tool.resolver_utils import is_external_id_valid, TagStatus


N_POOLS = 5


class ResolvePackets(object):
    def __init__(self, tags_in_test, owner_id, env, resolve_q, set_tags_status_df, stop_event_trig, logger_name,
                 gui_type=None, tag_status=None, wait_after_run=True, is_gcp=False, do_parallel_request=False, base_url=None):
        """

        @param tags_in_test: external ids of the tags in the test
        @type tags_in_test: list
        @param owner_id:
        @type owner_id:
        @param env:
        @type env:
        @param resolve_q: queu with element as following: {'tag': TAG_ADV_ADRESS, 'payload': PACKET_PAYLOAD}
        @type resolve_q: Queue
        @param set_tags_status_df: function to set the tags status dataframe
        @type set_tags_status_df: function
        @param stop_event_trig:
        @type stop_event_trig: Event
        @param logger_name:
        @type logger_name:
        """
        self.tags_in_test = tags_in_test
        self.owner_id = owner_id
        self.env = env
        self.client = None
        self.logger = logging.getLogger(logger_name)
        self.base_url = base_url
        self.connect_to_cloud(gui_type, is_gcp)
        self.tag_status = tag_status or TagStatus
        self.wait_after_run = wait_after_run
        self.resolve_q = resolve_q
        self.set_tags_status_df = set_tags_status_df
        self.stop_event = stop_event_trig if stop_event_trig is not None else threading.Event()
        self.thread_pool = ThreadPool(N_POOLS) if do_parallel_request else None
        self.do_parallel_request = do_parallel_request

    def connect_to_cloud(self, gui_type=None, is_gcp=False):
        """
        Establishes a secure connection to the cloud service for data storage and validation.

        Parameters: - env (str): Specifies the cloud environment to connect to. It can be either 'prod' for
        production or 'test' for testing.

        Steps:
        1. Reads the user's cloud configuration file to obtain API keys and owner IDs.
        2. Validates the owner ID against a predefined list of valid owner IDs.
        3. Initializes the cloud client using the API key and specified environment.
        4. Logs the successful establishment of the cloud connection.

        Note: If the connection fails or configurations are invalid, the function will raise an exception and close
        the Gateway port.
        """
        try:
            k = GetApiKey(env=self.env, owner_id=self.owner_id, gui_type=gui_type)
            api_key = k.get_api_key()
            if api_key == '':
                raise Exception(f'Could not found an api key for owner id {self.owner_id} and env {self.env}')
            cloud = 'GCP' if is_gcp else ''
            region = 'us-central1' if is_gcp else 'us-east-2'

            self.client = ManufacturingClient(api_key=api_key, env=self.env, cloud=cloud, region=region,
                                              logger_=self.logger.name, base_url=self.base_url)
            self.logger.info('Connection to the cloud was established')

        except Exception as e:
            raise Exception(f'Problem connecting to cloud {e}')

    def run(self):
        need_to_resolve = None
        while True:
            if self.stop_event.is_set():
                break
            try:
                need_to_resolve = None
                if not self.resolve_q.empty():
                    if self.do_parallel_request:
                        self.get_external_ids_and_update()
                    else:
                        self.get_external_id_and_update()
                else:
                    time.sleep(1)
            except Exception as e:
                self.logger.warning(f'got exception during ResolvePacket: run: {e}. '
                                    f'with need to resolve: {need_to_resolve}')
        self.logger.info('end of packet resolver loop')
        self.stop()

    def update_tag_status(self, tag, status, ex_id):
        allowed_keys = ['tag', 'adv_address', 'adva']
        adva = 'unknown'
        for k in allowed_keys:
            if k in tag.keys():
                adva = tag[k]
                break
        tag_status = {'adv_address': [adva],
                      'resolve_status': [status],
                      'external_id': [ex_id]}
        for k, v in tag.items():
            if k not in tag_status:
                tag_status[k] = [v]
        self.logger.info(f'new resolved results: {tag_status}')
        self.set_tags_status_df(tag_status)

    def check_tag_status(self, ex_id):
        if ex_id['externalId'] in self.tags_in_test:
            status = self.tag_status.INSIDE_TEST
        elif is_external_id_valid(ex_id['externalId']):
            status = self.tag_status.OUT_VALID
        else:
            status = self.tag_status.OUT_INVALID
        self.logger.info(f'found new tag in test: {ex_id} with status: {status}')
        return status

    def get_external_id_and_update(self):
        need_to_resolve = None
        try:
            need_to_resolve, ex_id = self.get_external_id()
            status = self.check_tag_status(ex_id=ex_id)
            self.update_tag_status(tag=need_to_resolve, status=status, ex_id=ex_id['externalId'])
        except Exception as e:
            self.logger.warning(f'got exception during ResolvePacket: get_external_id_and_update: {e}. '
                                f'with need to resolve: {need_to_resolve}')
            if need_to_resolve is not None and \
                    'tag' in need_to_resolve.keys() and 'payload' in need_to_resolve.keys():
                self.update_tag_status(tag=need_to_resolve, status=self.tag_status.OUT_INVALID, ex_id='unknown')
    
    def get_external_ids_and_update(self):
        need_to_resolve_list, ex_id_list = [], []
        try:
            need_to_resolve_list, ex_id_list = self.get_externals_ids()
        except Exception as e:
            self.logger.warning(f'got exception during ResolvePacket: get_external_id : {e}')
        
        for need_to_resolve, ex_id in zip(need_to_resolve_list, ex_id_list):
            try:
                status = self.check_tag_status(ex_id=ex_id)
                self.update_tag_status(tag=need_to_resolve, status=status, ex_id=ex_id['externalId'])
            except Exception as e:
                self.logger.warning(f'got exception during ResolvePacket: update: {e}. '
                                    f'with need to resolve: {need_to_resolve}')
                if need_to_resolve is not None and \
                        'tag' in need_to_resolve.keys() and 'payload' in need_to_resolve.keys():
                    self.update_tag_status(tag=need_to_resolve, status=self.tag_status.OUT_INVALID, ex_id='unknown')

    def get_externals_ids(self):
        n = min([self.resolve_q.qsize(), N_POOLS])
        all_payloads = []
        all_need_to_resolve = []
        for _ in range(n):
            if self.resolve_q.empty():
                break
            need_to_resolve = self.resolve_q.get(block=False)
            self.logger.info(f'try to resolve the following payload: {need_to_resolve}')
            all_need_to_resolve.append(need_to_resolve)
            all_payloads.append(need_to_resolve['payload'])
        if all_payloads:
            self.logger.info(f'start resolve pooling with {len(all_payloads)} payloads')
            ex_ids = self.thread_pool.map(self.resolve_payload, all_payloads)
            self.logger.info(f'end resolve pooling with {len(all_payloads)} payloads')
        else: 
            ex_ids = []
        return all_need_to_resolve, ex_ids

    def resolve_payload(self, payload):
        try:
            res = self.client.resolve_payload(payload=payload, owner_id=self.owner_id, verbose=True)
        except WiliotCloudError as e:
            self.logger.warning(f'got exception during client resolve payload: {e}')
            res = {'externalId': 'CloudError'}
        return res

    def get_external_id(self):
        need_to_resolve = self.resolve_q.get(block=False)
        self.logger.info(f'try to resolve the following payload: {need_to_resolve}')
        ex_id = self.client.resolve_payload(payload=need_to_resolve['payload'],
                                            owner_id=self.owner_id, verbose=True)
        return need_to_resolve, ex_id

    def stop(self):
        if not self.wait_after_run:
            return
        time.sleep(3)
        if not self.resolve_q.empty():
            n = self.resolve_q.qsize()
            for _ in range(n):
                try:
                        if self.do_parallel_request:
                            self.get_external_ids_and_update()
                            break
                        else:
                            self.get_external_id_and_update()
                except Exception as e:
                    self.logger.warning(f'got exception during ResolvePacket: stop: {e}')
        self.logger.info('stop resolver process')
