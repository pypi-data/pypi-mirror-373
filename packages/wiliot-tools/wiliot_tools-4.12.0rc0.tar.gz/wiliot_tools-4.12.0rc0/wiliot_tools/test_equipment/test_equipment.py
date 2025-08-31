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
from time import time, sleep
import logging
import sys
import serial  # type: ignore
import serial.tools.list_ports  # type: ignore
from yoctopuce.yocto_temperature import YAPI, YRefParam, YTemperature
from yoctopuce.yocto_humidity import YHumidity
from yoctopuce.yocto_lightsensor import YLightSensor
import os
from datetime import datetime
import select
import socket
import pandas as pd

from wiliot_core import WiliotDir, enable_class_method


class EquipmentError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        # print('calling str')
        if self.message:
            return 'EquipmentError: {msg}'.format(msg=self.message)
        else:
            return 'EquipmentError has been raised'


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    available_ports = [s.device for s in serial.tools.list_ports.comports()]
    if len(available_ports) == 0:
        available_ports = [s.name for s in serial.tools.list_ports.comports()]
        if len(available_ports) == 0:
            print("no serial ports were found. please check your connections")
    return available_ports


class Attenuator(object):
    '''
    Support all attn classes for:
    '''

    def __init__(self, ATTN_type, comport='AUTO'):
        if 'MCDI-USB' in ATTN_type:
            self._active_TE = Attenuator.MCDI_USB()
        elif 'MCDI' in ATTN_type:
            self._active_TE = Attenuator.MCDI()
        elif 'API' in ATTN_type or 'Weinschel' in ATTN_type:
            self._active_TE = Attenuator.API(comport)

        else:
            pass

    def GetActiveTE(self):
        return self._active_TE

    class MCDI(object):

        def __init__(self):
            dotnet = False
            utils_dir = os.path.join(os.path.dirname(__file__), 'utils')
            sys.path.append(utils_dir)
            if dotnet == True:
                import clr  # pythonnet, manually installed with a downloaded wheel and pip
                import ctypes  # module to open utils files
                clr.AddReference("System.IO")
                import System.IO
                System.IO.Directory.SetCurrentDirectory(utils_dir)
                clr.AddReference('mcl_RUDAT_NET45')
                from mcl_RUDAT_NET45 import USB_RUDAT
                self.Device = USB_RUDAT()
                self.Device.Connect()
                info = self.DeviceInfo()
                print('Found Attenuator: Model {}, {} ,{} '.format(info[0], info[1], info[2]))
            else:
                from USB_RUDAT import USBDAT
                self.Device = USBDAT()
                info = self.DeviceInfo()
                print('Found Attenuator: Model {}, {} ,{} '.format(info[0], info[1], info[2]))

        def DeviceInfo(self):
            cmd = ":MN?"
            model_name = self.Device.Send_SCPI(cmd, "")
            cmd = ":SN?"
            serial = self.Device.Send_SCPI(cmd, "")
            cmd = ":FIRMWARE?"
            fw = self.Device.Send_SCPI(cmd, "")
            # return [model_name[1], serial[1], fw[1]]  #dotnet
            return [model_name, serial, fw]

        def Setattn(self, attn):
            cmd = ":SETATT:" + str(attn)
            status = int(self.Device.Send_SCPI(cmd, ""))
            if status == 0:
                print('Command failed or invalid attenuation set')
            elif status == 1:
                # print('Command completed successfully')
                print('Attenuation set to  {}[dB]'.format(float(self.Getattn())))
            elif status == 2:
                print(
                    'Requested attenuation was higher than the allowed range, the attenuation was set to the device�s maximum allowed value')
            # print(status)

        def Getattn(self):
            cmd = ":ATT?"
            Resp = float(self.Device.Send_SCPI(cmd, ""))
            # print(Resp)
            # if status == 0:
            #     print('Command failed or invalid attenuation set')
            # elif status == 1:
            #     print('Command completed successfully')
            return Resp

    class MCDI_USB(object):
        # 64 bit array to send to USB
        cmd1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0]  # 64 bit array to send to USB

        def __init__(self):
            import usb
            # find the device
            self.dev = usb.core.find(idVendor=0x20ce, idProduct=0x0023)
            # was it found?
            if self.dev is None:
                raise ValueError('Device not found')
            # set the active configuration. with no args we use first config.
            #  for Linux only
            if sys.platform == 'linux':

                for configuration in self.dev:
                    for interface in configuration:
                        ifnum = interface.bInterfaceNumber
                    if not self.dev.is_kernel_driver_active(ifnum):
                        continue
                    try:
                        # print "detach kernel driver from device %s: interface %s" % (dev, ifnum)
                        self.dev.detach_kernel_driver(ifnum)
                    except usb.core.USBError:
                        pass

            self.dev.set_configuration()
            self.cmd1[0] = 41
            self.dev.write(0x01, self.cmd1)  # SN
            s = self.dev.read(0x81, 64)
            self.SerialNumber = ""
            i = 1
            while (s[i] > 0):
                self.SerialNumber = self.SerialNumber + chr(s[i])
                i = i + 1
            self.cmd1[0] = 40
            self.dev.write(0x01, self.cmd1)  # Model
            s = self.dev.read(0x81, 64)
            self.ModelName = ""
            i = 1
            while (s[i] > 0):
                self.ModelName = self.ModelName + chr(s[i])
                i = i + 1

            self.Maximum_Attn = float(self.ModelName[11:])
            self.cmd1[0] = 99
            self.dev.write(0x01, self.cmd1)  # FW
            s = self.dev.read(0x81, 64)
            self.FW = ""
            self.FW = chr(s[5]) + chr(s[6])
            self.status_message = 'Found Attenuator: Model {}, SN: {} , FW: {}, Maximum attenuation: {}dB '.format(
                str(self.ModelName), str(self.SerialNumber), str(self.FW), str(self.Maximum_Attn))
            print(self.status_message)

        def ReadSN(self):
            return str(self.SerialNumber)

        def ReadMN(self):
            return str(self.ModelName)

        def ReadFW(self):
            return str(self.FW)

        def ReadMaxRange(self):
            return self.Maximum_Attn

        def Setattn(self, Attn):
            self.cmd1[0] = 19
            self.cmd1[1] = int(Attn)
            self.cmd1[2] = int((Attn - int(Attn)) * 4)
            if Attn > self.Maximum_Attn:
                print('Attenuation not in Range,setting maximum = {} '.format(str(self.Maximum_Attn)))
                self.cmd1[1] = int(self.Maximum_Attn)
                self.cmd1[2] = int((self.Maximum_Attn - int(self.Maximum_Attn)) * 4)
            # self.dev.set_configuration()

            try:
                self.dev.write(0x01, self.cmd1)  # Set attenuation
                s = self.dev.read(0x81, 64)
                self.new_att = 'Setting Attenuation = {}dB '.format(str(s[1] + s[2] / 4))
                print(self.new_att)
                return s[1] + s[2] / 4
            except Exception as e:
                print(e)
                self.new_att = e
                return s

        def Getattn(self):
            # self.dev.set_configuration()
            try:
                self.cmd1[0] = 18
                self.dev.write(0x01, self.cmd1)  # Get attenuation
                s = self.dev.read(0x81, 64)
                self.new_att = 'Current Attenuation = {}dB '.format(str(s[1] + s[2] / 4))
                print(self.new_att)
                return s[1] + s[2] / 4
            except Exception as e:
                print(e)
                self.new_att = e
                return s

        def Send_SCPI(self, SCPIcmd, tmp):
            # send SCPI commands (to supported firmware only!)
            self.cmd1[0] = 42
            l1 = 0
            l1 = len(SCPIcmd)
            indx = 1
            while (indx <= l1):
                self.cmd1[indx] = ord(SCPIcmd[indx - 1])
                indx = indx + 1
            self.cmd1[indx] = 0
            self.dev.write(0x01, self.cmd1)  # SCP Command up to 60 chars;
            s = self.dev.read(0x81, 64)
            i = 1
            RetStr = ""
            while (s[i] > 0):
                RetStr = RetStr + chr(s[i])
                i = i + 1
            return str(RetStr)

    class API(object):

        def __init__(self, comport="AUTO"):
            self.baudrate = 9600
            if comport == "AUTO":
                ports_list = serial_ports()
                for port in ports_list:
                    self.comport = port
                    try:
                        self.s = serial.Serial(self.comport, self.baudrate, timeout=0.5)
                    except Exception as e:
                        print(f'could not connect {self.comport}, try another port due to; {e}')
                        continue
                    sleep(1)
                    self.s.flushInput()
                    self.s.flushOutput()
                    sleep(0.1)
                    # Turn the console off
                    self.s.write("CONSOLE DISABLE\r\n".encode())
                    # Flush the buffers
                    sleep(0.1)
                    self.s.flush()
                    self.s.flushInput()
                    self.s.flushOutput()
                    self.s.write("*IDN?\r\n".encode())
                    sleep(0.1)
                    if self.s.in_waiting > 1:
                        resp = self.s.readline().decode("utf-8")
                    else:
                        resp = ''
                    self.model = resp
                    if ("Aeroflex" in resp or "Weinschel" in resp or 'API' in resp):
                        print('Found ' + resp.strip('\r\n') + ' on port: ' + port)
                        break
                    elif '8311' in resp or '8331' in resp:
                        print('Found ' + resp.strip('\r\n') + ' on port: ' + port)
                    else:
                        pass
            else:
                self.s = serial.Serial(comport, self.baudrate, timeout=0.5)
                sleep(1)
                self.s.write("CONSOLE DISABLE\r\n".encode())
                # Flush the buffers
                self.s.flush()
                self.s.flushInput()
                self.s.flushOutput()
                self.Query("*IDN?\r\n")
                resp = self.Query("*IDN?\r\n")
                self.model = resp
                if ("Aeroflex" in resp) or ("4205" in resp):
                    print('Found ' + resp.strip('\r\n') + ' on port: ' + comport)
                elif '8311' in resp or '8331' in resp:
                    print('Found ' + resp.strip('\r\n') + ' on port: ' + comport)
                else:
                    self.close_port()
                    print('Aeroflex Attenuator not found on selected port, check connection', file=sys.stderr)

        def Write(self, cmd, wait=False):
            """Send the input cmd string via COM Socket"""
            if self.s.isOpen():
                pass
            else:
                self.s.open()
            self.s.flushInput()
            sleep(1)
            try:
                self.s.write(str.encode(cmd))
                sleep(0.1)  # Commands may be lost when writing too fast

            except:
                pass
            # self.s.close()

        def Query(self, cmd):
            """Send the input cmd string via COM Socket and return the reply string"""
            if self.s.isOpen():
                pass
            else:
                self.s.open()
                sleep(0.1)
            # self.s.flushInput()
            sleep(1)
            try:
                self.s.write(cmd.encode())
                sleep(0.1)
                if self.s.in_waiting > 0:
                    data = self.s.readline().decode("utf-8")
                else:
                    data = ''
            except:
                data = ''
            # self.s.close()
            return data

        def close_port(self):
            if self.s is not None and self.s.isOpen():
                self.s.close()

        def is_open(self, check_port=False):
            if self.s is not None:
                if check_port:
                    try:
                        self.Query("*IDN?\r\n")
                        resp = self.Query("*IDN?\r\n")
                        self.model = resp
                        if ("Aeroflex" in resp):
                            return True
                        elif '8311' in resp or '8331' in resp:
                            return True
                    except:
                        self.close_port()
                else:
                    return self.s.isOpen()
            return False

        def Setattn(self, attn):
            cmd = "ATTN {:.2f}\r\n".format(attn)
            self.Write(cmd)
            value = self.Getattn()
            value = float(value)
            if value != attn:
                print(f'Error setting attenuation: new : {attn} current: {value}')
            return value

        def Getattn(self):
            cmd = "ATTN?\r\n"
            value = self.Query(cmd)
            return value


