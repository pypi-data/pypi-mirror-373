from __future__ import annotations
import re
import pytest

from src.scheduling_and_allocation.model import Course, Section, WeekDay, ConflictType, Block


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


def init_scenario_and_schedule():
    pass


@pytest.fixture(autouse=True)
def before_and_after():
    pass


class Lab:
    def __lt__(self, other: Lab):
        return True


class Stream:
    def __lt__(self, other: Stream):
        return True


class Teacher:
    def __lt__(self, other: Teacher):
        return True

course = Course()


def test_id():
    """Verifies that the id property works as intended."""
    section = Section(course)
    old_id = section.id
    section = Section(course)
    assert section.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""

    existing_id = 912
    section1 = Section(course, section_id=existing_id)
    assert section1.id == existing_id
    section2 = Section(course)
    assert section2.id == existing_id + 1
    section3 = Section(course, section_id=existing_id - 5)
    assert section3.id == existing_id - 5
    section4 = Section(course)
    assert section4.id == section2.id + 1


# region General & Properties
def test_constructor_default_values():
    """Checks that the constructor uses default values"""
    s = Section(course)
    assert isinstance(s.number, str)
    assert isinstance(s.name, str)


def test_section_created_success():
    """Checks that Section is created correctly"""
    number = "3A"

    name = "My Section"
    s = Section(course, number, name)
    assert s.name == name
    assert s.number == number


def test_hours_are_block_hours():
    """Checks if this section has blocks, it returns the number of blocks hours"""
    s = Section(course)
    hours = 22
    s.course.hours = hours
    block1 = s.add_block(WeekDay.Monday, 9.5, 3)
    block2 = s.add_block(WeekDay.Monday, 10.5, 3.5)
    assert s.hours == (block1.duration + block2.duration)


def test_hours_are_course_hours_if_no_blocks():
    """Checks if this section has blocks, if it doesn't, return course hours"""
    s = Section(course)
    hours = 22
    s.course.hours_per_week = hours
    assert s.hours == s.course.hours_per_week


def test_get_title():
    """Checks that title is retrievable and includes name or number"""
    name = "My Section"
    assert name in Section(course, name=name).title

    number = "3A"
    assert number in Section(course, number=number).title


def test_set_num_students():
    """Checks that num_students can be set_default_fonts_and_colours"""
    s = Section(course)
    num = 20
    s.num_students = num
    assert s.num_students == num

def test_is_conflicted_detects_conflicts_correctly():
    """Checks that the is_conflicted method correctly picks up conflicted_number blocks"""
    s = Section(course)
    block1 = s.add_block(WeekDay.Monday, 10.5, 3)
    block1.add_conflict(ConflictType.LUNCH)
    assert s.is_conflicted()


def test_is_conflicted_detects_ok_correctly():
    """Checks that the is_conflicted method doesn't return false positive"""
    s = Section(course)
    s.add_block(WeekDay.Monday, 13, 2)
    s.add_block(WeekDay.Monday, 13, 2)
    s.add_block(WeekDay.Monday, 13, 2)
    assert not s.is_conflicted()


def test_string_representation_with_valid_name():
    n = "10"
    s = Section(course, number=n, name="For students taking calculus")
    assert re.search(f"{n}" + r".*?For students taking calculus", str(s))


def test_string_representation_with_invalid_name():
    n = "10"
    s = Section(course, number=n, name=f"Section {n}")
    assert str(s) == f"Section {10}"


def test_string_representation_with_no_name():
    n = "10"
    s = Section(course, number=n)
    assert str(s) == f"Section {10}"


# endregion

# region Block
def test_add_block_valid():
    """Checks that a valid blocks can be added"""
    s = Section(course)
    b = s.add_block(WeekDay.Monday, 13, 2)
    assert b in s.blocks()


def test_get_block_by_id_valid():
    """Checks that blocks can be retrieved by id"""
    s = Section(course)
    b1 = s.add_block(WeekDay.Monday, 13, 2)
    b1_id = b1.id
    s.add_block(WeekDay.Tuesday, 12, 5)
    assert s.get_block_by_id(b1_id) == b1


def test_get_block_by_id_invalid():
    """Checks that None is returned when get_block_by_id is passed a non-blocks id"""
    s = Section(course)
    assert s.get_block_by_id(-1) is None


def test_remove_block_valid():
    """Checks that when passed a valid blocks, it will be removed"""
    s = Section(course)
    b1 = s.add_block(WeekDay.Monday, 13, 2)
    b2 = s.add_block(WeekDay.Monday, 13, 2)
    s.remove_block(b1)
    assert b1 not in s.blocks()
    assert b2 in s.blocks()


