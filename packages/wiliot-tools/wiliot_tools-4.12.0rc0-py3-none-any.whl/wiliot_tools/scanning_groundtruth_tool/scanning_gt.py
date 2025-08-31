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

import json
import threading
import time
from queue import Queue
import datetime

from wiliot_api import PlatformClient
from wiliot_core import set_logger, GetApiKey
from wiliot_tools.test_equipment.test_equipment import CognexDataMan
from wiliot_tools.association_tool.association_configs import is_wiliot_code


class ScanGT(object):
    def __init__(self, user_config):
        logger_path, logger = set_logger(app_name='ScanGroundtruth')
        self.scanner = CognexDataMan(log_name=logger.name)
        self.logger = logger
        self.user_config = user_config
        if not self.scanner.connected:
            raise Exception('Could not connect to Cognex. please check connection and other app usage')
        self.scanner.reset()
        self.scanned = []
        self.scanned_q = Queue(maxsize=1000)
        self.event_thread = None

        g = GetApiKey(gui_type='ttk', owner_id=self.user_config['owner_id'], env='prod', client_type='asset')
        api_key = g.get_api_key()
        self.client = PlatformClient(api_key=api_key, owner_id=self.user_config['owner_id'])

    def scan(self):
        if self.user_config['need_to_trigger'].lower() == 'yes':
            self.scanner.send_command('TRIGGER ON')
            self.logger.info('sent trigger to scanner')
        elif self.user_config['need_to_trigger'].lower() == 'no':
            pass
        else:
            self.logger.warning(f'unsupported trigger mechanism: {self.user_config["need_to_trigger"]}')
        scanned_codes = self.scanner.read_batch(n_msg=1, wait_time=1.0)

        for new_scanned in scanned_codes:
            self.logger.info(f'scanned new code: {new_scanned}')

        if self.user_config['need_to_trigger'].lower() == 'yes':
            self.scanner.reset()
        return scanned_codes

    def run(self):
        self.event_thread = threading.Thread(target=self.send_generic_event, args=())
        self.event_thread.start()
        self.logger.info('app started')
        while True:
            time.sleep(0)
            try:
                scanned_codes = self.scan()
                for scanned_code in scanned_codes:
                    if scanned_code in self.scanned:
                        self.logger.info(f'got code duplication: {scanned_code}, drop code and move to the next one')
                        continue
                    if not is_wiliot_code(scanned_code):
                        self.logger.warning(f'got non-wiliot code: {scanned_code}, drop code and move to the next one')
                        continue
                    self.scanned.append(scanned_code)
                    timestamp = round(datetime.datetime.now().timestamp() * 1000)

                    if self.scanned_q.full():
                        self.logger.warning(f'scanned queue is full drop event: {scanned_code, timestamp}')
                    else:
                        self.scanned_q.put({'code': scanned_code, 'timestamp': timestamp})

            except Exception as e:
                self.logger.warning(f'got exception during run: {e}')
                self.scanner.reconnect()
                if not self.scanner.connected:
                    raise Exception('could not reconnect to Scanner')

    def send_generic_event(self):
        while True:
            new_event = None
            try:
                if self.scanned_q.empty():
                    time.sleep(1)
                    continue

                new_event = self.scanned_q.get()
                self.logger.info(f'found new event: {new_event}')
                status = self.client.generate_generic_event(asset_id=self.user_config['asset_id'],
                                                            category_id=self.user_config['category_id'],
                                                            event_name=self.user_config['event_name'],
                                                            value=new_event['code'],
                                                            key_set=[],
                                                            start=new_event['timestamp'],
                                                            end=new_event['timestamp'])
                if status:
                    self.logger.info(f'Generic event of {new_event} was sent successfully!!')
                else:
                    self.logger.warning(f'Failed to send generic event to cloud for {new_event}, try again')
                    if self.scanned_q.full():
                        self.logger.warning(f'scanned queue is full drop event: {new_event}')
                    else:
                        self.scanned_q.put(new_event)
            except Exception as e:
                self.logger.warning(f'got exception during send_generic_event: {e}')
                if new_event is not None:
                    self.logger.info(f'try to send again: {new_event}')
                    if self.scanned_q.full():
                        self.logger.warning(f'scanned queue is full drop event: {new_event}')
                    else:
                        self.scanned_q.put(new_event)


if __name__ == '__main__':
    import os

    dir_name = os.path.dirname(os.path.abspath('__file__'))
    gt_config_file = 'gt_config.json'
    config_path = os.path.join(dir_name, gt_config_file)
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            run_config = json.load(f)
    else:
        run_config = {'owner_id': '880628326685',
                      'asset_id': 'genericEvents',
                      'category_id': '47b4f186-99c5-4474-850c-b6f699132b73',
                      'event_name': 'groundTruthToolPixelScanOnly',
                      'need_to_trigger': 'no'}

        with open(config_path, 'w') as f:
            json.dump(run_config, f)

    gt = ScanGT(user_config=run_config)
    gt.run()
