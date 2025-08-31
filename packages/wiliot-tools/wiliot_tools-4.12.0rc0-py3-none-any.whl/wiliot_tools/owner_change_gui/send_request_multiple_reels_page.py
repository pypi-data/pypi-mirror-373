import configparser
import os
try:
    from tkinter import filedialog
except Exception as e:
    print(f'could not import tkinter: {e}')
from CTkMessagebox import CTkMessagebox
from owner_change_utils import *
from datetime import datetime

class MultiReelRequestPage(ctk.CTkFrame):

    def __init__(self, parent, show_page_callback):
        super().__init__(parent)
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)
        self.tree = None
        self.parent.attached_df = None
        self.cbs = []
        label = ctk.CTkLabel(self, text="Create Request (Multiple Reels)", font=("Arial", 28, "bold"))
        label.pack(pady=50)
        show_img(self)
        start_y = self.start_y = 50
        label = ctk.CTkLabel(self, text="API Key:")
        label.place(x=50, y=60 + start_y)

        self.api_key_entry = ctk.CTkEntry(self, width=200, show="*")
        self.api_key_entry.place(x=140, y=60 + start_y)
        self.api_key_entry.insert(0, self.parent.api_key)

        label = ctk.CTkLabel(self, text="From Owner:")
        label.place(x=50, y=110 + start_y)

        # self.from_owner_entry = combobox = ctk.CTkComboBox(master=self,
        #                                                    values=["wiliot-ops", "108502199256 (tadbik-mnf)"],
        #                                                    width=200, justify="center")

        self.from_owner_entry = ctk.CTkEntry(self, width=200)
        self.from_owner_entry.place(x=140, y=110 + start_y)
        self.from_owner_entry.insert(0, 'wiliot-ops')

        self.file_attach_label = ctk.CTkLabel(self, text="")
        self.file_attach_label.place(x=140, y=160 + start_y)
        self.cloud_dest_entry = ctk.CTkComboBox(master=self,values=["AWS", "WMT"],width=200, justify="center")
        self.cloud_dest_entry.place(x=140, y= 20 + start_y)
        self.cloud_dest_entry.set('WMT')
        btn = ctk.CTkButton(self, text="Attach File", command=self.browse_file, width=70)
        btn.place(x=50, y=160 + start_y)

        for i in range(4):
            combobox = ctk.CTkComboBox(master=self,
                                       values=["-"],
                                       command=self.combobox_callback,
                                       width=200, justify="center")
            combobox.place(x=90 + 275 * i, y=210 + start_y)
            self.cbs.append(combobox)

        self.tree = self.parent.create_tree_view(self, pd.DataFrame(columns=self.parent.cols), height=20)
        self.tree.place(x=50, y=240 + start_y)

        btn = ctk.CTkButton(self, text="Back", command=self.show_page_callback, width=120)
        btn.place(x=50, y=self.parent.H - 50)

        btn = ctk.CTkButton(self, text="Send Request", command=self.send_request, width=120)
        btn.place(x=self.parent.W / 2 - 60, y=self.parent.H - 50)

        self.display_attached_file()

    def combobox_callback(self, event):
        self.update_df()

    def select_closest_col(self):
        for cb in self.cbs:
            cb.set('-')
        for col in self.parent.attached_df.columns:
            lo_col = col.lower()
            if 'prefix' in lo_col:
                self.cbs[0].set(col)
            if 'first' in lo_col or 'start' in lo_col or 'init' in lo_col:
                self.cbs[1].set(col)
            if 'last' in lo_col or 'end' in lo_col:
                self.cbs[2].set(col)
            if 'to' in lo_col and 'owner' in lo_col:
                self.cbs[3].set(col)

    def send_request(self):
        try:
            failed_to_owners = []
            expections = []
            if self.parent.attached_df is None:
                raise Exception("No File is Attached")
            df = self.parent.attached_df[self.parent.selected_cols]
            df.columns = self.parent.cols
            verify_file(df)
            self.parent.save_api_keys(self.api_key_entry.get(), self.parent.wmt_api_key)
            from_owner = self.from_owner_entry.get()  # .split(" ")[0]
            cloud_dest = self.cloud_dest_entry.get()
            if from_owner == "" or self.parent.api_key == "":
                raise Exception("Some Fields are Empty!")
            if not self.parent.yes_no_question("This action is irreversible, Please make sure the target cloud is correct. \nAre you sure you want to continue?"):
                return
            for to_owner in df['To Owner'].unique():
                org_to_owner = to_owner
                try:
                    request_df = df[df['To Owner'] == to_owner]
                    tags_df = create_tags_df(request_df)
                    df = request_df.copy()
                    df['To Owner'] = to_owner
                    df['Cloud Destination'] = cloud_dest
                    if self.parent.tadbik == 'True':
                        to_owner = '852213717688'
                        cloud_dest = None
                    request_id = self.parent.send_request_file(from_owner, to_owner, tags_df, cloud_dest)
                    df.to_csv('data/' + request_id + '.csv', index=False)
                    request_df = pd.DataFrame([[request_id, '-', '-', '-', '-', '-', '-', str(datetime.now())[:16], cloud_dest]],
                                              columns=self.parent.requests_cols)
                    self.parent.requests_df = pd.concat([request_df, self.parent.requests_df])
                except Exception as ex:
                    failed_to_owners.append(org_to_owner)
                    expections.append(str(ex))
            if len(failed_to_owners) > 0:
                for failed_to_owner, expection in zip(failed_to_owners, expections):
                    request_df = pd.DataFrame(
                        [[expection, from_owner, failed_to_owner, 'failed', '-', '-', '-', str(datetime.now())[:16], cloud_dest]],
                        columns=self.parent.requests_cols)
                    self.parent.requests_df = pd.concat([request_df, self.parent.requests_df])
                    print(f'\n - To Owner: {failed_to_owner} reason: {expection}')
                message = f"Requests Failed For These Owners:\n {failed_to_owners}"
                message += "\n\n Please find file failed_owners.csv in the same dirictory as the input file," \
                           "\nplease fix the issues and upload again."
                df[df['To Owner'].isin(failed_to_owners)].to_csv(
                    os.path.join(os.path.dirname(self.parent.filename), "failed_owners.csv"))
                CTkMessagebox(master=self, title="Error", message=message, icon="cancel", width=500, height=200)

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
        self.parent.selected_cols = [cb.get() for cb in self.cbs]
        display_df = self.parent.attached_df[self.parent.selected_cols]
        display_df.columns = self.parent.cols
        if self.tree is not None:
            self.tree.destroy()
        self.tree = self.parent.create_tree_view(self, display_df, height=20)
        self.tree.place(x=50, y=240 + self.start_y)

    def display_attached_file(self):
        if self.parent.attached_df is None:
            self.file_attach_label.configure(text=f"Please Attach a File", text_color="black")
            return

        for cb, col in zip(self.cbs, self.parent.selected_cols):
            cb.configure(values=self.parent.attached_df.columns)
            cb.set(col)
        self.select_closest_col()
        self.update_df()
        self.file_attach_label.configure(text=f"File is Attached : {os.path.basename(self.parent.filename)}",
                                         text_color="green")