class Tescom:
    """
    Control TESCOM testing chambers
    """
    open_cmd = b'OPEN\r'
    close_cmd = b'CLOSE\r'
    com_port_obj = None
    models_list = ['TC-5064C', 'TA-7011AP', 'TC-5063A', 'TC-5970CP']

    def __init__(self, port=None):
        self.port = port
        try:
            if port is not None:
                self.connect(port)

        except Exception as e:
            print(e)
            print("Tescom - Connection failed")

    def connect(self, port):
        """
        :param port: com port to connect
        :return: com port obj
        """
        try:
            com_port_obj = self.com_port_obj = serial.Serial(port=port, baudrate=9600, timeout=1)
            if com_port_obj is not None:
                self.door_cmd = None
                self.com_port_obj.write(b'MODEL?\r')
                sleep(0.1)
                model = str(self.com_port_obj.read(14))
                parts = [p for p in model.split("'")]
                parts = [p for p in parts[1].split(" ")]
                self.model = parts[0]
                if len(self.model) > 0:
                    print("RF chamber connected to port " + str(port))
                    print("Tescom - Chamber model:", self.model)
                else:
                    print("Tescom - Error! Chamber is not responding")
                    return
                if self.model in self.models_list:
                    self.door_cmd = b'DOOR?\r'
                else:
                    self.door_cmd = b'LID?\r'
            else:
                raise Exception
        except Exception as e:
            # print(e)
            print(f"Tescom - Could not connect to port {port} due to {e}")
            return None

    def close_port(self):
        """
        closes com port
        """
        try:
            self.com_port_obj.close()
            print("RF chamber disconnected from port: " + str(self.port))
        except Exception as e:
            print("Could not disconnect")

    def open_chamber(self):
        """
        opens chamber
        :return: "OK" if command was successful
        """
        if self.is_door_open():
            print("Chamber is open")
            return 'OK'
        try:
            print(f"Chamber {self.port} is opening")
            self.com_port_obj.reset_input_buffer()
            self.com_port_obj.reset_output_buffer()
            self.com_port_obj.write(self.open_cmd)
            res = ''
            wait_counter = 0
            if self.door_cmd is not None:
                while 'OK' not in res:
                    if wait_counter >= 15:
                        raise Exception(f"Error in opening chamber {self.port}")
                    res = self.com_port_obj.read(14).decode(
                        'utf-8').upper().rstrip('\r')
                    if len(str(res)) > 0:
                        print(f'Chamber {self.port} status: ' + str(res))
                    wait_counter += 1
                    sleep(0.1)
                if not self.is_door_open():
                    raise Exception(
                        f"{self.port} Door status doesn't match command sent!")
            print(f"Chamber {self.port} is open")
            return 'OK'
        except Exception as e:
            print(e)
            return "FAIL"

    def close_chamber(self):
        """
        closes chamber
        :return: "OK" if command was successful
        """
        if self.is_door_closed():
            print("Chamber closed")
            return 'OK'
        try:
            print(f"CHAMBER {self.port} IS CLOSING, CLEAR HANDS!!!")
            sleep(2)
            self.com_port_obj.write(self.close_cmd)
            res = ''
            wait_counter = 0
            if self.door_cmd is not None:
                while 'READY' not in res:
                    if wait_counter >= 5:
                        raise Exception(f"chamber {self.port} status is NOT ready")
                    res = self.com_port_obj.read(14).decode(
                        'utf-8').upper().rstrip('\r')
                    if 'ERR' in res or 'READY' in res or 'OK' in res:
                        print(f'Chamber {self.port} status: ' + str(res))
                    else:
                        print(f'Chamber {self.port} did not answered: {res}' + str(res))
                    if 'ERR' in res:
                        return "FAIL"
                    wait_counter += 1
                    sleep(0.1)
                if not self.is_door_closed():
                    raise Exception(
                        f"{self.port} Door status doesn't match command sent!")
            print(f"Chamber {self.port} closed")
            return 'OK'
        except Exception as e:
            print(f"Error in closing chamber {self.port}, due to {e}")
            return "FAIL"

    def is_connected(self):
        if self.com_port_obj is None:
            return False
        return self.com_port_obj.isOpen()

    def get_state(self):
        state = ''
        rsp = ''
        try:
            self.com_port_obj.reset_input_buffer()
            sleep(0.1)
            if self.door_cmd is None:
                return state
            self.com_port_obj.write(self.door_cmd)
            sleep(0.1)
            rsp = self.com_port_obj.read(14)
            state = rsp.decode('utf-8').upper().rstrip('\r')
        except Exception as e:
            print(f'Could not communicate with chamber due to {e}. Got response:{rsp}. please check chamber connection')
        return state

    def is_door_open(self):
        state = self.get_state()
        if 'OPEN' in state:
            return True
        return False

    def is_door_closed(self):
        state = self.get_state()
        if 'CLOSE' in state:
            return True
        return False


