import platform
import json
try:
    from PIL import Image, ImageTk
    import customtkinter as ctk
except Exception as e:
    print(f'could not import tkinter: {e}')
import pandas as pd
import os
import subprocess
from datetime import datetime


def show_img(frame):
    try:
        image = Image.open("resources/wiliot.png")
        image = image.resize((150, 75))
        tk_image = ImageTk.PhotoImage(image)
        image_label = ctk.CTkLabel(frame, text="", image=tk_image)
        image_label.image = tk_image
        image_label.place(x=1220, y=0)
    except:
        print("image was not found")


def can_be_int(value):
    try:
        val = int(value)
        return val < 10000
    except ValueError:
        return False


def create_tags_df(request_df):
    rows = []
    for i, row in request_df.iterrows():
        for x in range(int(row['First Tag']), int(row['Last Tag']) + 1):
            rows.append(row['Ex. ID Prefix'] + "T" + str(x).zfill(4))
    rows = set(rows)
    return pd.DataFrame([[row] for row in rows], columns=['tagId']).sort_values('tagId')


def verify_file(df):
    if not all((df['Ex. ID Prefix'].str.len() >= 3)):
        raise ValueError(f"Not all values for column 'Ex. ID Prefix' are correct\n"
                         "please verify that all values at least 3 letters")

    if not df['First Tag'].apply(can_be_int).all():
        raise ValueError(f"Not all values for column 'First Tag' are numbers and under 10000")

    if not df['Last Tag'].apply(can_be_int).all():
        raise ValueError(f"Not all values for column 'Last Tag' are numbers and under 10000")

    if not df['To Owner'].apply(lambda x: x != "").all():
        raise ValueError(f"To Owner column has empty values")

    for i, row in df.iterrows():
        if str(row['First Tag']).zfill(4) > str(row['Last Tag']).zfill(4):
            raise ValueError(f"First Tag is bigger than Last Tag\n"
                             f"({row['Ex. ID Prefix']}, {row['First Tag']}, {row['Last Tag']})")


def open_csv_with_excel(csv_file_path):
    if not os.path.exists(csv_file_path):
        raise Exception(f"The file {csv_file_path} does not exist.")
    timestamp_now_secs = datetime.now().strftime("%Y%m%d%H%M%S")
    new_path = csv_file_path[:-4]+timestamp_now_secs+".csv"
    pd.read_csv(csv_file_path, index_col=None).to_csv(new_path, index=False)
    try:
        if platform.system() == "Windows":
            subprocess.Popen(["start", "excel", new_path], shell=True)
        elif platform.system() == "Darwin":
            subprocess.call(["open", "-a", "Microsoft Excel", new_path])
        else:
            print("This function is not supported on this operating system.")
    except FileNotFoundError:
        raise Exception("Microsoft Excel is not found. Please make sure Excel is installed on your computer.")
    except Exception as e:
        print(f"An error occurred: {e}")
