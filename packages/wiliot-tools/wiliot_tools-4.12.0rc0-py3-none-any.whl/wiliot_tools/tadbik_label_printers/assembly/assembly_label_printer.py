from wiliot_api import ManufacturingClient

from wiliot_tools.tadbik_label_printers.assembly.data.default_values import empty_page, default_config
from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui
from wiliot_tools.tadbik_label_printers.label_printer_tools import *


class AssemblyLabelPrinter:
    def __init__(self, env="prod"):
        self.sensor = YoctoSensor()
        self.sensor.connect()
        self.counter = 0
        self.last_assembly_id = None
        self.history = self.read_history()
        self.config = self.read_config()
        self.client = get_manufacturing_client(env)
        self.init_widgets()
        self.app.layout.title("assembly Label Printer")
        self.events()
        self.app.add_recurrent_function(cycle_ms=1000, function=self.recurrent)
        self.load_assembly_data()
        self.app.set_parent(self)
        self.inputs_security()
        self.app.run()

    def init_widgets(self):
        main_dict = {}
        main_dict["assembly_id"] = list(self.history.keys())[::-1]
        self.last_assembly_id = main_dict["assembly_id"][0]
        main_dict["operator_name"] = ['-'] + self.config['operator_name']
        main_dict["inlay"] = ['-'] + self.config['inlay']
        main_dict["assembled_reel_width"] = ''
        main_dict["#_of_lanes_in_antenna_design"] = ['-'] + self.config['#_of_lanes_in_antenna_design']
        main_dict["assembled_reel_count"] = ['-'] + self.config['assembled_reel_count']
        main_dict.update({k: {'value': v} for k, v in main_dict.items()})
        main_dict["warning"] = {'value': '-', 'widget_type': 'label', 'options': {'fg': 'red'}, 'columnspan': 2}
        main_dict["assembled_reel_width"] = {'value': '', 'text': 'Assembled reel width (e.g. 1,1,2)'}
        main_dict['tabs'] = {}

        types = ['Placement', 'Removal']
        wafers = ['First', 'Second', 'Third']
        tabs_dict = {}
        for i, wafer in enumerate(wafers):
            for j, type in enumerate(types):
                tab_dict = {}
                tab_name = wafer + ' ' + type
                tab_dict["wafer_qr_code"] = ''

                if type == 'Removal':
                    tab_dict['wafer_dies_qty_assembled'] = ''
                tab_dict['record_time'] = ''
                tab_dict["temperature"] = ''
                tab_dict["humidity"] = ''
                tab_dict["date"] = ''
                x = str(i * 2 + j + 1) + ') '
                tabs_dict.update({x + k: {'value': v, 'tab': tab_name} for k, v in tab_dict.items()})

                tabs_dict[x + 'record_time'] = {'value': 'Record Date & Sensors', 'widget_type': 'button',
                                                'columnspan': 2,
                                                'tab': tab_name}
                tabs_dict[x + 'next'] = {'value': 'Next', 'widget_type': 'button', 'columnspan': 1,
                                         'tab': tab_name}
        main_dict['total_dies_qty_assembled'] = {'value': 0, 'disabled': True}
        main_dict['assembly_label'] = {'value': '', 'disabled': True}
        main_dict['wafers'] = {'value': '', 'disabled': True}
        main_dict['print_label'] = {'value': title_button('Print Label', 25), 'widget_type': 'button',
                                    'columnspan': 2}
        main_dict['save_and_start_new_assembly'] = {'value': 'Save & Start New assembly', 'widget_type': 'button',
                                                    'columnspan': 2}
        WiliotGui.format_label = lambda self, x: x.replace('_', ' ').capitalize() if ')' not in x else x.split(")")[1][
                                                                                                       1:].replace('_',
                                                                                                                   ' ').capitalize()
        main_dict['tabs'] = tabs_dict
        main_dict["output"] = {'value': '', 'widget_type': 'label', 'columnspan': 2}

        self.app = WiliotGuiCustomized(main_dict, full_screen=False, theme='wiliot', do_button_config=False)

    def events(self):
        for i in range(1, 7):
            self.app.add_event(
                widget_key=f'tabs_{i}) record_time',
                event_type='button',
                command=lambda i=i: self.update_date_and_sensors(i))
            self.app.add_event(
                widget_key=f'tabs_{i}) next',
                event_type='button',
                command=self.go_to_next_tab
            )
        self.app.add_event(widget_key=f'print_label', event_type='button', command=self.print_label)
        self.app.add_event(widget_key=f'save_and_start_new_assembly', event_type='button',
                           command=self.save_and_start_new_assembly)
        self.app.add_event(widget_key=f'assembly_id', event_type='<<ComboboxSelected>>', command=self.save_and_load)

    def update_date_and_sensors(self, i):
        self.app.update_widget(widget_key=f'tabs_{i}) date', new_value=get_israel_time())
        temp = self.sensor.get_temperature()
        if temp is None:
            temp = 'Not Connected'
        hum = self.sensor.get_humidity()
        if hum is None:
            hum = 'Not Connected'
        self.app.update_widget(widget_key=f'tabs_{i}) temperature', new_value=temp)
        self.app.update_widget(widget_key=f'tabs_{i}) humidity', new_value=hum)

    def go_to_next_tab(self):
        notebook = self.app.widgets_tabs['tabs']['layout']
        current_tab = notebook.index(notebook.select())
        total_tabs = notebook.index('end')

        next_tab = (current_tab + 1) % total_tabs
        notebook.select(next_tab)

    def inputs_security(self):
        dropdowns = ['assembly_id', 'operator_name', 'inlay', '#_of_lanes_in_antenna_design', 'assembled_reel_count']
        for dd in dropdowns:
            self.app.widgets[dd].config(state='readonly')

        def only_numeric_input(input_value):
            if input_value == "" or all(char.isdigit() for i, char in enumerate(input_value)):
                return True
            return False

        vcmd = (self.app.class_tk.register(only_numeric_input), '%P')
        for i in [2, 4, 6]:
            self.app.widgets[f'tabs_{i}) wafer_dies_qty_assembled'].config(validate='key', validatecommand=vcmd)

        def only_numeric_input(input_value):
            if input_value == "" or all(
                    (char.isdigit() and i % 2 == 0) or (char in (',', ',') and i % 2 == 1) for i, char in
                    enumerate(input_value)):
                return True
            return False

        vcmd = (self.app.class_tk.register(only_numeric_input), '%P')
        self.app.widgets[f'assembled_reel_width'].config(validate='key', validatecommand=vcmd)

    def check_width_lanes(self, values):
        width = values['assembled_reel_width']
        lanes = values['#_of_lanes_in_antenna_design']
        assembled_reel_count = values['assembled_reel_count']
        width = width.replace(",", ",")
        if width == '' or lanes == '-':
            self.app.update_widget(widget_key='warning', new_value='')
            return
        if width[-1] == ',':
            width = width[:-1]
        widths = [int(x) for x in width.split(',')]
        width = sum(widths)
        lanes = int(lanes)
        if width != lanes:
            self.app.update_widget(widget_key='warning',
                                   new_value=f'The sum of assembled reel widths ({width}) does not match the number of lanes ({lanes}).')
        elif assembled_reel_count != '-' and int(assembled_reel_count) != len(widths):
            self.app.update_widget(widget_key='warning',
                                   new_value=f'The number of assembled reel widths ({len(widths)}) does not match the assembled reel count ({assembled_reel_count}).')
        else:
            self.app.update_widget(widget_key='warning', new_value='')

    def sum_counts(self, values):
        sum_vals = 0
        for i in [2, 4, 6]:
            val = values.get(f'tabs_{i}) wafer_dies_qty_assembled', 0)
            try:
                val = int(val)
            except ValueError:
                val = 0
            sum_vals += val
        self.app.update_widget(widget_key=f'total_dies_qty_assembled', disabled=False)
        self.app.update_widget(widget_key=f'total_dies_qty_assembled', new_value=sum_vals, disabled=True)

    def update_assembly_label(self, values):
        assembly_id = values['assembly_id']

        inlay = values['inlay']
        if inlay == '-':
            inlay = '???'

        lanes_in_antenna_design = values['#_of_lanes_in_antenna_design']
        if lanes_in_antenna_design == '-':
            lanes_in_antenna_design = '?'

        dates = [values[f'tabs_{i}) date'] for i in range(1, 7) if values[f'tabs_{i}) date'] != '']
        if len(dates) == 0:
            end_date = None
        else:
            end_date = format_date(max(dates))
        if end_date is None:
            end_date = "????????"

        assembled_reel_count = values['assembled_reel_count']
        if assembled_reel_count == '-':
            assembled_reel_count = '?'

        assembly_label = f'{inlay}_{lanes_in_antenna_design}_{end_date}_{assembled_reel_count}'
        if '?' in assembly_label:
            run_num = '?'
        else:
            labels = set([y['assembly_label'] for x, y in self.history.items() if x != assembly_id])
            run_num = 1
            while f"{assembly_label}_{run_num}" in labels:
                run_num += 1
        assembly_label = f"{assembly_label}_{run_num}"
        self.app.update_widget(widget_key=f'assembly_label', disabled=False)
        self.app.update_widget(widget_key=f'assembly_label', new_value=assembly_label, disabled=True)

    def update_wafers(self, values):
        wafers = self.get_wafers(values)
        wafers = ", ".join(wafers)
        self.app.update_widget(widget_key=f'wafers', disabled=False)
        self.app.update_widget(widget_key=f'wafers', new_value=wafers, disabled=True)

    def recurrent(self):
        values_out = self.app.get_all_values()
        self.check_width_lanes(values_out)
        self.sum_counts(values_out)
        self.update_assembly_label(values_out)
        self.update_wafers(values_out)
        if self.counter % 10 == 9:
            self.save_history(output_message=False)

        self.counter += 1

    @staticmethod
    def read_history():
        try:
            with open(os.path.join('data', 'assembly_history.json'), 'r') as file:
                file = json.load(file)
            return file
        except FileNotFoundError:
            return {"1": {}}

    @staticmethod
    def read_config():
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
        assembly_id = str(values.get("assembly_id"))
        self.history[assembly_id] = values
        if output_message:
            print("Saved current page successfully.")

    def save_history(self, output_message=True):
        try:
            self.save_page(output_message)
            with open(os.path.join('data', 'assembly_history.json'), 'w') as file:
                json.dump(self.history, file, indent=4)
            if output_message:
                print("History saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving history: {e}")

    def load_assembly_data(self):
        assembly_id = self.app.get_all_values().get("assembly_id")
        data = self.history.get(assembly_id, {})
        for key, value in data.items():
            self.app.update_widget(widget_key=key, new_value=value)

    def reset_page(self):
        for key, value in empty_page.items():
            self.app.update_widget(widget_key=key, new_value=value)

    def save_and_start_new_assembly(self):
        self.save_history()
        last_id = list(self.history.keys())[::-1][0]
        self.reset_page()
        assembly_id = str(int(last_id) + 1)
        self.app.update_widget(widget_key=f'assembly_id', new_value=assembly_id,
                               options=[assembly_id] + list(self.history.keys())[::-1])
        self.last_assembly_id = assembly_id

    def save_and_load(self, _):
        values = self.app.get_all_values()
        assembly_id = values.get("assembly_id")
        values["assembly_id"] = self.last_assembly_id
        self.history[self.last_assembly_id] = values
        self.last_assembly_id = assembly_id
        self.load_assembly_data()



    def get_wafers(self, values):
        try:
            wafers = []
            for i in [1, 3, 5]:
                wafer = values[f'tabs_{i}) wafer_qr_code']
                if wafer == '':
                    continue
                lot = wafer.split('.')[0]
                wafer = wafer.split('_')[-1]
                if len(lot) != 9 or not int(wafer):
                    raise ValueError(f"Invalid wafer {wafer}")
                wafer = f"{lot}.{wafer}"
                wafers.append(wafer)
            return wafers
        except Exception as e:
            return ['Invalid QR Code']

    def verify_values(self, values):
        error_messages = []

        if values.get('operator_name') == '-':
            error_messages.append('Please select an operator name.')

        if values.get('inlay') == '-':
            error_messages.append('Please select an inlay.')

        if values.get('#_of_lanes_in_antenna_design') == '-':
            error_messages.append('Please select the number of lanes in antenna design.')

        if values.get('assembled_reel_count') == '-':
            error_messages.append('Please select an assembled reel count.')

        widths_str = values.get('assembled_reel_width', '').replace(',', ',')
        if not widths_str:
            error_messages.append('Please enter the assembled reel width.')
        else:
            widths_list = widths_str.strip(',').split(',')
            try:
                widths = [int(w.strip()) for w in widths_list]
            except ValueError:
                error_messages.append('Assembled reel width must be a comma-separated list of integers.')
            else:
                lanes_str = values.get('#_of_lanes_in_antenna_design')
                try:
                    lanes = int(lanes_str)
                except ValueError:
                    error_messages.append('Invalid number of lanes in antenna design.')
                else:
                    if sum(widths) != lanes:
                        error_messages.append(
                            f'The sum of assembled reel widths ({sum(widths)}) does not match the number of lanes ({lanes}).')
                    else:
                        assembled_reel_count = values.get('assembled_reel_count')
                        if assembled_reel_count != '-' and int(assembled_reel_count) != len(widths):
                            error_messages.append(
                                f'The number of assembled reel widths ({len(widths)}) does not match the assembled reel count ({assembled_reel_count}).')

                    inlay = values.get('inlay')
                    inlay_lanes = self.config['inlay_rows'].get(inlay)
                    if lanes != inlay_lanes:
                        error_messages.append(
                            f'The lanes in antenna design ({lanes}) does not match the number of lanes for the inlay {inlay} ({inlay_lanes}).')

        dates = []
        for i in range(1, 7):
            key_qr_code = f'tabs_{i}) wafer_qr_code'
            key_qty = f'tabs_{i}) wafer_dies_qty_assembled'
            key_date = f'tabs_{i}) date'
            key_temperature = f'tabs_{i}) temperature'
            key_humidity = f'tabs_{i}) humidity'

            if not values.get(key_qr_code) and i % 2 == 1 and i != 1:
                break

            if not values.get(key_qr_code):
                error_messages.append(f'Please enter wafer QR code in tab {i}.')

            if i % 2 == 0:
                if values.get(f'tabs_{i-1}) wafer_qr_code') != values.get(key_qr_code):
                    error_messages.append(f"QR codes in tab {i-1} and {i} don't match")
                qty_str = values.get(key_qty)
                if not qty_str:
                    error_messages.append(f'Please enter wafer dies quantity assembled in tab {i}.')
                else:
                    try:
                        qty = int(qty_str)
                        if qty <= 0:
                            raise ValueError
                    except ValueError:
                        error_messages.append(
                            f'Invalid wafer dies quantity assembled in tab {i}. Please enter a positive integer.')

            if not values.get(key_date):
                error_messages.append(f'Please record date and sensors in tab {i}.')
            else:
                dates.append(values.get(key_date))

            if not values.get(key_date) or not values.get(key_temperature) or not values.get(key_humidity):
                error_messages.append(f'Please record date and sensors in tab {i}.')

        wafers = self.get_wafers(values)
        if 'Invalid QR Code' in wafers:
            error_messages.append('Invalid wafer QR code(s). Please check the wafer QR codes.')

        if not wafers or wafers == ['']:
            error_messages.append('Please enter at least one valid wafer QR code.')

        if len(wafers) != len(set(wafers)):
            error_messages.append('Please make sure that wafer names are different.')

        if str(dates) != str(sorted(dates)):
            error_messages.append('Please make sure that the dates are ascending.')

        if error_messages:

            full_error_message = error_messages[0]
            self.app.update_widget(widget_key='output', new_value=full_error_message, color='red')
            return False
        else:
            return True

    def print_label(self):
        values = self.app.get_all_values()
        self.update_assembly_label(values)
        self.update_wafers(values)
        values = self.app.get_all_values()
        if not self.verify_values(values):
            return
        assembly_label = values['assembly_label']
        wafers = values['wafers'].split(", ")
        wafers = wafers + [''] * (3 - len(wafers))
        total_dies_qty_assembled = int(values.get("total_dies_qty_assembled"))
        assembled_reel_count = int(values.get("assembled_reel_count"))
        lanes_in_antenna_design = int(values.get("#_of_lanes_in_antenna_design"))
        qty_per_reel = total_dies_qty_assembled // lanes_in_antenna_design
        qr_code = f"{assembly_label}_{'_'.join(wafers)}"
        label = f"""
                     ^XA
                    ^FO0,0^GFA,3024,3024,27,,::::::::::::::::::::::gK01FCQ03F8,::::gK01FCP0F3F8,gK01FCO03IF8,gK01FCO07IF8,:gK01FCO0F0FF8,gK01FCO0F07F8,gK01FCO0E07F8,:gK01FCO0F07F8,gK01FCO0F8FF8,gK01FCO07IF8,O0FEI0FE001FC07F01FC07FL03IF8,O0FEI0FE001FC07F01FC07FL01JFC,O0FEI0FE001FC07F01FC07FJ0EI03FFC,O0FEI0FE001FC07F01FC07FI0FFE003FFC,O0FEI0FE001FC07F01FC07F003IF003FFC,O0FEI0FE001FC07F01FC07F007IFC03FFC,O0FEI0FE001FC07F01FC07F00JFE03FFC,O0FEI0FE001FCJ01FCJ01KF03FFC,O0FEI0FE001FCJ01FCJ03KF03F8,O0FEI0FE001FCJ01FCJ03KF83F8,O0FEI0FE001FC07F01FC07F07FC07F83F8,O0FEI0FE001FC07F01FC07F07F803FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FE001FE3F8,::O0FEI0FE001FC07F01FC07F0FE001FC3F8,O0FEI0FE001FC07F01FC07F0FF001FC3F8,O0FEI0FE001FC07F01FC07F07F003FC3F8,O0FEI0FE001FC07F01FC07F07F807FC3F8,O0FEI0FE001FC07F01FC07F07FE1FF83F8,O0FEI0FE001FC07F01FC07F03KF83F8,O0FEI0FE001FC07F01FC07F01KF03F8,O0FEI0FE001FC07F01FC07F01JFE03F8,O0FEI0FE001FC07F01FC07F00JFC03F8,O0FEI0FE001FC07F01FC07F003IF803F8,O0FEI0FE001FC07F01FC07F001FFE003F8,O0FE001FE001FC07F01FC07FI03F8003F8,O0FF001FE001FC07F01FC07FN03F8,O07F003FF003FC07F01FC07FN03FC,O07F803FF807F807F01FC07FN01FE,O07FE0IFC0FF807F01FC07FN01FF03,O03PF007F01FC07FO0JF8,O01PF007F01FC07FO0JFC,O01OFE007F01FC07FO07IFE,P0JFEJFC007F01FC07FO03JF,P07IF87IF8007F01FC07FO01IFE,P01IF03FFEI07F01FC07FP07FFC,Q07FC007F8I07F01FC07FP01FE,,::::::::::::::::::::::::::::::::^FS
                    ^LH0,0
                            ^FO420,15^BQN,2,5,L
                    ^FDMA,{qr_code}^FS
                    ^FO370,200^A0N,30,30^FD{assembly_label}^FS
                    ^FO30,200^A0N,40,40^FDBEFORE CONV^FS
                    ^FO30,90^A0N,28,28^FD{wafers[0]}^FS
                    ^FO30,125^A0N,28,28^FD{wafers[1]}^FS
                    ^FO30,160^A0N,28,28^FD{wafers[2]}^FS
                    ^FO230,90^A0N,28,28^FDQty Per Lane:^FS
                    ^FO230,125^A0N,28,28^FD{qty_per_reel}^FS
                    ^XZ
                    """
        for i in range(assembled_reel_count):
            if print_label(label, self.config.get("printer_name")):
                self.app.update_widget(widget_key='output',
                                       new_value=f'Labels successfully sent to printer on {datetime.now()}', color='green')
            else:
                self.app.update_widget(widget_key='output', new_value='Failed to connect to the printer.', color='red')
        upload_json_to_s3(self.client, values, assembly_label, 'assembly')


if __name__ == '__main__':
    AssemblyLabelPrinter()
