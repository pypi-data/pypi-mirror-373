import threading
from owner_change_utils import *


class RequestDetails(ctk.CTkFrame):

    def __init__(self, parent, show_page_callback, request_id=None):
        super().__init__(parent)
        self.tags_df = None
        self.parent = parent
        self.show_page_callback = lambda: show_page_callback(self)
        self.tree = None
        self.request_id = request_id

        label = ctk.CTkLabel(self, text="Request Details", font=("Arial", 28, "bold"))
        label.pack(pady=50)
        show_img(self)
        self.tags_cols = ['tagId', 'status', 'comment']
        ctk.CTkLabel(self, text="Reels Details", font=("Arial", 25)).place(x=250, y=100)
        ctk.CTkLabel(self, text="Tags Details", font=("Arial", 25)).place(x=750, y=100)
        reels_df = pd.read_csv(f"data/{request_id}.csv")
        if "To Owner" in reels_df:
            reels_df = reels_df.drop("To Owner", axis=1)
        for col in ['Total Tags', 'Passed', 'Failed']:
            reels_df[col] = '-'
        self.tree = self.parent.create_tree_view(self, reels_df, equal_width=False, width=700, height=25)
        self.tree.place(x=50, y=150)
        self.tree.bind("<<TreeviewSelect>>", self.update_tags_df)

        self.tags_tree = self.parent.create_tree_view(self, pd.DataFrame(columns=self.tags_cols), equal_width=False,
                                                      width=600, height=25)
        self.tags_tree.place(x=550, y=150)
        self.selection_box = ctk.CTkComboBox(master=self,
                                             values=['All', 'Succeeded Only', 'Failed Only'], justify='center',
                                             command=self.update_tags_df)
        self.selection_box.place(x=920, y=100)
        self.selection_box.set('Failed Only')
        btn = ctk.CTkButton(self, text="Back", command=self.show_page_callback, width=120)
        btn.place(x=50, y=self.parent.H - 50)

        btn = ctk.CTkButton(master=self, text="Open in Excel",
                            command=lambda: open_csv_with_excel("data/tags_tmp.csv"), width=220,
                            font=('Helvetica', 14))
        btn.place(x=self.parent.W / 2 - 110, y=self.parent.H - 100)

        threading.Thread(target=self.get_tags).start()

    def update_tags_df(self, _):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        values = self.tree.item(selected_item[0], 'values')
        ext_id_prefix = values[0]
        first_tag = str(values[1]).zfill(4)
        last_tag = str(values[2]).zfill(4)
        if ext_id_prefix != 'All Reels':
            filtered_df = self.tags_df.loc[ext_id_prefix]
            if isinstance(filtered_df, pd.Series):
                filtered_df = pd.DataFrame([filtered_df], columns=filtered_df.index)
            filtered_df = filtered_df[
                (filtered_df['tagId'].str[-4:] >= first_tag) &
                (filtered_df['tagId'].str[-4:] <= last_tag)
                ]
        else:
            filtered_df = self.tags_df
        if self.selection_box.get().lower() != 'all':
            filtered_df = filtered_df[filtered_df['status'] == self.selection_box.get().lower().split(" ")[0]]
        self.tags_tree.destroy()
        self.tags_tree = self.parent.create_tree_view(self, pd.DataFrame(filtered_df[self.tags_cols]),
                                                      equal_width=False, width=600, height=25)
        self.tags_tree.place(x=550, y=150)
        self.update_colors_tags()
        self.update_colors_reels()

    def get_tags(self):
        self.tags_df = self.parent.get_request_tags_info(self.request_id)
        fails_path = os.path.join("data", self.request_id + "_tags.csv")
        if os.path.exists(fails_path):
            fails_df = pd.read_csv(fails_path)
            self.tags_df = pd.merge(left=self.tags_df, right=fails_df, left_on='tagId', right_on='external_id', how='left')
            self.tags_df['comment'] = self.tags_df['fail_bin_str']
        self.tags_tree.destroy()
        self.tags_df['comment'] = self.tags_df['comment'].apply(lambda x: '-' if str(x).lower() == 'nan' else x)
        self.tags_tree = self.parent.create_tree_view(self, pd.DataFrame(columns=self.tags_cols), equal_width=False,
                                                      width=600, height=25)
        self.tags_tree.place(x=550, y=150)
        self.tags_df['prefix'] = self.tags_df['tagId'].str[:-5]
        self.tags_df = self.tags_df.set_index('prefix')
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            ext_id_prefix = values[0]
            first_tag = str(values[1]).zfill(4)
            last_tag = str(values[2]).zfill(4)
            filtered_df = self.tags_df.loc[ext_id_prefix]
            if isinstance(filtered_df, pd.Series):
                filtered_df = pd.DataFrame([filtered_df], columns=filtered_df.index)
            total_tags_df = filtered_df[
                (filtered_df['tagId'].str[-4:] >= first_tag) &
                (filtered_df['tagId'].str[-4:] <= last_tag)
                ]
            passed_tags_df = total_tags_df[(total_tags_df['status'] == 'succeeded')]
            failed_tags_df = total_tags_df[(total_tags_df['status'] == 'failed')]
            new_values = list(values)[:3] + [len(total_tags_df), len(passed_tags_df), len(failed_tags_df)]
            self.tree.item(item, values=new_values)
        passed_tags_df = self.tags_df[(self.tags_df['status'] == 'succeeded')]
        failed_tags_df = self.tags_df[(self.tags_df['status'] == 'failed')]
        item_id = self.tree.insert("", 0, values=["All Reels", '-', '-', len(passed_tags_df) + len(failed_tags_df),
                                                  len(passed_tags_df), len(failed_tags_df)])
        self.tree.selection_set(item_id)
        self.update_colors_tags()
        self.update_colors_reels()

    def update_colors_tags(self):
        try:
            self.tags_tree.tag_configure('red', foreground='#d44e2a')
            self.tags_tree.tag_configure('green', foreground='#39a987')
            self.tags_tree.tag_configure('yellow', foreground='#FFBF00')
            self.tags_tree.tag_configure('orange', foreground='orange')
        except:
            pass
        for i, item in enumerate(self.tags_tree.get_children()):
            values = self.tags_tree.item(item, "values")
            if values[1] == 'failed':
                self.tags_tree.item(item, tags=('red',))
            elif values[1] == 'succeeded':
                self.tags_tree.item(item, tags=('green',))

    def update_colors_reels(self):
        try:
            self.tree.tag_configure('red', foreground='#d44e2a')
            self.tree.tag_configure('green', foreground='#39a987')
            self.tree.tag_configure('yellow', foreground='#FFBF00')
            self.tree.tag_configure('orange', foreground='orange')
        except:
            pass
        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, "values")
            if values[3] != '-' and int(values[4]) == int(values[3]):
                self.tree.item(item, tags=('green',))
            elif values[3] != '-' and int(values[5]) == int(values[3]):
                self.tree.item(item, tags=('red',))
            elif values[3] != '-' and int(values[5]) > 0:
                self.tree.item(item, tags=('orange',))
