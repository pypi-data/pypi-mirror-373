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
import time
import datetime
import serial  # type: ignore
import multiprocessing as mp
import serial.tools  # type: ignore
import keyboard

from wiliot_tools.test_equipment.test_equipment import CognexDataMan
from wiliot_tools.association_tool.association_configs import WILIOT_MIN_NUM_CODE, ASSET_NUM_CODES
from wiliot_tools.association_tool.association_configs import is_wiliot_code, is_asset_code
from wiliot_tools.association_tool.send_association_to_cloud import CloudAssociation, TIME_BTWN_REQUEST
from wiliot_core import set_logger


MAX_TIME_BTWN_LABEL = 1
MIN_TIME_BTWN_LABEL = 0.500
MIN_TIME_TO_READ = 0.200
ARDUINO_BAUD_RATE = 1000000
CHECK_LIVE_TIME = 600  # seconds
TIME_BTWN_RECOVERY = 3


class ScannerAssociation(object):
    def __init__(self, logger_name, is_stop_event, new_label_event, associate_q):
        """
        :param logger_name: the logger name
        :type logger_name: str
        """
        self.is_stop = is_stop_event
        self.is_new_label = new_label_event
        self.logger = logging.getLogger(logger_name)
        self.associate_q = associate_q

        self.scanner = CognexDataMan(log_name=logger_name)
        # TODO add here config to upload cognex file
        if not self.scanner.connected:
            raise Exception('Could not connect to Cognex. please check connection and other app usage')

    def run(self):
        self.logger.info('Starts Scanner Association')
        t_start = time.time()
        need_to_recovery = False

        while True:
            if self.is_stop.is_set():
                self.logger.info('stop Scanner Association')
                break
            try:
                if self.is_new_label.is_set():
                    self.scanner.reset()

                    self.scanner.send_command('TRIGGER ON')
                    complete_label_read = {'status': False, 'wiliot_code': [], 'asset_code': [], 'timestamp': 0}

                    # Scanning
                    scanned_codes = self.scanner.read_batch(wait_time=MIN_TIME_BTWN_LABEL)
                    if not scanned_codes:
                        self.scanner.send_command('TRIGGER OFF')
                        scanned_codes = self.scanner.read_batch(wait_time=MIN_TIME_TO_READ)

                    for new_scanned in scanned_codes:
                        self.logger.info(f'scanned new code: {new_scanned}')
                        t_start = time.time()

                    self.check_scanned_codes(scanned_codes, complete_label_read)

                    # send data to cloud
                    if self.associate_q.full():
                        self.logger.warning(f'association queue is full. discard association for {complete_label_read}')
                    self.associate_q.put(complete_label_read)

                    # end of label scanning:
                    self.check_end_of_label(complete_label_read)
                    self.is_new_label.clear()
                    # TODO add save image scanner

                else:
                    self.scanner.reset()
                    time.sleep(0.050)
            except Exception as e:
                self.logger.warning(f'During Scanner run the following exception occurred: {e}')
                need_to_recovery = True

            # check live and recovery
            if time.time() - t_start > CHECK_LIVE_TIME or need_to_recovery:
                still_running = self.scanner.is_open()
                if not still_running:
                    try:
                        still_running = self.scanner.reconnect()
                    except Exception as e:
                        still_running = False
                        self.logger.warning(f'lost communication with the scanner due to: {e}')
                if still_running:
                    print('scanner is alive')  # for the console and not for logging
                    need_to_recovery = False
                else:
                    self.logger.warning(f'Scanner: trying again in {TIME_BTWN_RECOVERY} seconds')
                    time.sleep(TIME_BTWN_RECOVERY)

                t_start = time.time()

        self.scanner.close_port()

    def check_scanned_codes(self, codes_in, complete_label_read):
        for code in codes_in:
            if is_wiliot_code(code):
                complete_label_read['wiliot_code'].append(code)
                complete_label_read['timestamp'] = datetime.datetime.now().timestamp()
            elif is_asset_code(code):
                complete_label_read['asset_code'].append(code)
                complete_label_read['timestamp'] = datetime.datetime.now().timestamp()
        if len(complete_label_read['wiliot_code']) >= WILIOT_MIN_NUM_CODE \
                and len(complete_label_read['asset_code']) == ASSET_NUM_CODES:
            complete_label_read['status'] = True
            self.logger.info(f'Found all codes for association! '
                             f'Wiliot:{complete_label_read["wiliot_code"]}, Asset: {complete_label_read["asset_code"]}')

    def check_end_of_label(self, label_read):
        if label_read is None:
            return
        if len(label_read['asset_code']) == 0 and len(label_read['wiliot_code']) == 0:
            self.logger.info(f"No codes were read")
        if len(label_read['asset_code']) < ASSET_NUM_CODES:
            self.logger.info(f"Not enough Asset codes were scanned: {label_read['asset_code']}")
        elif len(label_read['asset_code']) > ASSET_NUM_CODES:
            self.logger.info(f"Too many Asset codes were scanned: {label_read['asset_code']}")
        elif len(label_read['wiliot_code']) < WILIOT_MIN_NUM_CODE:
            self.logger.info(f"Not enough Wiliot codes were scanned: {label_read['asset_code']}")


