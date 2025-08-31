import json
import time
import traceback
from datetime import datetime
from PIL import Image, ImageTk
import os
from wiliot_api import ManufacturingClient, WiliotCloudError
from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui
from yoctopuce.yocto_api import YAPI, YRefParam
from yoctopuce.yocto_humidity import YHumidity
from yoctopuce.yocto_temperature import YTemperature
import requests
from zebra import Zebra
from wiliot_core import GetApiKey
import pytz

def get_israel_time(retries=3):
    return str(datetime.now(tz=pytz.timezone("Asia/Jerusalem"))).split(".")[0]
    # primary_url = "https://timeapi.io/api/Time/current/zone?timeZone=Asia/Jerusalem"
    # backup_url = "http://worldtimeapi.org/api/timezone/Asia/Jerusalem"
    #
    # for attempt in range(retries):
    #     try:
    #         response = requests.get(primary_url)
    #         if response.status_code == 200:
    #             data = response.json()
    #             current_time = data['dateTime']
    #             return current_time.split(".")[0].replace("T", " ")
    #         else:
    #             print(f"Primary API returned unexpected status code: {response.status_code}")
    #     except requests.exceptions.RequestException as ex:
    #         print(f"Primary API attempt {attempt + 1} failed: {ex}")
    #
    #     try:
    #         response = requests.get(backup_url)
    #         if response.status_code == 200:
    #             data = response.json()
    #             current_time = data['datetime']
    #             return current_time.split(".")[0].replace("T", " ")
    #         else:
    #             print(f"Backup API returned unexpected status code: {response.status_code}")
    #     except requests.exceptions.RequestException as ex:
    #         print(f"Backup API attempt {attempt + 1} failed: {ex}")
    #
    # print("Failed to retrieve Israel time after multiple attempts.")
    # return None


def title_button(title, width):
    width = width - len(title)
    title = ' ' * (width // 2) + title + ' ' * (width // 2)
    if width % 2 == 1:
        title += ' '
    return title


def get_manufacturing_client(env):
    owner_id = '852213717688'
    if env == 'test':
        owner_id = 'wiliot-ops'
    key_obj = GetApiKey(env=env, owner_id=owner_id)
    key = key_obj.get_api_key()
    if key:
        try:
            return ManufacturingClient(env=env, api_key=key)
        except:
            print("Unable to create an instance of ManufacturingClient.")
            return
    else:
        print("Please enter an API key in the config.json file to enable log uploads to the cloud.")
        return


def upload_json_to_s3(client, data, name, directory):
    if client is None:
        print("Please enter an API key in the config.json file to enable log uploads to the cloud.")
        return
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{name}_{timestamp}.json"
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
    try:
        res = client.partner_upload_file_to_s3(file_path=filename, directory=directory)
        print("Log was uploaded to the cloud successfully!")
        print("Response:", res)
    except WiliotCloudError:
        print("Log upload to the cloud failed!")
    except Exception as e:
        print("Log upload to the cloud failed due to exception", e)
    os.remove(filename)


def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%d%m%Y")
    except ValueError:
        return None


def print_label(label, printer_name):
    try:
        zebra_printer = Zebra()
        zebra_printer.connection = 'usb'
        zebra_printer.device = 'USB001'
        zebra_printer.setqueue(printer_name)
        zebra_printer.output(label)
        return True
    except Exception:
        print("Failed to print label!")
        traceback.print_exc()
        return False


class YoctoSensor(object):
    def __init__(self):
        self.sensor = None
        errmsg = YRefParam()
        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            raise Exception('yocto temperature sensor got init error: {}'.format(errmsg.value))

    def connect(self, target='any'):
        if target == 'any':
            # retrieve any temperature sensor
            self.sensorHum = YHumidity.FirstHumidity()
            self.sensorTemp = YTemperature.FirstTemperature()

        elif target == '':
            print('specified invalid target')
            return False
        else:
            self.sensorHum = YHumidity.FindHumidity(target + '.humidity')
            self.sensorTemp = YTemperature.FindTemperature(target + '.temperature')

        if self.sensorHum is None or self.sensorTemp is None or self.get_sensor_name() == 'unresolved':
            print('Failed to connect to sensor')
            return False

        else:
            return True

    def get_sensor_name(self):
        if self.sensor is None:
            # print('no sensor is connected. try to call connect() first')
            return ''

        sensor_str = self.sensor.describe()
        name_str = sensor_str.split('=')[1].split('.')[0]
        return name_str

    def get_humidity(self):
        if self.sensorHum is None:
            # print('sensor is not connected. try to call connect() first')
            return None
        if not (self.sensorHum.isOnline()):
            # print('sensor is not connected or disconnected during run')
            return None

        return self.sensorHum.get_currentValue()

    def get_temperature(self):
        if self.sensorTemp is None:
            # print('sensor is not connected. try to call connect() first')
            return None
        if not (self.sensorTemp.isOnline()):
            # print('sensor is not connected or disconnected during run')
            return None

        return self.sensorTemp.get_currentValue()

    @staticmethod
    def exit_app():
        YAPI.FreeAPI()


class WiliotGuiCustomized(WiliotGui):
    def on_close(self):
        self.parent.save_history()
        self.exit_gui()

    def set_parent(self, parent):
        self.parent = parent
