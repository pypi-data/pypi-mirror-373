from __future__ import annotations
import sys
from os import path
import pytest

from src.scheduling_and_allocation.model import SemesterType, Course, InvalidSectionNumberForCourseError


class Lab:
    def __lt__(self, other: Lab):
        return True


class Stream:
    def __lt__(self, other: Stream):
        return True


class Teacher:
    def __init__(self):
        self.firstname = ""
        self.lastname = ""
    def __lt__(self, other: Teacher):
        return True


def test_full_constructor():
    """Verifies that constructor parameters are applied correctly"""
    num = "102-NYA-043"
    name = "My Course"
    sem = SemesterType.summer
    alloc = False
    c = Course(num, name, sem, 3.0, alloc)
    assert c.name == name
    assert c.number == num
    assert c.semester == SemesterType.validate(sem)
    assert c.needs_allocation == alloc
    assert c.hours_per_week == 3.0


def test_name_getter():
    """Verifies that name getter works as intended."""
    course = Course("420-101", "Intro to Programming")
    assert course.name == "Intro to Programming"


def test_name_setter():
    """Verifies that name setter works as intended."""
    course = Course("420-101")
    name = "Intro to Programming"
    course.name = name
    assert name == course.name


def test_number_getter():
    """Verifies that the number getter works as intended."""
    course = Course("420-101")
    x=course.number
    assert course.number == '420-101'


def test_add_section_returns_section():
    """Verifies that add_section returns a section"""
    course_2 = Course("420-101")
    section = course_2.add_section(section_id=1)
    assert len(course_2.sections()) == 1
    assert section.course == course_2


def test_add_section_good():
    """Verifies that add_section can add a valid Section to this Course, and that the Course is
    added to the Section itself. """
    course_2 = Course("420-101")
    section = course_2.add_section(section_id=1)
    assert len(course_2.sections()) == 1
    assert section.course == course_2


def test_add_section_duplicate():
    """Verifies that add_section() raises an Exception when trying to add a duplicate of an
    existing Section to the Course. """
    course_1 = Course("abc")
    course_1.add_section(number="dupl", section_id=1)
    with pytest.raises(InvalidSectionNumberForCourseError) as e:
        course_1.add_section(number="dupl", section_id=2)
    assert "section number is not unique" in str(e.value).lower()


def test_get_section_good():
    """Verifies that get_section_by_number() returns an existing section from this Course."""
    course = Course("abc")
    num = "420.AO"
    section = course.add_section(num, section_id=1)
    assert course.get_section_by_number(num).id == section.id


def test_get_section_bad():
    """Verifies that get_section_by_number() doesn't crash the program when trying to get_by_id a Section
    that doesn't exist. """
    course = Course("abc")
    bad_num = "420"
    assert course.get_section_by_number(bad_num) is None


def test_get_section_by_id_good():
    """Verifies that get_section_by_id() works when receiving a valid Section ID as input."""
    course = Course("abc")
    section = course.add_section(section_id=1)
    assert course.get_section_by_id(1).id == section.id


def test_get_section_by_id_bad():
    """Verifies that get_section_by_id() won't crash the program when given a bad ID as input,
    returning None instead. """
    course = Course("abc")
    course.add_section(section_id=1)
    bad_id = 999
    assert course.get_section_by_id(bad_id) is None


def test_get_section_by_name_good():
    """Verifies that get_sections_by_name() returns a list with the correct section when given
    a valid name as input. """
    course = Course("abc")
    name = "test"
    course.add_section("a", name)
    course.add_section("b", name)
    course.add_section("c", "x")
    course.add_section("d", "y")
    sections = course.get_sections_by_name(name)
    assert len(sections) == 2 and "a" in (s.number for s in sections) and "b" in (s.number for s in sections)


def test_get_section_by_name_bad():
    """Verifies that get_sections_by_name() returns an empty tuple when given an invalid
    section name. """
    course = Course("abc")
    course.add_section("",  "test")
    bad_name = "foo"
    sections = course.get_sections_by_name(bad_name)
    assert len(sections) == 0


def test_remove_section_good():
    """Verifies that remove_section() works as intended when asked to remove a legitimate
    Section. """
    course = Course("abc")
    section1 = course.add_section("a")
    section2 = course.add_section("b")
    course.remove_section(section2)
    assert len(course.sections()) == 1
    assert course.sections()[0].id == section1.id


