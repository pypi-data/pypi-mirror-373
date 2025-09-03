import pytest

from src.scheduling_and_allocation.model import Teacher


# ============================================================================
# Stream
# ============================================================================
def test_dept_getter():
    teacher = Teacher("Jane", "Doe", "CompSci")
    assert teacher.department == "CompSci"


def test_dept_setter():
    teacher = Teacher("Jane", "Doe", "CompSci")
    teacher.department = "Mathematics"
    assert teacher.department == "Mathematics"


def test_firstname_getter():
    teacher = Teacher("Jane", "Doe", "CompSci")
    assert teacher.firstname == "Jane"


def test_lastname_getter():
    teacher = Teacher("Jane", "Doe", "CompSci")
    assert teacher.lastname == "Doe"


def test_release_setter_getter():
    teacher = Teacher("Jane", "Doe", "CompSci")
    teacher.release = 11.3
    assert teacher.release == 11.3


def test_string_representation_short():
    teacher = Teacher("Jane", "Doe", "CompSci")
    assert str(teacher) == f"{teacher.firstname} {teacher.lastname}"


def test_firstname_setter_good():
    """Verifies that firstname setter can set_default_fonts_and_colours a valid first name."""
    teach = Teacher("John", "Smith")
    new_f_name = "Bob"
    teach.firstname = new_f_name
    assert new_f_name == teach.firstname


def test_firstname_setter_with_spaces():
    """Verifies that firstname setter can set_default_fonts_and_colours a valid first name which has spaces."""
    teach = Teacher("John", "Smith")
    new_f_name = "Bob Blue"
    teach.firstname = new_f_name
    assert new_f_name == teach.firstname


def test_firstname_setter_bad():
    """Verifies that firstname setter doesn't change for invalid input (empty strings)."""
    teach = Teacher("John", "Smith")
    bad_name = " "
    teach.bad_name = bad_name
    assert teach.firstname == "John"


def test_lastname_setter_good():
    """Verifies that the lastname setter can set_default_fonts_and_colours a valid (non-empty) last name for the Teacher."""
    teach = Teacher("John", "Smith")
    new_l_name = "Forstinger"
    teach.lastname = new_l_name
    assert new_l_name == teach.lastname


def test_lastname_setter_with_spaces():
    """Verifies that the lastname setter can set_default_fonts_and_colours a valid
    (non-empty) last name (with spaces) for the Teacher."""
    teach = Teacher("John", "Smith")
    new_l_name = "Forstinger Blue"
    teach.lastname = new_l_name
    assert new_l_name == teach.lastname
