import configparser
from datetime import datetime
from owner_change_utils import *
from internal_functions import get_owner_details


class OneReelRequestPage(ctk.CTkFrame):

    def __init__(self, parent, show_page_callback):
        super().__init__(parent)
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)
        self.tree = None
        self.parent.attached_df = None
        show_img(self)

        start_y = 150
        label_width = 120
        entry_width = 200
        y_spacing = (self.parent.H - start_y)/10
        x_spacing = 50

        label = ctk.CTkLabel(self, text="Create Request (One Reel)", font=("Arial", 28, "bold"))
        label.pack(pady=50)

        label = ctk.CTkLabel(self, text="API Key:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y)

        self.api_key_entry = ctk.CTkEntry(self, width=entry_width, show="*")
        self.api_key_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y)
        self.api_key_entry.insert(0, self.parent.api_key)

        label = ctk.CTkLabel(self, text="From Owner:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + y_spacing)

        self.from_owner_entry = ctk.CTkEntry(self, width=entry_width)
        self.from_owner_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + y_spacing)
        self.from_owner_entry.insert(0, 'wiliot-ops')


        label = ctk.CTkLabel(self, text="To Owner:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 2 * y_spacing)

        self.to_owner_entry = ctk.CTkEntry(self, width=entry_width)
        self.to_owner_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 2 * y_spacing)

        btn = ctk.CTkButton(self, text="Check", command=self.get_owner_details, font=("Arial", 15), width=8)
        btn.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 2.5 * y_spacing)

        self.owner_details = ctk.CTkLabel(self, text="", font=("Arial", 15))
        self.owner_details.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 2.5 * y_spacing)

        label = ctk.CTkLabel(self, text="Ex. ID Prefix:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 3 * y_spacing)

        self.ex_id_prefix_entry = ctk.CTkEntry(self, width=entry_width)
        self.ex_id_prefix_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 3 * y_spacing)

        label = ctk.CTkLabel(self, text="First Tag:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 4 * y_spacing)

        self.first_tag_entry = ctk.CTkEntry(self, width=entry_width)
        self.first_tag_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 4 * y_spacing)

        label = ctk.CTkLabel(self, text="Last Tag:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 5 * y_spacing)

        self.last_tag_entry = ctk.CTkEntry(self, width=entry_width)
        self.last_tag_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 5 * y_spacing)

        label = ctk.CTkLabel(self, text="Cloud Destination:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 6 * y_spacing)

        # self.cloud_destination = ctk.CTkEntry(self, width=entry_width)
        # self.cloud_destination.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 6 * y_spacing)
        self.cloud_destination = ctk.CTkComboBox(master=self, values=['AWS', 'WMT'], justify='center',width=entry_width)
        self.cloud_destination.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 6 * y_spacing)
        self.cloud_destination.set('WMT')

        label = ctk.CTkLabel(self, text="WMT API Key:", font=("Arial", 15))
        label.place(x=self.parent.W / 2 - label_width - 10 - x_spacing, y=start_y + 7 * y_spacing)

        self.wmt_api_key_entry = ctk.CTkEntry(self, width=entry_width, show="*")
        self.wmt_api_key_entry.place(x=self.parent.W / 2 + 10 - x_spacing, y=start_y + 7 * y_spacing)
        self.wmt_api_key_entry.insert(0, self.parent.wmt_api_key)

        btn = ctk.CTkButton(self, text="Back", command=self.show_page_callback, width=120)
        btn.place(x=50, y=self.parent.H - 50)

        btn = ctk.CTkButton(self, text="Send Request", command=self.send_request, width=200)
        btn.place(x=self.parent.W / 2 - btn.winfo_reqwidth() / 2, y=start_y + 8 * y_spacing)

    def get_owner_details(self):
        owner = self.to_owner_entry.get()
        if len(owner) == 0:
            self.owner_details.configure(text="No owner ID")
            return
        data = get_owner_details(owner)
        if data is None or len(data) == 0:
            self.owner_details.configure(text="Unable to find the owner")
            return
        new_text = data[0].get("name") + ", "+ data[0].get("primaryEmail")
        self.owner_details.configure(text=new_text)

    def verify_request(self):
        if len(self.ex_id_prefix_entry.get()) < 3:
            raise ValueError(f"Ex. ID Prefix value must be at least 3 letters")

        if not can_be_int(self.first_tag_entry.get()):
            raise ValueError(f"First Tag must be a number and under 10000")

        if not can_be_int(self.last_tag_entry.get()):
            raise ValueError(f"Last Tag must be a number and under 10000")

        if str(self.first_tag_entry.get()).zfill(4) > str(self.last_tag_entry.get()).zfill(4):
            raise ValueError(f"First Tag is bigger than Last Tag")

    def send_request(self):
        try:
            self.verify_request()
            self.parent.save_api_keys(self.api_key_entry.get(), self.wmt_api_key_entry.get())

            df = pd.DataFrame([[self.ex_id_prefix_entry.get(), self.first_tag_entry.get(), self.last_tag_entry.get()]],
                              columns=self.parent.cols[:-1])
            tags_df = create_tags_df(df)
            from_owner = self.from_owner_entry.get()
            to_owner = self.to_owner_entry.get()
            cloud_destination = self.cloud_destination.get()
            df['To Owner'] = to_owner
            df['Cloud Destination'] = cloud_destination
            if from_owner == "" or to_owner == "" or self.parent.api_key == "":
                raise Exception("Some Fields are Empty!")
            if not self.parent.yes_no_question("This action is irreversible, Please make sure the target cloud is correct. \nAre you sure you want to continue?"):
                return
            if self.parent.tadbik == 'True':
                to_owner = '852213717688'
                cloud_destination = None
            request_id = self.parent.send_request_file(from_owner, to_owner, tags_df, cloud_destination)
            df.to_csv('data/' + request_id + '.csv', index=False)
            request_df = pd.DataFrame([[request_id, '-', '-', '-', '-', '-', '-', str(datetime.now())[:16], cloud_destination]],
                                      columns=self.parent.requests_cols)
            self.parent.requests_df = pd.concat([request_df, self.parent.requests_df])
            self.show_page_callback()
        except Exception as ex:
            self.parent.show_error_popup(str(ex))
