import pandas as pd
import pathlib
import datetime

from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui

wg = WiliotGui(params_dict={'folder_path': {'text': 'please select folder to merge', 'value': '', 'widget_type': 'file_input', 'options': 'folder'}},
               title='Mrged Data')

values = wg.run()

folder_base = pathlib.Path(values['folder_path'])
file_list_path = list(folder_base.rglob("*.csv"))

df = pd.DataFrame()
for f in file_list_path:
    if 'merged_data_' in f.name:
        print(f'ignore file: {f} continue to the next file')
        continue
    new_df = pd.read_csv(f)
    new_df.insert(loc=len(new_df.columns), column='fileName', value=f.name.replace('.csv', ''))
    new_df.insert(loc=len(new_df.columns), column='folderName', value=f.parent.name)

    df = pd.concat([df, new_df], ignore_index=True)

df.to_csv(folder_base.joinpath(f'merged_data_{datetime.datetime.now().strftime("%d%m%Y_%H%M%S")}.csv'))
print('done')