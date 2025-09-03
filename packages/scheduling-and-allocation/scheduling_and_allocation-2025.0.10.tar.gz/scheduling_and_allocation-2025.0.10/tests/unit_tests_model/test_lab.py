import pytest
import sys
from os import path

from src.scheduling_and_allocation.model import Lab, TimeSlot, WeekDay


# ============================================================================
# Lab
# ============================================================================
def test_number_getter():
    """Verifies that number getter works as intended."""
    num = "R-101"
    lab = Lab(num)
    assert lab.number == num


def test_descr_getter():
    """Verifies that Lab's name getter works as intended."""
    room = "R-101"
    descr = "Worst place in the world."
    lab = Lab(room, descr)
    assert lab.description == descr


def test_descr_setter():
    """Verifies that the name setter works as intended."""
    lab = Lab()
    descr = "Worst place in the world."
    lab.descr = descr
    assert lab.descr == descr


def test_add_unavailable():
    time_slot1 = TimeSlot(WeekDay.Wednesday, 12.5, 3.5, False)
    time_slot2 = TimeSlot(WeekDay.Thursday, 12.5, 3.5, False)
    lab = Lab()
    lab.add_unavailable_slot(time_slot1)
    lab.add_unavailable_slot(time_slot2)
    assert len(lab.unavailable_slots()) == 2


def test_remove_unavailable_good():
    """Verifies that remove_unavailable_slot() can remove a TimeSlot from Lab based on the received
    TimeSlot ID. """
    day = WeekDay.Monday
    start = 8.5
    dur = 2.0
    lab = Lab()
    t1 = lab.add_unavailable_slot(TimeSlot(day, start, dur))
    t2 = lab.add_unavailable_slot(TimeSlot(day, start, dur))
    lab.remove_unavailable_slot(t1)
    assert len(lab.unavailable_slots()) == 1
    assert lab.unavailable_slots()[0] == t2


def test_unavailable():
    """Verifies that unavailable() returns a list of all unavailable TimeSlots for this Lab."""
    day_1 = WeekDay.Monday
    start_1 = 8.5
    dur_1 = 2.0
    day_2 = WeekDay.Tuesday
    start_2 = 10.0
    dur_2 = 1.5
    lab = Lab()
    lu1 = lab.add_unavailable_slot(TimeSlot(day_1, start_1, dur_1))
    lu2 = lab.add_unavailable_slot(TimeSlot(day_2, start_2, dur_2))
    times = lab.unavailable_slots()
    assert len(times) == 2
    assert lu1 in lab.unavailable_slots()
    assert lu2 in lab.unavailable_slots()


def test_unavailable_no_slots():
    """Verifies that unavailable() returns an empty tuple if no TimeSlots have been assigned to
    this Lab. """
    lab = Lab()
    slots = lab.unavailable_slots()
    assert type(slots) is tuple and len(slots) == 0


def test_string_representation_full():
    """Verifies that the string representation returns a string containing the Lab's number and
    title attributes. """
    num = "R-101"
    desc = "Worst place in the world."
    lab = Lab(num, desc)
    to_string = str(lab)
    assert f"{num}: {desc}" in to_string


def test_string_representation_short():
    """Verifies that string representation returns a string containing only the Lab's number if
    it lacks a title attribute. """
    num = "R-101"
    lab = Lab(num)
    desc = str(lab)
    assert num == desc