# endregion

# region Lab

def test_assign_lab_valid():
    """Checks that a valid lab can be added, if there is a block"""
    s = Section(course)
    s.add_block(WeekDay.Monday, 13, 2)
    lab = Lab()
    s.add_lab(lab)
    assert lab in s.labs()


def test_remove_lab_valid():
    """Checks that when passed a valid lab, it will be removed & deleted"""
    s = Section(course)
    s.add_block(WeekDay.Monday, 13, 2)
    lab = Lab()
    s.add_lab(lab)
    s.remove_lab(lab)
    assert lab not in s.labs()


def test_remove_lab_not_there():
    """Checks that when passed not-included lab, it will still be 'removed' """
    s = Section(course)
    s.add_block(WeekDay.Monday, 13, 2)
    lab = Lab()
    s.remove_lab(lab)
    assert lab not in s.labs()


# endregion

# region Teacher

def test_assign_teacher_valid():
    """Checks that a valid teacher can be added"""
    s = Section(course)
    s.add_block()
    t = Teacher()
    s.add_teacher(t)
    assert t in s.teachers()


def test_get_teacher_allocation_valid():
    """Checks that get_teacher_allocation returns the correct allocation hours"""
    s = Section(course)
    t = Teacher()
    hours = 12
    s.add_teacher(t)
    s.set_teacher_allocation(t, hours)
    assert s.get_teacher_allocation(t) == hours


