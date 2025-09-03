from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter.simpledialog import Dialog

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../../"))
import src.scheduling_and_allocation.modified_tk.InitGuiFontsAndColours as fac

mw = tk.Tk()
mw.geometry("400x400")

class ChangeFont(Dialog):
    def __init__(self, frame:tk.Frame, title="Change Font", font_size: int=10):
        self.warning_label = None
        self.label_big = None
        self.label_normal = None
        self.label_small = None
        self.font_size_tk = tk.StringVar(value=str(font_size))
        self.fonts = fac.TkFonts(frame.winfo_toplevel(), font_size)

        super().__init__(frame.winfo_toplevel(), title)

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:tk.Frame):
        """
        :param frame: the frame where you are gonna put stuff
        """
        subframe = tk.Frame(frame)
        self.frame=frame

        self.label_small:tk.Label = tk.Label(frame, text="Small text: ABC abc 0123", font=self.fonts.small)
        self.label_normal:tk.Label = tk.Label(frame, text="Normal text: ABC abc 0123", font=self.fonts.normal)
        self.label_big:tk.Label = tk.Label(frame, text="Big text: ABC abc 0123", font=self.fonts.big)
        self.warning_label = tk.Label(frame, text="Must restart application for font changes to take effect!!",
                 font=self.fonts.bigbold)

        modify_font = frame.winfo_toplevel().register(self._change_font)
        font_size_label=tk.Label(subframe, text="Font Size:")
        font_size_entry = tk.Entry(subframe, textvariable=self.font_size_tk,
                                   validate='key',
                                   validatecommand=(modify_font, '%P', '%s')
                                   )

        # layout
        self.warning_label.pack(side="top", expand=1, fill='x', pady=20, padx=10)
        subframe.pack(side="top", expand=1, fill='x', pady=20)
        font_size_label.pack(side='left', expand=1, fill='x', padx=10)
        font_size_entry.pack(side='left', expand=1, fill='x', padx=10)

        self.label_small.pack(side='top', expand=1, fill='x', padx=20)
        self.label_normal.pack(side='top', expand=1, fill='x', padx=20)
        self.label_big.pack(side='top', expand=1, fill='x', padx=20)

        return font_size_entry

    def _change_font(self, number: str, *_):
        if number == "":
            return True
        try:
            int(number)

            self.fonts = fac.TkFonts(frame.winfo_toplevel(), int(number))
            self.warning_label.config(font=self.fonts.bigbold)
            self.label_big.config(font=self.fonts.big)
            self.label_small.config(font=self.fonts.small)
            self.label_normal.config(font=self.fonts.normal)
            return True
        except ValueError:
            return False

    # ================================================================================================================
    # validate before applying
    # ================================================================================================================
    def validate(self):
        """
        Is the data, as entered by the user, valid?
        :return: True if data is good (changes are applied), false otherwise (nothing happens)
        """
        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        """apply the changes and close the dialog"""
        pass


frame = tk.Frame(mw)
tk.Label(frame,text="Sample Text").pack()
frame.pack(expand=1, fill='both')
dg = ChangeFont(frame)

mw.mainloop()