def test_sections():
    """Verifies that sections() returns a list of all the Sections assigned to this Course."""
    course = Course("abc")
    section1 = course.add_section("420", section_id=1)
    section2 = course.add_section("555", section_id=2)
    sections = course.sections()
    assert len(sections) == 2
    assert section1 is not None and section1 in sections
    assert section2 is not None and section2 in sections


def test_number_of_sections():
    """Verifies that number_of_sections() correctly returns the number of Sections assigned
    to this Course. """
    course = Course("abc")
    course.add_section("420", section_id=1)
    course.add_section("555", section_id=2)
    assert course.number_of_sections() == len(course.sections())


def test_sections_for_teacher():
    """Verifies that get_sections_for_teacher() returns a list of all sections featuring this
    teacher in this course. """
    # Note, sections have to have blocks, or this won't work
    course = Course("abc")
    section_1 = course.add_section("420")
    section_2 = course.add_section("421")
    section_1.add_block()
    section_2.add_block()
    teach = Teacher()
    section_1.add_teacher(teach)
    teach_sections = course.get_sections_for_teacher(teach)
    assert section_1 in teach_sections
    assert section_2 not in teach_sections


def test_sections_for_teacher_empty():
    """Verifies that get_sections_for_teacher() returns an empty list if no Teacher has been
    assigned to the Course. """
    course = Course("abc")
    course.add_section("420")
    course.add_section("421")
    teach2 = Teacher()
    teach_sections = course.get_sections_for_teacher(teach2)
    assert len(teach_sections) == 0


def test_has_teacher():
    """Verifies that has_teacher() returns True if the specified Teacher has been assigned to
    this course. """
    # NOTE: section has to have blocks for this to work
    course = Course("abc", "Course 1")
    section = course.add_section("420", "Section 1")
    section.add_block()
    teacher = Teacher()
    section.add_teacher(teacher)
    assert course.has_teacher(teacher)


def test_does_not_have_teacher():
    """Verifies that has_teacher() returns False if the specified Teacher has not been assigned to
    this course. """
    course = Course("abc", "Course 1")
    section = course.add_section("420", "Section 1")
    teacher = Teacher()
    section.add_teacher(teacher)
    teacher_not_assigned = Teacher()
    assert not course.has_teacher(teacher_not_assigned)


def test_blocks_good():
    """Verifies that blocks() returns a list of all Blocks that have been assigned to this
    Course. """
    course = Course("abc")
    section = course.add_section("420")
    block1 = section.add_block()
    block2 = section.add_block()
    blocks = course.blocks()
    assert len(blocks) == 2 and block1 in blocks and block2 in blocks


def test_blocks_bad():
    """Verifies that blocks() returns an empty list when the Sections of this Course contain
    no Blocks. """
    course = Course("abc")
    course.add_section("420", section_id=1)
    blocks = course.blocks
    assert len(blocks()) == 0


def test_str_representation_full():
    """Too difficult to set_default_fonts_and_colours up, and not an issue (for now) if the wrong string is returned"""


def test_description():
    """Verifies that title prints a brief string containing the Course's
    number and name. """
    course = Course("abc", "Course 1")
    description = course.title
    assert f"{course.number}: {course.name}" in description


def test_streams():
    """Verifies that stream_ids() returns a list of all Streams belonging to the Sections of
    this Course. """
    course = Course("abc", "Course 1")
    section = course.add_section("420",  "Section 1")
    stream = Stream()
    section.add_stream(stream)
    streams = course.streams
    assert len(streams()) == 1 and stream in streams()


def test_streams_empty():
    """Verifies that stream_() returns an empty list if no Streams are assigned to this
    Course. """
    course = Course("abc", "Course 1")
    course.add_section("420",  "Section 1")
    streams = course.streams
    assert len(streams()) == 0


def test_has_stream():
    """Verifies that has_stream_with_id() returns true if the passed Stream exists within the Course."""
    course = Course("abc", "Course 1")
    section = course.add_section("420",  "Section 1")
    stream = Stream()
    section.add_stream(stream)
    assert course.has_stream(stream) is True


