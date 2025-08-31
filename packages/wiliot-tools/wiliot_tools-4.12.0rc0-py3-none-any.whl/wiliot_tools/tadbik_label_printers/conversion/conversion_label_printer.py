import json
import os
import time
try:
    import tkinter as tk
except Exception as e:
    print(f'could not import tkinter: {e}')
from datetime import datetime

from wiliot_tools.tadbik_label_printers.conversion.data.default_values import default_config
from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui
from wiliot_tools.tadbik_label_printers.label_printer_tools import *


class ConversionLabelPrinter:
    def __init__(self, env="prod"):
        self.sensor = YoctoSensor()
        self.sensor.connect()
        self.counter = 0
        self.last_batch_id = None
        self.history = self.read_history()
        self.config = self.read_config()
        self.client = get_manufacturing_client(env)
        self.init_widgets()
        self.app.layout.title("conversion Label Printer")
        self.events()
        self.app.add_recurrent_function(cycle_ms=1000, function=self.recurrent)
        self.load_batch_data()
        self.app.set_parent(self)
        self.inputs_security()
        self.app.run()

    def init_widgets(self):
        main_dict = {}
        main_dict["operator_name"] = ['-'] + self.config.get('operator_name', [])
        main_dict["product_configuration"] = ['-'] + self.config.get('product_configuration', ['Cardboard', 'Plastic', 'Light'])
        main_dict["inlay"] = ['-'] + self.config.get('inlay', [])
        main_dict["start_date"] = ''
        main_dict["assembled_reel_qr_code"] = ''
        main_dict["lanes_ids"] = ''
        main_dict["number_of_lanes"] = ['-'] + self.config.get('number_of_lanes', [])
        main_dict["converted_reels_serial_number"] = list(
            range(1, int(self.config.get('converted_reels_serial_number', 200)) + 1))
        main_dict["seq_assy_reel"] = list(range(1, int(self.config.get('seq_assy_reel', 100)) + 1))
        main_dict["humidity"] = ''
        main_dict["temperature_input"] = ''
        main_dict["print_label"] = {'value': title_button('Print Label', 36), 'widget_type': 'button', 'columnspan': 3}
        main_dict["assembled_reel_conversion_completion"] = {
            'value': title_button('Assembled Reel conversion Completion', 36), 'widget_type': 'button', 'columnspan': 3}
        main_dict["output"] = {'value': '', 'widget_type': 'label', 'options': {'fg': 'red'}, 'columnspan': 3}
        main_dict["end_date"] = ''
        main_dict["total_batch_conversion_tags_qty"] = ''
        main_dict["batch_conversion_completion"] = {'value': title_button('Batch conversion Completion', 36),
                                                    'widget_type': 'button', 'columnspan': 3}
        main_dict["warning"] = {'value': '', 'widget_type': 'label', 'options': {'fg': 'red'}, 'columnspan': 3}

        main_dict = {k: {'value': v} if not isinstance(v, dict) else v for k, v in main_dict.items()}

        main_dict["humidity"] = [
            {"input": {'value': '', 'widget_type': 'entry',
                       'text': 'Humidity'}},
            {"record": {'value': 'Record Humidity & Temperature', 'widget_type': 'button'}}
        ]
        main_dict["temperature_input"] = {'value': '', 'text': 'Temperature'}
        main_dict["start_date"] = [
            {"batch_conversion_start_date": {'value': '', 'widget_type': 'entry',
                                             'text': 'Batch conversion start date'}},
            {"record_start_date": {'value': 'Record Date', 'widget_type': 'button'}}
        ]
        main_dict["end_date"] = [
            {"batch_conversion_end_date": {'value': '', 'widget_type': 'entry',
                                           'text': 'Batch conversion end date'}},
            {"record_end_date": {'value': 'Record Date', 'widget_type': 'button'}}
        ]
        main_dict["lanes_ids"] = {'value': '', 'text': 'Lanes IDs (e.g. A,B,C)'}


        self.app = WiliotGuiCustomized(main_dict, full_screen=True, theme='wiliot', do_button_config=False)

    def events(self):
        self.app.add_event(widget_key='humidity_record', event_type='button', command=self.update_sensors)
        self.app.add_event(widget_key='print_label', event_type='button', command=self.print_label)
        self.app.add_event(widget_key='assembled_reel_conversion_completion', event_type='button',
                           command=self.assembled_reel_conversion_completion)
        self.app.add_event(widget_key='batch_conversion_completion', event_type='button',
                           command=self.batch_conversion_completion)

        self.app.add_event(widget_key='inlay', event_type='<<ComboboxSelected>>', command=self.update_inlay)
        self.app.add_event(widget_key='start_date_record_start_date', event_type='button',
                           command=lambda: self.app.update_widget(widget_key='start_date_batch_conversion_start_date',
                                                                  new_value=get_israel_time()))
        self.app.add_event(widget_key='end_date_record_end_date', event_type='button',
                           command=lambda: self.app.update_widget(widget_key='end_date_batch_conversion_end_date',
                                                                  new_value=get_israel_time()))

    def update_sensors(self):
        temp = self.sensor.get_temperature()
        if temp is None:
            temp = 'Not Connected'
        hum = self.sensor.get_humidity()
        if hum is None:
            hum = 'Not Connected'
        self.app.update_widget(widget_key=f'temperature_input', new_value=temp)
        self.app.update_widget(widget_key=f'humidity_input', new_value=hum)

    def inputs_security(self):
        dropdowns = ['operator_name', 'inlay', 'seq_assy_reel', 'number_of_lanes', 'converted_reels_serial_number']
        for dd in dropdowns:
            self.app.widgets[dd].config(state='readonly')

        def only_letters_and_commas(input_value):
            if input_value == "" or all(
                    ('A' <= char.upper() <= 'F' and i % 2 == 0) or (char in (',', ',') and i % 2 == 1) for i, char in
                    enumerate(input_value)):
                return True
            return False

        vcmd = (self.app.class_tk.register(only_letters_and_commas), '%P')
        self.app.widgets['lanes_ids'].config(validate='key', validatecommand=vcmd)

        def only_numbers(input_value):
            if input_value == "" or all(char.isdigit() for i, char in enumerate(input_value)):
                return True
            return False

        vcmd = (self.app.class_tk.register(only_numbers), '%P')
        self.app.widgets['total_batch_conversion_tags_qty'].config(validate='key', validatecommand=vcmd)

    def recurrent(self):
        if self.counter % 10 == 9:
            self.save_history(output_message=False)
        self.counter += 1

    def read_history(self):
        try:
            with open(os.path.join('data', 'conversion_history.json'), 'r') as file:
                file = json.load(file)
            return file
        except FileNotFoundError:
            return {get_israel_time(): {}}

    def read_config(self):
        try:
            with open('config.json', 'r') as file:
                file = json.load(file)
            return file
        except FileNotFoundError:
            with open('config.json', 'w') as file:
                json.dump(default_config, file, indent=4)
            return default_config

    def save_page(self, output_message=True):
        values = self.app.get_all_values()
        batch_id = max(self.history.keys())
        self.history[batch_id] = values
        if output_message:
            print("Saved current page successfully.")

    def save_history(self, output_message=True):
        try:
            self.save_page(output_message)
            with open(os.path.join('data', 'conversion_history.json'), 'w') as file:
                json.dump(self.history, file, indent=4)
            if output_message:
                print("History saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving history: {e}")

    def load_batch_data(self):
        batch_id = max(self.history.keys())
        data = self.history.get(batch_id, {})
        for key, value in data.items():
            self.app.update_widget(widget_key=key, new_value=value)

    def assembled_reel_conversion_completion(self):
        self.app.update_widget(widget_key='assembled_reel_qr_code', new_value='')
        current_seq_assy_reel = self.app.get_all_values().get('seq_assy_reel')
        if current_seq_assy_reel != '-':
            next_reel = int(current_seq_assy_reel) + 1
            self.app.update_widget(widget_key='seq_assy_reel', new_value=str(next_reel))
        else:
            self.app.update_widget(widget_key='seq_assy_reel', new_value='1')
        self.app.update_widget(widget_key='converted_reels_serial_number', new_value='1')

    def batch_conversion_completion(self):
        self.history[get_israel_time()] = {}
        self.app.update_widget(widget_key='end_date_batch_conversion_end_date', new_value='')
        self.app.update_widget(widget_key='seq_assy_reel', new_value='1')
        self.app.update_widget(widget_key='converted_reels_serial_number', new_value='1')

        self.app.update_widget(widget_key='operator_name', new_value='-')
        self.app.update_widget(widget_key='inlay', new_value='-')
        self.app.update_widget(widget_key='start_date_batch_conversion_start_date', new_value='')
        self.app.update_widget(widget_key='total_batch_conversion_tags_qty', new_value='')
        self.app.update_widget(widget_key='lanes_ids', new_value='')
        self.app.update_widget(widget_key='number_of_lanes', new_value='-')
        self.app.update_widget(widget_key='assembled_reel_qr_code', new_value='')
        self.app.update_widget(widget_key='output', new_value='')
        self.app.update_widget(widget_key='warning', new_value='')
        self.app.update_widget(widget_key='humidity_input', new_value='')
        self.app.update_widget(widget_key='temperature_input', new_value='')
        self.save_history()

    def update_inlay(self, _):
        pass

    def verify_values(self, values):
        error_messages = []

        if values.get('operator_name') == '-':
            error_messages.append('Please select an operator name.')

        if values.get('inlay') == '-':
            error_messages.append('Please select an inlay.')

        batch_start_date = format_date(values['start_date_batch_conversion_start_date'])
        if batch_start_date is None:
            error_messages.append('Batch conversion start date is not a valid date format.')

        assembled_reel_qr_code = values.get('assembled_reel_qr_code')
        if not assembled_reel_qr_code:
            error_messages.append('Please scan the Assembled Reel QR Code.')
        elif assembled_reel_qr_code.split("_")[0] != values.get('inlay'):
            error_messages.append('The scanned QR code does not match the selected inlay.')

        lanes_ids = values['lanes_ids'].replace(' ', '').rstrip(',').split(',')
        if not lanes_ids or lanes_ids == ['']:
            error_messages.append('Please enter Lane IDs.')

        number_of_lines = values.get('number_of_lanes')
        if number_of_lines == '-':
            error_messages.append('Please select the number of lanes.')

        if not error_messages and len(lanes_ids) != int(number_of_lines):
            error_messages.append(
                f'The number of Lane IDs provided ({len(lanes_ids)}) does not match the selected number of lanes ({number_of_lines}).')

        if values.get('humidity_input') == '' or values.get('temperature_input') == '':
            error_messages.append('Please record the humidity and temperature.')

        if error_messages:
            full_error_message = error_messages[0]
            self.app.update_widget(widget_key='output', new_value=full_error_message, color='red')
            return False
        else:
            return True

    def print_label(self):
        values = self.app.get_all_values()
        if not self.verify_values(values):
            return

        self.app.update_widget(widget_key='humidity_input', new_value='')
        self.app.update_widget(widget_key='temperature_input', new_value='')

        inlay = values['inlay']
        seq_assy_reel = values['seq_assy_reel']
        lanes_ids = values['lanes_ids'].replace(' ', '').rstrip(',').split(',')
        conv_date = format_date(values['start_date_batch_conversion_start_date'])
        converted_reels_serial_number = values['converted_reels_serial_number']
        product_config = values['product_configuration']

        for lane_id in lanes_ids:
            label_name = f"{inlay}_{seq_assy_reel}_{lane_id.upper()}_{conv_date}_{converted_reels_serial_number}"
            label = f"""
                     ^XA
                    ^FO0,0^GFA,3024,3024,27,,::::::::::::::::::::::gK01FCQ03F8,::::gK01FCP0F3F8,gK01FCO03IF8,gK01FCO07IF8,:gK01FCO0F0FF8,gK01FCO0F07F8,gK01FCO0E07F8,:gK01FCO0F07F8,gK01FCO0F8FF8,gK01FCO07IF8,O0FEI0FE001FC07F01FC07FL03IF8,O0FEI0FE001FC07F01FC07FL01JFC,O0FEI0FE001FC07F01FC07FJ0EI03FFC,O0FEI0FE001FC07F01FC07FI0FFE003FFC,O0FEI0FE001FC07F01FC07F003IF003FFC,O0FEI0FE001FC07F01FC07F007IFC03FFC,O0FEI0FE001FC07F01FC07F00JFE03FFC,O0FEI0FE001FCJ01FCJ01KF03FFC,O0FEI0FE001FCJ01FCJ03KF03F8,O0FEI0FE001FCJ01FCJ03KF83F8,O0FEI0FE001FC07F01FC07F07FC07F83F8,O0FEI0FE001FC07F01FC07F07F803FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FE3F8,::O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F07F003FC3F8,O0FEI0FE001FC07F01FC07F07F807FC3F8,O0FEI0FE001FC07F01FC07F07FE1FF83F8,O0FEI0FE001FC07F01FC07F03KF83F8,O0FEI0FE001FC07F01FC07F01KF03F8,O0FEI0FE001FC07F01FC07F01JFE03F8,O0FEI0FE001FC07F01FC07F00JFC03F8,O0FEI0FE001FC07F01FC07F003IF803F8,O0FEI0FE001FC07F01FC07F001FFE003F8,O0FE001FE001FC07F01FC07FI03F8003F8,O0FF001FE001FC07F01FC07FN03F8,O07F003FF003FC07F01FC07FN03FC,O07F803FF807F807F01FC07FN01FE,O07FE0IFC0FF807F01FC07FN01FF03,O03PF007F01FC07FO0JF8,O01PF007F01FC07FO0JFC,O01OFE007F01FC07FO07IFE,P0JFEJFC007F01FC07FO03JF,P07IF87IF8007F01FC07FO01IFE,P01IF03FFEI07F01FC07FP07FFC,Q07FC007F8I07F01FC07FP01FE,,::::::::::::::::::::::::::::::::^FS
                    ^LH0,0
                            ^FO450,15^BQN,2,5,L
                    ^FDMA,{label_name}^FS
                    ^FO370,200^A0N,30,30^FD{label_name}^FS
                    ^FO30,200^A0N,40,40^FDAFTER CONV^FS
                    ^FO30,125^A0N,28,28^FDRow#{lane_id.upper()}^FS
                    ^XZ
                    """
            if product_config == 'Plastic':
                reel_name = self.get_reel_name()
                reel_row_name = f"{reel_name}_{lane_id.upper()}"
                reel_name_label = f"""
                     ^XA
                    ^FO0,0^GFA,3024,3024,27,,::::::::::::::::::::::gK01FCQ03F8,::::gK01FCP0F3F8,gK01FCO03IF8,gK01FCO07IF8,:gK01FCO0F0FF8,gK01FCO0F07F8,gK01FCO0E07F8,:gK01FCO0F07F8,gK01FCO0F8FF8,gK01FCO07IF8,O0FEI0FE001FC07F01FC07FL03IF8,O0FEI0FE001FC07F01FC07FL01JFC,O0FEI0FE001FC07F01FC07FJ0EI03FFC,O0FEI0FE001FC07F01FC07FI0FFE003FFC,O0FEI0FE001FC07F01FC07F003IF003FFC,O0FEI0FE001FC07F01FC07F007IFC03FFC,O0FEI0FE001FC07F01FC07F00JFE03FFC,O0FEI0FE001FCJ01FCJ01KF03FFC,O0FEI0FE001FCJ01FCJ03KF03F8,O0FEI0FE001FCJ01FCJ03KF83F8,O0FEI0FE001FC07F01FC07F07FC07F83F8,O0FEI0FE001FC07F01FC07F07F803FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FE3F8,::O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F07F003FC3F8,O0FEI0FE001FC07F01FC07F07F807FC3F8,O0FEI0FE001FC07F01FC07F07FE1FF83F8,O0FEI0FE001FC07F01FC07F03KF83F8,O0FEI0FE001FC07F01FC07F01KF03F8,O0FEI0FE001FC07F01FC07F01JFE03F8,O0FEI0FE001FC07F01FC07F00JFC03F8,O0FEI0FE001FC07F01FC07F003IF803F8,O0FEI0FE001FC07F01FC07F001FFE003F8,O0FE001FE001FC07F01FC07FI03F8003F8,O0FF001FE001FC07F01FC07FN03F8,O07F003FF003FC07F01FC07FN03FC,O07F803FF807F807F01FC07FN01FE,O07FE0IFC0FF807F01FC07FN01FF03,O03PF007F01FC07FO0JF8,O01PF007F01FC07FO0JFC,O01OFE007F01FC07FO07IFE,P0JFEJFC007F01FC07FO03JF,P07IF87IF8007F01FC07FO01IFE,P01IF03FFEI07F01FC07FP07FFC,Q07FC007F8I07F01FC07FP01FE,,::::::::::::::::::::::::::::::::^FS
                    ^LH0,0
                            ^FO300,15^BQN,2,5,L
                    ^FDMA,{reel_row_name}^FS
                    ^FO290,150^A0N,40,40^FD{reel_row_name}^FS
                    ^XZ
                    """
                print(f"Printing label: {reel_row_name} \n {reel_name_label}")
                if print_label(reel_name_label, self.config.get("printer_name")):
                    with open('reel_name.json', 'w') as file:
                        json.dump({'reel_name': reel_name}, file, indent=4)

            if print_label(label, self.config.get("printer_name")):
                self.app.update_widget(widget_key='output',
                                       new_value=f'Labels successfully sent to printer on {datetime.now()}',
                                       color='green')
            else:
                self.app.update_widget(widget_key='output', new_value='Failed to connect to the printer.', color='red')
            print(f"Printing label: {label_name} \n {label}")
        next_serial_number = int(converted_reels_serial_number) + 1
        self.app.update_widget(widget_key='converted_reels_serial_number', new_value=str(next_serial_number))
        label_names = f"{inlay}_{seq_assy_reel}_{lanes_ids[0].upper()}-{lanes_ids[-1].upper()}_{conv_date}_{converted_reels_serial_number}"
        upload_json_to_s3(self.client, values, label_names, 'conversion')

    def get_last_reel_name(self):
        try:
            with open('reel_name.json', 'r') as file:
                file = json.load(file)
            return file['reel_name']
        except FileNotFoundError:
            with open('reel_name.json', 'w') as file:
                json.dump({'reel_name': '0ZZZ'}, file, indent=4)
            return '9ZZZ'

    @staticmethod
    def inc36(s):
        digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        s = list(s)
        i = len(s) - 1
        carry = 1
        while i >= 0 and carry:
            v = digits.index(s[i]) + carry
            s[i] = digits[v % 36]
            carry = v // 36
            i -= 1
        if carry:
            s.insert(0, digits[carry])
        return ''.join(s)

    def get_reel_name(self):
        reel_name = self.get_last_reel_name()
        reel_name = self.inc36(reel_name)
        return reel_name




if __name__ == '__main__':
    ConversionLabelPrinter()