class LabelCounter(object):
    def __init__(self, logger_name, is_stop_event, new_label_event, max_movement_time=0):
        self.is_stop = is_stop_event
        self.is_new_label = new_label_event
        self.logger = logging.getLogger(logger_name)

        available_ports = self.get_arduino_ports()
        try:
            for port in available_ports:
                self.arduino = serial.Serial(port, ARDUINO_BAUD_RATE, timeout=0.1)
                time.sleep(1)
                self.config(max_movement_time)
                self.port = port
                self.max_movement_time = max_movement_time
                break
        except Exception as e:
            self.logger.warning(f"could not connect to the Arduino due to {e}")
            raise Exception('could not connect to the Arduino')

    def config(self, max_movement_time):
        """
        @return:
        @rtype:
        """
        self.arduino.write(f'*time_btwn_triggers {int(max_movement_time)}'.encode())
        time.sleep(2)
        while self.arduino.in_waiting > 0:
            rsp = self.arduino.readline()

            if rsp.decode() == f'Max movement time was set to {int(max_movement_time)}[sec]\r\n':
                self.logger.info(f'config Arduino and got the following msg: {rsp.decode()}')
                return
            else:
                rsp_to_print = rsp.decode().strip("\r\n")
                self.logger.info(f'wait for Arduino config ack, got the following msg: {rsp_to_print}')

        raise Exception('Arduino Configuration was failed')

    def get_arduino_ports(self):
        """
        Gets all the ports we have, then chooses Arduino's ports
        """
        arduino_ports = []
        available_ports = [s for s in serial.tools.list_ports.comports()]
        for p in available_ports:
            if 'Arduino' in p.description:
                arduino_ports.append(p.device)
        if not arduino_ports:
            self.logger.warning('No Arduino was detected. please check connection')
            raise Exception('No Arduino was detected. please check connection')
        return arduino_ports

    def run(self):
        self.logger.info('Starts Label Sensor Task')
        data = ''
        t_start = time.time()
        need_to_recovery = False
        need_send_alive_msg = True
        t_alive_msg = time.time()

        while True:
            if self.is_stop.is_set():
                self.logger.info('stop Label Sensor Task')
                break

            try:
                tmp = self.arduino.readline()
            except Exception as e:
                self.logger.warning(f"got exception during readline need to check connection: {e}")
                need_to_recovery = True
                tmp = b''

            if len(tmp) > 0:
                try:
                    t_start = time.time()
                    data += tmp.decode()
                    if '\n' not in data:
                        continue  # got partial rsp

                    if "pulses detected" in data:
                        self.is_new_label.set()
                        data = ''
                    elif 'Wiliot' in data:
                        data = ''
                        print('Arduino is alive')  # for the console and not for logging
                    need_to_recovery = False
                    need_send_alive_msg = True
                    self.logger.info(f'got rsp from arduino msg: cur: {tmp}, cum: {data}')

                except Exception as e:
                    self.logger.warning(f'got exception during decoded arduino msg: {e}')
                    data = ''
                    continue

            # check live and recovery
            if time.time() - t_start > CHECK_LIVE_TIME or need_to_recovery:
                if need_send_alive_msg or time.time() - t_alive_msg > 1:
                    sent_alive_msg = self.is_alive()
                    if sent_alive_msg:
                        need_send_alive_msg = False
                        t_alive_msg = time.time()
                    else:
                        self.logger.warning(f'Arduino: trying again in {TIME_BTWN_RECOVERY} seconds')
                        time.sleep(TIME_BTWN_RECOVERY)

                t_start = time.time()

        self.arduino.close()

    def is_alive(self):
        try:
            self.arduino.write('*id'.encode())
        except Exception as e:
            self.logger.warning(f'could not send msg to Arduino due to: {e}')
            try:
                self.arduino.close()
                time.sleep(1)
                self.arduino = serial.Serial(self.port, ARDUINO_BAUD_RATE, timeout=0.1)
                time.sleep(1)
                self.config(self.max_movement_time)
                return True
            except Exception as e:
                self.logger.warning(f'could not close serial comm Arduino due to: {e}')
                return False
        return True


