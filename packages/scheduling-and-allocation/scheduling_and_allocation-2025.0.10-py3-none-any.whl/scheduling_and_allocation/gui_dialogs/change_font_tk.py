"""
Change the default font size for the application
"""
from __future__ import annotations

import tkinter as tk
from tkinter.simpledialog import Dialog
from tkinter.messagebox import showinfo
from ..Utilities.Preferences import Preferences
from ..modified_tk import TkFonts


class ChangeFont(Dialog):
    def __init__(self, mw: tk.Tk, preferences: Preferences, title="Change Font"):
        self.warning_label = None
        self.label_big = None
        self.label_normal = None
        self.label_small = None
        self.preferences = preferences
        self.font_size_tk = tk.StringVar(value=str(self.preferences.font_size()))
        self.fonts = TkFonts(mw, self.preferences.font_size())

        super().__init__(mw, title)

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

    # ================================================================================================================
    # change the displayed font size
    # ================================================================================================================
    def _change_font(self, number: str, *_):
        if number == "":
            return True
        try:
            int(number)
            self.fonts = TkFonts(self.frame.winfo_toplevel(), int(number))
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
        try:
            font_size = int(self.font_size_tk.get())
            self.preferences.font_size(font_size)
            self.preferences.save()
            showinfo("Changing themes", "Changing fonts will not take affect until "
                                                     "you close and re-open application")

        except ValueError:
            pass
