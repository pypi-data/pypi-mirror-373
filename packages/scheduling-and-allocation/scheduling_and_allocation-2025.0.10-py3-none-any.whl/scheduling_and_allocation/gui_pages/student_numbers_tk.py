from __future__ import annotations
import tkinter as tk
from functools import partial

from ..modified_tk import Scrolled
from ..gui_generics.number_validations import validate_int, entry_int

# =======================================================================================================
# data class for holding info about sections
# =======================================================================================================
class SectionData:
    def __init__(self, section_name, number_of_students, handler):
        self.name = section_name
        self.number_of_students = number_of_students
        self.handler = handler



# =======================================================================================================
# Student Numbers
# =======================================================================================================
class StudentNumbersTk:
    def __init__(self, frame: tk.Frame, data:dict[str, list[SectionData]] = None):
        """
        creates the Panes for each semester
        :param frame:
        :param data: information about the sections. dict[Course Name] = Section Data
        """

        self.frame = frame
        for w in frame.winfo_children():
            w.destroy()

        self.data = data if data is not None else {}
        self._update_handlers = []

        f = Scrolled(
            self.frame,
            "Frame",
            scrollbars='e',
            border=5,
            relief='flat',
        )

        self.pane = f

        # put data into widget
        self.refresh()
        self.pane.bind('<Leave>', func=self.save)

    # -----------------------------------------------------------------------------------------------------------------
    # recreate the gui based on the information in self.data
    # -----------------------------------------------------------------------------------------------------------------
    def refresh(self):
        """
        Refresh the gui
        """
        self._update_handlers.clear()

        if self.pane is None:
            return

        frame = self.pane.widget
        for w in frame.winfo_children():
            w.destroy()

        frame.columnconfigure(1, weight=5)
        frame.columnconfigure(0, weight=1)

        row = 1
        for course_name in self.data.keys():
            tk.Label(frame,
                     text=course_name,
                     anchor='w',
                     width=40
                     ).grid(column=0, row=row, columnspan=2, sticky='nsew', pady=(10,0))
            row += 1

            for section_data in self.data[course_name]:
                tk.Label(frame,
                         width=4,
                         text=section_data.name,
                         anchor='e',
                         ).grid(column=0, row=row, sticky='nsew')
                tk_var = tk.StringVar(value=section_data.number_of_students)
                entry = entry_int(frame, tk_var)
                entry.grid(column=1, row=row, sticky='nw')
                entry.bind("<Return>", lambda e: e.widget.tk_focusNext().focus())
                entry.bind("<FocusIn>", lambda e: self.pane.see(e.widget))

                # create a separate handler for every entry widget, called when
                # this entire widget loses focus (as opposed to every time the data is
                # modified)
                self._update_handlers.append(partial(_update_number, tk_var, section_data.handler))
                row += 1

    # -----------------------------------------------------------------------------------------------------------------
    # called when the user focus for the entry widget is lost
    # -----------------------------------------------------------------------------------------------------------------
    def save(self, *_):
        """Call each save or update handlers.
        Inputs to the handler are
        """
        for handler in self._update_handlers:
            handler()

# =======================================================================================================
# update number
# =======================================================================================================
def _update_number(tk_var: tk.StringVar, handler, *_):
    """
    :param tk_var: the variable holding the data in the entry widget
    :param handler: the presenter defined function to update the section number
    :param _: tk event
    """
    if validate_int(tk_var.get(),"Invalid Int","number of students must be a valid number"):
        handler(int(tk_var.get()))
