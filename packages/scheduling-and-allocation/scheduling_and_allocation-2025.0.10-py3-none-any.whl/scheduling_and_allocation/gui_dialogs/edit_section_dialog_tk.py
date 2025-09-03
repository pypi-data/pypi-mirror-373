"""Dialog box to edit a 'section' object"""
from __future__ import annotations
import re

import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.simpledialog import Dialog
from typing import Callable, TYPE_CHECKING

from .dialog_utilities import validate_class_times_equals_course_time, \
    get_block_info_from_tk_widgets, refresh_gui_blocks
from ..gui_generics.add_remove_tk import AddRemoveTk

if TYPE_CHECKING:
    from ..model import Stream, Lab, Teacher

# =====================================================================================================================
# Edit Section - add blocks, teachers, labs, streams
# =====================================================================================================================
class EditSectionDialogTk(Dialog):
    def __init__(self, frame: tk.Frame,
                 *,
                 course_description: str,
                 section_description: str = "",
                 assigned_teachers: list[Teacher] = None,
                 non_assigned_teachers: list[Teacher],
                 assigned_labs: list[Lab] = None,
                 non_assigned_labs: list[Lab],
                 assigned_streams: list[Stream] = None,
                 non_assigned_streams: list[Stream],
                 current_blocks: list[tuple[str, float, float]] = None,
                 course_hours: float,
                 apply_changes: Callable[[str, list, list, list, list], None]):
        """
        Edit Section - add blocks, teachers, labs, streams
        :param frame: the parent of the dialog box
        :param course_description: Number and name of course
        :param section_description: Description for Section
        :param assigned_teachers: which teachers have been assigned to this section
        :param non_assigned_teachers: which teachers have NOT been assigned to this section
        :param assigned_labs: which labs have been assigned to this section
        :param non_assigned_labs: which labs have not been assigned to this section
        :param assigned_streams: streams which have been assigned to this section
        :param non_assigned_streams: streams which have not been assigned to this section
        :param current_blocks: What blocks (class times) have been assigned
        :param apply_changes: what to call when the user is finished updating their request
        :param course_hours:
        """

        self.block_tk_variables = []
        self.course_hours = course_hours
        self.current_blocks = current_blocks if current_blocks is not None else []
        self.block_frames = None
        self.course_description = course_description
        self.top_frame = frame
        self._assigned_teachers = assigned_teachers if assigned_teachers is not None else []
        self._assigned_labs = assigned_labs if assigned_labs is not None else []
        self._assigned_streams = assigned_streams if assigned_streams is not None else []
        self._non_assigned_teachers = non_assigned_teachers
        self._non_assigned_labs = non_assigned_labs
        self._non_assigned_streams = non_assigned_streams
        self._apply_changes = apply_changes

        self.description = tk.StringVar(value=section_description)

        self.style = ttk.Style(frame.winfo_toplevel())

        dialog_title = "Edit Section"
        super().__init__(frame.winfo_toplevel(), dialog_title)

    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame: tk.Frame):

        # ------------------------------------------------------------------------------------------------------------
        # Info
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame = tk.Frame(frame)
        section_info_frame = tk.Frame(frame)
        lbl = tk.Label(course_info_frame, text=self.course_description, anchor='center')
        lbl.pack(expand=1, fill='both', padx=15, pady=5)
        default_font = tkFont.nametofont(lbl.cget("font"))
        family = default_font["family"]
        size = default_font["size"] + 2
        lbl.config(font=(family, size))
        tk.Label(section_info_frame, text="Section Description", anchor='e', width=20).pack(side='left', padx=10,
                                                                                            pady=5)
        description = tk.Entry(section_info_frame, textvariable=self.description, )
        description.pack(side='left', padx=10, pady=5)

        # ------------------------------------------------------------------------------------------------------------
        # Blocks
        # ------------------------------------------------------------------------------------------------------------
        self.block_frames = tk.Frame(frame)
        for block_info in self.current_blocks:
            opt_day = tk.StringVar(value=block_info[0])
            opt_hour = tk.StringVar(value=str(block_info[1]))
            opt_duration = tk.StringVar(value=str(block_info[2]))
            self.block_tk_variables.append((opt_day, opt_hour, opt_duration))

        # ------------------------------------------------------------------------------------------------------------
        # Teacher/Lab/Stream Add/Remove
        # ------------------------------------------------------------------------------------------------------------
        teacher_assignments_frame = tk.Frame(frame)
        AddRemoveTk(teacher_assignments_frame, self._non_assigned_teachers, self._assigned_teachers,
                    "Assign Teacher to all Classes", "Remove Teacher from all Classes", height=6)

        lab_assignments_frame = tk.Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._non_assigned_labs, self._assigned_labs,
                    "Assign Lab to all Classes", "Remove Lab from all Classes", height=6)

        stream_assignments_frame = tk.Frame(frame)
        AddRemoveTk(stream_assignments_frame, self._non_assigned_streams, self._assigned_streams,
                    "Assign Stream to Section", "Remove Stream from Section", height=6)

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame.grid(row=0, column=0)
        section_info_frame.grid(row=1, column=0)
        self.block_frames.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        teacher_assignments_frame.grid(row=3, column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=4, column=0, sticky='nsew', padx=5, pady=5)
        stream_assignments_frame.grid(row=5, column=0, sticky='nsew', padx=5, pady=5)

        self.refresh()

        return description

    # ================================================================================================================
    # add a new block
    # ================================================================================================================
    def add_new_block(self):
        self.block_tk_variables.append((tk.StringVar(value="Monday"), tk.StringVar(value="8.0"), tk.StringVar(value="1.5")))
        self.refresh()

    # ================================================================================================================
    # update the gui to reflect the number of blocks
    # ================================================================================================================
    def refresh(self):
        refresh_gui_blocks(self)
        tk.Button(self.block_frames, text="Add New Class Time", command=self.add_new_block, padx=5).pack(expand=1, fill='y')

    # ================================================================================================================
    # are blocks set up properly?
    # ================================================================================================================
    def validate(self):
        if not validate_class_times_equals_course_time(self.block_tk_variables, float(self.course_hours)):
            return False
        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        new_blocks = get_block_info_from_tk_widgets(self.block_tk_variables)
        self._apply_changes(self.description.get(), self._assigned_teachers, self._assigned_labs,
                            self._assigned_streams, new_blocks)
