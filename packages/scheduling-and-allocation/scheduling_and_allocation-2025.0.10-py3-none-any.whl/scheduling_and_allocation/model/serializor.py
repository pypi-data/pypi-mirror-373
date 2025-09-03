from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING, Iterable

import csv

from . import TimeSlot
from .enums import ResourceType, SemesterType
from .enums import WeekDay

# stuff that we need just for type checking, not for actual functionality

if TYPE_CHECKING:
    from .block import Block
    from .stream import Stream
    from .section import Section
    from .teacher import Teacher
    from .lab import Lab
    from .course import Course
    from .schedule import Schedule


# TODO: not saving or reading synced blocks

class CSVSerializor:
    last_line_number_read:int  = -1
    last_line_read:str = ""

    # ============================================================================
    # write csv file
    # ============================================================================
    @staticmethod
    def write(schedule: Schedule, file: str):
        """Write all the details of the schedule to a file, throws an exception if the file cannot be written to"""

        with open(file, 'w', newline='') as f:
            w = csv.writer(f, delimiter=',',
                           quotechar='|', quoting=csv.QUOTE_MINIMAL)

            # --------------------------------------------------------------------
            # write all the 'collectables' first
            # --------------------------------------------------------------------
            w.writerow([None, 'number', 'description'])
            for lab in sorted(schedule.labs()):
                w.writerow(["lab", lab.number, lab.description])
                for unavail in lab.unavailable_slots():
                    w.writerow(["unavailable", "", unavail.day, unavail.start, unavail.duration,
                                int(unavail.movable)])
            w.writerow([])

            w.writerow([None, 'number', 'description'])
            for stream in sorted(schedule.streams()):
                w.writerow(["stream", stream.number, stream.description])
            w.writerow([])

            w.writerow([None, 'number', 'first name', 'last name', 'department', 'release'])
            for teacher in sorted(schedule.teachers(), key=lambda x: x.number):
                w.writerow(
                    ["teacher", teacher.number, teacher.firstname, teacher.lastname,
                     teacher.department, teacher.release])
            w.writerow([])

            # --------------------------------------------------------------------
            # courses/sections/blocks
            # --------------------------------------------------------------------
            w.writerow([])
            w.writerow([None, None, 'DESCRIPTION', 'OF', 'FIELDS'])
            w.writerow([None, 'number', 'name', 'semester', 'needs allocation', 'hours_per_week', 'COURSE'])
            w.writerow([None, 'id', 'number', 'name', 'students', 'SECTION'])
            w.writerow([None, 'id', 'day', 'start', 'duration', 'movable', 'BLOCK'])
            w.writerow([])
            for course in sorted(schedule.courses()):
                w.writerow(["course", course.number, course.name, course.semester.value,
                            int(course.needs_allocation), course.hours_per_week])

                for section in course.sections():
                    w.writerow([])
                    w.writerow(["section", None, section.number, section.name, section.num_students])

                    for s in section.streams():
                        w.writerow(["add_stream", s.number])

                    for block in section.blocks():
                        w.writerow(["add_block", None, block.day.name, block.start,
                                    block.duration, int(block.movable)])
                        for teacher in sorted(block.teachers(), key=lambda t: t.number):
                            w.writerow(["add_block_teacher", teacher.number])
                        for lab in sorted(block.labs(), key=lambda ll: ll.number):
                            w.writerow(["add_lab", lab.number])

                    if len(section.section_defined_teachers()) != 0:
                        w.writerow([])
                        w.writerow([None, None, None, 'assigne allocation, but not assigned to any blocks'])
                        w.writerow([None, 'id', 'allocation'])
                        for teacher in sorted(section.section_defined_teachers(), key=lambda t: t.number):
                            w.writerow(["add_section_teacher", teacher.number, section.get_teacher_allocation(teacher)])

                w.writerow([])

    # ============================================================================
    # read from CSV file
    # ============================================================================
    @staticmethod
    def read_file(schedule: Schedule, file: str):
        """Parse the details of a schedule from a file, throws an exception if the file cannot be read from"""

        CSVSerializor.last_line_number_read = -1
        CSVSerializor.last_line_read = ""

        with open(file, 'r', newline='') as f:
            reader = csv.reader(f, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            CSVSerializor._parse_schedule_info(schedule, reader)

        schedule.calculate_conflicts()

    # ============================================================================
    # parse the csv file from an iterable of lists
    # ============================================================================
    @classmethod
    def _parse_schedule_info(cls, schedule: Schedule, reader: Iterable):
        current_obj: Any = None
        course_obj: Optional[Course] = None
        section_obj: Optional[Section] = None
        block_obj: Optional[Block] = None

        for line_number, row in enumerate(reader, start=1):
            CSVSerializor.last_line_number_read = line_number
            CSVSerializor.last_line_read = row

            if not row or row[0] == "":
                continue

            match row[0]:
                # -------------------------------------------------------------
                # collections (teachers, labs, streams
                # -------------------------------------------------------------
                case "lab":
                    (num, descr) = row[1:3]
                    current_obj = schedule.add_update_lab(number=num, description=descr)

                case "unavailable" if current_obj.resource_type == ResourceType.lab:
                    (day, start, duration, movable) = row[1:5]
                    current_obj.add_unavailable_slot(TimeSlot(
                        day=WeekDay.get_from_string(day), start=start, duration=float(duration), movable=bool(int(movable))))

                case 'stream':
                    (number, descr) = row[1:3]
                    current_obj = schedule.add_update_stream(number=number, description=descr)

                case 'teacher':
                    (number, fname, lname, dept, release) = row[1:6]
                    current_obj: Teacher = schedule.add_update_teacher(firstname=fname, lastname=lname, department=dept,
                                                                teacher_id=number)
                    current_obj.release = float(release)

                # -------------------------------------------------------------
                # courses/sections/blocks
                # -------------------------------------------------------------
                case 'course':
                    (number, name, semester, allocation, hours) = row[1:6]
                    course_obj: Course = schedule.add_update_course(number=number,
                                                                    name=name,
                                                                    semester=SemesterType(int(semester)),
                                                                    needs_allocation=bool(int(allocation)),
                                                                    hours = hours)

                case 'section' if course_obj is not None:
                    (number, name, students) = row[2:5]
                    section_obj: Section = course_obj.add_section(number=number, name=name)
                    section_obj.num_students = int(students)

                case "add_stream" if section_obj is not None:
                    s: Optional[Stream] = schedule.get_stream_by_number(row[1])
                    if s is not None:
                        section_obj.add_stream(s)

                case "add_section_teacher" if section_obj is not None:
                    t: Optional[Teacher] = schedule.get_teacher_by_number(row[1])
                    if t is not None:
                        section_obj.add_teacher(t)
                        if len(row) > 2 and row[2] != '':
                            section_obj.set_teacher_allocation(t, float(row[2]))

                case "add_block" if section_obj is not None:
                    (day, start, duration, movable) = row[2:6]
                    x = WeekDay.get_from_string(day)
                    block_obj: Block = section_obj.add_block(
                        day=WeekDay.get_from_string(day), start=float(start), duration=float(duration),
                                 movable=bool(int(movable)))

                case "add_block_teacher" if block_obj is not None:
                    t: Optional[Teacher] = schedule.get_teacher_by_number(row[1])
                    if t is not None:
                        block_obj.add_teacher(t)

                case "add_lab" if block_obj is not None:
                    l: Lab = schedule.get_lab_by_number(row[1])
                    if l is not None:
                        block_obj.add_lab(l)

