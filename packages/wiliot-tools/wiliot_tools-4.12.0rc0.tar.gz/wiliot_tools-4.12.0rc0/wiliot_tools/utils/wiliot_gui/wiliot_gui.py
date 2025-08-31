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

try:
    import json
    import os
    import sys
    import time
    import tkinter as tk
    from tkinter import ttk, filedialog
    import re
    from ttkbootstrap.widgets import Button
    from ttkbootstrap import Style
    from wiliot_tools.utils.wiliot_gui.theme.setup_theme import setup_theme
    from PIL import Image, ImageTk
except Exception as e:
    print(f'could not import WiliotGUI imports: {e}')


MAC_SCREEN_RATIO = 0.875
FONT_TXT = ("Gudea", 12)
FONT_TXT_WARNING = ("Gudea", 12, "bold")
FONT_BUTTONS = ("Gudea", 16, "bold")


def popup_message(msg, logger=None, title='Error', font=("Helvetica", 14, 'bold'), log='info', bg=None, tk_frame=None):
    """
    Displays a popup message to the user.

    Args:
        msg (str): The message to be displayed in the popup.
        logger (object, optional): A logger object to log the message. Defaults to None.
        title (str, optional): The title of the popup window. Defaults to 'Error'.
        font (tuple, optional): The font to be used in the popup message. Defaults to ("Helvetica", 14, 'bold').
        log (str, optional): The log level to use when logging the message. Defaults to 'info'.
        bg (str, optional): The background color of the popup window. Defaults to None.
        tk_frame (object, optional): The parent Tkinter frame to use for the popup. Defaults to None.

    Returns:
        None :(
    """

    if tk_frame and tk_frame.winfo_exists():
        popup = tk.Toplevel(tk_frame)
    else:
        popup = tk.Tk()
    popup.wm_title(title)
    if bg is not None:
        popup.configure(bg=bg)
    if logger:
        getattr(logger, log)(f'{title} - {msg}')

    def popup_exit():
        popup.quit()
        popup.destroy()

    label = tk.Label(popup, text=msg, font=font)
    label.pack(side="top", fill="x", padx=10, pady=10)
    b1 = Button(popup, text="Okay", command=popup_exit)
    b1.pack(padx=10, pady=10)
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = int((popup.winfo_screenwidth() / 2) - (width / 2))
    y = int((popup.winfo_screenheight() / 2) - (height / 2))
    popup.geometry(f"{width}x{height}+{x}+{y}")
    popup.protocol("WM_DELETE_WINDOW", popup_exit)
    popup.mainloop()