class AssociationTool(object):
    def __init__(self, stop_key='esc'):
        self.logger_path, self.logger = set_logger(app_name='AssociationTool',
                                                   dir_name='association_tool', file_name='association_log')
        self.is_stop_event = threading.Event()
        self.new_label_event = threading.Event()
        associate_q = mp.Queue(maxsize=100)
        stop_mp_event = mp.Event()
        try:
            self.label_counter_thread = None
            self.label_counter = LabelCounter(logger_name=self.logger.name,
                                              is_stop_event=self.is_stop_event,
                                              new_label_event=self.new_label_event)
        except Exception as e:
            self.logger.warning(f'could no init LabelCounter due to {e}')
            raise Exception(f'could no init LabelCounter due to {e}')
        self.logger.info('init LabelCounter succeed')

        try:
            self.scanner_association_thread = None
            self.scanner_association = ScannerAssociation(logger_name=self.logger.name,
                                                          is_stop_event=self.is_stop_event,
                                                          new_label_event=self.new_label_event,
                                                          associate_q=associate_q)
        except Exception as e:
            self.logger.warning(f'could no init ScannerAssociation due to {e}')
            raise Exception(f'could no init ScannerAssociation due to {e}')
        self.logger.info('init ScannerAssociation succeed')

        try:
            self.cloud_association_process = mp.Process(target=CloudAssociation, args=(associate_q, stop_mp_event))
        except Exception as e:
            self.logger.warning(f'could no init CloudAssociation due to {e}')
            raise Exception(f'could no init CloudAssociation due to {e}')
        self.logger.info('init CloudAssociation succeed')
        self.associate_q = associate_q
        self.stop_mp_event = stop_mp_event

        self.start_app()
        self.run_app(stop_key)

    def start_app(self):
        self.label_counter_thread = threading.Thread(target=self.label_counter.run, args=())
        self.label_counter_thread.start()
        self.scanner_association_thread = threading.Thread(target=self.scanner_association.run, args=())
        self.scanner_association_thread.start()
        self.cloud_association_process.start()

    def run_app(self, exit_key='esc'):
        t_start = time.time()
        while True:
            time.sleep(0.250)
            try:
                if keyboard.is_pressed(exit_key):  # if key 'q' is pressed
                    self.logger.info('User Exit app!')
                    break
            except Exception as e:
                self.logger.info(f'during keyboard checking the following error occurs: {e}')
            if time.time() - t_start > CHECK_LIVE_TIME:
                print('association tool is still running')
                t_start = time.time()

        self.stop_app()

    def stop_app(self):
        self.is_stop_event.set()
        self.stop_mp_event.set()
        self.logger.info('wait for all process to be completed')
        self.label_counter_thread.join(timeout=60)
        self.scanner_association_thread.join(timeout=60)
        self.cloud_association_process.join(timeout=60)
        if self.label_counter_thread.is_alive():
            self.logger.warning('label_counter_thread is stuck please hard shut down the app')
        if self.scanner_association_thread.is_alive():
            self.logger.warning('scanner_association_thread is stuck please hard shut down the app')
        if self.cloud_association_process.is_alive():
            self.logger.warning('cloud_association_process is stuck please hard shut down the app')
        self.logger.info('Association Tool is done')


if __name__ == '__main__':
    stop_key = 'esc'

    AssociationTool(stop_key=stop_key)
