import json
import os
import time
try:
    import tkinter as tk
except Exception as e:
    print(f'could not import tkinter: {e}')
from datetime import datetime

from wiliot_tools.tadbik_label_printers.offline.data.default_values import default_config
from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui
from wiliot_tools.tadbik_label_printers.label_printer_tools import *


class OfflineLabelPrinter:
    def __init__(self, env="prod"):
        self.counter = 0
        self.history = self.read_history()
        self.config = self.read_config()
        self.client = get_manufacturing_client(env)
        self.init_widgets()
        self.app.layout.title("Offline Label Printer")
        self.events()
        self.app.add_recurrent_function(cycle_ms=100, function=self.recurrent)
        self.load_data()
        self.app.set_parent(self)
        self.inputs_security()
        self.app.run()

    def init_widgets(self):
        main_dict = {}
        main_dict["auto_focus"] = False
        main_dict["operator_name"] = ['-'] + self.config.get('operator_name', [])
        main_dict["inlay"] = ['-'] + self.config.get('inlay', [])
        main_dict["converted_reel_name"] = ''
        main_dict["sample_test_first_ext_id"] = {'value': '', 'text': 'Sample Test First Ext. ID#'}
        main_dict["sample_test_last_ext_id"] = {'value': '', 'text': 'Sample Test Last Ext. ID# '}
        main_dict["fg_reel_first_ext_id"] = {'value': '0000', 'text': 'FG Reel First Ext. ID#'}
        main_dict["fg_reel_last_ext_id"] = {'value': '', 'text': 'FG Reel Last Ext. ID#'}
        main_dict["offline_test_date"] = ''
        main_dict = {k: {'value': v} if not isinstance(v, dict) else v for k, v in main_dict.items()}
        main_dict["offline_test_date"] = [
            {"input": {'value': '', 'widget_type': 'entry', 'text': 'Offline Test Date'}},
            {"record": {'value': 'Record Date', 'widget_type': 'button'}}
        ]
        main_dict['label_name'] = {'value': '', 'disabled': True}
        main_dict['sample_test_range'] = {'value': '', 'disabled': True}
        main_dict['fg_reel_range'] = {'value': '', 'disabled': True}
        main_dict["print_label"] = {'value': title_button('Print Label', 36), 'widget_type': 'button', 'columnspan': 3}
        main_dict["output"] = {'value': '', 'widget_type': 'label', 'options': {'fg': 'red'}, 'columnspan': 3}
        self.app = WiliotGuiCustomized(main_dict, full_screen=False, theme='wiliot', do_button_config=False)

    def reset_page(self):
        self.history[get_israel_time()] = {}
        self.app.update_widget(widget_key='inlay', new_value='-')
        self.app.update_widget(widget_key='converted_reel_name', new_value='')
        self.app.update_widget(widget_key='sample_test_first_ext_id', new_value='')
        self.app.update_widget(widget_key='sample_test_last_ext_id', new_value='')
        self.app.update_widget(widget_key='fg_reel_first_ext_id', new_value='0000')
        self.app.update_widget(widget_key='fg_reel_last_ext_id', new_value='')
        self.app.update_widget(widget_key='offline_test_date_input', new_value='')

        self.save_history()

    def events(self):
        self.app.add_event(widget_key='offline_test_date_record', event_type='button', command=self.record_test_date)
        self.app.add_event(widget_key='print_label', event_type='button', command=self.print_label)

    def record_test_date(self):
        current_date = get_israel_time()
        self.app.update_widget(widget_key='offline_test_date_input', new_value=current_date)

    def inputs_security(self):
        dropdowns = ['operator_name', 'inlay']
        for dd in dropdowns:
            self.app.widgets[dd].config(state='readonly')

    def update_outputs(self, values):
        separator = self.config.get('separator', 'T')
        offline_test_date = format_date(values.get('offline_test_date_input')) or '????????'
        converted_reel_name = values.get('converted_reel_name', '')
        lane_id = converted_reel_name.split('_')[2] if len(converted_reel_name.split('_')) >= 3 else '?'

        def get_ids(ext_id):
            if ext_id == '':
                return '???', '????'
            parts = ext_id.split(separator)
            if len(parts) == 1:
                number = parts[0]
                reel_id = '???'
            elif len(parts) == 2:
                reel_id, number = parts
            else:
                reel_id, number = '???', '????'
            if not (len(number) == 4 and all([char.isdigit() for char in number])):
                number = '????'
            return reel_id, number

        reel_id, sample_test_first = get_ids(values.get('sample_test_first_ext_id'))
        _, sample_test_last = get_ids(values.get('sample_test_last_ext_id'))
        _, fg_reel_first = get_ids(values.get('fg_reel_first_ext_id'))
        _, fg_reel_last = get_ids(values.get('fg_reel_last_ext_id'))

        label_name = f"{reel_id}_{lane_id}_{offline_test_date}"
        sample_test_range = f"{sample_test_first}-{sample_test_last}"
        fg_reel_range = f"{fg_reel_first}-{fg_reel_last}"

        for key, value in [('label_name', label_name), ('sample_test_range', sample_test_range),
                           ('fg_reel_range', fg_reel_range)]:
            if values.get(key) != value:
                self.app.update_widget(widget_key=key, new_value=value, disabled=True)

        label_name = f"{reel_id}_{lane_id}_{offline_test_date}"
        sample_test_range = f"{sample_test_first}-{sample_test_last}"
        fg_reel_range = f"{fg_reel_first}-{fg_reel_last}"

        self.app.update_widget(widget_key=f'label_name', disabled=False)
        self.app.update_widget(widget_key=f'label_name', new_value=label_name, disabled=True)

        self.app.update_widget(widget_key=f'sample_test_range', disabled=False)
        self.app.update_widget(widget_key=f'sample_test_range', new_value=sample_test_range, disabled=True)

        self.app.update_widget(widget_key=f'fg_reel_range', disabled=False)
        self.app.update_widget(widget_key=f'fg_reel_range', new_value=fg_reel_range, disabled=True)

    def get_current_focus(self):
        try:
            current_widget = self.app.layout.focus_get()
            for key, widget in self.app.widgets.items():
                if widget == current_widget:
                    return key
            return
        except Exception:
            return

    def set_focus_to_widget(self, widget_key):
        if widget_key in self.app.widgets:
            self.app.widgets[widget_key].focus_set()

    def auto_focus(self, values):
        if not values.get('auto_focus'):
            return
        order = ['converted_reel_name', 'sample_test_first_ext_id', 'sample_test_last_ext_id', 'fg_reel_last_ext_id']
        focused_widget = self.get_current_focus()
        if focused_widget not in order[:-1]:
            return
        if self.config[focused_widget+'_length'] != len(values.get(focused_widget)):
            return
        self.set_focus_to_widget(order[order.index(focused_widget)+1])

    def recurrent(self):
        values = self.app.get_all_values()
        self.auto_focus(values)
        self.update_outputs(values)
        if self.counter % 100 == 99:
            self.save_history(output_message=False)
        self.counter += 1

    def read_history(self):
        try:
            with open(os.path.join('data', 'offline_history.json'), 'r') as file:
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
            with open(os.path.join('data', 'offline_history.json'), 'w') as file:
                json.dump(self.history, file, indent=4)
            if output_message:
                print("History saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving history: {e}")

    def load_data(self):
        batch_id = max(self.history.keys())
        data = self.history.get(batch_id, {})
        for key, value in data.items():
            self.app.update_widget(widget_key=key, new_value=value)

    def verify_values(self, values):
        error_messages = []
        if values.get('operator_name') == '-':
            error_messages.append('Please select an operator name.')
        if values.get('inlay') == '-':
            error_messages.append('Please select an inlay.')
        converted_reel_name = values.get('converted_reel_name')
        if not converted_reel_name:
            error_messages.append('Please scan the Converted Reel Name.')
        sample_test_first_ext_id = values.get('sample_test_first_ext_id')
        if not sample_test_first_ext_id:
            error_messages.append('Please scan the Sample Test First Ext. ID#.')
        sample_test_last_ext_id = values.get('sample_test_last_ext_id')
        if not sample_test_last_ext_id:
            error_messages.append('Please scan the Sample Test Last Ext. ID#.')
        fg_reel_first_ext_id = values.get('fg_reel_first_ext_id')
        if not fg_reel_first_ext_id:
            error_messages.append('Please enter the FG Reel First Ext. ID#.')
        fg_reel_last_ext_id = values.get('fg_reel_last_ext_id')
        offline_test_date = format_date(values.get('offline_test_date_input'))
        if offline_test_date is None:
            error_messages.append('Offline Test Date is not a valid date format.')
        if not fg_reel_last_ext_id:
            error_messages.append('Please scan the FG Reel Last Ext. ID#.')
        if '?' in values.get('label_name'):
            error_messages.append('Invalid label name.')
        if '?' in values.get('sample_test_range'):
            error_messages.append('Invalid sample test range.')
        elif int(values.get('sample_test_range').split('-')[0]) >= int(values.get('sample_test_range').split('-')[1]):
            error_messages.append('sample test first is bigger/equal to sample test last.')
        if '?' in values.get('fg_reel_range'):
            error_messages.append('Invalid fg reel range.')
        elif int(values.get('fg_reel_range').split('-')[0]) >= int(values.get('fg_reel_range').split('-')[1]):
            error_messages.append('fg reel first is bigger/equal to sample test last.')
        label_name = values.get('label_name').split("_")
        if not ('A' <= label_name[1] <= 'F' and len(label_name[1]) == 1):
            error_messages.append('Invalid Lane ID.')
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
        inlay = values.get('inlay')
        label_name = values.get('label_name')
        sample_test_range = values.get('sample_test_range')
        fg_reel_range = values.get('fg_reel_range')
        label_ranges = ['AFTER TEST', f'Ext.ID {sample_test_range}', f'Ext.ID {fg_reel_range}']
        for label_range in label_ranges:
            label = f"""
                     ^XA
                    ^FO0,0^GFA,3024,3024,27,,::::::::::::::::::::::gK01FCQ03F8,::::gK01FCP0F3F8,gK01FCO03IF8,gK01FCO07IF8,:gK01FCO0F0FF8,gK01FCO0F07F8,gK01FCO0E07F8,:gK01FCO0F07F8,gK01FCO0F8FF8,gK01FCO07IF8,O0FEI0FE001FC07F01FC07FL03IF8,O0FEI0FE001FC07F01FC07FL01JFC,O0FEI0FE001FC07F01FC07FJ0EI03FFC,O0FEI0FE001FC07F01FC07FI0FFE003FFC,O0FEI0FE001FC07F01FC07F003IF003FFC,O0FEI0FE001FC07F01FC07F007IFC03FFC,O0FEI0FE001FC07F01FC07F00JFE03FFC,O0FEI0FE001FCJ01FCJ01KF03FFC,O0FEI0FE001FCJ01FCJ03KF03F8,O0FEI0FE001FCJ01FCJ03KF83F8,O0FEI0FE001FC07F01FC07F07FC07F83F8,O0FEI0FE001FC07F01FC07F07F803FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FE3F8,::O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F07F003FC3F8,O0FEI0FE001FC07F01FC07F07F807FC3F8,O0FEI0FE001FC07F01FC07F07FE1FF83F8,O0FEI0FE001FC07F01FC07F03KF83F8,O0FEI0FE001FC07F01FC07F01KF03F8,O0FEI0FE001FC07F01FC07F01JFE03F8,O0FEI0FE001FC07F01FC07F00JFC03F8,O0FEI0FE001FC07F01FC07F003IF803F8,O0FEI0FE001FC07F01FC07F001FFE003F8,O0FE001FE001FC07F01FC07FI03F8003F8,O0FF001FE001FC07F01FC07FN03F8,O07F003FF003FC07F01FC07FN03FC,O07F803FF807F807F01FC07FN01FE,O07FE0IFC0FF807F01FC07FN01FF03,O03PF007F01FC07FO0JF8,O01PF007F01FC07FO0JFC,O01OFE007F01FC07FO07IFE,P0JFEJFC007F01FC07FO03JF,P07IF87IF8007F01FC07FO01IFE,P01IF03FFEI07F01FC07FP07FFC,Q07FC007F8I07F01FC07FP01FE,,::::::::::::::::::::::::::::::::^FS
                    ^LH0,0
                            ^FO420,10^BQN,2,5,L
                    ^FDMA,{label_name}^FS
                    ^FO370,140^A0N,30,30^FD{label_name}^FS
                    ^FO30,200^A0N,35,35^FD{label_range}^FS
                    ^FO30,125^A0N,35,35^FDInlay {inlay}^FS
                    
                    ^FO330,190^GFA,294,294,7,JF800FFC,JF807IF8,JF01JFE,IFE07KF8,IFC0LFC,FI01FE003FE,FI03F8I07F,FI07FJ03F8,FI0FCK0FC,F001F807F8078,F001F01FFE03,F003F03IF,F003E0JF8,F007C0FF7FC,F007C1F807C,F007C3F0038,F00783E,F00F87C,:JF87C,JF878,:JF87C,F00F87C,:F00783E,F007C3F0038,F007C1F807C,F007C0FF7FC,F003E0JF8,F003F03IF,F001F01FFE03,F001F807F8078,FI0FCK0FC,FI07FJ03F8,FI03F8I07F,FI01FE003FE,FJ0LFC,FJ07KF8,EJ01JFE,CK07IF8,8L0FFC,^FS
                    ^FO385,190^A0N,15,15^FDU.S FCC ID: 2AXVQ-WILIOT3^FS
                    ^FO385,205^A0N,15,15^FDCanada FCC ID: 26623-WILIOT3^FS
                    ^FO385,220^A0N,11,11^FDWiliot GEN3 Hyper-thin Bluetooth IoT edge^FS
                    ^XZ
                    """
            print(f"Printing label: {label_name} \n {label}")
            if print_label(label, self.config.get("printer_name")):
                self.app.update_widget(widget_key='output',
                                       new_value=f'Label successfully sent to printer on {datetime.now()}', color='green')
                self.reset_page()

            else:
                self.app.update_widget(widget_key='output', new_value='Failed to connect to the printer.', color='red')
        upload_json_to_s3(self.client, values, label_name, 'after-test')


if __name__ == '__main__':
    OfflineLabelPrinter()
