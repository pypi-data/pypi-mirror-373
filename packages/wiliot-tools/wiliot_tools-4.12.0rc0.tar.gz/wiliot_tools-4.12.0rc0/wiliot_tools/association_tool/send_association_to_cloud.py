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

import datetime
import time
import requests
import json

from wiliot_core import GetApiKey, set_logger
from wiliot_api import PlatformClient, TagRole, WiliotCloudError

TIME_BTWN_REQUEST = 20  # seconds
URL_PATH = 'https://us-central1-wiliot-firefly.cloudfunctions.net/ingest-assocation-data-printer-test'
OWNER_ID = '185369804174'
GDC_TYPE = 'hvdc'  # options: outbound-pallet, hvdc
CATEGORY_ID = '1e55d376-a12f-4f75-9583-ff8bad995d35'
IS_GCP = False


class CloudAssociation(object):
    def __init__(self, associate_q, stop_event, owner_id=OWNER_ID, is_gcp=IS_GCP, category_id=CATEGORY_ID,
                 time_btwn_request=TIME_BTWN_REQUEST, initiator_name=None, logger_config=None, base_url=None):
        """
        @type associate_q Queue
        @param associate_q each element of the queue is a dict {'wiliot_code': [], 'asset_code': [], 'timestamp': 0 or datetime.datetime.now().timestamp()}
        """
        logger_config = logger_config if logger_config is not None else {}
        self.logger_path, self.logger = set_logger(app_name='CloudAssociation',
                                                   dir_name=logger_config.get('dir_name', 'cloud_association'), 
                                                   folder_name=logger_config.get('folder_name', ''), 
                                                   file_name='cloud_association_log')
        self.associate_q = associate_q
        self.is_stop_event = stop_event
        self.time_btwn_request = time_btwn_request
        self.associate_batch = {}
        self.connection_setting = {'is_gcp': is_gcp, 'owner_id': owner_id, 'initiator_name': initiator_name, 'base_url': base_url}
        
        self.connect()

        try:
            self.base_payload = {"scan_source": "gdc",
                                 "pixel_id": [],
                                 "asset_id": None,
                                 "gdc_type": GDC_TYPE,
                                 "timestamp": datetime.datetime.now().timestamp(),
                                 "printer": True}
            self.category_id = category_id
        except Exception as e:
            self.logger.warning(f'Could not create the base payload due to {e}')
            raise Exception(f'Could not create the base payload due to {e}')

        if associate_q:
            self.run()

    def connect(self):
        try:
            g = GetApiKey(gui_type='ttk', env='prod', owner_id=self.connection_setting['owner_id'], client_type='asset')
            api_key = g.get_api_key()
            if self.connection_setting['is_gcp']:
                cloud='GCP'
                region='us-central1'
            else:
                cloud=''
                region='us-east-2'
            self.client = PlatformClient(api_key=api_key, owner_id=self.connection_setting['owner_id'],  env='prod', logger_=self.logger.name,
                                            cloud=cloud, region=region, initiator_name=self.connection_setting['initiator_name'], base_url=self.connection_setting['base_url'])
            self.logger.info('client was connected')
        except Exception as e:
            self.logger.warning(f' Could not create a client due to {e}')
            raise Exception(f' Could not create a client due to {e}')

    def run(self):
        last_cloud_post = time.time()
        while not self.is_stop_event.is_set():
            bad_association = []
            if time.time() - last_cloud_post > self.time_btwn_request:
                last_cloud_post = time.time()
                if self.associate_batch:
                    bad_association = self.send_batch_to_cloud()
                    self.associate_batch = {}

            if self.associate_q.empty():
                time.sleep(1)
            else:
                n = self.associate_q.qsize()
                for _ in range(n):
                    data = self.associate_q.get(timeout=1)
                    self.add_data_to_batch(data)

            for b_ass in bad_association:  # try again bad association
                self.add_data_to_batch(b_ass)

        self.stop_app()

    def stop_app(self):
        self.logger.info('Checking there are no new request to send to the cloud...')
        time.sleep(1)
        while not self.associate_q.empty():
            data = self.associate_q.get(timeout=1)
            self.add_data_to_batch(data)

        if self.associate_batch:
            self.logger.info('sending data to cloud before exiting CloudAssociation')
            bad_association = self.send_batch_to_cloud()
            if len(bad_association):
                self.logger.warning(f'association was done with the following bad association: {bad_association}')
        self.logger.info('CloudAssociation is Done')

    def add_data_to_batch(self, data):
        wiliot_code = data['wiliot_code']  # list
        asset_id = data['asset_code']
        timestamp = data['timestamp']

        if not isinstance(asset_id, str):
            if len(asset_id) != 1:
                self.logger.warning(f"{'Too many' if len(asset_id) > 1 else 'No'} Asset codes were scanned: {asset_id}")
                return
            asset_id = asset_id[0] if asset_id else None
        if asset_id in self.associate_batch.keys():
            for c in wiliot_code:
                if c not in self.associate_batch[asset_id]['pixel_id']:
                    self.associate_batch[asset_id]['pixel_id'].append(c)
        else:
            self.associate_batch[asset_id] = {'pixel_id': wiliot_code}
        self.associate_batch[asset_id]['timestamp'] = timestamp

    def send_batch_to_cloud(self):
        bad_association = []
        payload = self.base_payload.copy()
        for asset_id, pixel_dict in self.associate_batch.items():
            payload["asset_id"] = asset_id
            payload["pixel_id"] = list(set(pixel_dict['pixel_id']))
            payload["timestamp"] = int(pixel_dict['timestamp'] * 1000)
            try:
                message = self.send_to_cloud_debug(payload)  # for debug
                if IS_GCP:
                    message = self.send_to_cloud(payload)
                else:  # AWS / VPC
                    message = self.create_asset_and_label(asset_id=payload["asset_id"], pixels=payload["pixel_id"])
            except Exception as e:
                message = {'status_code': 999,
                           'data': f'Exception during send_to_cloud {e}'}
                try:
                    self.logger.info('try to reconnect to client')
                    time.sleep(1)
                    self.connect()
                except Exception as e:
                    self.logger.warning('failed to reconnect to client, wait for 5 seconds and try again')
                    time.sleep(5)

            bad_association = self.handle_results(message, asset_id, pixel_dict, bad_association)
        return bad_association

    def handle_results(self, message, asset_id, pixel_dict, bad_association):
        if message['status_code'] == 201:
            self.logger.info(f'Successful Association for {asset_id}: {message}')
        else:
            bad_association.append({'asset_code': asset_id,
                                    'wiliot_code': pixel_dict['pixel_id'],
                                    'timestamp': pixel_dict['timestamp']})
            if message['status_code'] in [404, 409, 504]:
                pass  # already handled
            elif message['status_code'] == 403:
                self.logger.warning(f'Failed Association for {asset_id} due '
                                    f'to Authentication and authorization issues: {message}')
            else:
                self.logger.warning(f'Failed Association for {asset_id} due '
                                    f'to Unexpected error: {message}')
        return bad_association

    def send_to_cloud(self, payload):
        self.client._renew_token()
        headers = {'Content-Type': 'Application/json',
                   'Authorization': f'Bearer {self.client.headers["Authorization"]}'}
        response = requests.post(url=URL_PATH, headers=headers,
                                 data=json.dumps({"data": payload}), params=None)
        try:
            message = response.json()
        except Exception as e:
            message = response.text

        if isinstance(message, str):
            message = {"data": message}
        message.update({'status_code': response.status_code})

        return message

    def send_to_cloud_debug(self, payload):
        self.logger.info(f'post: url={URL_PATH}, headers={self.client.headers}, data={json.dumps({"data": payload})}')
        return {'data': 'debug', 'status_code': 201}

    def create_asset_and_label(self, asset_id: str, pixels: list):
        """
        Creates an asset with the given category and pixel.
        :param asset_id: Required -
        :param pixels: Required - list of pixel IDs to associate with the asset
        """
        res = {"data": f"no asset id or pixels: asset: {asset_id}, pixels: {pixels}",
               "status_code": 700}

        platform_client = self.client
        self.logger.info(f"Trying to create an asset in owner {platform_client.owner_id} ")
        if not asset_id or not pixels:
            self.logger.info(res['data'])
            return res
        try_again = 'first'
        while try_again:
            if try_again == 'associate':
                bad_res_list = []
                for pixel in pixels:
                    try:
                        success = platform_client.associate_pixel_to_asset(asset_id=asset_id, pixel_id=pixel)
                        """
                        url: 'https://api.us-east-2.prod.wiliot.cloud//v1/traceability/owner/<OWNER_ID>/asset/<ASSET_ID>/tag/<PIXEL_ID>'
                        the above pixel id after decoding, i.e. (01)00850027865010(21)0bm6T0000 is %2801%2900850027865010%2821%290bm6T0000
                        data: {}
                        """

                        if success:
                            self.logger.info(f"Associated pixel {pixel} to asset {asset_id}")
                        else:
                            raise Exception("Association failed with no cloud exception")
                    except Exception as e:
                        if e.args[0]['status_code'] == 400 and \
                                'tagId is already associated with this asset' in e.args[0]['error']:
                            self.logger.info(f"pixel {pixel} is already associate to asset {asset_id}")
                            continue
                        res = {"data": f"Association for {asset_id} and {pixel} failed due to {e}",
                               "status_code": 710}
                        bad_res_list.append(res)
                if bad_res_list:
                    res = {"data": '\n'.join([b_res["data"] for b_res in bad_res_list]),
                           "status_code": 710}
                else:
                    res = {"data": f"Associated pixels {pixels} to asset {asset_id}",
                           "status_code": 201}
                try_again = ''
            else:
                try_again = ''
                try:
                    res = platform_client.create_asset(None, asset_id=asset_id,
                                                       category_id=self.category_id,
                                                       pixels=[{'tagId': p, 'role': TagRole.DEFAULT}
                                                               for p in pixels])
                    """
                    url: 'https://api.us-east-2.prod.wiliot.cloud//v2/traceability/owner/<OWNER_ID>/asset'
                    headers: {'accept': 'application/json', 
                              'Content-Type': 'application/json', 
                              'Authorization': <TOKEN>}
                    data: {"id": <ASSET_ID>, 
                           "name": null, 
                           "categoryId": <CATEGORY_ID>, 
                            "tags": [{"tagId": <PIXEL_ID1>, "role": "DEFAULT"}, 
                                     {"tagId": <PIXEL_ID2>, "role": "DEFAULT"}], 
                            "status": null}'
                    """
                    if res:
                        created_asset_id = res['id']
                        msg = f"Asset {created_asset_id} created with pixels {pixels}"
                        self.logger.info(msg)
                        self.logger.info(res)
                        res['status_code'] = 201
                        res['data'] = msg

                except WiliotCloudError as wce:
                    self.logger.error(f"Error when creating asset {asset_id}: {wce.args}")
                    res = {"data": wce.args[0].get('error'),
                           "status_code": wce.args[0].get('status_code', '')}
                    # What we do depends on the status code
                    if wce.args[0].get('status_code', '') == 404:
                        # Either the pixel or the category do not exist in this account
                        self.logger.warning(f"One or more of the pixels do not exist in the account")
                        self.logger.warning(wce.args[0].get('error'))
                    elif wce.args[0].get('status_code', '') == 504:
                        # If the upstream server timed out - return from here - this will be retried
                        self.logger.error("Upstream server timeout")
                    elif wce.args[0].get('status_code', '') == 409:
                        # There are two situations we can get a 409 error:
                        # 1. The tag is already associated with another asset - can happen when an asset ID and pixel
                        # are scanned more than once. In this case - we log and exit because there is nothing
                        # else to do
                        if wce.args[0].get("error", "").lower().find("already associated") != -1:
                            self.logger.error(f"Tag {pixels} already associated with an asset")
                        # 2. Due to a previous failure - the asset has already been created - log and continue
                        # to add labels to this asset
                        else:
                            # If the asset already exists - log this but keep going - we might need to add labels
                            self.logger.error(f"Asset {asset_id} already exists")
                            try_again = 'associate'
                    else:
                        self.logger.error(f"Unexpected Cloud error during asset creation: {wce}")
                except Exception as e:
                    self.logger.error(f"Unexpected error during asset creation: {e}")
                    res = {"data": f"Unexpected error during asset creation: {e}",
                           "status_code": 900}

        return res


if __name__ == '__main__':
    c = CloudAssociation(None, None, owner_id='880628326685', category_id='1d721672-6463-4ef7-b664-04b299eed961', initiator_name='WiliotTest')
    # c.create_asset_and_label(asset_id='PBLwXi75264', pixels=['7j6T3464'])
    
    # base_str = '(01)00850027865010(21)0bm6T'
    # for i in range(5000):
    #     new_tag = base_str + str(i).zfill(4)
    #     c.create_asset_and_label(asset_id=new_tag, pixels=[new_tag])

    # c.create_asset_and_label(asset_id='01234', pixels=['(01)00850027865010(21)0bm6T0000',
    #                                                    '(01)00850027865010(21)0bm6T0001'])
    # c.create_asset_and_label(asset_id='01235', pixels=['(01)00850027865010(21)0bm7T0000'])
    # c.create_asset_and_label(asset_id='01231', pixels=['(01)00850027865010(21)0bm6T0003',
    #                                                    '(01)00850027865010(21)0bm6T0004'])
    # c.create_asset_and_label(asset_id='01236', pixels=['(01)00850027865010(21)0bm6T0005',
    #                                                    '(01)00850027865010(21)0bm6T0005'])
    print('done')
