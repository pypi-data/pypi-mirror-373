import csv
import math
from typing import Optional

from ..model import Schedule, Section, Block, Teacher


def time_string(hour) -> str:
    minutes, hours = math.modf(hour)
    return f"{int(hours)}{int(round(minutes*60, 0)):02d}"


def registrars_output(schedule: Schedule, filename: str):
    headers = ["Course Name",
               "Course No.",
               "Section",
               "Start Time",
               "End Time",
               "Day",
               "Teacher Last Name",
               "Teacher First Name",
               "Room",
               "Other Rooms Used"
               ]
    fh = open(filename, "w")

    csv_file = csv.writer(fh)
    csv_file.writerow(headers)

    for course in (c for c in schedule.courses() if c.needs_allocation):
        for section in course.sections():

            # non classroom teaching
            if len(section.blocks()) == 0:
                row = [course.name, course.number, section.number, "","", ""]
                rows = add_teachers(section.section_defined_teachers(), row)
                for row in rows:
                    add_labs(section, row)
                    csv_file.writerow(row)
                continue

            # classroom teaching
            for block in section.blocks():
                row = [course.name, course.number, section.number, time_string(block.start),
                       time_string(block.start + block.duration), block.day.name.capitalize()]
                rows = add_teachers(block.teachers(), row)
                for row in rows:
                    add_labs(section, row)
                    csv_file.writerow(row)
    return ""

def add_labs(object: Section|Block, initial_row: list):
    labs = object.labs()
    if len(labs) == 0:
        initial_row.extend(["",""])
    elif len(labs) == 1:
        initial_row.extend([labs[0].number,""])
    else:
        initial_row.extend([labs[0].number, " ".join((l.number for l in labs[1:]))])

def add_teachers(teachers: tuple[Teacher, ...], initial_row: list) -> list[list[str]]:
    rows = []
    if len(teachers) == 0:
        rows.append(["",""])
    for teacher in teachers:
        rows.append([teacher.lastname, teacher.firstname])
    updated_rows = []
    for row in rows:
        updated_rows.append([*initial_row])
        updated_rows[-1].extend(row)
    return updated_rows