class WiliotGui(object):
    try:
        class_tk = tk.Tk()
        class_style = Style()
    except Exception as e:
        print(f'could not init WiliotGui due to: {e}')
        class_tk = None
        class_style = None

    def __init__(self, params_dict=None, params_path=None, assets_path=None, parent=None, do_gui_init=True,
                 do_button_config=True, exit_sys_upon_cancel=True, full_screen=False, theme='wiliot',
                 width_offset=100, height_offset=100, disable_all_children_windows=True, screen_ratio=None,
                 title="Wiliot GUI"):

        """
        :param params_dict: dictionary, each key represent a different parameter,
                            each value is a dictionary in itself with the following format:
                            'value': the param default value, auto bool -> create checkbox, str -> create entry,
                            list/tuple -> create combobox,
                            'text': optional, if specified will be the widget label otherwise the key will be used
                            'widget_type': if specified will be the type of widget to create,
                            currently only supports file_input
        :type params_dict: dict
        :param params_path: json with the above param dict, see param_dict description
        :type params_path: str
        :param do_gui_init
        :type do_gui_init bool
        :param do_button_config
        :type do_button_config bool
        :param exit_sys_upon_cancel if True, the gui will call system exit to stop the app
        :type exit_sys_upon_cancel bool
        """
        if not assets_path:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_path = os.path.join(script_dir, 'assets')

        # minimize the main tk which stays open the whole app runtime
        WiliotGui.class_tk.geometry('0x0')
        WiliotGui.class_tk.wm_state('iconic')
        self.img_ref = None  # do not delete this variable, uses as image pointer
        self.values = None
        self.cancel_event = False
        self.sys_cancel = exit_sys_upon_cancel
        self.parent = parent
        self.disable_all_children_windows = disable_all_children_windows
        if parent is not None and disable_all_children_windows:
            self.update_all_win_children_state(state='disable')

        if params_path:
            try:
                with open(params_path, 'r') as file:
                    self.params_dict = json.load(file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Error: The file {params_path} was not found.")
            except json.JSONDecodeError:
                raise json.JSONDecodeError(f"Error: The file {params_path} could not be decoded as JSON.",
                                           doc=params_path, pos=0)
        elif params_dict:
            self.params_dict = params_dict
        else:
            self.params_dict = {}
        self.assets_path = assets_path
        self.layout = tk.Toplevel(WiliotGui.class_tk) if parent is None else tk.Toplevel(parent)
        self.last_resize_time = time.time()
        self.debounce_delay = 0.01
        self.widgets = {}
        self.widgets_vals = {}
        self.widgets_groups = {}
        self.widgets_tabs = {}
        self.style = WiliotGui.class_style
        self.logo_photo, self.logo_label = setup_theme(style=self.style, layout=self.layout, theme_name=theme)
        self.theme_name = theme
        self.width_offset = width_offset
        self.height_offset = height_offset
        self.title = title

        if do_gui_init:
            self.initialize_gui(full_screen=full_screen, screen_ratio=screen_ratio)

        if do_button_config:
            self.button_configs()

    def update_geometry(self):
        screen_w = self.layout.winfo_screenwidth()
        screen_h = self.layout.winfo_screenheight()
        self.layout.update_idletasks()
        max_col, _ = self.layout.grid_size()
        self.logo_label.grid(columnspan=max_col)
        width = self.layout.winfo_width() + self.width_offset
        height = self.layout.winfo_height() + self.height_offset
        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))
        self.layout.geometry(f"{width}x{height}+{x}+{y}")

    def apply_screen_ratio(self, screen_ratio=1.0):
        screen_width = int(screen_ratio * self.layout.winfo_screenwidth())
        screen_height = int(screen_ratio * self.layout.winfo_screenheight())
        self.layout.geometry(f"{screen_width}x{screen_height}+0+0")

    def initialize_gui(self, full_screen=False, screen_ratio=None):
        """
        Initializes the GUI by setting up the window, logo, buttons and widgets.

        This function...functions as a simple way to set up the GUI by calling the `setup_window`, `setup_logo`,
        and `create_widgets` methods.
        It also binds the `resize_bg_image` method to the `<Configure>` event of the layout.

        Parameters:
            self : The instance of the WiliotGui class.
            full_screen: if True, opens the gui in full screen

        Returns:
            None
        """
        self.setup_window(full_screen=full_screen, screen_ratio=screen_ratio)
        self.layout.protocol("WM_DELETE_WINDOW", self.on_close)
        if self.parent is not None and self.disable_all_children_windows:
            self.layout.attributes('-topmost', True)  # pop window up
            self.layout.attributes('-topmost', False)  # allow user to move wind if needed

    def setup_window(self, full_screen=False, screen_ratio=None):
        """
        Sets up the window for the GUI based on the number of parameters in the `params_dict` attribute.

        Args:
            full_screen (bool): if True GUI will be full screen mode
        Returns:
            None
        """
        self.layout.title(self.title)
        if full_screen:
            if sys.platform != 'darwin':
                self.layout.state('zoomed')
            else:
                self.apply_screen_ratio(screen_ratio=MAC_SCREEN_RATIO)
        elif screen_ratio:
            self.apply_screen_ratio(screen_ratio=screen_ratio)

        # Make the app responsive
        for index in range(20):
            self.layout.columnconfigure(index=index, weight=1)
            self.layout.rowconfigure(index=index, weight=1)

        if self.parent is None:
            font_txt = FONT_TXT_WARNING if self.style.theme_use() == 'warning' else FONT_TXT
            self.layout.option_add("*font", font_txt)
        self.create_widgets()
        self.update_geometry()

    def create_widgets(self):
        """
        A function that creates widgets based on the params_dict attribute.

        This function iterates over the key-value pairs in the given dictionary.
        For each key-value pair, it performs the following steps:

        1. Formats the key using the `format_label` method.
        2. Calculates the row and column for the widget based on the current row and column.
        3. Checks the type of the value:
            - If the value is a boolean, it adds a checkbox widget using the `add_widget` method.
            - If the value is a list, it adds a combobox widget using the `add_widget` method.
            - For any other type, it adds an entry widget using the `add_widget` method.
        4. Increments the current row and column based on the maximum number of items per column.

        The function uses the following parameters:
        - `self`: The instance of the class that contains the function.
        """
        start_row = 1  # Adjust this value to position widgets below the logo
        current_row = start_row
        current_column = 0

        new_keys = {}
        for key, widget_dict in self.params_dict.items():
            if isinstance(widget_dict, dict) and all(isinstance(v, dict) for v in widget_dict.values()):
                # If the value is a nested dictionary, place all elements in the same row
                for index, (sub_key, sub_widget_dict) in enumerate(widget_dict.items()):
                    text_label = sub_widget_dict['text'] if 'text' in sub_widget_dict.keys() else self.format_label(
                        sub_key)
                    widget_key = f"{key}_{sub_key}"  # Ensures unique keys for sub-widgets
                    self.add_widget(widget_type=sub_widget_dict.get('widget_type'),
                                    label_text=text_label,
                                    options=sub_widget_dict.get('options'),
                                    default_value=sub_widget_dict.get('value', ''),
                                    widget_key=widget_key,
                                    widget_group=sub_widget_dict.get('group'),
                                    widget_tab={'name': key, 'tab': sub_widget_dict.get('tab')},
                                    columnspan=sub_widget_dict.get('columnspan', 1),
                                    rowspan=sub_widget_dict.get('rowspan', 1),
                                    row=current_row, column=current_column)
                    current_row += 1
                    new_keys[widget_key] = {'widget_type': sub_widget_dict.get('widget_type')}

            elif isinstance(widget_dict, list):
                for widget_row_dict in widget_dict:
                    sub_key = list(widget_row_dict.keys())[0]
                    sub_widget_dict = widget_row_dict[sub_key]
                    text_label = sub_widget_dict['text'] if 'text' in sub_widget_dict.keys() else self.format_label(
                        sub_key)
                    widget_key = f"{key}_{sub_key}"  # Ensure unique keys for sub-widgets
                    self.add_widget(widget_type=sub_widget_dict.get('widget_type'),
                                    label_text=text_label,
                                    options=sub_widget_dict.get('options'),
                                    default_value=sub_widget_dict.get('value', ''),
                                    widget_key=widget_key,
                                    widget_group=sub_widget_dict.get('group'),
                                    columnspan=sub_widget_dict.get('columnspan', 1),
                                    rowspan=sub_widget_dict.get('rowspan', 1),
                                    row=current_row, column=current_column)
                    current_column += 1 * (2 if sub_widget_dict.get('widget_type') not in ['label', 'button'] else 1)

                    new_keys[widget_key] = {'widget_type': sub_widget_dict.get('widget_type')}

                # Reset column after processing the list
                current_column = 0
                current_row += 1

            else:
                text_label = widget_dict['text'] if 'text' in widget_dict.keys() else self.format_label(key)
                widget_key = key  # Ensure the correct key is used

                self.add_widget(widget_type=widget_dict.get('widget_type'),
                                label_text=text_label,
                                options=widget_dict.get('options'),
                                default_value=widget_dict.get('value', ''),
                                widget_key=widget_key,
                                widget_group=widget_dict.get('group'),
                                columnspan=widget_dict.get('columnspan', 1),
                                rowspan=widget_dict.get('rowspan', 1),
                                row=current_row, column=current_column)

                current_row += 1

        self.params_dict = {**self.params_dict, **new_keys}

    @staticmethod
    def format_label(label):
        return label.replace('_', ' ').capitalize()

    def continue_script(self):
        pass

    def on_submit(self):
        """
        Handles the event when the submit button is clicked.

        This function is called when the submit button is clicked in the GUI.
        It updates the `params_dict` attribute with the current values of the widgets
        and then destroys the layout of the GUI.

        Parameters:
            self (WiliotGui): The instance of the WiliotGui class.
        """

        print("Submitted")
        self.submit_event = True
        for key, widget_var in self.params_dict.items():
            widget = self.widgets.get(key)
            if widget:
                if isinstance(widget, tk.BooleanVar):
                    self.params_dict[key]['output'] = widget.get()
                elif isinstance(widget, tk.StringVar):
                    self.params_dict[key]['output'] = widget.get()
        self.layout.quit()
        self.layout.destroy()

    def on_close(self):
        print("Window closed by user")
        self.exit_gui()

    def exit_gui(self):
        self.cancel_event = True
        self.layout.quit()
        self.layout.destroy()
        if self.sys_cancel:
            sys.exit()

    def exit_app(self):
        if self.parent is not None:
            self.layout.destroy()
        WiliotGui.class_tk.destroy()

    def on_cancel(self):
        """
        Cancels the action and destroys the layout of the GUI.
        Parameters:
            self (WiliotGui): The instance of the WiliotGui class.
        """
        print("Action cancelled by user")
        self.exit_gui()

    def get_cancel_event(self):
        return self.cancel_event

    def set_button_command(self, button_key, command):
        """
        Sets the command to be executed when a button is clicked.

        Args:
            button_key (str): The key of the button widget.
            command (callable): The function to be called when the button is clicked.

        Returns:
            None
        """

        if button_key in self.widgets:
            button_widget = self.widgets[button_key]
            if isinstance(button_widget, Button):
                button_widget.config(command=command)

    def button_configs(self, submit_button_text="SUBMIT", submit_command=None,
                       cancel_button_text='CANCEL', cancel_command=None):
        """
        Configures the buttons for the GUI layout with the specified submit and cancel commands,
        font style, and font size.

        Parameters:
            self (WiliotGui): The instance of the WiliotGui class.
            submit_button_text (str): The string presented on the button
            submit_command (function): The command to execute on submit.
            cancel_button_text (str): The string presented on the button
            cancel_command (function): The command to execute on cancel.
        """
        if submit_command is None:
            submit_command = self.on_submit
        if cancel_command is None:
            cancel_command = self.on_cancel
        max_col, max_row = self.layout.grid_size()
        submit_button = Button(self.layout, text=submit_button_text, command=submit_command,
                               style="custom.Accent.TButton")
        submit_button.grid(row=max_row, column=0, padx=0, pady=0, sticky="w")

        cancel_button = Button(self.layout, text=cancel_button_text, command=cancel_command,
                               style="custom.Accent.TButton")
        cancel_button.grid(row=max_row, column=max_col, padx=0, pady=0, sticky="e")
        self.update_geometry()

    def run(self, save_path=''):
        self.layout.mainloop()
        if self.parent is not None and self.disable_all_children_windows:
            self.update_all_win_children_state(state='enable')
            self.parent.attributes('-topmost', True)  # pop window up
            self.parent.attributes('-topmost', False)  # allow user to move wind if needed
        values = self.get_all_values() if not self.cancel_event else None
        if values and save_path:
            with open(save_path, 'w') as f:
                json.dump(values, f)
        return values

    def add_widget(self, widget_type, label_text, options=None, default_value=None, row=0, column=0, padx=10, pady=5,
                   widget_key=None, widget_group=None, widget_tab=None, columnspan=1, rowspan=1):
        """
        Adds a widget to the layout based on the specified widget type.

        Parameters:
            widget_type (str): The type of widget to add. Valid options are:
                - 'checkbox': A checkbox widget that allows the user to select or deselect a value.
                - 'combobox': A combobox widget that displays a dropdown list of options and allows the user to
                              select one.
                - 'entry': A text entry widget that allows the user to enter text.
                - 'file_input': A file input widget that is essentially an entry widget with an additional
                                button to browse and select a file.
                - 'button': A button widget that can be clicked to perform an action.
                - 'label': A label widget that displays text.
                - 'canvas': A canvas widget that can be used to draw graphics.
            label_text (str): The text to display as the label for the widget.
            options (list, optional): A list of options for the widget. Only applicable for 'combobox' widget type.
            default_value (Any, optional): The default value for the widget.
            row (int, optional): The row position for the widget.
            column (int, optional): The column position for the widget.
            padx (int, optional): The horizontal padding for the widget.
            pady (int, optional): The vertical padding for the widget.
            widget_key (str, optional): The key to use for the widget in the self.widgets dictionary.
            widget_group (str, optional): The group to use for the widget. If specified, the widget will be placed
                                          inside a LabelFrame with the specified group name.
            widget_tab (dict, optional): The tab to use for the widget. If specified, the widget will be placed
                                         inside a tab with the specified tab name.
            columnspan (int, optional): The number of columns to stretch the widget upon.
            rowspan (int, optional): The number of rows to stretch the widget upon.

        Returns:
            The widget variable associated with the added widget.

        Raises:
            Exception: If an unsupported widget type is specified.
        """
        var = None
        if widget_type is None:
            if isinstance(default_value, bool):
                widget_type = 'checkbox'
            elif isinstance(default_value, list) or isinstance(default_value, tuple):
                widget_type = 'combobox'
            else:
                widget_type = 'entry'

        if widget_tab is not None:
            if widget_tab['name'] not in self.widgets_tabs.keys():
                notebook = ttk.Notebook(self.layout)
                notebook.grid(row=row, column=column, sticky="nsew", columnspan=3, padx=padx)

                new_tab = ttk.Frame(notebook)
                for index in range(10):
                    new_tab.columnconfigure(index=index, weight=1)
                    new_tab.rowconfigure(index=index, weight=1)
                notebook.add(new_tab, text=widget_tab['tab'])

                self.widgets_tabs[widget_tab['name']] = {'layout': notebook,
                                                         'tab': {
                                                             widget_tab['tab']: {'layout': new_tab,
                                                                                 'row': 0}}}
                row = 0
                layout = new_tab
            elif widget_tab['tab'] not in self.widgets_tabs[widget_tab['name']]['tab'].keys():
                notebook = self.widgets_tabs[widget_tab['name']]['layout']
                new_tab = ttk.Frame(notebook)
                for index in range(10):
                    new_tab.columnconfigure(index=index, weight=1)
                    new_tab.rowconfigure(index=index, weight=1)
                notebook.add(new_tab, text=widget_tab['tab'])
                self.widgets_tabs[widget_tab['name']]['tab'][widget_tab['tab']] = {'layout': new_tab, 'row': 0}
                row = 0
                layout = new_tab
            else:
                layout = self.widgets_tabs[widget_tab['name']]['tab'][widget_tab['tab']]['layout']
                row = self.widgets_tabs[widget_tab['name']]['tab'][widget_tab['tab']]['row']
                row += 1
                self.widgets_tabs[widget_tab['name']]['tab'][widget_tab['tab']]['row'] = row
        else:
            layout = self.layout

        if widget_group is not None:
            if widget_group not in self.widgets_groups.keys():
                layout = tk.LabelFrame(layout, text=widget_group)
                layout.grid(row=row, column=column, columnspan=2, padx=(20, 10), pady=(20, 10), sticky="nsew")
                self.widgets_groups[widget_group] = {'layout': layout, 'row': 0}
                row = 0
            else:
                layout = self.widgets_groups[widget_group]['layout']
                row = self.widgets_groups[widget_group]['row']
                row += 1
                self.widgets_groups[widget_group]['row'] = row
        else:
            layout = layout

        if widget_type not in ['button', 'label', 'image']:
            label = tk.Label(layout, text=label_text)
            label.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
            column += 1  # Move to the next column for the widget

        if widget_type == 'checkbox':
            var = tk.BooleanVar(value=default_value)
            style_str = "success.Roundtoggle.TCheckbutton" \
                if self.theme_name == 'wiliot' else "warning.Roundtoggle.TCheckbutton"
            widget = ttk.Checkbutton(layout, variable=var, style=style_str)

        elif widget_type == 'combobox':
            if not isinstance(default_value, list) and not isinstance(default_value, tuple):
                default_value = [default_value]
            var = tk.StringVar(value=default_value[0])
            options = options if options is not None else tuple(default_value)
            widget = ttk.Combobox(layout, values=options, textvariable=var)
        elif widget_type == 'entry':
            var = tk.StringVar(value=default_value)
            widget = tk.Entry(layout, textvariable=var)
            widget.configure(bg='white')
        elif widget_type == 'file_input':
            var = tk.StringVar(value=default_value)
            widget = tk.Entry(layout, textvariable=var)
            widget.configure(bg='white')
            is_multiple = (options == 'multiple')
            is_folder = (options == 'folder')
            browse_button = Button(layout, text="Browse",
                                   command=lambda: self.browse_files(var=var,
                                                                     is_multiple=is_multiple, is_folder=is_folder))
            browse_button.grid(row=row, column=column + 1, padx=0, pady=pady, sticky="ew")
            self.widgets[widget_key + '_browse_button'] = browse_button # variable for browse button to change its state later
        elif widget_type == 'button':
            button_txt = default_value if default_value else label_text
            widget = Button(layout, text=button_txt)
            padx = padx + len(button_txt)
        elif widget_type == 'label':
            var = tk.StringVar(value=default_value)
            widget = tk.Label(layout, textvariable=var)
            if isinstance(options, dict):
                if 'font' in options:
                    widget.configure(font=options['font'])
                if 'fg' in options:
                    widget.configure(fg=options['fg'])
                if 'bg' in options:
                    widget.configure(bg=options['bg'])
        elif widget_type == 'canvas':
            widget = tk.Canvas(layout, width=150, height=300)
        elif widget_type == 'image':
            img_path = default_value
            if os.path.isfile(img_path):
                try:
                    width = options.get("width", 150) if options else 150
                    height = options.get("height", 150) if options else 150

                    img = Image.open(img_path)
                    img = img.resize((width, height), Image.LANCZOS)
                    self.img_ref = ImageTk.PhotoImage(img)
                    widget = tk.Label(layout, image=self.img_ref)
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
                    widget = tk.Label(layout, text="Error loading image")
            else:
                widget = tk.Label(layout, text="Image not found")
        elif widget_type == 'spinbox':
            var = tk.StringVar(value=default_value)
            widget = tk.Spinbox(layout, from_=options[0], to=options[-1], textvariable=var)
        else:
            raise Exception('could not select the relevant widget type')

        widget.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew", columnspan=columnspan, rowspan=rowspan)
        self.widgets_vals[widget_key] = var  # Use widget_key
        self.widgets[widget_key] = widget  # Use widget_key

    @staticmethod
    def browse_files(var, is_multiple=False, is_folder=False):
        if is_multiple:
            filenames = filedialog.askopenfilenames(title="Select Files", )
        elif is_folder:
            filenames = filedialog.askdirectory(title="Select a Folder", )
        else:
            filenames = filedialog.askopenfilename(title="Select a File", )
        var.set(filenames)

    def get_all_values(self):
        values = {}
        for key, param in self.params_dict.items():
            if isinstance(param, list) or (
                    isinstance(param, dict) and all(isinstance(v, dict) for v in param.values())):
                continue
            else:
                if param.get('widget_type') not in ['canvas', 'button']:
                    widget = self.widgets_vals.get(key)
                    if widget:
                        values[key] = widget.get()
                        if param.get('widget_type', '') == 'file_input':
                            values[key] = self.extract_file_names(values[key])
        return values

    @staticmethod
    def extract_file_names(str_in):
        if os.path.exists(str_in):
            return str_in
        match = re.findall(r"'(.*?)'", str_in)
        if match:
            files_out = [file.strip() for file in match]
        else:
            return str_in
        return files_out[0] if len(files_out) == 1 else files_out

    def update_widget(self, widget_key, new_value=None, color=None, disabled=None, options=None, button_style=None):
        widget_var = self.widgets_vals.get(widget_key)
        widget = self.widgets.get(widget_key)
        if new_value is not None:
            if isinstance(widget, tk.Label) or isinstance(widget, ttk.Checkbutton):
                widget_var.set(new_value)
            elif isinstance(widget, ttk.Combobox):
                widget_var.set(new_value)
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, new_value)
            elif isinstance(widget, Button):
                widget.config(text=new_value)
            else:
                print(f'Unsupported widget type: {type(widget)} in {widget_key} widget')

        if options is not None and isinstance(widget, ttk.Combobox):
            widget['values'] = options

        if color is not None:
            if isinstance(widget, Button):
                self.update_button_style(widget=widget, widget_key=widget_key, color=color, button_style=button_style)
            else:
                widget.config(fg=color)
        if disabled is not None:
            state = 'disabled' if disabled else 'normal'
            widget.config(state=state)
            if self.widgets.get(widget_key + '_browse_button'):
                self.widgets[widget_key + '_browse_button'].config(state=state)

    def add_event(self, widget_key, command, event_type=None):
        """
        Adds an event to a widget.

        Args:
            widget_key (str): The key of the widget to add the event to.
            command (callable): The function to call when the event occurs.
            event_type (str, optional): The type of event to bind to. Defaults to '<FocusOut>'.

        Returns:
            bool: True if the event was added successfully, False otherwise.
        """

        widget = self.widgets.get(widget_key) or self.widgets_tabs.get(widget_key, {'layout': None})['layout']

        if isinstance(widget, Button) or event_type == 'button' or event_type == 'checkbox':
            widget.configure(command=command)
            return True
        if event_type is None:
            if isinstance(widget, ttk.Combobox) or event_type == 'combobox':
                event_type = '<FocusIn>'
            elif isinstance(widget, tk.Entry) or event_type == 'entry':
                event_type = '<KeyRelease>'
            else:
                event_type = '<FocusOut>'

        widget.bind(event_type, command)

    def add_recurrent_function(self, cycle_ms, function):
        self.layout.after(ms=cycle_ms, func=self.wrapper_recurrent_func(cycle_ms=cycle_ms, function=function))

    def wrapper_recurrent_func(self, cycle_ms, function):
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
            self.layout.after(ms=cycle_ms, func=wrapper)

        return wrapper

    @staticmethod
    def update_button_style(widget, widget_key, color, button_style):
        style = Style()
        style_name = f"{widget_key}.TButton"
        if button_style:
            style.configure(style_name, **button_style)
        else:
            style.configure(style_name, background=color, foreground='white')
        widget.config(style=style_name)

    @staticmethod
    def update_all_win_children_state(win=None, state='disable'):
        def update_win(cur_win):
            for child in cur_win.winfo_children():
                if (isinstance(child, tk.Tk) or isinstance(child, tk.Toplevel)) and '-disabled' in child.attributes():
                    child.attributes('-disabled', disabled)
                    update_win(child)

        if win is None:
            win = WiliotGui.class_tk
        if 'disable' in state:
            disabled = True
            state = 'disabled'
        elif 'enable' in state or 'normal' in state:
            disabled = False
            state = 'normal'
        else:
            raise Exception('update_all_win_children_state: the supported states are disable, enable')
        update_win(win)


