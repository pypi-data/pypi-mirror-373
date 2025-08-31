try:
    from tkinter import ttk
except Exception as e:
    print(f'could not import tkinter: {e}')
from wiliot_api import ManufacturingClient
from owner_change_requests_page import *
from requests_details_page import *
from send_request_multiple_reels_page import *
from send_request_one_reel_page import *
import traceback


class OwnerChangeApp(ctk.CTk):
    def __init__(self, env='prod'):
        super().__init__()
        self.env = env
        self.prev_api_key = ""
        self.api_key = ""
        self.prev_wmt_api_key = ""
        self.wmt_api_key = ""
        self.tadbik = ""
        if env in ('prod', 'test'):
            self.seperator = 'T'
        else:
            self.seperator = '-'
        self.client = None
        self.wmt_client = None
        style = ttk.Style(self)
        style.configure("Treeview.Heading", background="#39a987", foreground="black")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        print(screen_width, screen_height)
        if screen_width > 1200:
            self.W = 1200
        else:
            self.W = screen_width - 100
        if screen_height > 800:
            self.H = 800
        else:
            self.H = screen_height - 100
        self.title("Owner Change")
        self.geometry(f"{self.W}x{self.H}")
        self.resizable(0, 0)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("resources/wiliot-green")
        if not os.path.exists("data"):
            os.makedirs("data")
        self.setup_config()
        self.attached_df = None
        self.requests_df = None
        self.col_width_dict = col_width()
        self.selected_cols = ['-', '-', '-', '-', '-']
        self.cols = ['Ex. ID Prefix', 'First Tag', 'Last Tag', 'To Owner']
        self.requests_cols = ['Tracking ID', 'From Owner', 'To Owner', 'Status', 'Total Tags', 'Passed', 'Failed',
                              'Sent At', 'Cloud Destination']
        OwnerChangeRequests(self, self.show_send_request_multiple_reels_page).pack(fill="both", expand=True)

    def save_api_keys(self, api_key, wmt_api_key):
        config = configparser.ConfigParser()
        self.api_key = api_key
        self.wmt_api_key = wmt_api_key
        config['API'] = {'key': self.api_key,
                         'wmt_key': self.wmt_api_key,
                         'tadbik': self.tadbik}
        with open('resources/config.ini', 'w') as configfile:
            config.write(configfile)

    def setup_config(self):
        config = configparser.ConfigParser()
        if not os.path.exists('resources/config.ini'):
            config['API'] = {'key': '', 'wmt_key': '', 'tadbik': 'False'}
            with open('resources/config.ini', 'w') as configfile:
                config.write(configfile)
        config.read('resources/config.ini')
        self.api_key = config['API'].get('key', '')
        self.wmt_api_key = config['API'].get('wmt_key', '')
        self.tadbik = config['API'].get('tadbik', 'False')
        print("Tadbik Version:",self.tadbik)

    def get_col_width(self, col, cols, width):
        return int(self.col_width_dict[col] * width / sum([self.col_width_dict[col] for col in cols]))

    def show_error_popup(self, message, width=400, height=200):
        CTkMessagebox(master=self, title="Error", message=message, icon="cancel", width=width, height=height)
        traceback.print_exc()

    def yes_no_question(self, message, width=400, height=200):
        msgbox = CTkMessagebox(
            master=self,
            title="Confirmation",
            message=message,
            icon="question",
            width=width,
            height=height,
            option_1="Yes",
            option_2="No"
        )
        response = msgbox.get()
        return response == "Yes"

    def show_request_details_page(self, request_id, prev_frame):
        prev_frame.destroy()
        RequestDetails(self, self.show_owner_change_requests_page, request_id=request_id).pack(fill="both", expand=True)

    def show_owner_change_requests_page(self, prev_frame):
        prev_frame.destroy()
        OwnerChangeRequests(self, self.show_send_request_multiple_reels_page).pack(fill="both", expand=True)

    def show_send_request_multiple_reels_page(self, prev_frame):
        prev_frame.destroy()
        MultiReelRequestPage(self, self.show_owner_change_requests_page).pack(fill="both", expand=True)

    def show_send_request_one_reel_page(self, prev_frame):
        prev_frame.destroy()
        OneReelRequestPage(self, self.show_owner_change_requests_page).pack(fill="both", expand=True)

    def save_data(self):
        self.requests_df.to_csv("data/requests.csv")

    def create_tree_view(self, frame, df, equal_width=True, height=23, width=100):
        height = int((height/23) * (self.H / 800)**2 * 23)
        tree = ttk.Treeview(frame, columns=list(df.columns), show="headings", height=height)
        for col in df.columns:
            tree.heading(col, text=col)
            if equal_width:
                tree.column(col, width=(self.W - width) // len(df.columns), anchor="center")
            else:
                tree.column(col, width=self.get_col_width(col, df.columns, self.W - width), anchor="center")

        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        return tree

    def check_client(self):
        if self.prev_api_key != self.api_key:
            self.client = ManufacturingClient(api_key=self.api_key, env=self.env)
            self.prev_api_key = self.api_key

        if self.prev_wmt_api_key != self.wmt_api_key and self.wmt_api_key != "":
            self.wmt_client = ManufacturingClient(api_key=self.wmt_api_key, env='wmt-prod', cloud='gcp',
                                                  region='us-central1')
            self.prev_wmt_api_key = self.wmt_api_key

    def send_request_file(self, from_owner, to_owner, df, cloud_destination=None):
        self.check_client()
        file_path = "data/tags_tmp.csv"
        df.to_csv(file_path)
        if cloud_destination != 'WMT':
            cloud_destination = None
        request_id = self.client.change_pixel_owner_by_file(from_owner, to_owner, file_path,
                                                            destination_cloud=cloud_destination)
        return request_id

    def get_request_aws_status(self, request_id):
        self.check_client()
        json_data = self.client.get_pixel_change_request_status(request_id)
        return json_data, json_data['status_code']

    def get_request_wmt_status(self, request_id, owner_id):
        self.check_client()
        json_data = self.wmt_client.get_import_pixel_request(owner_id, request_id)
        # print(json_data)
        return json_data, json_data['status_code']

    def send_import_request_wmt(self, request_id, owner_id):
        self.check_client()
        json_data = self.wmt_client.import_pixels(owner_id, request_id)
        return json_data

    def get_request_tags_info(self, request_id):
        file_path = "data/tags_tmp.csv"
        with open(file_path, "w") as f:
            self.check_client()
            self.client.get_pixel_change_request_details(request_id, f)
        df = pd.read_csv(file_path)
        return df

if __name__ == "__main__":
    app = OwnerChangeApp('prod')
    app.mainloop()