class BarcodeScanner:
    def __init__(self, com_port: str = None, baud_rate: int = 115200, config: bool = True,
                 log_type: str = 'NO_LOG', write_to_log: bool = False, timeout: str = '1000', log_name: str = None,
                 is_flash=True):
        """
        Initialize the QRScanner object.
        Datasheet:
        https://cdn.rtscan.net/wp-content/uploads/2022/06/User_Manual_RT214_RT217_RT235_RT240_2022.05_1.0.6.pdf
        For the first use, you will need to scan 3 barcode to initial comport connection:
        https://wiliot.atlassian.net/wiki/spaces/FW/pages/2566029407/RTscan+Barcode+Scanner
        @param com:
        @type com:
        @param baud:
        @type baud:
        @param config:
        @type config:
        @param log_type:
        @type log_type:
        @param write_to_log:
        @type write_to_log:
        @param timeout:
        @type timeout:
        """
        self.prefix = '~0000@'
        self.suffix = ';'
        self.com_port = com_port
        self.serial_connection = None
        self.device_signature = "NLS-N1"
        self.log_type = log_type
        self.write_to_log = write_to_log
        self.sgtin_length = 31

        if log_name is None:
            self.qr_logger = logging.getLogger('QRLogger')
        else:
            self.qr_logger = logging.getLogger(log_name)

        if com_port is not None:
            self.open_port(com_port, baud_rate=baud_rate, config=config, timeout=timeout, is_flash=is_flash)
        else:
            self.auto_connect(timeout=timeout)

        if self.write_to_log:
            self.create_log_file()

    def create_log_file(self):
        """
        Create a log file.
        """
        wiliot_dir = WiliotDir()
        wiliot_dir.create_dir('QR_scan')
        app_dir = wiliot_dir.get_wiliot_root_app_dir()
        log_dir = os.path.join(app_dir, 'QR_scan')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_filename = os.path.join(log_dir, f"QR_read_log_{current_time}.log")
        with open(self.log_filename, 'w') as f:
            f.write("Log file created.\n")

    def auto_connect(self, baud_rate: int = 115200, config: bool = True, timeout: str = '1000'):
        """
        Automatically connect to the COM port.
        """
        com_port = self.find_com_port(baud_rate)
        if com_port is not None:
            self.open_port(com_port, baud_rate, config, timeout=timeout)
        else:
            self.qr_logger.error("No suitable COM port found.")
            sys.exit(1)

    def is_rtscan_rt235(self, com_port: str, baud_rate: int = 115200) -> bool:
        """
        Check if the device is RTscan RT235.
        """
        try:
            with serial.Serial(com_port, baud_rate, timeout=1) as ser:
                ser.write(str.encode(self.prefix + "QRYPDN" + self.suffix))
                sleep(0.1)
                response = ser.read_all().decode()
                return self.device_signature in response
        except Exception as e:
            self.qr_logger.error(f"Error in is_rtscan_rt235: {e}")
            return False

    def find_com_port(self, baud_rate: int = 115200) -> str:
        """
        Find the COM port.
        """
        com_ports = serial.tools.list_ports.comports()
        for com_port in com_ports:
            if com_port.vid == 7851 and com_port.pid == 7430:
                if self.is_rtscan_rt235(com_port.device, baud_rate):
                    return com_port.device
        return None

    def open_port(self, com_port: str, baud_rate: int = 115200, config: bool = True, timeout: str = '1000',
                  is_flash: bool = True):
        """
        Open the COM port.
        """
        try:
            if not self.is_rtscan_rt235(com_port, baud_rate):
                raise Exception(f'{com_port} is not a barcode scanner')
            self.serial_connection = serial.Serial(com_port, baud_rate, timeout=(int(timeout) + 50) / 1000)
        except Exception as e:
            self.close_port()
            raise Exception(f'Could not connect to {com_port}: {e}')

        if self.serial_connection is not None and self.log_type != 'NO_LOG':
            self.qr_logger.info(f'Barcode scanner ({com_port}) connected.')
        elif self.serial_connection is None:
            self.qr_logger.error(f'Barcode scanner - Problem connecting {com_port}')
            return

        self.com_port = com_port
        self.serial_connection.writeTimeout = 0.5  # write timeout.
        if config:
            self.configure(time_out=timeout, ill_scn=str(int(is_flash)))

    def close_port(self):
        """
        Close the COM port.
        """
        if self.serial_connection is not None and self.serial_connection.isOpen():
            self.serial_connection.close()

    def is_open(self) -> bool:
        """
        Check if the COM port is open.
        """
        try:
            res = self.manual_configure(['QRYPDN'])
            if 'NLS-N1' in str(res):
                return True
            return False
        except:
            return False

    def configure(self, ill_scn='1', aml_ena='1', grb_ena='0', grb_vll='2', ats_ena='0', ats_dur='36000', scn_mod='0',
                  pwb_ena='0', rrdr_en='1', grd_ena='0', grd_dur='1', time_out='10', bad_msg_en=True, symbologies=None):
        '''
        ill_scn - illumination:         0-off, 1-normal, 2-always on
        aml_ena - aiming:               0-off, 1-normal, 2-always on
        pwb_ena - power on beep         0-off, 1-on
        grb_ena - good read beep        0-off, 1-on
        grd_ena - good read enable      0-off, 1-on
        grd_dur - good read duration    1-36000 [msec]
        ats_ena - auto sleep            0-disable, 1-enable
        ats_dur - sleep duration        1-36000 [sec]
        rrdr_en - Reread reset          0-off, 1-on
        scn_mod - scan mode             0-level mode, 2-sense mode, 3-continuous mode, 7-batch mode
        symbologies - a list of strings representing the symbologies to enable, e.g. ['QR', 'PDF417', 'EAN13']

        Level Mode:
        In this mode, the scanner waits for a trigger pull to activate a decode session. The decode session continues until a barcode is decoded or you release the trigger.
        Command trigger mode:
        This mode requires you to send a command (1B 31 in hex) to activate a decode session.

        Sense Mode:
        In this mode, the scanner activates a decode session every time it detects a barcode presented to it. The decode session continues until a barcode is decoded or the decode session timeout expires. You can adjust the sensitivity and reread timeout to avoid undesired rereading of the same barcode in a given period of time. You can also adjust the image stabilization timeout to give the scanner time to adapt to ambient environment after it decodes a barcode and “looks” for another.

        Continuous Mode:
        In this mode, the scanner automatically starts one decode session after another. To suspend/resume barcode reading, simply press the trigger. You can adjust the reread timeout to avoid undesired rereading of the same barcode in a given period of time. Note that when switching to this mode by scanning the Continuous Mode barcode, the scanner will stop barcode reading for 3 seconds before starting scanning continuously.

        Batch Mode:
        In this mode, a trigger pull activates a round of multiple decode sessions. The round of multiple scans continues until you release the trigger. Rereading the same barcode is not allowed in the same round.
        '''
        sleep(0.1)
        params = {'ILLSCN': ill_scn, 'AMLENA': aml_ena, 'GRBENA': grb_ena, 'ATSENA': ats_ena,
                  'NGRENA': '1' if bad_msg_en else '0',
                  'GRBVLL': grb_vll, 'ATSDUR': ats_dur, 'SCNMOD': scn_mod, 'RRDREN': rrdr_en, 'GRDENA': grd_ena,
                  'GRDDUR': grd_dur,
                  'PWBENA': pwb_ena, 'ORTSET': time_out}
        params = [key + value for key, value in params.items()]

        if symbologies is not None:
            for symbology in symbologies:
                params.append('SYMB_' + symbology + '1')

        t, isSuccess = self.manual_configure(params)
        if isSuccess and self.log_type != 'NO_LOG':
            self.qr_logger.info(f'Barcode scanner ({self.com_port}) configured successfully.')
        elif not isSuccess:
            self.qr_logger.error(f'Barcode scanner ({self.com_port}) configuration failed.')

    def restore_all_factory_defaults(self):
        """
        Restore all factory defaults.
        """
        sleep(0.1)
        params = {'FACDEF': ''}
        params = [key + value for key, value in params.items()]
        t, isSuccess = self.manual_configure(params)
        if isSuccess and self.log_type != 'NO_LOG':
            self.qr_logger.info(f'Barcode scanner ({self.com_port}) restored factory default successfully.')
        elif not isSuccess:
            self.qr_logger.error(f'Barcode scanner ({self.com_port}) restored factory default failed.')

    def manual_configure(self, params):
        """
        Manually configure the scanner.
        """
        self.serial_connection.flushInput()
        self.serial_connection.flushOutput()
        sleep(0.1)
        bad_msg = '460d0a'  # 46 = F, #0d = /r #0a = /n -> means that every error or decoding timeout will send the message F/r/n -> will be translated by serial lib as F<NewLine>
        enter_setup_mode = 'SETUPE1'
        exit_setup_mode = 'SETUPE0'
        # Enter setup mode
        self.serial_connection.write(str.encode(self.prefix + enter_setup_mode + self.suffix))
        # Insert configuration
        configs = self.prefix + ';'.join(params) + self.suffix
        self.serial_connection.write(str.encode(configs))
        if 'NGRENA1' in params:
            self.serial_connection.write(
                str.encode(self.prefix + 'NGRSET' + bad_msg + self.suffix))  # Set message to empty
        if 'SCNMOD2' in params:
            self.serial_connection.write(
                str.encode(self.prefix + 'SENLVL5' + bad_msg + self.suffix))  # Set sensitivity to high 1-20
        # Exit setup mode
        self.serial_connection.write(str.encode(self.prefix + exit_setup_mode + self.suffix))
        sleep(0.1)
        t, isSuccess = self.trigger_stop_settings()
        return t, isSuccess

    def scan(self):
        """
        Scan the QR code.
        """
        t = None
        try:
            self.serial_connection.write(b"\x1b\x31")
        except Exception as e:
            raise Exception(f'Scanner: Error sending message through UART- Check connection {e}')
        start_time = datetime.now()
        t = self.serial_connection.readline()
        end_time = datetime.now()
        elapsed_time_ms = (end_time - start_time).total_seconds() * 1000
        return t, elapsed_time_ms

    def scan_and_flush(self):
        """
        Scan the QR code and flush the buffer.
        """
        def clean_scan_f(input_scan):
            try:
                decoded_scan = input_scan.decode()
                stripped_scan = decoded_scan.strip()
                clean_str = stripped_scan.replace('\r\n', '').replace('\x06', '').replace('\x01', '')
                return clean_str
            except UnicodeDecodeError:
                return None

        if self.serial_connection is None:
            self.qr_logger.error("Error: Serial object not initialized")
            return None

        scanned, elapsed_time_ms = self.scan()

        if scanned:
            clean_scan = clean_scan_f(scanned)
            if clean_scan == 'F':
                return None, elapsed_time_ms
            else:
                return clean_scan, elapsed_time_ms

        else:
            if self.is_open():
                self.serial_connection.reset_input_buffer()
                self.serial_connection.reset_output_buffer()
                sleep(0.1)
                scanned, elapsed_time_ms = self.scan()
                if scanned:
                    clean_scan = clean_scan_f(scanned)
                    if clean_scan == 'F':
                        return None, elapsed_time_ms
                    else:
                        return clean_scan, elapsed_time_ms
                else:
                    raise Exception('Error reading barcode data - Serial problem')
            else:
                raise Exception('Error in Scanner Serial connection')

    def scan_ext_id(self, need_to_trigger=True):
        """
        Scan the external ID.
        @param need_to_trigger to keep same behavior as the Cognex
        """
        barcode_read = ''
        start_time = time()
        try:
            barcode_read, elapsed_time_ms = self.scan_and_flush()
            if barcode_read is None:
                return None, None, None, None
            elif barcode_read == '':
                raise Exception('Error in Scanner Serial connection')
            else:
                full_data, cur_id, reel_id, gtin = self.read_barcode(barcode_read)
            if self.write_to_log:
                with open(self.log_filename, 'a') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_message = f"{timestamp} - {full_data} - Elapsed Time: {elapsed_time_ms:.2f} ms\n"
                    f.write(log_message)

            return full_data, cur_id, reel_id, gtin
        except Exception as e:
            self.qr_logger.error(f'{e} - Check connection')
            raise Exception(f'{e} - Check connection')

    def read_barcode(self, barcode_read):
        """
        Read the barcode.
        """
        try:
            if '(01)' in barcode_read:
                barcodes = barcode_read.split("(01)")
                for i, single_barcode in enumerate(barcodes[1:], 1):
                    full_data = f"(01){single_barcode}"
                    gtin = ')'.join(full_data.split(')')[:2]) + ')'
                    tag_data = full_data.split(')')[2]
                    cur_id = tag_data.split('T')[1].strip("' ").split('(')[0]
                    reel_id = tag_data.split('T')[0].strip("' ")

                    if full_data and cur_id and reel_id and gtin:
                        self.qr_logger.info(
                            f'Wiliot QR detected GTin: {gtin}, Reel: {reel_id}, ID:{cur_id}')
                        return full_data, cur_id, reel_id, gtin
            else:
                full_data = cur_id = reel_id = gtin = barcode_read
                gtin_val = True if len(full_data) == self.sgtin_length else False
                if gtin_val:
                    cur_id = full_data.split('T')[1].strip("' ").split('(')[0]
                    reel_id = full_data.split('T')[0].strip("' ")[-4:]
                    gtin = full_data.split('T')[0].strip("' ")[:-4]
                    self.qr_logger.info('Wiliot QR detected GTin: {}, Reel: {}, ID:{}'.format(gtin, cur_id, reel_id))
                    return full_data, cur_id, reel_id, gtin
                else:
                    try:
                        if full_data == 'F':
                            self.qr_logger.info('No barcode detected - Decoding timeout reached')
                            return None, None, None, None
                        elif full_data == '':
                            raise Exception('Problem with barcode scanner')
                        else:
                            cur_id = full_data.split('T')[1]
                            reel_id = full_data.split('T')[0]
                            gtin = ''
                            self.qr_logger.info('Wiliot QR detected Reel: {}, ID:{}'.format(cur_id, reel_id))

                    except Exception:
                        self.qr_logger.info('Not Wiliot barcode')

                    return full_data, cur_id, reel_id, gtin

        except Exception as e:
            self.qr_logger.error(f"Error during reading Wiliot barcode: {e}")
            raise Exception

        return None, None, None, None

    def auto_scan(self):
        """
        Automatically scan the QR code.
        """
        self.serial_connection.write(b"\x1b\x32")
        t = self.serial_connection.read_all()
        self.qr_logger.info(f'auto scan: got msg {t}')
        return t

    def trigger_stop_settings(self):
        """
        Trigger stop settings.
        """
        sleep(0.05)
        t = self.serial_connection.read_all()
        sleep(0.05)
        acks = str(t).split(';')[:-1]
        isSuccess = all([True if ack.endswith('\\x06') else False for ack in acks])
        return t, isSuccess

    def trigger_off(self):
        """
        to keep same behavior as the Cognex
        @return:
        @rtype:
        """
        pass


