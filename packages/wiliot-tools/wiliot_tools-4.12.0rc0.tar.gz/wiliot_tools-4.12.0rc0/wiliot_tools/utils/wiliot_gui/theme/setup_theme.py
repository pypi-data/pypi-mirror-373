"""
Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""

try:
    import os
    import tkinter as tk
    from PIL import Image, ImageTk
except Exception as e:
    print(f'could not import tkinter: {e}')

FONT_TXT = ("Gudea", 12)
FONT_TXT_WARNING = ("Gudea", 12, "bold")
FONT_BUTTONS = ("Gudea", 16, "bold")
DEBUGGING = False


def setup_theme(style, layout, theme_name='wiliot'):
    if style.theme_use() != theme_name:
        if DEBUGGING:
            print('update_theme') 
        if style.theme_use() not in ['wiliot', 'warning']:
            style.load_user_themes(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'themes.json'))
            style.theme_use('wiliot')

        # Styles for TNotebook (tabs)
        style.configure("TNotebook", tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", padding=[5, 1], background="#ffffff")
        style.map("TNotebook.Tab",
                  background=[("selected", "#0dabb6")],
                  expand=[("selected", [3, 3, 3, 3])],
                  foreground=[("selected", "#ffffff")],
                  font=[("selected", FONT_TXT)],
                  )

        # Styles for TCombobox (dropdown menu)
        style.configure("TCombobox",
                        padding=[5, 1], background="#ffffff", fieldbackground="#ffffff",
                        selectforeground="#ffffff", arrowcolor="#00fffb")

        style.configure('TButton', font=FONT_TXT)
        style.configure('custom.Accent.TButton', font=FONT_BUTTONS)

        # elif theme_name == 'warning':
        # layout.configure(bg='#ff0000')
        # style.configure("TLabelFrame", background="#ff3633", fieldbackground="#ff3633", font=FONT_TXT)
        # style.configure("TCombobox",
        #                 padding=[5, 1], background="#ff3633", fieldbackground="#ff3633",
        #                 selectforeground="#ffffff", arrowcolor="#ffffff", border="#ced4da")
        # style.configure('TButton', font=FONT_TXT, background='#aaaaaa', foreground='#ffffff',
        #                 border="#ced4da", selectbg="#ff0000", selectfg='#ffffff', primary='#aaaaaa')
        # style.configure('custom.Accent.TButton', font=FONT_BUTTONS, background='white', foreground='red',
        #                 border="#ced4da", selectbg="#ff0000", selectfg='#ffffff', primary='#aaaaaa')
        # style.configure('TLabel', font=FONT_TXT, background='#ff0000', foreground='white')
        # else:
        #     raise Exception('theme names supports only: wiliot, warning')

    im_name = 'logo.png' if theme_name == 'wiliot' else 'warning.png'
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), im_name)
    logo_image = Image.open(logo_path)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(layout, image=logo_photo)
    logo_label.grid(row=0, column=0, pady=20, sticky="we")
    return logo_photo, logo_label
    # ****DO NOT TOUCH IT FOR NOW IF YOU'RE CLEANING THE CODE****
    # Styles for TButton
    # theme_style.configure("TButton",
    #                       background="#00fffb", foreground="#2b2221", padding=[5, 5],
    #                       font=("Gudea", 14), borderwidth=0, relief="flat", anchor="center"
    #                       )
    # theme_style.map("TButton",
    #                 background=[("active", "#0ECDFF"), ("disabled", "#f0f0f0")],
    #                 foreground=[("disabled", "#a3a3a3")],
    #                 relief=[("pressed", "sunken"), ("!pressed", "raised")],
    #                 bordercolor=[("focus", "#000000")],
    #                 highlightbackground=[("focus", "#0000ff")],
    #                 highlightcolor=[("focus", "#2b2221")]
    #                 )
