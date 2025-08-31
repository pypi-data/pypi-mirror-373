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

from wiliot_tools.test_equipment.test_equipment import YoctoSensor
from wiliot_tools.utils.wiliot_gui.wiliot_gui import *
from functools import partial


class YoctoSensorGUI:
    def __init__(self):
        self.main_sensor = self.initialize_sensor()
        self.real_values_array = []
        self.measured_values_array = []

    def initialize_sensor(self):
        try:
            sensor = YoctoSensor(logger='Light')
            return sensor
        except Exception as ee:
            popup_message('No sensor is connected')
            raise SystemExit('No sensor is connected')

    def update_light_value(self, read_gui):
        try:
            light_value = self.main_sensor.get_light()
            read_gui.update_widget(widget_key='-LIGHT-', new_value=light_value)
        except Exception as e:
            read_gui.update_widget(widget_key='-LIGHT-', new_value=f'Current Light Value: Error: {e}')

    def single_calibration(self):
        read_dict = {
            '-LIGHT-': {
                'text': '',
                'value': 'Current Light Value:',
                'widget_type': 'label',
            },
            'real_value': {
                'text': 'Enter real LUX value:',
                'value': '',
                'widget_type': 'entry',
                'options': {'size': (4, 1)},
            },
        }
        read_gui = WiliotGui(params_dict=read_dict, exit_sys_upon_cancel=False, title='Single Calibration')
        read_gui.add_recurrent_function(cycle_ms=100, function=partial(self.update_light_value, read_gui))
        values = read_gui.run()
        try:
            real_value = int(values['real_value'])
            self.main_sensor.calibration_light_point(real_value)
        except Exception as e:
            popup_message('Invalid real LUX value')

    def collect_calibration_points(self):
        calibration_dict = {
            'add_value_row': [
                {'real_value': {
                    'text': 'Enter real LUX value:',
                    'value': '',
                    'widget_type': 'entry',
                }},
                {
                    'add_button': {
                        'text': 'Add',
                        'widget_type': 'button',
                    },
                }
            ],
        }

        def on_add_calib_button():
            calib_values = calibration_gui.get_all_values()
            real_value = calib_values['add_value_row_real_value']
            if real_value:
                try:
                    real_value = float(real_value)
                    measured_value = self.main_sensor.get_light()
                    self.real_values_array.append(real_value)
                    self.measured_values_array.append(measured_value)
                    popup_message(f'Added: Real LUX: {real_value}, Measured LUX: {measured_value}')
                    if len(self.real_values_array) >= 2:
                        calibration_gui.update_widget(widget_key='submit_button', disabled=False)
                except ValueError:
                    popup_message('Invalid real LUX value')

        def on_submit_button():
            self.main_sensor.calibration_points(self.real_values_array, self.measured_values_array)
            popup_message('Calibration submitted')

        calibration_gui = WiliotGui(params_dict=calibration_dict, exit_sys_upon_cancel=False, do_button_config=False,
                                    title='Light Sensor Calibration')
        calibration_gui.button_configs(submit_command=on_submit_button)
        calibration_gui.add_event(widget_key='add_value_row_add_button', command=on_add_calib_button,
                                  event_type='button')

    def read_sensor_data(self):

        read_dict = {
            '-LIGHT-': {
                'text': 'Current Light Value:',
                'value': '',
                'widget_type': 'label',
            },
            'close': {
                'text': 'Close',
                'widget_type': 'button',
            },
        }

        read_gui = WiliotGui(params_dict=read_dict, do_button_config=False, exit_sys_upon_cancel=False,
                             title='Read Sensor Data')
        read_gui.add_recurrent_function(cycle_ms=100, function=partial(self.update_light_value, read_gui))
        read_gui.add_event(widget_key='close', command=read_gui.on_cancel, event_type='button')

    def run(self):
        params_dict = {
            'calibrate_points': {
                'text': 'Calibrate Points',
                'widget_type': 'button',
            },
            'calib_and_read': [
                {'calibration': {
                    'text': 'Calibration',
                    'widget_type': 'button',
                }},
                {'read_data': {
                    'text': 'Read Data',
                    'widget_type': 'button',
                }},
            ],
            'quit': {
                'text': 'Quit',
                'widget_type': 'button',
            },
        }

        main_gui = WiliotGui(params_dict=params_dict, do_button_config=False, title='Light Sensor Calibration')
        main_gui.add_event(widget_key='calibrate_points', command=self.collect_calibration_points, event_type='button')
        main_gui.add_event(widget_key='calib_and_read_calibration', command=self.single_calibration,
                           event_type='button')
        main_gui.add_event(widget_key='calib_and_read_read_data', command=self.read_sensor_data, event_type='button')
        main_gui.add_event(widget_key='quit', command=main_gui.on_close, event_type='button')
        main_gui.run()


# Run the GUI
if __name__ == '__main__':
    gui = YoctoSensorGUI()
    gui.run()
