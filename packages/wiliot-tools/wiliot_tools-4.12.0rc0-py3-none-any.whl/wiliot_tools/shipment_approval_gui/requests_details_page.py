import threading
from shipment_approval_utils import *


class RequestDetails(ctk.CTkFrame):

    def __init__(self, parent, show_page_callback, request_id=None):
        super().__init__(parent)
        self.tags_tree = None
        self.tags_df = None
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)
        self.tree = None
        self.request_id = request_id

        label = ctk.CTkLabel(self, text="Request Details", font=("Arial", 28, "bold"))
        label.pack(pady=50)
        show_img(self)
        self.tags_cols = ['external_id', 'reason']
        self.show_tags_df(pd.DataFrame(columns=self.tags_cols))
        btn = ctk.CTkButton(self, text="Back", command=self.show_page_callback, width=120)
        btn.place(x=50, y=self.parent.H - 50)

        btn = ctk.CTkButton(master=self, text="Open in Excel",
                            command=lambda: open_csv_with_excel("data/tags_tmp.csv"), width=220,
                            font=('Helvetica', 14))
        btn.place(x=self.parent.W / 2 - 110, y=self.parent.H - 100)

        threading.Thread(target=self.get_tags).start()

    def show_tags_df(self, df):
        self.tags_tree = self.parent.create_tree_view(self, df, equal_width=True, width=100, height=25)
        self.tags_tree.place(x=50, y=150)

    def get_tags(self):
        self.tags_df = self.parent.get_request_tags_info(self.request_id)
        self.tags_tree.destroy()
        self.tags_df['reason'] = self.tags_df['reason'].apply(lambda x: '-' if str(x).lower() == 'nan' else x)
        self.tags_df['external_id'] = self.tags_df['external_id'].apply(lambda x: '-' if str(x).lower() == 'nan' else x)
        self.show_tags_df(self.tags_df)
        self.update_colors_tags()

    def update_colors_tags(self):
        try:
            self.tags_tree.tag_configure('red', foreground='#d44e2a')
        except:
            pass
        for i, item in enumerate(self.tags_tree.get_children()):
            self.tags_tree.item(item, tags=('red',))