def test_assign_teacher_valid_allocation_hours_default_to_section_hours():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is set_default_fonts_and_colours to section hours"""
    s = Section(course)
    s.add_block()
    course.hours = 15
    t = Teacher()
    s.add_teacher(t)
    assert s.get_teacher_allocation(t) == s.hours
    t2 = Teacher()
    s.add_teacher(t2)
    assert s.get_teacher_allocation(t2) == s.hours

def test_has_teacher_valid():
    """Checks has_teacher returns True if teacher is included"""
    s = Section(course)
    s.add_block()
    t = Teacher()
    s.add_teacher(t)
    assert s.has_teacher(t)


def test_has_teacher_not_found():
    """Checks has_teacher returns False if teacher is not included"""
    s = Section(course)
    s.add_block()
    t = Teacher()
    assert not s.has_teacher(t)

def test_remove_all_deletes_all_teachers():
    """Checks that remove_all_teachers will correctly delete them all"""
    s = Section(course)
    s.add_teacher(Teacher())
    s.add_teacher(Teacher())
    s.add_teacher(Teacher())
    s.remove_all_teachers()
    assert len( s.teachers()) == 0


def test_teachers_in_blocks_in_teachers_property():
    s = Section(course)
    b1: Block = s.add_block(WeekDay.Monday, 13, 1.5)
    b2: Block = s.add_block(WeekDay.Monday, 13, 1.5)
    t1 = Teacher()
    t2 = Teacher()
    t3 = Teacher()
    s.add_teacher(t3)
    s.add_teacher(t1)
    s.add_teacher(t2)

    assert len(s.teachers()) == 3
    assert t1 in s.teachers()
    assert t2 in s.teachers()
    assert t3 in s.teachers()
    assert t1 in b1.teachers()
    assert t3 in b1.teachers()
    assert t2 in b2.teachers()
    assert t3 in b2.teachers()
    assert len(b1.teachers()) == 3
    assert len(b2.teachers()) == 3

def test_remove_teacher_valid():
    """Checks that when passed a valid teacher, it will be removed"""
    s = Section(course)
    s.add_block()
    t = Teacher()
    t2 = Teacher()
    s.add_teacher(t)
    s.add_teacher(t2)
    s.remove_teacher(t)
    assert not s.has_teacher(t)
    assert s.has_teacher(t2)


def test_remove_all_deletes_all_teachers():
    """Checks that remove_all_teachers will correctly delete them all"""
    s = Section(course)
    s.add_block()
    s.add_teacher(Teacher())
    s.add_teacher(Teacher())
    s.add_teacher(Teacher())
    s.remove_all_teachers()
    assert len( s.teachers()) == 0



# -------------------------------------------------------------------------------------------------
# teacher allocation
# -------------------------------------------------------------------------------------------------
def test_section_allocation_no_blocks():
    """Checks that a valid teacher can be added, and that the teacher allocation hours is saved as set"""
    s = Section(course)
    t = Teacher()
    s.set_teacher_allocation(t, 3)
    assert s.get_teacher_allocation(t) == 3

def test_section_allocation_hrs_equals_block_time():
    """If allocation is equal to total block time, then assign teacher to all blocks"""
    s = Section(course)
    b1 = s.add_block(duration=5)
    b2 = s.add_block(duration=2)
    t = Teacher()
    s.set_teacher_allocation(t, 7)
    assert s.get_teacher_allocation(t) == 7
    assert b1.has_teacher(t)
    assert b2.has_teacher(t)

def test_section_allocation_hrs_fits_one_block_time():
    """If allocation is equal to total block time, then assign teacher to all blocks"""
    s = Section(course)
    b1 = s.add_block(duration=5)
    b2 = s.add_block(duration=2)
    t = Teacher()
    s.set_teacher_allocation(t, 5)
    assert s.get_teacher_allocation(t) == 5
    assert b1.has_teacher(t)
    assert not b2.has_teacher(t)

def test_section_allocation_hrs_does_not_any_block_time():
    """If allocation cannot fit properly into combination of blocks, no blocks are set"""
    s = Section(course)
    b1 = s.add_block(duration=5)
    b2 = s.add_block(duration=2)
    t = Teacher()
    s.set_teacher_allocation(t, 1.5)
    assert s.get_teacher_allocation(t) == 1.5
    assert not b1.has_teacher(t)
    assert not b2.has_teacher(t)

def test_section_allocation_hrs_fits_one_block_time_with_leftover():
    """If allocation cannot fit properly into combination of blocks, no blocks are set"""
    s = Section(course)
    b1 = s.add_block(duration=5)
    b2 = s.add_block(duration=2)
    t = Teacher()
    s.set_teacher_allocation(t, 3)
    assert s.get_teacher_allocation(t) == 3
    assert not b1.has_teacher(t)
    assert not b2.has_teacher(t)

def test_section_allocation_hrs_larger_than_sum_block_times():
    """If allocation cannot fit properly into combination of blocks, no blocks are set"""
    s = Section(course)
    b1 = s.add_block(duration=5)
    b2 = s.add_block(duration=2)
    t = Teacher()
    s.set_teacher_allocation(t, 8)
    assert s.get_teacher_allocation(t) == 8
    assert not b1.has_teacher(t)
    assert not b2.has_teacher(t)

def test_section_allocation_preference_given_to_block_with_no_teacher():
    """When assigning blocks, first assign to blocks that have no teacher"""
    s = Section(course)
    b1 = s.add_block(duration=2)
    b2 = s.add_block(duration=2)
    t1 = Teacher()
    t2 = Teacher()
    b1.add_teacher(t2)
    s.set_teacher_allocation(t1, 2)
    assert s.get_teacher_allocation(t1) == 2
    assert not b1.has_teacher(t1)
    assert b2.has_teacher(t1)

def test_section_allocation_preference_given_to_block_with_no_teacher2():
    """When assigning blocks, first assign to blocks that have no teacher"""
    s = Section(course)
    b1 = s.add_block(duration=2)
    b2 = s.add_block(duration=2)
    t1 = Teacher()
    t2 = Teacher()
    b2.add_teacher(t2)
    s.set_teacher_allocation(t1, 2)
    assert s.get_teacher_allocation(t1) == 2
    assert not b2.has_teacher(t1)
    assert b1.has_teacher(t1)

def test_section_allocation_assign_to_block_with_teacher():
    """When assigning blocks, if not possible otherwise, assign to block with teacher"""
    s = Section(course)
    b1 = s.add_block(duration=2)
    b2 = s.add_block(duration=2)
    t1 = Teacher()
    t2 = Teacher()
    s.add_teacher(t2)
    s.set_teacher_allocation(t1, 2)
    assert s.get_teacher_allocation(t1) == 2
    assert ((not b2.has_teacher(t1) and b1.has_teacher(t1)) or
            (b2.has_teacher(t1) and not b1.has_teacher(t1)))

def test_section_allocation_hours_returned_even_if_teacher_assigned_to_section_without_allocation():
    """When assigning blocks, first assign to blocks that have no teacher"""
    s = Section(course)
    b1 = s.add_block(duration=2)
    b2 = s.add_block(duration=2)
    t2 = Teacher()
    s.add_teacher(t2)
    assert s.get_teacher_allocation(t2) == 4

def test_has_allocated_teacher_valid_false_unless_specifically_allocated():
    s = Section(course)
    s.add_block()
    t = Teacher()
    s.add_teacher(t)
    assert s.has_teacher(t)
    assert t not in s.section_defined_teachers()

def test_has_allocated_teacher_valid_true_if_specifically_allocated():
    s = Section(course)
    s.add_block()
    t = Teacher()
    s.set_teacher_allocation(t, 5)
    assert not s.has_teacher(t)
    assert t in s.section_defined_teachers()
    assert s.has_allocated_teacher(t)


def test_remove_allocation_teacher_valid1():
    """Remove teacher removes allocated teacher (whose hrs fit into blocks properly)"""
    s = Section(course)
    hours = 5
    s.add_block(3)
    s.add_block(2)
    t_added_teacher = Teacher()
    t_allocated_teacher = Teacher()
    s.add_teacher(t_added_teacher)
    s.set_teacher_allocation(t_allocated_teacher, hours)
    s.remove_allocation(t_allocated_teacher)
    assert s.get_teacher_allocation(t_allocated_teacher) == 0
    assert not s.has_teacher(t_allocated_teacher)
    assert not s.has_allocated_teacher(t_allocated_teacher)
    assert s.has_teacher(t_added_teacher)

def test_remove_teacher_valid2():
    """Remove teacher removes allocated teacher (whose hrs don't fit into blocks properly)"""
    s = Section(course)
    hours = 7
    s.add_block(3)
    s.add_block(2)
    t_added_teacher = Teacher()
    t_allocated_teacher = Teacher()
    s.add_teacher(t_added_teacher)
    s.set_teacher_allocation(t_allocated_teacher, hours)
    s.remove_allocation(t_allocated_teacher)
    assert s.get_teacher_allocation(t_allocated_teacher) == 0
    assert not s.has_teacher(t_allocated_teacher)
    assert not s.has_allocated_teacher(t_allocated_teacher)
    assert s.has_teacher(t_added_teacher)


def test_remove_teacher_not_remove_allocated_teacher():
    """Checks that when passed a valid allocated teacher, is not removed by simple remove """
    """Remove teacher removes allocated teacher (whose hrs don't fit into blocks properly)"""
    s = Section(course)
    hours = 7
    s.add_block(3)
    s.add_block(2)
    t_added_teacher = Teacher()
    t_allocated_teacher = Teacher()
    s.add_teacher(t_added_teacher)
    s.set_teacher_allocation(t_allocated_teacher, hours)
    s.remove_teacher(t_allocated_teacher)
    assert s.get_teacher_allocation(t_allocated_teacher) == 7
    assert not s.has_teacher(t_allocated_teacher)
    assert s.has_allocated_teacher(t_allocated_teacher)
    assert s.has_teacher(t_added_teacher)



# -------------------------------------------------------------------------------------------------
# stream
# -------------------------------------------------------------------------------------------------

def test_assign_stream_valid():
    """Checks that a valid stream can be added"""
    s = Section(course)
    st = Stream()
    s.add_stream(st)
    assert st in s.streams()


def test_has_stream_valid():
    """Checks has_stream_with_id returns True if stream is included"""
    s = Section(course)
    st = Stream()
    s.add_stream(st)
    assert s.has_stream(st)


def test_has_stream_not_found():
    """Checks has_stream_with_id returns False if stream is not included"""
    s = Section(course)
    st = Stream()
    assert not s.has_stream(st)


def test_remove_stream_valid():
    """Checks that when passed a valid stream"""
    s = Section(course)
    st = Stream()
    s.add_stream(st)
    s.remove_stream(st)
    assert st not in s.streams()


def test_remove_stream_not_there():
    """Checks that when passed not-included stream, it will still be 'removed' """
    s = Section(course)
    st = Stream()
    s.remove_stream(st)
    assert s not in s.streams()


def test_remove_all_deletes_all_streams():
    """Checks that remove_all_streams will correctly delete them all"""
    s = Section(course)
    s.add_stream(Stream())
    s.add_stream(Stream())
    s.add_stream(Stream())
    s.remove_all_streams()
    assert not s.streams()

def test_remove_teacher_from_all_blocks_removes_from_section():
    s=Section(course)
    teacher=Teacher()
    b=s.add_block(1,1,1)
    b2=s.add_block(1,1,1)
    s.add_teacher(teacher)
    assert teacher in b2.teachers()
    assert teacher in b.teachers()

    b.remove_teacher(teacher)
    b2.remove_teacher(teacher)
    assert len(s.teachers()) == 0



# endregion
