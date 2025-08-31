import threading
try:
    import customtkinter as ctk
except Exception as e:
    print(f'could not import tkinter: {e}')
import pandas as pd
from wiliot_api import WiliotCloudError
import os
from owner_change_utils import show_img, open_csv_with_excel, create_tags_df
from internal_functions import *


class OwnerChangeRequests(ctk.CTkFrame):
    def __init__(self, parent, show_page_callback):
        super().__init__(parent)
        self.threads = {}
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)

        label = ctk.CTkLabel(self, text="Owner Change Requests", font=("Arial", 28, "bold"))
        label.pack(pady=50)
        if self.parent.requests_df is None:
            try:
                self.parent.requests_df = pd.read_csv('data/requests.csv', index_col=0, dtype=str)
            except FileNotFoundError:
                self.parent.requests_df = pd.DataFrame(columns=self.parent.requests_cols)
        # df = self.parent.df
        self.tree = self.parent.create_tree_view(self, self.parent.requests_df, equal_width=False)
        self.tree.tag_configure('red', foreground='#d44e2a')
        self.tree.tag_configure('green', foreground='#39a987')
        self.tree.tag_configure('yellow', foreground='#FFBF00')
        self.tree.tag_configure('orange', foreground='orange')
        self.tree.pack(pady=20, padx=20)
        self.color_requests()

        btn = ctk.CTkButton(master=self, text="Request Details", command=self.request_details, width=220,
                            font=('Helvetica', 14))
        btn.place(x=self.parent.W / 2 - 110, y=self.parent.H - 150)

        btn = ctk.CTkButton(master=self, text="Open Full Data in Excel",
                            command=lambda: open_csv_with_excel("data/requests.csv"), width=220,
                            font=('Helvetica', 14))
        btn.place(x=self.parent.W / 2 - 110, y=self.parent.H - 100)
        self.delete_btn = ctk.CTkButton(master=self, text="Delete Selected", command=lambda: self.delete(), width=220,
                                        font=('Helvetica', 14))
        self.delete_btn.place(x=50, y=self.parent.H - 150)

        self.delete_btn = ctk.CTkButton(master=self, text="Delete All", command=lambda: self.delete(all=True),
                                        width=220,
                                        font=('Helvetica', 14))
        self.delete_btn.place(x=50, y=self.parent.H - 100)

        btn = ctk.CTkButton(self, text="Create Request (Multiple Reels)", command=self.show_page_callback, width=220)
        btn.place(x=self.parent.W - 270, y=self.parent.H - 100)

        btn = ctk.CTkButton(self, text="Create Request (One Reel)",
                            command=lambda: self.parent.show_send_request_one_reel_page(self),
                            width=220)
        btn.place(x=self.parent.W - 270, y=self.parent.H - 150)
        show_img(self)
        self.after(1, self.refresh)

    def request_details(self):
        items = self.tree.selection()
        if len(items) == 0:
            self.parent.show_error_popup("No Request Was Selected!")
            return
        item = items[0]
        if self.tree.item(item, "values")[3] != 'Done':
            self.parent.show_error_popup("The Request has not been Processed Yet!")
            return
        request_id = self.tree.item(item, "values")[0]
        self.parent.show_request_details_page(request_id, self)

    def color_requests(self):
        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, "values")
            if values[3].replace("WMT-", "") in ('not-started', 'processing', 'exported', 'processed', 'checking-fails'):
                self.tree.item(item, tags=('yellow',))
            elif values[3] == 'failed':
                self.tree.item(item, tags=('red',))
            elif values[3] == 'Done' and int(values[5]) == 0:
                self.tree.item(item, tags=('red',))
            elif values[3] == 'Done' and int(values[4]) - int(values[5]) > 0:
                self.tree.item(item, tags=('orange',))
            elif values[3] == 'Done':
                self.tree.item(item, tags=('green',))

    def sync(self):
        self.parent.requests_df = pd.DataFrame(
            [self.tree.item(item, "values") for item in self.tree.get_children()],
            columns=self.parent.requests_cols
        )

    def get_request_status(self, request_id, cloud_destination, status, account_id):
        if cloud_destination == 'WMT' and status.startswith("WMT"):
            response, status_code = self.parent.get_request_wmt_status(request_id, account_id)
            print(response)
            if 'status' in response:
                response['status'] = 'WMT-' + response['status']
        else:
            response, status_code = self.parent.get_request_aws_status(request_id)
            print(response)
            if 'status' in response and response['status'] == 'exported':
                if cloud_destination == 'WMT':
                    try:
                        if response['passed'] != 0:
                            self.parent.send_import_request_wmt(request_id, account_id)
                        else:
                            response['status'] = 'Done'
                            return response, status_code

                    except WiliotCloudError as ex:
                        if 'Already exist' not in str(ex):
                            raise Exception(ex)

                    response, status_code = self.get_request_status(request_id, 'WMT', 'WMT', account_id)
        return response, status_code


    def update_requests(self):
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            request_id = values[0]
            status = values[3].replace("WMT-", "")
            if status in ('not started', 'not-started', '-', 'processing', 'processed', 'exported', 'checking-fails'):
                response, status_code = self.get_request_status(values[0], values[-1], values[3], values[2])
                if status_code == 200:
                    new_values = list(response.values())[:7] + list(values)[7:]
                    if new_values[2] is None:
                        new_values[2] = values[2]
                        new_values[1] = values[1]
                    new_status = new_values[3].replace("WMT-", "")

                    if new_status in 'processed' and values[2] == '852213717688' and self.parent.tadbik == 'True':
                        request_id = values[0]
                        df = pd.read_csv('data/' + request_id + '.csv')
                        tags_df = create_tags_df(df, self.parent.seperator)
                        to_owner = list(df['To Owner'])[0]
                        from_owner = '852213717688'
                        cloud_destination = list(df['Cloud Destination'])[0]
                        new_request_id = self.parent.send_request_file(from_owner, to_owner, tags_df, cloud_destination)
                        df.to_csv('data/' + new_request_id + '.csv', index=False)
                        new_values[3] = 'not-started'
                        new_values[0] = new_request_id
                        new_values[-1] = cloud_destination

                    elif new_status in 'processed' and values[-1] == 'AWS':
                        new_values[3] = 'cloud-done'

                    if new_values[3] == 'WMT-processed' and values[-1] == 'WMT':
                        response, status_code = self.get_request_status(values[0], 'AWS', values[3], values[2])
                        new_values = list(response.values())[:7] + list(values)[7:]
                        new_values[-1] = 'WMT'
                        new_values[3] = 'cloud-done'

                    if new_values[3] == 'cloud-done' or new_values[3] == 'checking-fails':
                        if new_values[-3] == 0 or os.path.exists(os.path.join("data", request_id + "_tags.csv")) or not os.path.exists('databricks_config.json'):
                            new_values[3] = 'Done'
                        elif new_values[-3] > 0 and request_id not in self.threads:
                            new_values[3] = 'checking-fails'
                            thread = threading.Thread(target=self.check_fails, args=[new_values]).start()
                            self.threads[request_id] = thread
                        else:
                            new_values[3] = 'checking-fails'

                    new_values = ['-' if str(v) == 'None' else v for v in new_values]
                    self.update_item(item, new_values)
                else:
                    values = list(values)
                    values[3] = 'failed'
                    self.update_item(item, values)
                    print(f"API Response {status_code}, Response: {response}")

        self.color_requests()
        self.sync()
        self.parent.save_data()

    @staticmethod
    def fix_external_ids(df):
        if len(df) == 0:
            return df
        rows = []
        for crn, crn_df in df.groupby('common_run_name'):
            last_ex_id = None
            for i, row in crn_df.reset_index().iterrows():
                if 'T' in str(row['external_id']):
                    last_ex_id = row['external_id']
                    rows.append(row)
                elif row['fail_bin_str'] in ('BAD_PRINTING', 'DUPLICATION_OFFLINE'):
                    if last_ex_id is None:
                        last_ex_id = min([ex for ex in crn_df['external_id'] if 'T' in str(ex)])
                    row['external_id'] = f'{last_ex_id.split("T")[0]}T{str(int(last_ex_id.split("T")[1])+1).zfill(4)}'
                    last_ex_id = row['external_id']
                    rows.append(row)

        return pd.DataFrame(rows)

    def check_fails(self, values):
        if PUBLIC_VERSION:
            return
        request_id = values[0]
        expected_owner_id = values[1]
        print("Checking Fails", request_id)
        tags_df = get_all_tags(request_id)
        print(f"tags found {len(tags_df)}")
        fails_df = get_fails_ids(request_id)
        print(f"fails found {len(fails_df)}")
        if tags_df is None:
            return False
        tags_df = self.fix_external_ids(tags_df)
        ex_prefixes = set([ex_id.split("T")[0] for ex_id in tags_df['external_id'] if 'T' in ex_id])
        df = pd.merge(fails_df, tags_df, on='external_id', how='left')
        df['fail_bin_str'] = df['fail_bin_str'].fillna("EXT_ID_NOT_IN_DATABRICKS")
        df['fail_bin_str'] = df.apply(lambda x: 'PREFIX_NOT_IN_DATABRICKS' if x['fail_bin_str'] == 'EXT_ID_NOT_IN_DATABRICKS' and x['external_id'].split("T")[0] not in ex_prefixes else x['fail_bin_str'],axis=1)
        passed_fails = len(df[(df['fail_bin_str'] == 'PASS')])
        if passed_fails > 0:
            print(f"passed fails found {passed_fails}")
            config = get_databricks_config()
            if config is None:
                return
            client = InternalClient(config.get("key"))
            if passed_fails > 500:
                df = df.head(500)
            df['fail_bin_str'] = df.apply(lambda x: check_cloud_issues(x, expected_owner_id, client), axis=1)
        good_bins = {'DUPLICATION_POST_PROCESS', 'DUPLICATION_OFFLINE', 'CORRUPTED_PACKET_POST_PROCESS', 'BAD_PRINTING'}
        df['fail_bin_str'] = df['fail_bin_str'].astype(str).apply(lambda x: x + " (it's OK)" if x in good_bins else x)
        df[['external_id', 'fail_bin_str']].to_csv(os.path.join("data", request_id + "_tags.csv"), index=False)
        print(df)
        return True


    def refresh(self):
        print('Refreshing Requests!')
        threading.Thread(target=self.update_requests).start()
        self.after(30000, self.refresh)

    def update_item(self, item_id, new_values):
        self.tree.item(item_id, values=new_values)

    def delete(self, all=False):
        if all:
            items = self.tree.get_children()
        else:
            items = self.tree.selection()
            if len(items) == 0:
                self.parent.show_error_popup("No Request Was Selected!")
                return
        for item in items:
            self.tree.delete(item)
        self.sync()