class CognexDataMan:
    CONTINUOUS_TRIGGER_TYPE = 4
    SGTIN_STRIP_LEN = 27
    SGTIN_LEN = 31
    REEL_ID_LEN = 4
    MIN_TIME_TO_READ = 0.200

    def __init__(self, port=None, baud_rate=115200, timeout=500, log_name=None, default_config=None, enable=True, host='', telnet_port=0, device_name=None, sim_csv_path=None):
        """
        https://support.cognex.com/docs/dmst_2322/web/EN/DMCC/Content/Topics/dmcc-main.html
        to download COGNEX GUI: https://support.cognex.com/en/downloads/detail/dataman/4512/1033
        @param port:
        @type port:
        @param baud_rate:
        @type baud_rate:
        @param default_config: dictionary where the command is the ket and the command value is the value,
                               e.g. {'TRIGGER.TYPE': '0', 'SYMBOL.QR': 'ON'}
        @type default_config: dict
        """
        self.device_name = device_name if device_name else 'DM'
        self.com_port = port
        self.baud_rate = int(baud_rate)
        self.timeout = int(timeout)
        self.host = host
        self.port = int(telnet_port)
        self.default_config = default_config
        self.enable = enable
        self.scanner = None
        self.connected = False
        if log_name is None:
            self.logger = logging.getLogger('CognexScannerLogger')
        else:
            self.logger = logging.getLogger(log_name)

        if not self.enable:
            self.connected = True
            self.sim_data = None
            if sim_csv_path is not None:
                import pandas as pd
                self.sim_data = pd.read_csv(sim_csv_path)
                self.sim_data_ind = 0
            return
        if self.com_port is not None or (self.host and self.port):
            self.connected = self.open_port()
        else:  # relevant only for serial comm
            all_ports = serial.tools.list_ports.comports()
            for port in all_ports:
                if port.manufacturer is not None and 'cognex' in port.manufacturer.lower():
                    try:
                        self.com_port = port.device
                        connected = self.open_port()
                    except Exception as e:
                        self.logger.warning(f'Could not connect to port {port} due to {e}')
                        continue
                    if connected:
                        self.connected = True
                        break

        if self.connected:
            self.init_configurations()
            self.com_port = port
            self.baud_rate = baud_rate

    def _connect(self, connection_configs=None):
        ser = serial.Serial(self.com_port, self.baud_rate, timeout=self.timeout/1000)
        ser.writeTimeout = 0.5
        return ser
    
    def _write(self, msg):
        self.scanner.write(msg.encode())
    
    def _read(self):
        return self.scanner.readline().decode()
    
    def _data_available(self):
        return self.scanner.in_waiting > 1
    
    def _reset(self):
        waiting_bytes = self.scanner.in_waiting
        if waiting_bytes != 0:
            self.scanner.reset_input_buffer()
        return waiting_bytes

    def _disconnect(self):
        if self.scanner.isOpen():
            self.scanner.close()
    
    @enable_class_method()
    def open_port(self, com_port: str = None, baud_rate: int = 115200, config: bool = True, timeout: str = '1000') -> bool:  # same signature as other scanner
        """

        @param com_port:
        @type com_port:
        @param baud_rate:
        @type baud_rate:
        @param timeout: timeout in msec
        @type timeout: int or str
        @param config: timeout in msec
        @type config: int or str
        @return:
        @rtype:
        """
        try:
            self.scanner = self._connect()
            sleep(1)
            connected = self.is_open()
            if connected and config:
                self.init_configurations()
            return connected
        except Exception as e:
            raise Exception(f"Failed to open port: {e}")

    @enable_class_method()
    def is_open(self) -> bool:
        try:
            dev_name = self.get_device_property('DEVICE.NAME')
            if self.device_name in dev_name:
                self.device_name = dev_name
                self.logger.info(f'connected to {dev_name}')
                return True
        except Exception as e:
            self.logger.info(f'device is not communicate due to {e}')
        return False

    def reconnect(self):
        self.logger.info(f'Try  to reconnect...')
        self.close_port()
        try:
            self.connected = self.open_port()
        except Exception as e:
            self.logger.warning(f'could not reconnect to device: {e}')
            if self.connected:
                self.init_configurations()
        return self.connected

    def configure(self, command, value):
        self.set_device_property(command, value)
        sleep(0.1)
        rsp = self.get_device_property(command)
        if str(value) not in rsp:
            raise Exception(f'Could not configure {command} to {value}. the {command} is currently set to {rsp}')

    def init_configurations(self):
        if self.default_config is not None:
            for cmd, val in self.default_config.items():
                self.configure(command=cmd, value=val)

    @enable_class_method()
    def send_command(self, command, command_id=123, checksum=0) -> None:
        command_header = f'||{checksum}:{command_id}>'
        footer = '\r\n'
        full_command = f'{command_header}{command}{footer}'
        try:
            self.logger.info('Message sent {}'.format(full_command.encode()))
            self._write(msg=full_command)
        except Exception as e:
            raise Exception(f"Failed to send command due to: {e}")

    @enable_class_method(sim_data_col='all_codes')
    def read_response(self) -> str:
        try:
            response = self._read()
            return response
        except Exception as e:
            raise Exception(f"Failed to read response: {e}")

    @enable_class_method(sim_data_col='all_codes', sim_data_func=lambda s: s.split(','))
    def read_batch(self, n_msg=1000, wait_time=0.0) -> list:
        """
        wait_time in seconds
        @param n_msg max number of msg to stop the reading batch
        @type n_msg int
        @param wait_time the max time in second till need to stop the reading batch
        @type wait_time float
        """
        rsp_out = []
        t_start = time()
        while len(rsp_out) < n_msg:
            if not self._data_available():
                if time() - t_start < wait_time:
                    sleep(0.050)
                    continue
                else:
                    break
            rsp = self.read_response()
            if rsp == '':
                break
            for r in rsp.split('\r\n'):
                if r in rsp_out:
                    continue
                rsp_out.append(r)
        return rsp_out

    def discover_device(self):
        self.send_command('GET DEVICE.TYPE')
        return self.read_response()

    def set_device_property(self, property_name, value):
        self.send_command(f'SET {property_name} {value}')
        sleep(0.1)
        return self.read_response()

    def get_device_property(self, property_name):
        self.send_command(f'GET {property_name}')
        sleep(0.1)
        return self.read_response()

    def trigger_on(self, continuously=False, trigger_type=0, need_to_config=False):
        """

        @param trigger_type: 0: Single (external), 1: Presentation (internal), 2: Manual (button), 3: Burst (external),
                     4: Self (internal), 5: Continuous (external)
                     * Single: Acquires a single image and attempts to decode any symbol it contains or more than one
                     symbol in cases where multicode is enabled. The reader relies on an external trigger source.
                     * Presentation: Repeatedly scans for a symbol and decodes it whenever one is detected.
                     The reader relies on an internal timing mechanism to acquire images.
                     * Burst: Performs multiple image acquisitions based on an external trigger and decodes one or
                     multiple symbols appearing in the sequence of images.
                     * Self: Similar to Presentation mode in that the reader perpetually scans for symbols and decodes
                     them each time one is detected. Unlike Presentation mode, however, Self mode supports multicode
                     results and a decode attempt occurs with every image. The main difference between Self and
                     Presentation is the fixed and exact interval for image acquisitions in Self.
                     * Continuous: Begins acquiring images based on a single external trigger and continues to acquire
                     images until a symbol is found and decoded, or until multiple images containing as many codes as
                     specified in multicode mode are located, or until the trigger is released.
        @type trigger_type: int
        @param continuously: if True, the scanner will read in continuous mode
        @type continuously: bool
        @param need_to_config: if True, first the scanner is configured with the relevant trigger type
        @type need_to_config: bool
        @return:
        @rtype:
        """
        if need_to_config:
            if continuously and trigger_type == 0:
                trigger_type = self.CONTINUOUS_TRIGGER_TYPE
            self.set_device_property('TRIGGER.TYPE', trigger_type)
        self.send_command('TRIGGER ON')

    def trigger_off(self):
        self.send_command('TRIGGER OFF')

    @enable_class_method()
    def reset(self) -> None:
        waiting_bytes = self._reset()
        if waiting_bytes:
            self.logger.info(f'clean buffer from {waiting_bytes} bytes')

    def scan_ext_id(self, need_to_trigger=True):
        if need_to_trigger:
            self.trigger_on(need_to_config=False)

        rsp = self.read_response()
        if rsp == '':
            return None, None, None, None

        if len(rsp) == self.SGTIN_STRIP_LEN or len(rsp) == self.SGTIN_LEN:
            cur_id = rsp.split('T')[1]
            gtin_and_reel_id = rsp.split('T')[0]
            reel_id = gtin_and_reel_id[-self.REEL_ID_LEN:]
            gtin = gtin_and_reel_id[:-self.REEL_ID_LEN]
        else:
            cur_id = rsp.split('T')[1]
            reel_id = rsp.split('T')[0]
            gtin = ''
        return rsp, cur_id, reel_id, gtin

    def beep(self, duration):
        self.send_command(f'BEEP {duration}')
        return self.read_response()

    def set_decoder_roi(self, x1, x2, y1, y2):
        self.send_command(f'SET DECODER.ROI {x1}, {x2}, {y1}, {y2}')
        return self.read_response()

    def set_ftp_image_ip_address(self, ip_address):
        self.send_command(f'SET FTP-IMAGE.IP-ADDRESS {ip_address}')
        return self.read_response()

    def get_mac_address(self):
        self.send_command('GET DEVICE.MAC-ADDRESS')
        return self.read_response()

    @enable_class_method()
    def close_port(self) -> None:
        self.connected = False
        try:
            self._disconnect()
        except Exception as e:
            raise Exception(f"Failed to close serial port: {e}")


