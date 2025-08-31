import pandas as pd

from config import FULL_COLUMNS, DISPLAY_COLS


class Requests:

    def __init__(self, parent):
        self.df = None
        self.read_local_file()
        self.parent = parent

    def read_local_file(self):
        try:
            self.df = pd.read_csv('data/requests.csv', index_col=0, dtype=str)
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=FULL_COLUMNS)
        # self.load_df()

    def get_df(self, cols):
        return self.df[cols]

    def delete(self, request_id):
        self.df = self.df[self.df['requestId'] != request_id]

    def add_row(self, row, cols=FULL_COLUMNS):
        new_row_df = pd.DataFrame([row], columns=cols)
        self.df = pd.concat([new_row_df, self.df]).reset_index(drop=True)
        return tuple(new_row_df[DISPLAY_COLS].iloc[0])

    def process_response(self, response):
        row = {}
        for i, col in enumerate(FULL_COLUMNS):
            if col in response:
                row[col] = response[col]
            elif "summaryData" in response and col in response["summaryData"]:
                row[col] = response["summaryData"][col]
            elif col.endswith("otherIssuesQty") and row["yield"] != "-":
                row[col] = row["failedPpAndShipmentTags"] - row["duplicationsQty"] - row["corruptedTagsQty"] - row["failedSerializationQty"]
            elif col.endswith("sampleTestStatus") and row["yield"] != "-":
                if "sampleTests" in response and len(response["sampleTests"]) > 0 and len([test for test in response["sampleTests"] if test['failBinStr'] == 'PASS']):
                    row[col] = 'Passed'
                else:
                    row[col] = 'Failed'
            elif col.endswith("Status") and row["yield"] != "-" and not col.startswith("yield"):
                if row[FULL_COLUMNS[i-1]] > 0:
                    row[col] = 'Failed'
                else:
                    row[col] = 'Passed'
            elif "sampleTest" in col and row['yield'] != "-":
                res_col = col.replace("sampleTest", "")
                res_col = res_col[0].lower() + res_col[1:]
                if "sampleTests" in response and len(response["sampleTests"]) > 0 and res_col in response["sampleTests"][0]:
                    if 'Avg' in col:
                        row[col] = ", \n".join([str(round(test[res_col], 2)) for test in response["sampleTests"]])
                    else:
                        row[col] = ", \n".join([str(test[res_col]) for test in response["sampleTests"]])
                else:
                    row[col] = "No Test"
            elif "commonRunNames" in response["summaryData"] and col == 'reelName':
                row[col] = response["summaryData"]["commonRunNames"].split("_20")[0]
            else:
                row[col] = "-"
        if row['yield'] != '-':
            row['yieldStatus'] = 'Passed' if float(row['yield'].replace("%", "")) >= 90 else 'Failed'
            row['customerApproval'] = 'Passed' if all([v == 'Passed' for k, v in row.items() if k.endswith('Status') and not k.startswith('process')]) else 'Failed'
            row['tadbikApproval'] = 'Passed' if float(row['yield'].replace("%", "")) >= 60 and row['sampleTestTestedTags'] != "No Test" else 'Failed'
        self.add_tags_ids(row)
        return self.add_row(row)

    def add_tags_ids(self, row):
        try:
            if row['processStatus'] != 'processed':
                return
            if row["failedPpAndShipmentTags"] == 0:
                df = pd.DataFrame(columns=['reason', 'external_id'])
            else:
                df = self.parent.get_request_tags_info(row['requestId'])
            for col in ['serializationTags', 'corruptedTags', 'duplicationTags']:
                row[col] = list(df[df['reason'].str.startswith(col.replace("Tags", ""))]['external_id'])
                df = df[~df['reason'].str.startswith(col.replace("Tags", ""))]
            row['otherIssuesTags'] = list(zip(df['external_id'], df['reason']))
        except Exception as e:
            print(e)
            row['processStatus'] = 'processing'


    def save_data(self):
        self.df.to_csv("data/requests.csv")
