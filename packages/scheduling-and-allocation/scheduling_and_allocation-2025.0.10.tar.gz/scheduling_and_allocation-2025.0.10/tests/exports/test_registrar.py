from __future__ import annotations

import os

import pytest

from src.scheduling_and_allocation.export.registrars_office import registrars_output
from src.scheduling_and_allocation.model import TimeSlot, Course, Section, Block, Lab, Teacher, ConflictType, Schedule


@pytest.fixture
def schedule1():
    schedule = Schedule()
    schedule.add_update_course("abc","ABC of cooking")

def test_reates_output_file():
    # prepare
    schedule = Schedule()

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 1, "header line was created"

def test_ignores_non_allocated_course():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    s_abc_1.add_teacher(Teacher("Fay","Runaway"))
    c_000 = schedule.add_update_course("000", "Dept Meeting",needs_allocation=False)
    s_000_1 = c_000.add_section()
    s_000_1.add_teacher(Teacher("Fay","Runaway"))
    s_000_1.add_teacher(Teacher("Babe","Ruth"))


    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 2, "only once course is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"


def test_no_teacher_within_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    b_s_abc_1 = s_abc_1.add_block(1,8.5,1.5)

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 2, "only once course is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "830"
    assert data[4] == "1000"
    assert data[5] == "Monday"
    assert data[6] == ""
    assert data[7] == ""

def test_no_teacher_no_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 2, "only once course is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == ""
    assert data[4] == ""
    assert data[5] == ""
    assert data[6] == ""
    assert data[7] == ""

def test_single_teacher_within_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)
    b_s_abc_2 = s_abc_1.add_block(3,11.5,1.5)
    b_s_abc_1.add_teacher(Teacher("Noah","Way"))
    b_s_abc_2.add_teacher(Teacher("Hugh","Bet"))

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 3, "only once course, but two blocks is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "830"
    assert data[4] == "1000"
    assert data[5] == "Tuesday"
    assert data[6] == "Way"
    assert data[7] == "Noah"

    data = rows[2].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "1130"
    assert data[4] == "1300"
    assert data[5] == "Wednesday"
    assert data[6] == "Bet"
    assert data[7] == "Hugh"

def test_single_teacher_no_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    s_abc_1.set_teacher_allocation(Teacher("Teddy","Bear"),3)
    # b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)
    # b_s_abc_2 = s_abc_1.add_block(3,11.5,1.5)
    # b_s_abc_1.add_teacher(Teacher("Noah","Way"))
    # b_s_abc_2.add_teacher(Teacher("Hugh","Bet"))

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 2, "only once course, no blocks is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == ""
    assert data[4] == ""
    assert data[5] == ""
    assert data[6] == "Bear"
    assert data[7] == "Teddy"

def test_multiple_teachers_within_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    # s_abc_1.set_teacher_allocation(Teacher("Teddy","Bear"),3)
    b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)
    b_s_abc_1.add_teacher(Teacher("Noah","Way"))
    b_s_abc_1.add_teacher(Teacher("Hugh","Bet"))

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 3, "only once course, two blocks is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "830"
    assert data[4] == "1000"
    assert data[5] == "Tuesday"
    assert data[6] == "Bet"
    assert data[7] == "Hugh"

    data = rows[2].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "830"
    assert data[4] == "1000"
    assert data[5] == "Tuesday"
    assert data[6] == "Way"
    assert data[7] == "Noah"

def test_multiple_teachers_no_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    s_abc_1.set_teacher_allocation(Teacher("Teddy","Bear"),1.5)
    s_abc_1.set_teacher_allocation(Teacher("Toodle","Loo"),1.5)

    # b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)
    # b_s_abc_1.add_teacher(Teacher("Noah","Way"))
    # b_s_abc_1.add_teacher(Teacher("Hugh","Bet"))

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = fh.readlines()
    assert len(rows) == 3, "only once course, zero blocks, two teachers, is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == ""
    assert data[4] == ""
    assert data[5] == ""
    assert data[6] == "Bear"
    assert data[7] == "Teddy"

    data = rows[2].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == ""
    assert data[4] == ""
    assert data[5] == ""
    assert data[6] == "Loo"
    assert data[7] == "Toodle"

def test_zero_lab_within_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = list(map(str.rstrip,fh.readlines()))
    assert len(rows) == 2, "only once course, one blocks is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "830"
    assert data[4] == "1000"
    assert data[5] == "Tuesday"
    assert data[6] == ""
    assert data[7] == ""
    assert data[8] == ""
    assert data[9] == ""


# handles zero lab with no block
def test_zero_lab_no_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    #b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = list(map(str.rstrip,fh.readlines()))
    assert len(rows) == 2, "only once course, one blocks is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == ""
    assert data[4] == ""
    assert data[5] == ""
    assert data[6] == ""
    assert data[7] == ""
    assert data[8] == ""
    assert data[9] == ""


def test_single_lab_within_block_and_fields_are_good():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)
    b_s_abc_1.add_lab(Lab("P322"))

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = list(map(str.rstrip,fh.readlines()))
    assert len(rows) == 2, "only once course, one blocks is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "830"
    assert data[4] == "1000"
    assert data[5] == "Tuesday"
    assert data[6] == ""
    assert data[7] == ""
    assert data[8] == "P322"
    assert data[9] == ""

# handles multiple labs with block
def test_multiple_labs_with_blocks():
    # prepare
    schedule = Schedule()
    c_abc = schedule.add_update_course("abc", "ABC of cooking")
    s_abc_1 = c_abc.add_section()
    b_s_abc_1 = s_abc_1.add_block(2,8.5,1.5)
    b_s_abc_1.add_lab(Lab("P322"))
    b_s_abc_1.add_lab(Lab("P107"))
    b_s_abc_1.add_lab(Lab("P325"))

    # execute
    filename="dummy.csv"
    if os.path.exists(filename):
        os.remove(filename)
    registrars_output(schedule, filename)

    # validate
    fh = open(filename,"r")
    rows = list(map(str.rstrip,fh.readlines()))
    assert len(rows) == 2, "only once course, one blocks is added to csv file"
    data = rows[1].split(",")
    assert data[1] == "abc", "the course added to the csv file is abd"
    assert data[2] == "1", "section number"
    assert data[3] == "830"
    assert data[4] == "1000"
    assert data[5] == "Tuesday"
    assert data[6] == ""
    assert data[7] == ""
    assert data[8] == "P107"
    assert data[9] == "P322 P325"

