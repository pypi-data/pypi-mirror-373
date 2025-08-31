import configparser

from config import DISPLAY_COLS
from shipment_approval_utils import *


class OneReelRequestPage(ctk.CTkFrame):

    def __init__(self, parent, show_page_callback):
        super().__init__(parent)
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)
        self.tree = None
        self.parent.attached_df = None
        show_img(self)

        start_y = 300
        label_width = 120
        entry_width = 200
        y_spacing = 70
        x_spacing = 50

        label = ctk.CTkLabel(self, text="Create Request (One Reel)", font=("Arial", 28, "bold"))
        label.pack(pady=50)

        label = ctk.CTkLabel(self, text="API Key:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y)

        self.api_key_entry = ctk.CTkEntry(self, width=entry_width, show="*")
        self.api_key_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y)
        self.api_key_entry.insert(0, self.parent.api_key)

        label = ctk.CTkLabel(self, text="Ex. ID Prefix:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 1 * y_spacing)

        self.ex_id_prefix_entry = ctk.CTkEntry(self, width=entry_width)
        self.ex_id_prefix_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 1 * y_spacing)


        btn = ctk.CTkButton(self, text="Back", command=self.show_page_callback, width=120)
        btn.place(x=50, y=self.parent.H - 50)

        btn = ctk.CTkButton(self, text="Send Request", command=self.send_request, width=200)
        btn.place(x=self.parent.W / 2 - btn.winfo_reqwidth() / 2, y=start_y + 4 * y_spacing)

    def verify_request(self):
        if len(self.ex_id_prefix_entry.get()) < 3:
            raise ValueError(f"Ex. ID Prefix value must be at least 3 letters")

        if self.parent.api_key == "":
            raise Exception("Some Fields are Empty!")

    def send_request(self):
        try:
            config = configparser.ConfigParser()
            self.parent.api_key = self.api_key_entry.get()
            config['API'] = {'key': self.parent.api_key}
            with open('resources/config.ini', 'w') as configfile:
                config.write(configfile)
            self.verify_request()
            external_id_prefix = self.ex_id_prefix_entry.get()
            request_id = self.parent.send_request(external_id_prefix)
            new_row = [request_id] + ['-'] * (len(DISPLAY_COLS) - 1)
            self.parent.requests.add_row(new_row, DISPLAY_COLS)
            self.show_page_callback()
        except Exception as ex:
            self.parent.show_error_popup(str(ex))
