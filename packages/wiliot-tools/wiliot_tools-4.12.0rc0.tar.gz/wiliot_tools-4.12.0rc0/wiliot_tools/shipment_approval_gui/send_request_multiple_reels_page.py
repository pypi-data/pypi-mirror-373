import configparser
try:
    from tkinter import filedialog
except Exception as e:
    print(f'could not import tkinter: {e}')

from config import DISPLAY_COLS
from shipment_approval_utils import *


class MultiReelRequestPage(ctk.CTkFrame):

    def __init__(self, parent, show_page_callback):
        super().__init__(parent)
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)
        self.tree = None
        self.parent.attached_df = None
        label = ctk.CTkLabel(self, text="Create Request (Multiple Reels)", font=("Arial", 28, "bold"))
        label.pack(pady=50)
        show_img(self)
        start_y = self.start_y = 50
        label = ctk.CTkLabel(self, text="API Key:")
        label.place(x=50, y=60 + start_y)

        self.api_key_entry = ctk.CTkEntry(self, width=200, show="*")
        self.api_key_entry.place(x=140, y=60 + start_y)
        self.api_key_entry.insert(0, self.parent.api_key)

        self.file_attach_label = ctk.CTkLabel(self, text="")
        self.file_attach_label.place(x=140, y=160 + start_y)

        btn = ctk.CTkButton(self, text="Attach File", command=self.browse_file, width=70)
        btn.place(x=50, y=160 + start_y)

        self.combobox = ctk.CTkComboBox(master=self,
                                        values=["-"],
                                        command=self.combobox_callback,
                                        width=200, justify="center")
        self.combobox.place(x=600, y=210 + start_y)

        self.tree = self.parent.create_tree_view(self, pd.DataFrame(columns=self.parent.cols), height=20, width=900)
        self.tree.place(x=450, y=240 + start_y)

        btn = ctk.CTkButton(self, text="Back", command=self.show_page_callback, width=120)
        btn.place(x=50, y=self.parent.H - 50)

        btn = ctk.CTkButton(self, text="Send Request", command=self.send_request, width=120)
        btn.place(x=self.parent.W / 2 - 60, y=self.parent.H - 50)

        self.display_attached_file()

    def combobox_callback(self, event):
        self.update_df()

    def select_closest_col(self):
        self.combobox.set('-')
        for col in self.parent.attached_df.columns:
            lo_col = col.lower()
            if "prefix" in lo_col or ('reel' in lo_col and 'id' in lo_col):
                self.combobox.set(col)

    def verify_request(self, ex_ids):
        if not all([len(ex_id) >= 3 for ex_id in ex_ids]):
            raise Exception("All reel external id prefix have at least 3 characters")
        if len(ex_ids) > 200:
            raise Exception("Can't send more than 200 reels at once")

    def send_request(self):
        try:
            ex_ids = set(self.parent.attached_df[self.combobox.get()])
            self.verify_request(ex_ids)
            config = configparser.ConfigParser()
            self.parent.api_key = self.api_key_entry.get()
            config['API'] = {'key': self.parent.api_key}
            with open('resources/config.ini', 'w') as configfile:
                config.write(configfile)
            for external_id_prefix in ex_ids:
                external_id_prefix = external_id_prefix.strip()
                print(f"request sent for reel_id {external_id_prefix}")
                request_id = self.parent.send_request(external_id_prefix)
                new_row = [request_id] + ['-'] * (len(DISPLAY_COLS) - 1)
                self.parent.requests.add_row(new_row, cols=DISPLAY_COLS)
                # request_df = pd.DataFrame([new_row], columns=DISPLAY_COLS)
                # self.parent.requests_df = pd.concat([request_df, self.parent.requests_df])
            self.show_page_callback()
        except Exception as ex:
            self.parent.show_error_popup(str(ex))

    def browse_file(self):
        try:
            filename = filedialog.askopenfilename(initialdir=__file__, title="Select Csv File",
                                                  filetypes=[("csv files", ".csv")])  #
            self.parent.attached_df = pd.read_csv(filename, dtype=str)
            self.parent.attached_df['-'] = ''
            self.parent.filename = filename
            self.display_attached_file()
        except Exception as ex:
            self.file_attach_label.configure(text=f"Error Attaching The File", text_color="red")
            raise Exception(ex)

    def update_df(self):
        self.parent.selected_cols = [self.combobox.get()]
        display_df = self.parent.attached_df[self.parent.selected_cols]
        display_df.columns = self.parent.cols
        if self.tree is not None:
            self.tree.destroy()
        self.tree = self.parent.create_tree_view(self, display_df, height=20, width=900)
        self.tree.place(x=450, y=240 + self.start_y)

    def display_attached_file(self):
        if self.parent.attached_df is None:
            self.file_attach_label.configure(text=f"Please Attach a File", text_color="black")
            return

        self.combobox.configure(values=self.parent.attached_df.columns)
        self.combobox.set(self.parent.selected_cols[0])

        self.select_closest_col()
        self.update_df()
        self.file_attach_label.configure(text=f"File is Attached : {os.path.basename(self.parent.filename)}",
                                         text_color="green")
