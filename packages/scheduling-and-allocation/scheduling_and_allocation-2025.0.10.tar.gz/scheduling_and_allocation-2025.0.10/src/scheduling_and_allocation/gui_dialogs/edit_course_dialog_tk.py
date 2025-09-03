"""Dialog box to edit a 'section' object"""
from __future__ import annotations

import tkinter as tk
import tkinter.messagebox as tk_message_box
import tkinter.simpledialog as simpledialog
from typing import Callable, Literal, TYPE_CHECKING

from ..gui_generics.number_validations import validate_int, entry_float, entry_int, validate_float
from .dialog_utilities import validate_class_times_equals_course_time, \
    get_block_info_from_tk_widgets, refresh_gui_blocks

from ..gui_generics.add_remove_tk import AddRemoveTk
if TYPE_CHECKING:
    from ..model import Lab, Teacher

# =====================================================================================================================
# Edit Course
# - add sections with blocks, teachers, labs
# =====================================================================================================================
class EditCourseDialogTk(simpledialog.Dialog):
    def __init__(self, frame:tk.Frame,
                 edit_or_add: Literal['edit','add'],
                 existing_course_numbers: list = None,
                 *,
                 course_number:str = "",
                 course_name: str = "",
                 course_hours: float = 3.0,
                 course_allocation: bool = True,
                 num_sections: int = 1,
                 assigned_teachers: list[Teacher] = None,
                 non_assigned_teachers: list[Teacher],
                 assigned_labs: list[Lab] = None,
                 non_assigned_labs: list[Lab],
                 current_blocks: list[tuple[str,float,float]] = None,
                 apply_changes: Callable[[str, str, float, bool, int, list, list, list], None]):
        """
        Edit Course  - add sections with blocks, teachers, labs
        :param frame: the parent of the dialog box
        :param edit_or_add: editing or adding a course?
        :param existing_course_numbers: all of the existing course numbers (to prevent duplication)
        :param course_number: course number
        :param course_name: course name
        :param course_hours: hours per week
        :param course_allocation: does the course require a teacher?
        :param num_sections: number of sections of this course
        :param assigned_teachers: which teachers have been assigned to this course
        :param non_assigned_teachers: which teachers have NOT been assigne to this course
        :param assigned_labs: which labs have been assigned to this course
        :param non_assigned_labs: which labs have not been assigned to this course
        :param current_blocks: What blocks (class times) have been assigned
        :param apply_changes: what to call when the user is finished updating their request
        """

        self.top_frame = frame
        self.edit_or_add = edit_or_add
        self.existing_course_numbers = [] if existing_course_numbers is None else existing_course_numbers
        self.course_number_tk = tk.StringVar(value = course_number)
        self.course_name_tk = tk.StringVar(value = course_name)
        self.course_hours_tk = tk.StringVar(value=str(course_hours))
        self.course_allocation_tk = tk.BooleanVar(value=course_allocation)
        self.num_sections_tk = tk.StringVar(value = str(num_sections))
        self._assigned_teachers = assigned_teachers if assigned_teachers is not None else []
        self._non_assigned_teachers = non_assigned_teachers
        self._assigned_labs = assigned_labs  if assigned_labs is not None else []
        self._non_assigned_labs = non_assigned_labs
        self.current_blocks = current_blocks if current_blocks is not None else []
        self._apply_changes = apply_changes


        self.block_tk_variables = []
        self.block_frames = None
        self.course_name = course_name

        dialog_title = "Edit Course" if self.edit_or_add == "edit" else "Add Course"
        super().__init__(frame.winfo_toplevel(), dialog_title)


    # ================================================================================================================
    # The content of the main body of the dialog box
    # ================================================================================================================
    def body(self, frame:tk.Frame):

        # ------------------------------------------------------------------------------------------------------------
        # Course
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame = tk.Frame(frame)
        tk.Label(course_info_frame, text="Course number", anchor='e', width=15).grid(row=0, column=0, sticky='nsew')
        en_course_number = tk.Entry(course_info_frame, textvariable=self.course_number_tk,)
        en_course_number.grid(row=0, column=1, sticky='nsew')
        if self.edit_or_add == 'edit':
            en_course_number.config(state='readonly')
            en_course_number.config(readonlybackground="#bbbbbb", foreground="#555555")

        tk.Label(course_info_frame, text="Course name", anchor='e', width=15).grid(row=1, column=0, sticky='nsew')
        en_course_name = tk.Entry(course_info_frame, textvariable=self.course_name_tk,)
        en_course_name.grid(row=1, column=1, sticky='nsew')

        tk.Label(course_info_frame, text="Hours per week", anchor='e', width=15).grid(row=2, column=0, sticky='nsew')
        en_course_name = entry_float(course_info_frame, textvariable=self.course_hours_tk)
        en_course_name.grid(row=2, column=1, sticky='nsew')

        tk.Label(course_info_frame, text="Needs Allocation", anchor='e', width=15).grid(row=3, column=0, sticky='nsew')
        en_allocation = tk.Checkbutton(course_info_frame, text="", offvalue=False, onvalue=True,
                                       variable=self.course_allocation_tk, width=20, justify='left')
        en_allocation.grid(row=3, column=1, sticky='w')

        # ------------------------------------------------------------------------------------------------------------
        # Sections/Blocks
        # ------------------------------------------------------------------------------------------------------------
        tk.Label(course_info_frame, text="Number of Sections", anchor='e', width=20).grid(row=4, column=0, sticky='nsew')
        description = entry_int(course_info_frame, textvariable=self.num_sections_tk)
        description.grid(row=4, column=1, sticky='nsew')

        self.block_frames = tk.Frame(frame)
        for index, block_info in enumerate(self.current_blocks):
            opt_day = tk.StringVar(value=block_info[0])
            opt_hour = tk.StringVar(value=str(block_info[1]))
            opt_duration = tk.StringVar(value=str(block_info[2]))
            self.block_tk_variables.append((opt_day, opt_hour, opt_duration))

        # ------------------------------------------------------------------------------------------------------------
        # Teacher/Lab/Stream Add/Remove
        # ------------------------------------------------------------------------------------------------------------
        teacher_assignments_frame = tk.Frame(frame)
        AddRemoveTk(teacher_assignments_frame, self._non_assigned_teachers, self._assigned_teachers,
                    "Assign Teacher to all Classes", "Remove Teacher from all Classes",height=10)

        lab_assignments_frame = tk.Frame(frame)
        AddRemoveTk(lab_assignments_frame, self._non_assigned_labs, self._assigned_labs,
                     "Assign Lab to all Classes","Remove Lab from all Classes", height=10)

        # ------------------------------------------------------------------------------------------------------------
        # layout
        # ------------------------------------------------------------------------------------------------------------
        course_info_frame.grid(row=0, column=0)
        self.block_frames.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        teacher_assignments_frame.grid(row=2,column=0, sticky='nsew', padx=5, pady=5)
        lab_assignments_frame.grid(row=3,column=0, sticky='nsew', padx=5, pady=5)

        self.refresh()

        return description

    # ================================================================================================================
    # add a new block
    # ================================================================================================================
    def add_new_block(self):
        self.block_tk_variables.append((tk.StringVar(value="Monday"), tk.StringVar(value="8.0"), tk.StringVar(value="1.5")))
        self.refresh()

    # ================================================================================================================
    # Update gui to reflect current info
    # ================================================================================================================
    def refresh(self):
        refresh_gui_blocks(self)
        tk.Button(self.block_frames, text="Add New Class Time", command=self.add_new_block, padx=5).pack(expand=1, fill='y')

    # ================================================================================================================
    # validate before applying
    # ================================================================================================================
    def validate(self):
        """
        Is the data, as entered by the user, valid?
        :return: True if data is good (changes are applied), false otherwise (nothing happens)
        """
        if self.edit_or_add == 'add':
            if self.course_number_tk.get() in self.existing_course_numbers:
                tk_message_box.showerror("Course Number",f"Course number '{self.course_number_tk.get()}' already exists")
                return False
        if not validate_float(self.course_hours_tk.get(),"Course hours", "The number of hours per week must be a valid float!"):
            return False

        if not validate_int(self.num_sections_tk.get(),"Number of Sections", "The number of sections must be an integer!"):
            return False

        if not validate_class_times_equals_course_time(self.block_tk_variables, float(self.course_hours_tk.get())):
            return False

        return True

    # ================================================================================================================
    # apply changes
    # ================================================================================================================
    def apply(self):
        """apply the changes and close the dialog"""
        new_blocks=get_block_info_from_tk_widgets(self.block_tk_variables)
        self._apply_changes(self.course_number_tk.get(), self.course_name_tk.get(),
                            float(self.course_hours_tk.get()),self.course_allocation_tk.get(),
                            int(self.num_sections_tk.get()), self._assigned_teachers,
                    self._assigned_labs, new_blocks)

