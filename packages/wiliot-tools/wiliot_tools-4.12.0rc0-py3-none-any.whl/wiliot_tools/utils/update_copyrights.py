from wiliot_tools.utils.wiliot_gui.wiliot_gui import *

current_year = 2025


def update_copyright_year(folder_path, year):
    original_copyright = "Copyright (c) 2016- 2025"
    updated_copyright = f"Copyright (c) 2016- {year}"

    for root_folder, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root_folder, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if original_copyright in content:
                    content = content.replace(original_copyright, updated_copyright)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)


if __name__ == '__main__':
    params_dic = {'folder':
                      {'text': 'Choose folder to update copyrights year',
                       'value': '',
                       'widget_type': 'file_input',
                       'options': 'folder'}}

    gui = WiliotGui(params_dict=params_dic, title='Update Wiliot Copyrights')
    values = gui.run()
    if values['folder'] != '':
        update_copyright_year(values['folder'], current_year)
        popup_message("Copyright year updated in all matching files.")
    else:
        popup_message("Not valid folder")
