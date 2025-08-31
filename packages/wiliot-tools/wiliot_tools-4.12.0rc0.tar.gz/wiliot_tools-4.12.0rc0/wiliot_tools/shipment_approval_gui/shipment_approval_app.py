from shipment_approval_main import ShipmentApprovalApp
import json
try:
    from PIL import Image, ImageTk
    import customtkinter as ctk
except Exception as e:
    print(f'could not import tkinter: {e}')
import pandas as pd
import os
import subprocess
import threading

if __name__ == "__main__":
    app = ShipmentApprovalApp()
    app.mainloop()
