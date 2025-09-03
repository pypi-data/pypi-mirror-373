"""Calculate the CI for a given teacher"""
from __future__ import annotations
from .ci_constants import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model.schedule import Schedule
    from ..model.course import Course
    from ..model.teacher import Teacher

# for debugging
print_flag = False


def debug(*args):
    if not print_flag:
        return
    print(args)

def calculate_ci(teacher:Teacher, schedule: Schedule):
    c = CICalc(teacher, schedule)
    return c.calculate()

class CICalc:
    def __init__(self, teacher:Teacher, schedule: Schedule):
        """
        :param teacher:
        :parm schedule:
        """
        self._reset()
        self.prep_hours = 0
        self.schedule = schedule
        self.teacher = teacher
        self.release = 0

    def _reset(self):
        self.pes = 0
        self.num_preps = 0
        self.hours = 0
        self.students = 0
        self.ntu_students = 0
        self.release = 0
        self.dirty_flag = False

    def calculate(self, ) -> float:
        """
        Calculate the CI for the teacher and schedule specified during the init
        """
        schedule = self.schedule
        teacher = self.teacher

        courses: list[Course] = [c for c in schedule.courses() if c.has_allocated_teacher(teacher)]

        self._reset()
        self.release = teacher.release or 0

        debug("")
        debug("")
        debug(f"--------- {teacher.firstname}---------")
        debug("courses list")
        for course in courses:
            debug(f"{course.number} {course.name}")
        debug("end list")

        # per course
        for course in courses:
            max_prep_hours = 0
            debug(f"*********** {course.name}")
            hours = 0

            # per section
            for section in course.get_sections_for_allocated_teacher(teacher):
                debug(f"   Section: {section}")
                hours = section.get_teacher_allocation(teacher)
                students = section.num_students

                debug(f"{course.name}, Section: {section.number}, hours: {hours}")

                max_prep_hours = max_prep_hours if max_prep_hours > hours else hours

                self.pes = self.pes + hours * students
                self.students += students
                # Perl ver includes commented hours >= 3 check
                self.ntu_students += students
                self.hours += hours

            self.prep_hours += hours
            self.num_preps += 1

        # return
        total = self._total()
        debug(f"CI {teacher}: {total}")
        return total

    def _total(self) -> float:

        # ------------------------------------------------------------------------
        # PES (based on # of students and contact hours)
        # ------------------------------------------------------------------------
        CI_student = self.pes * PES_FACTOR
        debug(f"PES: {self.pes}\nStudent factor: {CI_student}")

        # bonus if pes is over 415
        surplus = self.pes - PES_BONUS_LIMIT
        bonus = surplus * PES_BONUS_FACTOR if surplus > 0 else 0
        debug(f"Bonus PES > 415: {bonus}")
        CI_student += bonus

        # another bonus if total number of students is over student_bonus_limit
        # (only for courses over 3 hours)
        debug(f"Students {self.students}")
        bonus = self.ntu_students * STUDENT_BONUS_FACTOR if self.ntu_students >= STUDENT_BONUS_LIMIT else 0
        debug(f"Bonus students over 75: {bonus}")
        CI_student += bonus

        # and yet another bonus if number of students is over Crazy student limit
        if self.ntu_students >= STUDENT_CRAZY_BONUS_LIMIT:
            bonus = (self.ntu_students - STUDENT_CRAZY_BONUS_LIMIT) * STUDENT_CRAZY_BONUS_FACTOR
            CI_student += bonus

        # ------------------------------------------------------------------------
        # Preps (based on # of prep hours PER course)
        # ------------------------------------------------------------------------
        CI_preps = self.prep_hours * PREP_FACTOR
        debug(f"Prep Hours {self.prep_hours}\nCI prep: {CI_preps}")

        # bonus if number is the PREP_BONUS_LIMIT
        if self.num_preps == PREP_BONUS_LIMIT:
            CI_preps += self.prep_hours * PREP_BONUS_FACTOR
            debug(f"CI bonus prep: {self.prep_hours * PREP_BONUS_FACTOR}")

        # more bonus if over the limit
        elif self.num_preps > PREP_BONUS_LIMIT:
            CI_preps += self.prep_hours * PREP_CRAZY_BONUS_FACTOR
            debug(f"CI bonus bonus prep: {self.prep_hours * PREP_CRAZY_BONUS_FACTOR}")

        # ------------------------------------------------------------------------
        # Hours (based on contact hours per week)
        # ------------------------------------------------------------------------
        CI_hours = self.hours * HOURS_FACTOR
        debug(f"CI hours: {CI_hours}")

        # ------------------------------------------------------------------------
        # Release
        # ------------------------------------------------------------------------
        CI_release = self.release * CI_FTE_PER_SEMESTER
        debug(f"CI release: {CI_release}")

        # ------------------------------------------------------------------------
        # all done
        # ------------------------------------------------------------------------
        return float(CI_release) + float(CI_hours) + float(CI_preps) + float(CI_student)