def test_has_stream_false():
    """Verifies that has_stream() returns false if the Course doesn't contain the passed
    Stream. """
    course = Course("abc", "Course 1")
    course.add_section("420",  "Section 1")
    bad_stream = Stream()
    assert course.has_stream(bad_stream) is False


def test_has_stream_false_doesnt_fail_with_no_sections():
    """Verifies that has_stream() returns false if the Course doesn't contain the passed
    Stream. """
    course = Course("abc", "Course 1")
    bad_stream = Stream()
    assert course.has_stream(bad_stream) is False


def test_assign_teacher_good():
    """Verifies that assign_teacher assigns the passed Teacher to all Sections of the
    Course. """
    # Note: sections requires blocks for this to work
    course = Course("abc", "Course 1")
    section1 = course.add_section("420",  "Section 1")
    section2 = course.add_section("421",  "Section 1")
    section1.add_block()
    section2.add_block()
    teacher = Teacher()
    course.add_teacher(teacher)
    teachers = section1.teachers
    assert len(teachers()) == 1 and teacher in teachers()
    teachers = section2.teachers
    assert len(teachers()) == 1 and teacher in teachers()


def test_assign_lab_good():
    """Verifies that assign_lab can assign a legitimate Lab to all Sections of the Course."""
    course = Course("abc", "Course 1")
    # NOTE: labs are only saved if we have blocks
    section = course.add_section("420",  "Section 1")
    section2 = course.add_section("421",  "Section 1")
    section.add_block()
    section2.add_block()
    lab = Lab()
    course.add_lab(lab)
    assert lab in section.labs()
    assert lab in section2.labs()


def test_assign_stream_good():
    """Verifies that assign_stream can successfully assign a valid Stream to all Sections
    of the Course. """
    course = Course("abc", "Course 1")
    section = course.add_section("420",  "Section 1")
    section2 = course.add_section("421", "Section 1")

    stream = Stream()
    course.add_stream(stream)
    assert len(section.streams()) == 1 and stream in section.streams()
    assert len(section2.streams()) == 1 and stream in section2.streams()


def test_remove_teacher_good():
    """Verifies that remove_teacher can successfully remove the specified Teacher from the
    Course. """
    course = Course("abc", "Course 1")
    teacher_1 = Teacher()
    teacher_2 = Teacher()
    # TODO: This is a bad design because I have to create a section before the teacher is assigned to it.
    section = course.add_section()
    section.add_block()
    course.add_teacher(teacher_1)
    course.add_teacher(teacher_2)
    course.remove_teacher(teacher_1)
    assert len(course.teachers()) == 1 and teacher_1 not in course.teachers()


def test_remove_all_teachers():
    """Verifies that remove_all_teachers() works as intended."""
    course = Course("abc", "Course 1")
    section1 = course.add_section("420",  "Section 1")
    section2 = course.add_section("421",  "Section 1")
    section1.add_block()
    section2.add_block()
    teacher_1 = Teacher()
    teacher_2 = Teacher()
    teacher_3 = Teacher()

    course.add_teacher(teacher_1)
    course.add_teacher(teacher_2)
    course.add_teacher(teacher_3)
    assert len(section1.teachers()) == 3
    assert len(course.teachers()) == 3
    course.remove_all_teachers()
    assert len(course.teachers()) == 0
    assert len(section1.teachers()) == 0
    assert len(section2.teachers()) == 0


def test_remove_stream_good():
    """Verifies that remove_stream() works as intended."""
    course = Course("abc", "Course 1")
    course.add_section("420",  "Section 1")
    course.add_section("421",  "Section 1")

    stream_1 = Stream()
    stream_2 = Stream()
    course.add_stream(stream_1)
    course.add_stream(stream_2)
    course.remove_stream(stream_1)
    assert len(course.streams()) == 1 and stream_1 not in course.streams() and stream_2 in course.streams()


def test_remove_all_streams():
    """Verifies that remove_all_streams() works as intended."""
    course = Course("abc", "Course 1")
    course.add_section("420",  "Section 1")
    stream_1 = Stream()
    stream_2 = Stream()
    course.add_stream(stream_1)
    course.add_stream(stream_2)
    course.remove_all_streams()
    assert len(course.streams()) == 0
