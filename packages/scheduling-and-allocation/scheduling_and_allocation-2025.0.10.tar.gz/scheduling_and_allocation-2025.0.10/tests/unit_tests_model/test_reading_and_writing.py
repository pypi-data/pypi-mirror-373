from __future__ import annotations

from filecmp import cmp
from os import path

import pytest

from src.scheduling_and_allocation.model import Schedule


def test_read():
    """stupidest simplest test whatsoever"""

    # reading doesn't crash
    # TODO: not a good test
    schedule = Schedule(path.dirname(__file__) + "/data_test_good_input.csv")



def test_read_write():
    """stupidest simplest test whatsoever"""

    # logic is that what it reads in is saved in the schedule object, so it should print out the
    # same info to the output file

    # TODO: not a good test
    schedule = Schedule(path.dirname(__file__) + "/data_test_good_input.csv")
    teachers_text = list()
    for t in schedule.teachers():
        teachers_text.append(schedule.teacher_details(t))

    schedule.write_file(path.dirname(__file__) + "/data_test_output.csv")
    assert (cmp(path.dirname(__file__) + "/data_test_good_input.csv", path.dirname(__file__) + "/data_test_output.csv"))


# test_read_write()


#schedule = s.Schedule(path.dirname(__file__) + "/test.csv")
def test_schedule_actually_has_stuff_in_it():
    """smoke test to see if schedule is actually populated with data - not validating data though"""
    schedule = Schedule(path.dirname(__file__) + "/data_test_good_input.csv")
    assert len(schedule._teachers) != 0
    assert len(schedule.courses()) != 0
    assert len(schedule.labs()) != 0
    assert len(schedule._streams) != 0

def test_blocks_movable_is_correct():
    schedule = Schedule(path.dirname(__file__) + "/data_test_good_input.csv")
    teacher = schedule.get_teacher_by_number("Bultena_Sandy")
    blocks = schedule.get_blocks_for_teacher(teacher)
    for b in blocks:
        assert b.movable()