if __name__ == "__main__":

    num = 0
    t_i = time.time()


    def disable_widget():
        values = app.get_all_values()
        return not values['enable_disable_widget']


    def update_str():
        values = app.get_all_values()
        return values['IMAGE']


    def increment_num():
        global num
        num += 1
        return num


    def my_recurrent_function():
        global t_i
        t_now = time.time() - t_i
        elapsed_str = f'elapsed time: {round(t_now, 2)}'
        app.update_widget('clock', elapsed_str)
        print(elapsed_str)


    my_params_dict = {}

    my_params_dict["DEBUG_UID"] = '0xd3d300000003'
    my_params_dict["NUM_ITERATIONS"] = str(int(1))
    my_params_dict["IMAGE"] = ["MainFlow.hex", "D3FSM_435.hex", "D4FSM_508.hex"]  # Choose image from generic flows

    my_params_dict["enable_disable_widget"] = True
    my_params_dict["RF_TESTS_EN"] = False
    my_params_dict["NUM_ITERATIONS"] = str(int(1))
    my_params_dict["IMAGE"] = ["MainFlow.hex", "D3FSM_435.hex", "D4FSM_508.hex"]  # Choose image from generic flows
    my_params_dict = {k: {'value': v} for k, v in my_params_dict.items()}

    my_params_dict['group_hi'] = {'value': True, 'group': 'my checkbox'}
    my_params_dict['group_bye'] = {'value': False, 'group': 'my checkbox'}

    my_params_dict['file1'] = {'value': '', 'widget_type': 'file_input'}
    my_params_dict['file2'] = {'value': '', 'widget_type': 'file_input'}
    my_params_dict['temperature_tab'] = {'min': {'value': 0, 'tab': 'tab1'},
                                         'max': {'value': 100, 'tab': 'tab2'}}
    my_params_dict['temperature_rows'] = [{'min': {'value': 0}}, {'max': {'value': 100}}]
    my_params_dict['file'] = {'value': '', 'widget_type': 'file_input', 'options': 'multiple'}

    my_params_dict['button'] = {'value': 'Hi', 'widget_type': 'button', 'columnspan': 2}
    my_params_dict['update_label'] = {'value': 'n press: 0', 'widget_type': 'label'}
    my_params_dict['clock'] = {'value': '', 'widget_type': 'label'}

    app = WiliotGui(my_params_dict, full_screen=True, theme='wiliot', title='First GUI')
    app.add_event(widget_key='button',
                  event_type='button',
                  command=lambda: app.update_widget(widget_key='update_label', new_value=increment_num()))
    app.add_event(widget_key='IMAGE',
                  event_type='<<ComboboxSelected>>',
                  command=lambda args: app.update_widget(widget_key='update_label', new_value=update_str()))
    app.add_event(widget_key='enable_disable_widget',
                  event_type='button',
                  command=lambda: app.update_widget(widget_key='IMAGE', disabled=disable_widget()))
    app.add_recurrent_function(cycle_ms=1000, function=my_recurrent_function)
    values_out = app.run()
    print(values_out)

    app = WiliotGui(my_params_dict, full_screen=False, theme='warning', exit_sys_upon_cancel=False, title='Second GUI')
    app.add_event(widget_key='button', event_type='button',
                  command=lambda: app.update_widget(widget_key='update_label', new_value=increment_num()))
    app.add_event(widget_key='IMAGE',
                  event_type='<<ComboboxSelected>>',
                  command=lambda args: app.update_widget(widget_key='update_label', new_value=update_str()))
    app.add_event(widget_key='enable_disable_widget',
                  event_type='button',
                  command=lambda: app.update_widget(widget_key='NUM_ITERATIONS', disabled=disable_widget()))
    app.add_recurrent_function(cycle_ms=1000, function=my_recurrent_function)
    values_out = app.run()
    print(values_out)

    i = 0
    while i < 5:
        print('check if all user GUI closed successfully')
        time.sleep(1)
        i += 1
    app.exit_app()
    i = 0
    while i < 5:
        print('check if main GUI closed successfully')
        time.sleep(1)
        i += 1
    print('done')
