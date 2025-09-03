from tkinter import *
import os
import sys

from src.scheduling_and_allocation.gui_dialogs.add_edit_block_dialog_tk import AddEditBlockDialogTk
from src.scheduling_and_allocation.model import Schedule

mw=Tk()
frame = Frame(mw)
frame.pack()
mw.geometry("400x400")

schedule = Schedule()

# teachers
t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id="1")
t2 = schedule.add_update_teacher("John", "Doe", teacher_id="2")
t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id="3")
t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id="4")

# labs
l1 = schedule.add_update_lab("P107", "C-Lab")
l2 = schedule.add_update_lab("P322", "Mac Lab")
l3 = schedule.add_update_lab("P325")
l4 = schedule.add_update_lab("BH311", "Britain Hall")
def apply_changes(number, hour, teachers, labs):
    print(number, hour, teachers, labs)

def go_edit():
    db = AddEditBlockDialogTk(frame, "edit", 1.5, [t1, t2, t3], [t4], [l2], [l1, l3, l4], apply_changes)
def go_add():
    db = AddEditBlockDialogTk(frame, "add", 1.5, [t1, t2, t3], [t4], [l2], [l1, l3, l4], apply_changes)

Button(frame, text="Edit Class Time", command=go_edit).pack()
Button(frame, text="Add Class Times", command=go_add).pack()

mw.mainloop()