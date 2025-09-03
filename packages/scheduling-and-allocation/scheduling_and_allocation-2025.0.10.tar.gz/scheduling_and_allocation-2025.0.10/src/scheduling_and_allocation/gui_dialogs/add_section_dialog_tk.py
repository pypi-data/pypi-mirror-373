"""Dialog box to edit a 'section' object"""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkFont
from tkinter.simpledialog import Dialog
from typing import Callable

from ..gui_generics.number_validations import validate_int, entry_int
from ..gui_dialogs.dialog_utilities import validate_class_times_equals_course_time, \
    get_block_info_from_tk_widgets, refresh_gui_blocks


# =====================================================================================================================
# Add a section to an existing course
# =====================================================================================================================
class AddSectionDialogTk(Dialog):
    def __init__(self, frame:tk.Frame,
                 *,
                 course_description: str,
                 course_hours: float,
                 apply_changes: Callable[[int, list], None]):
        """
        :param frame: parent frame of this dialog box
        :param course_description: The name of the course
        :param course_hours: How many hours is this course per week
        :param apply_changes: Who ya gonna call (Ghost Busters) to update the schedule with the users' changes
        """

        self.block_tk_variables = []
        self.course_hours = course_hours
        self.current_blocks =  []
        self.block_frames = None
        self.course_description = course_description
        self.top_frame = frame
        self._apply_changes = apply_changes

        self.description = tk.StringVar(value = "")
        self.number_of_sections = tk.StringVar(value="1")

        dialog_title = "Add Section(s)"
        super().__init__(frame.winfo_toplevel(), dialog_title)

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:tk.Frame):

        # ------------------------------------------------------------------------------------------------------------
        # Info
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame = tk.Frame(frame)
        section_info_frame = tk.Frame(frame)
        lbl = tk.Label(course_info_frame,text=self.course_description, anchor='center',width=20)
        lbl.pack(expand=1,fill='both',padx=15,pady=5)
        default_font = tkFont.nametofont(lbl.cget("font"))
        family = default_font["family"]
        size = default_font["size"] + 2
        lbl.config(font=(family, size))

        tk.Label(section_info_frame, text="How many sections?", anchor='e', width=20).pack(side='left', padx=10, pady=5)
        en_number = entry_int(section_info_frame, textvariable=self.number_of_sections)
        en_number.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # Blocks ... there are no blocks, so just set up the frame
        # ------------------------------------------------------------------------------------------------------------
        self.block_frames = tk.Frame(frame)

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame.grid(row=0, column=0)
        section_info_frame.grid(row=1, column = 0)
        self.block_frames.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

        self.refresh()

        return en_number

    # ================================================================================================================
    # refresh blocks
    # ================================================================================================================
    def add_new_block(self):
        """
        Add a new block (class time) to the section
        """
        self.block_tk_variables.append((tk.StringVar(value="Monday"),tk.StringVar(value="8.0"), tk.StringVar(value="1.5")))
        self.refresh()

    def refresh(self):
        """
        redraw all the blocks (class times)
        """
        refresh_gui_blocks(self)
        tk.Button(self.block_frames, text="Add New Class Time", command=self.add_new_block,padx=5).pack(expand=1, fill='y')


    # ================================================================================================================
    # are blocks set up properly?
    # ================================================================================================================
    def validate(self):
        """
        Is the data, as entered by the user, valid?
        :return: True if data is good (changes are applied), false otherwise (nothing happens)
        """
        if not validate_int(self.number_of_sections.get(),"Number of Sections", "Number of sections must be a number!"):
            return False

        if not validate_class_times_equals_course_time(self.block_tk_variables, float(self.course_hours)):
            return False

        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        """apply the changes and close the dialog"""
        new_blocks=get_block_info_from_tk_widgets(self.block_tk_variables)
        self._apply_changes( int(self.number_of_sections.get()), new_blocks )