class CognexNetwork(CognexDataMan):
    def __init__(self, port=None, baud_rate=115200, timeout=500, log_name=None, default_config=None, enable=True, host='', telnet_port=0, device_name=None):
        super().__init__(port, baud_rate, timeout, log_name, default_config, enable, host, telnet_port, device_name)
    
    def _connect(self, connection_configs=None):
        server_address = (self.host, self.port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(0.1)
        client.connect(server_address)
        return client
    
    def _write(self, msg):
        self.scanner.sendall(msg.encode())

    def _read(self):
        return self.scanner.recv(1024).decode()
    
    def _data_available(self):
        ready_cmd = select.select([self.scanner], [], [], 0)
        return self.scanner in ready_cmd[0]

    def _reset(self):
        waiting_bytes = self._data_available()
        if waiting_bytes > 0:
            self.scanner.recv(waiting_bytes)
        return waiting_bytes

    def _disconnect(self):
        try:
            self.scanner.close()
        except Exception as e:
            self.logger.warning(f'could not close socket connection due to: {e}')


class CognexDebug(CognexDataMan):
    def __init__(self, port='COM', baud_rate=115200, timeout=500, log_name=None, default_config=None, enable=True, host='', telnet_port=0, device_name=None, csv_path_file=None, column_name='all_codes'):
        self.df = pd.read_csv(csv_path_file) if csv_path_file else None
        self.column_name = column_name
        self.i = 0
        super().__init__(port, baud_rate, timeout, log_name, default_config, enable, host, telnet_port, device_name)
    
    def _connect(self, connection_configs=None):
        return None
    
    def _write(self, msg):
        return

    def _read(self):
        data = self.df.iloc[self.i][self.column_name] if self.df is not None else ''
        self.i += 1
        return data + '\r\n'
    
    def _data_available(self):
        return self.i < len(self.df) if self.df is not None else False

    def _reset(self):
        return 0

    def _disconnect(self):
        return


class YoctoTemperatureSensor(object):
    def __init__(self):
        self.sensor = None
        errmsg = YRefParam()
        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            raise EquipmentError('yocto temperature sensor got init error: {}'.format(errmsg.value))

    def connect(self, target='any'):
        if target == 'any':
            # retrieve any temperature sensor
            self.sensor = YTemperature.FirstTemperature()
        elif target == '':
            print('specified invalid target')
            return False
        else:
            self.sensor = YTemperature.FindTemperature(target + '.temperature')
        if self.sensor is None or self.get_sensor_name() == 'unresolved':
            print('No module connected')
            return False
        else:
            return True

    def get_sensor_name(self):
        if self.sensor is None:
            print('no sensor is connected. try to call connect() first')
            return ''

        sensor_str = self.sensor.describe()
        name_str = sensor_str.split('=')[1].split('.')[0]
        return name_str

    def get_temperature(self):
        if self.sensor is None:
            print('sensor is not connected. try to call connect() first')
            return float('nan')
        if not (self.sensor.isOnline()):
            print('sensor is not connected or disconnected during run')
            return float('nan')

        return self.sensor.get_currentValue()

    @staticmethod
    def exit_app():
        YAPI.FreeAPI()


class YoctoSensor(object):
    def __init__(self, logger, target=None):
        self.temperature_sensor = None
        self.humidity_sensor = None
        self.light_sensor = None
        self.logger = logger
        errmsg = YRefParam()
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            raise EquipmentError(f'Yocto sensor initialization error: {errmsg.value}')
        try:
            self.connect(target='any' if target is None else target)
        except Exception as ee:
            self.logger.info('Sensor is not connected')
            raise Exception('Sensor is not connected')

    def connect(self, target='any'):
        sensor_mapping = {
            'temperature': (YTemperature.FirstTemperature, YTemperature.FindTemperature),
            'humidity': (YHumidity.FirstHumidity, YHumidity.FindHumidity),
            'light': (YLightSensor.FirstLightSensor, YLightSensor.FindLightSensor)
        }

        if not target:
            raise ValueError('Invalid target specified')

        for sensor_type in sensor_mapping.keys():
            sensor = sensor_mapping[sensor_type][0]() if target == 'any' else sensor_mapping[sensor_type][1](
                f'{sensor_type}.{sensor_type}')
            setattr(self, f'{sensor_type}_sensor', sensor)

        if not any(getattr(self, f'{sensor_type}_sensor') for sensor_type in sensor_mapping.keys()):
            raise EquipmentError('No module connected')

        return True

    def get_sensor_names(self):
        names = []
        for sensor in [self.temperature_sensor, self.humidity_sensor, self.light_sensor]:
            if sensor:
                name_str = sensor.describe().split('=')[1].split('.')[0]
                names.append(name_str)

        if not names:
            raise EquipmentError('No sensor is connected. Try to call connect() first')

        return names

    def get_temperature(self):
        try:
            return self._get_sensor_value(self.temperature_sensor, 'temperature')
        except Exception as ee:
            return 0

    def get_humidity(self):
        try:
            return self._get_sensor_value(self.humidity_sensor, 'humidity')
        except Exception as ee:
            return 0

    def get_light(self):
        try:
            return self._get_sensor_value(self.light_sensor, 'light')
        except Exception as ee:
            return 0

    def _get_sensor_value(self, sensor, sensor_type):
        if not sensor or not sensor.isOnline():
            raise EquipmentError(f'{sensor_type.capitalize()} sensor is not connected. Try to call connect() first')

        return sensor.get_currentValue()

    def calibration(self, real_value, calib_bool=True):
        """
        calibration and cancel calibration function.
        @param calib_bool: if True Calibration otherwise Cancel Calibration
        @type calib_bool: bool
        """
        if calib_bool:
            value_before = [self.get_light()]
            value_after = [real_value]
        else:
            value_before = []
            value_after = []
        f = YLightSensor.FirstLightSensor()
        f.calibrateFromPoints(value_before, value_after)
        f.get_module().saveToFlash()

    def calibration_points(self, real_values_array, measured_value_array):
        """
        Perform calibration using points: at least 2.
        """
        if len(real_values_array) != len(measured_value_array) and len(real_values_array) < 2:
            raise ValueError("Array must have an even number of elements. and more then 2 samples")

        f = YLightSensor.FirstLightSensor()
        if not f.isOnline():
            raise EquipmentError("Light sensor is not connected.")

        f.calibrateFromPoints(measured_value_array, real_values_array)
        f.get_module().saveToFlash()

    def calibration_light_point(self, val):
        """
        Changes the sensor-specific calibration parameter so that the current value
        matches a desired target (linear scaling).

        @param calibratedVal : the desired target value.

        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if not self.light_sensor or not self.light_sensor.isOnline():
            raise EquipmentError("Light sensor is not connected.")
        return self.light_sensor.calibrate(calibratedVal=val)

    @staticmethod
    def exit_app():
        YAPI.FreeAPI()