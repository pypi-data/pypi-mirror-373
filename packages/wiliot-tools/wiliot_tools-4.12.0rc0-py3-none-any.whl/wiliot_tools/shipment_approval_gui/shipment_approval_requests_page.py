import threading
import time
try:
    import customtkinter as ctk
except Exception as e:
    print(f'could not import tkinter: {e}')

from requests_df import Requests
from config import DISPLAY_COLS
from shipment_approval_utils import show_img, open_csv_with_excel


class ShipmentApprovalRequests(ctk.CTkFrame):
    def __init__(self, parent, show_page_callback):
        super().__init__(parent)
        self.running_thread = False
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)
        # self.full_cols = ['requestId', 'processStatus', 'externalIdPrefix', 'totalTestedTags', 'passedTags',
        #                   'failedOfflineTags', 'failedPpAndShipmentTags', 'yield', 'failedSerializationQty',
        #                   'corruptedTagsQty', 'duplicationsQty', 'numOfCommonRunNames', 'commonRunNames',
        #                   'firstExternalId', 'lastExternalId', 'gapsTagsQty', 'gapsTags', 'uploadedAt']
        label = ctk.CTkLabel(self, text="Shipment Approval Requests", font=("Arial", 28, "bold"))
        label.pack(pady=50)
        if self.parent.requests is None:
            self.parent.requests = Requests(self.parent)
        # df = self.parent.df
        self.tree = self.parent.create_tree_view(self, self.parent.requests.get_df(DISPLAY_COLS), equal_width=False)
        self.tree.tag_configure('red', foreground='#d44e2a')
        self.tree.tag_configure('green', foreground='#39a987')
        self.tree.tag_configure('yellow', foreground='#FFBF00')
        self.tree.tag_configure('orange', foreground='orange')
        self.tree.pack(pady=20, padx=20)
        self.color_requests()

        btn = ctk.CTkButton(master=self, text="Request Details", command=self.request_details, width=220,
                            font=('Helvetica', 14))
        btn.place(x=self.parent.W / 2 - 110, y=self.parent.H - 150)

        btn = ctk.CTkButton(master=self, text="Open Full Data in Excel", command=lambda : open_csv_with_excel("data/requests.csv"), width=220,
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
        if self.tree.item(item, "values")[2] != 'processed':
            self.parent.show_error_popup("The Request has not been Processed Yet!")
            return
        request_id = self.tree.item(item, "values")[0]
        self.parent.show_request_details_page(request_id, self)

    def color_requests(self):
        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, "values")
            if values[2] in ('not started', 'wait for the process complete', 'processing', 'sent for processing'):
                self.tree.item(item, tags=('yellow',))
            elif values[2] in ('failed', 'missing commonRunNames'):
                self.tree.item(item, tags=('red',))
            elif values[2] == 'processed' and all([values[i] == 'Passed' for i in range(-1, -7, -1)]):
                self.tree.item(item, tags=('green',))
            elif values[2] == 'processed':
                self.tree.item(item, tags=('red',))


    # def sync(self):
    #     self.parent.requests_df = pd.DataFrame(
    #         [self.tree.item(item, "values") for item in self.tree.get_children()],
    #         columns=self.parent.requests_cols
    #     )

    def update_request(self, item, response):
        request_id = response['requestId']
        self.parent.requests.delete(request_id)
        display_values = self.parent.requests.process_response(response)
        self.tree.item(item, values=display_values)

    def update_requests(self):
        self.running_thread = True
        print('Refreshing Requests!')
        try:
            for item in self.tree.get_children():
                values = self.tree.item(item, "values")
                if values[2] in ('not started', '-', 'processing', 'sent for processing', 'wait for the process complete'):
                    response, status_code = self.parent.get_request_status(values[0])
                    print(response)
                    if status_code == 200:
                        # new_values = [response.get(col, '-') if col in response else response['summaryData'].get(col, '-')
                        #               for col in self.full_cols]
                        self.update_request(item, response)
                    else:
                        values = list(values)
                        values[2] = 'failed'
                        self.update_request(item, values)
                        print(f"API Response {status_code}, Response: {response}")

            self.color_requests()
            self.parent.requests.save_data()
            print('Done Refreshing')
            self.running_thread = False
        except Exception as e:
            self.running_thread = False
            raise e


    def refresh(self):
        if not self.running_thread:
            threading.Thread(target=self.update_requests).start()
        self.after(30000, self.refresh)

    def delete(self, all=False):
        if all:
            items = self.tree.get_children()
        else:
            items = self.tree.selection()
            if len(items) == 0:
                self.parent.show_error_popup("No Request Was Selected!")
                return
        for item in items:
            request_id = self.tree.item(item, "values")[0]
            self.parent.requests.delete(request_id)
            self.tree.delete(item)
        self.parent.requests.save_data()
