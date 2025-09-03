from functools import partial
import tkinter as tk

from src.scheduling_and_allocation.gui_pages.student_numbers_tk import SectionData, StudentNumbersTk
from src.scheduling_and_allocation.model import Schedule
from src.scheduling_and_allocation.presenter.student_numbers import StudentData

import os

bin_dir: str = os.path.dirname(os.path.realpath(__file__))

file = f"{bin_dir}/../unit_tests_presenter/data_fall.csv"
schedule = Schedule(file)

data: StudentData = StudentData()

def refresh():
    for course in (c for c in schedule.courses() if c.needs_allocation):
        data.add_course(course.title)

        for section in course.sections():
            section_data = SectionData(section.name, section.num_students, partial(data_changed_handler, section))
            data.add_section(course.title, section_data)

    return data

def data_changed_handler(section, number:int):
    section.num_students = number
refresh()


mw = tk.Tk()
frame = tk.Frame(mw)
frame.pack(expand=1, fill='both')

ns = StudentNumbersTk(frame, data.courses)


mw.mainloop()
