from __future__ import annotations

from functools import partial

from ..gui_pages.student_numbers_tk import StudentNumbersTk, SectionData
from ..model import Section
from ..model.schedule import Schedule


# =======================================================================================================
# Student Numbers
# =======================================================================================================
class StudentNumbers:
    """StudentNumbers - provides methods / objects for entering number_of_students of students per course per section"""

    # ----------------------------------------------------------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, dirty_method, frame, schedule: Schedule):
        self.dirty_method = dirty_method
        self.frame = frame
        self.data: StudentData = StudentData()
        self.schedule = schedule

        self.refresh()
        self.gui: StudentNumbersTk = StudentNumbersTk(self.frame, self.data.courses)

    # ----------------------------------------------------------------------------------------------------------------
    # gather data
    # ----------------------------------------------------------------------------------------------------------------
    def refresh(self):

        for course in (c for c in self.schedule.courses() if c.needs_allocation):
            self.data.add_course(course.title)

            for section in course.sections():
                section_data = SectionData(section.name, section.num_students, partial(self.data_changed_handler, section))
                self.data.add_section(course.title, section_data)

        return self.data

    # ----------------------------------------------------------------------------------------------------------------
    # data change handler
    # ----------------------------------------------------------------------------------------------------------------
    def data_changed_handler(self, section: Section, number:int):
        section.num_students = number
        self.dirty_method(True)

# =======================================================================================================
# Student Data - create simple data structure to store info
# =======================================================================================================
class StudentData:
    def __init__(self):
        self.courses: dict[str, list[SectionData]] = {}

    def add_course(self, course_name:str):
        self.courses[course_name] = []

    def add_section(self, course_name,  section_data):
        self.courses[course_name].append(section_data)

    def clear(self):
        self.courses.clear()

    def __iter__(self):
        return self.courses


