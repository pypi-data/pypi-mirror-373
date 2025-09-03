import pytest

from src.scheduling_and_allocation.model import Schedule, Course, Stream, Lab, Teacher, WeekDay


# ============================================================================
# tests
# ============================================================================
def test_constructor():
    schedule = Schedule()
    assert isinstance(schedule, Schedule)


def test_interface():
    schedule = Schedule()
    assert hasattr(schedule, "read_file")
    assert hasattr(schedule, "write_file")

    assert hasattr(schedule, 'add_update_course')
    assert hasattr(schedule, 'add_update_stream')
    assert hasattr(schedule, 'add_update_lab')
    assert hasattr(schedule, 'add_update_teacher')

    assert hasattr(schedule, 'labs')
    assert hasattr(schedule, 'courses')
    assert hasattr(schedule, 'teachers')
    assert hasattr(schedule, 'streams')

    assert hasattr(schedule, 'get_course_by_number')
    assert hasattr(schedule, 'get_lab_by_number')
    assert hasattr(schedule, 'get_stream_by_number')
    assert hasattr(schedule, 'get_teacher_by_name')

    assert hasattr(schedule, 'get_teacher_by_number')

    assert hasattr(schedule, 'remove_teacher')
    assert hasattr(schedule, 'remove_stream')
    assert hasattr(schedule, 'remove_lab')
    assert hasattr(schedule, 'remove_course')

    assert hasattr(schedule, "get_teachers_assigned_to_any_course")
    assert hasattr(schedule, 'get_streams_assigned_to_any_course')
    assert hasattr(schedule, 'get_labs_assigned_to_any_course')
    assert hasattr(schedule, 'get_courses_for_teacher')

    assert hasattr(schedule, 'sections')
    assert hasattr(schedule, 'blocks')

    assert hasattr(schedule, 'get_sections_for_teacher')
    assert hasattr(schedule, 'get_sections_for_stream')
    assert hasattr(schedule, 'get_blocks_for_teacher')
    assert hasattr(schedule, 'get_blocks_in_lab')
    assert hasattr(schedule, 'get_blocks_for_stream')
    assert hasattr(schedule, 'get_blocks_for_obj')

    assert hasattr(schedule, 'clear_all_from_course')
    assert hasattr(schedule, 'calculate_conflicts')


def test_add_course():
    s = Schedule()
    assert len(s._courses) == 0
    c1 = s.add_update_course('420-DBF')
    assert len(s._courses) == 1
    c2 = s.add_update_course('420-ABC')
    assert len(s._courses) == 2
    assert c1.number in s._courses
    assert c2.number in s._courses
    assert isinstance(c1, Course)


def test_add_stream():
    s = Schedule()
    assert len(s._streams) == 0
    c1 = s.add_update_stream('4A')
    assert len(s._streams) == 1
    c2 = s.add_update_stream('4B')
    assert len(s._streams) == 2
    assert c1.number in s._streams
    assert c2.number in s._streams
    assert isinstance(c1, Stream)


def test_add_lab():
    s = Schedule()
    assert len(s._labs) == 0
    c1 = s.add_update_lab('4A')
    assert len(s._labs) == 1
    c2 = s.add_update_lab('4B')
    assert len(s._labs) == 2
    assert c1.number in s._labs
    assert c2.number in s._labs
    assert isinstance(c1, Lab)


def test_add_teacher():
    s = Schedule()
    assert len(s._teachers) == 0
    c1 = s.add_update_teacher('4A', 'Doe')
    assert len(s._teachers) == 1
    c2 = s.add_update_teacher('4B', 'Doe')
    assert len(s._teachers) == 2
    assert c1.number in s._teachers
    assert c2.number in s._teachers
    assert isinstance(c1, Teacher)


def test_return_courses_as_tuple():
    s = Schedule()
    assert len(s.courses()) == 0
    o1 = Course('ABC')
    o2 = Course('ABD')
    s._courses = {o1.number: o1, o2.number: o2}
    assert len(s.courses()) == 2
    assert isinstance(s.courses(), tuple)
    assert o1 in s.courses()
    assert o2 in s.courses()


def test_return_labs_as_tuple():
    s = Schedule()
    assert len(s.labs()) == 0
    o1 = Lab('ABC')
    o2 = Lab('ABD')
    s._labs = {o1.number: o1, o2.number: o2}
    assert len(s.labs()) == 2
    assert isinstance(s.labs(), tuple)
    assert o1 in s.labs()
    assert o2 in s.labs()


def test_return_streams_as_tuple():
    s = Schedule()
    assert len(s.streams()) == 0
    o1 = Stream('ABC')
    o2 = Stream('ABD')
    s._streams = {o1.number: o1, o2.number: o2}
    assert len(s.streams()) == 2
    assert isinstance(s.streams(), tuple)
    assert o1 in s.streams()
    assert o2 in s.streams()


def test_return_teachers_as_tuple():
    s = Schedule()
    assert len(s.teachers()) == 0
    o1 = Teacher('ABC', 'Doe')
    o2 = Teacher('DEF', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2}
    assert len(s.teachers()) == 2
    assert isinstance(s.teachers(), tuple)
    assert o1 in s.teachers()
    assert o2 in s.teachers()


def test_get_course_by_number():
    s = Schedule()
    o1 = Course('ABC')
    o2 = Course('DEF')
    s._courses = {o1.number: o1, o2.number: o2}
    assert o2 == s.get_course_by_number('DEF')
    assert o1 == s.get_course_by_number('ABC')
    assert s.get_course_by_number("boo") is None


def test_get_lab_by_number():
    s = Schedule()
    o1 = Lab('ABC')
    o2 = Lab('DEF')
    s._labs = {o1.number: o1, o2.number: o2}
    assert o2 == s.get_lab_by_number('DEF')
    assert o1 == s.get_lab_by_number('ABC')
    assert s.get_lab_by_number("boo") is None


def test_get_stream_by_number():
    s = Schedule()
    o1 = Stream('ABC')
    o2 = Stream('DEF')
    s._streams = {o1.number: o1, o2.number: o2}
    assert o2 == s.get_stream_by_number('DEF')
    assert o1 == s.get_stream_by_number('ABC')
    assert s.get_stream_by_number("boo") is None


def test_get_teacher_by_name():
    s = Schedule()
    o1 = Teacher('Jane', 'Doe')
    o2 = Teacher('John', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2}
    assert o2 == s.get_teacher_by_name('John', 'Doe')
    assert o2 == s.get_teacher_by_name('JoHn', 'dOe')
    assert o1 == s.get_teacher_by_name('Jane', 'Doe')
    assert s.get_teacher_by_name("Jane", "boo") is None


def test_get_teacher_by_number():
    s = Schedule()
    o1 = Teacher('Jane', 'Doe')
    o2 = Teacher('John', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2}
    assert o2 == s.get_teacher_by_number(o2.number)
    assert o1 == s.get_teacher_by_number(o1.number)
    assert s.get_teacher_by_number("666666") is None


def test_get_teacher_by_id():
    s = Schedule()
    o1 = Teacher('Jane', 'Doe')
    o2 = Teacher('John', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2}
    assert o2 == s.get_teacher_by_number(o2.number)
    assert o1 == s.get_teacher_by_number(o1.number)


def test_remove_course():
    s = Schedule()
    o1 = Course('ABC')
    o2 = Course('DEF')
    s._courses = {o1.number: o1, o2.number: o2}
    s.remove_course(o2)
    assert len(s._courses) == 1
    assert o2 not in s._courses.values()

    # try to remove non-existent course
    s.remove_course(Course("XYZ"))
    assert True


def test_remove_teacher_simple():
    s = Schedule()
    o1 = Teacher('ABC', 'Doe')
    o2 = Teacher('DEF', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2}
    s.remove_teacher(o2)
    assert len(s._teachers) == 1
    assert o2 not in s._teachers.values()

    # try to remove non-existent teacher
    s.remove_teacher(Teacher("XYZ", 'Doe'))
    assert True


def test_remove_teacher_from_courses():
    s = Schedule()
    o1 = Teacher('ABC', 'Doe')
    o2 = Teacher('DEF', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("C2")
    # NOTE: adding teachers is meaningless unless there are sections in the course
    # NOTE: adding teachers is meaningless unless there are blocks in the section
    st1 = c1.add_section("ABC")
    st2 = c2.add_section("DEF")
    st1.add_block()
    st2.add_block()
    c1.add_teacher(o1)
    c1.add_teacher(o2)
    c2.add_teacher(o1)
    c2.add_teacher(o2)

    s.remove_teacher(o2)
    assert len(s._teachers) == 1
    assert o2 not in c1.teachers()
    assert o2 not in c2.teachers()
    assert o1 in c1.teachers()
    assert o1 in c2.teachers()


def test_remove_lab_simple():
    s = Schedule()
    o1 = Lab('ABC')
    o2 = Lab('DEF')
    s._labs = {o1.number: o1, o2.number: o2}
    s.remove_lab(o2)
    assert len(s._labs) == 1
    assert o2 not in s._teachers.values()

    # try to remove non-existent lab
    s.remove_lab(Lab("XYZ"))
    assert True


def test_remove_lab_complex():
    s = Schedule()
    o1 = Lab('ABC')
    o2 = Lab('DEF')
    s._labs = {o1.number: o1, o2.number: o2}

    c1 = s.add_update_course("C1")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    b1 = s1.add_block(WeekDay.get_from_string('MOnday'), 9.0, 1)
    b2 = s1.add_block(WeekDay.get_from_string('MONDAY'), 10.0, 1)
    b3 = s2.add_block(WeekDay.get_from_string('mon'), 10.0, 1)
    s1.add_lab(o2)
    b3.add_lab(o2)
    c1.add_lab(o1)

    assert o2 in b1.labs()
    assert o2 in b2.labs()
    assert o2 in b3.labs()
    assert o2 in s1.labs()
    assert o2 in s2.labs()
    s.remove_lab(o2)
    assert len(s._labs) == 1
    assert o2 not in b1.labs()
    assert o2 not in b2.labs()
    assert o2 not in b3.labs()
    assert o2 not in s1.labs()
    assert o2 not in s2.labs()


def test_remove_stream_simple():
    s = Schedule()
    o1 = Stream('ABC')
    o2 = Stream('DEF')
    s._streams = {o1.number: o1, o2.number: o2}
    s.remove_stream(o2)
    assert len(s._streams) == 1
    assert o2 not in s._streams.values()

    # try to remove non-existent stream
    s.remove_stream(Stream("XYZ"))
    assert True


def test_remove_stream_from_courses():
    s = Schedule()
    o1 = Stream('ABC')
    o2 = Stream('DEF')
    s._streams = {o1.number: o1, o2.number: o2}

    c1 = s.add_update_course("C1")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s1.add_stream(o1)
    s2.add_stream(o2)

    assert o2 not in s1.streams()
    assert o2 in s2.streams()
    assert o2 in c1.streams()
    s.remove_stream(o2)
    assert len(s._streams) == 1
    assert o2 not in s1.streams()
    assert o2 not in s2.streams()
    assert o2 not in c1.streams()


def test_get_teachers_assigned_to_any_course():
    s = Schedule()
    o1 = Teacher('ABC', 'Doe')
    o2 = Teacher('DEF', 'Doe')
    o3 = Teacher('XYZ', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2, o3.number: o3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("C2")
    # NOTE: adding teachers is meaningless unless there are sections in the course
    st1 = c1.add_section("ABC")
    st2 = c2.add_section("DEF")
    st1.add_block()
    st2.add_block()
    c1.add_teacher(o1)
    c1.add_teacher(o2)
    c2.add_teacher(o1)

    assert len(s.teachers()) == 3
    assert o3 in s.teachers()
    assert o3 not in s.get_teachers_assigned_to_any_course()
    assert o2 in s.get_teachers_assigned_to_any_course()
    assert o1 in s.get_teachers_assigned_to_any_course()
    assert len(s.get_teachers_assigned_to_any_course()) == 2


def get_streams_assigned_to_any_course():
    s = Schedule()
    o1 = Stream('ABC')
    o2 = Stream('DEF')
    o3 = Stream('XYZ')
    s._streams = {o1.number: o1, o2.number: o2, o3.number: o3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("C2")
    c1.add_stream(o1)
    c1.add_stream(o2)
    c2.add_stream(o1)

    assert len(s.streams()) == 3
    assert o3 in s.streams()
    assert o3 not in s.get_streams_assigned_to_any_course()
    assert o2 in s.get_streams_assigned_to_any_course()
    assert o1 in s.get_streams_assigned_to_any_course()
    assert len(s.get_streams_assigned_to_any_course()) == 2


def get_labs_assigned_to_any_course():
    s = Schedule()
    o1 = Lab('ABC')
    o2 = Lab('DEF')
    o3 = Lab('XYZ')
    s._labs = {o1.number: o1, o2.number: o2, o3.number: o3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("C2")
    c1.add_lab(o1)
    c1.add_lab(o2)
    c2.add_lab(o1)

    assert len(s.labs()) == 3
    assert o3 in s.labs
    assert o3 not in s.get_labs_assigned_to_any_course()
    assert o2 in s.get_labs_assigned_to_any_course()
    assert o1 in s.get_labs_assigned_to_any_course()
    assert len(s.get_labs_assigned_to_any_course()) == 2


def get_courses_for_teacher():
    s = Schedule()
    o1 = Teacher('ABC', 'Doe')
    o2 = Teacher('DEF', 'Doe')
    o3 = Teacher('XYZ', 'Doe')
    s._teachers = {o1.number: o1, o2.number: o2, o3.number: o3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("C2")
    c3 = s.add_update_course("C3")
    c1.add_teacher(o1)
    c1.add_teacher(o2)
    c2.add_teacher(o1)

    assert c1 in s.get_courses_for_teacher(o1)
    assert c2 in s.get_courses_for_teacher(o1)
    assert c3 not in s.get_courses_for_teacher(o1)
    assert len(s.get_courses_for_teacher(o1)) == 2
    assert c1 in s.get_courses_for_teacher(o2)
    assert c2 not in s.get_courses_for_teacher(o2)
    assert len(s.get_courses_for_teacher(o2)) == 1
    assert c3 not in s.get_courses_for_teacher(o2)


def test_sections():
    s = Schedule()
    o1 = Lab('ABC')
    o2 = Lab('DEF')
    s._labs = {o1.number: o1, o2.number: o2}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("C2")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    assert len(s.sections()) == 4
    assert s1 in s.sections()
    assert s2 in s.sections()
    assert s3 in s.sections()
    assert s4 in s.sections()


def test_blocks():
    s = Schedule()
    o1 = Lab('ABC')
    o2 = Lab('DEF')
    s._labs = {o1.number: o1, o2.number: o2}

    c1 = s.add_update_course("C1")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    sections = s.sections()
    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 10.0, 1)

    assert len(s.blocks()) == 3
    x = s.blocks()
    assert b1 in s.blocks()
    assert b2 in s.blocks()
    assert b3 in s.blocks()


def test_get_sections_for_teacher():
    s = Schedule()
    l1 = Lab('ABC')
    l2 = Lab('DEF')
    s._labs = {l1.number: l1, l2.number: l2}
    st1 = Stream('ABC')
    st2 = Stream('DEF')
    s._streams = {st1.number: st1, st2.number: st2}
    t1 = Teacher("ABC", "Doe")
    t2 = Teacher("DEF", "Doe")
    t3 = Teacher("XYZ", "Doe")
    s._teachers = {t1.number: t1, t2.number: t2, t3.number: t3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("c3")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 10.0, 1)
    b4 = s3.add_block(WeekDay.Monday, 9.0, 1)
    b5 = s3.add_block(WeekDay.Monday, 10.0, 1)
    b6 = s4.add_block(WeekDay.Monday, 10.0, 1)

    c1.add_teacher(t1)
    c2.add_teacher(t2)

    s1.add_stream(st1)
    s3.add_stream(st1)
    s2.add_stream(st2)
    s4.add_stream(st2)

    c1.add_lab(l1)
    c2.add_lab(l2)

    assert len(s.get_sections_for_teacher(t1)) == 2
    assert s1 in s.get_sections_for_teacher(t1)
    assert s2 in s.get_sections_for_teacher(t1)
    assert isinstance(s.get_sections_for_teacher(t1), tuple)
    assert len(s.get_sections_for_teacher(t3)) == 0


def test_get_sections_for_stream():
    s = Schedule()
    l1 = Lab('ABC')
    l2 = Lab('DEF')
    s._labs = {l1.number: l1, l2.number: l2}
    st1 = Stream('ABC')
    st2 = Stream('DEF')
    s._streams = {st1.number: st1, st2.number: st2}
    t1 = Teacher("ABC", "Doe")
    t2 = Teacher("DEF", "Doe")
    t3 = Teacher("XYZ", "Doe")
    s._teachers = {t1.number: t1, t2.number: t2, t3.number: t3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("c3")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 10.0, 1)
    b4 = s3.add_block(WeekDay.Monday, 9.0, 1)
    b5 = s3.add_block(WeekDay.Monday, 10.0, 1)
    b6 = s4.add_block(WeekDay.Monday, 10.0, 1)

    c1.add_teacher(t1)
    c2.add_teacher(t2)

    s1.add_stream(st1)
    s3.add_stream(st1)
    s2.add_stream(st2)
    s4.add_stream(st2)

    c1.add_lab(l1)
    c2.add_lab(l2)

    assert len(s.get_sections_for_stream(st2)) == 2
    assert s2 in s.get_sections_for_stream(st2)
    assert s4 in s.get_sections_for_stream(st2)
    assert s1 not in s.get_sections_for_stream(st2)


def test_get_blocks_for_teacher():
    s = Schedule()
    l1 = Lab('ABC')
    l2 = Lab('DEF')
    s._labs = {l1.number: l1, l2.number: l2}
    st1 = Stream('ABC')
    st2 = Stream('DEF')
    s._streams = {st1.number: st1, st2.number: st2}
    t1 = Teacher("ABC", "Doe")
    t2 = Teacher("DEF", "Doe")
    t3 = Teacher("XYZ", "Doe")
    s._teachers = {t1.number: t1, t2.number: t2, t3.number: t3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("c3")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 10.0, 1)
    b4 = s3.add_block(WeekDay.Monday, 9.0, 1)
    b5 = s3.add_block(WeekDay.Monday, 10.0, 1)
    b6 = s4.add_block(WeekDay.Monday, 10.0, 1)

    c1.add_teacher(t1)
    c2.add_teacher(t2)

    s1.add_stream(st1)
    s3.add_stream(st1)
    s2.add_stream(st2)
    s4.add_stream(st2)

    c1.add_lab(l1)
    c2.add_lab(l2)

    assert len(s.get_blocks_for_teacher(t1)) == 3
    assert b1 in s.get_blocks_for_teacher(t1)
    assert b2 in s.get_blocks_for_teacher(t1)
    assert b3 in s.get_blocks_for_teacher(t1)
    assert len(s.get_blocks_for_teacher(t3)) == 0


def test_get_blocks_in_lab():
    s = Schedule()
    l1 = Lab('ABC')
    l2 = Lab('DEF')
    l3 = Lab('XYZ')
    s._labs = {l1.number: l1, l2.number: l2}
    st1 = Stream('ABC')
    st2 = Stream('DEF')
    s._streams = {st1.number: st1, st2.number: st2}
    t1 = Teacher("ABC", "Doe")
    t2 = Teacher("DEF", "Doe")
    t3 = Teacher("XYZ", "Doe")
    s._teachers = {t1.number: t1, t2.number: t2, t3.number: t3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("c3")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 10.0, 1)
    b4 = s3.add_block(WeekDay.Monday, 9.0, 1)
    b5 = s3.add_block(WeekDay.Monday, 10.0, 1)
    b6 = s4.add_block(WeekDay.Monday, 10.0, 1)

    c1.add_teacher(t1)
    c2.add_teacher(t2)

    s1.add_stream(st1)
    s3.add_stream(st1)
    s2.add_stream(st2)
    s4.add_stream(st2)

    c1.add_lab(l1)
    c2.add_lab(l2)

    assert len(s.get_blocks_in_lab(l1)) == 3
    assert b1 in s.get_blocks_in_lab(l1)
    assert b2 in s.get_blocks_in_lab(l1)
    assert b3 in s.get_blocks_in_lab(l1)
    assert isinstance(s.get_blocks_in_lab(l1), tuple)
    assert len(s.get_blocks_in_lab(l3)) == 0


def test_get_blocks_for_stream():
    s = Schedule()
    l1 = Lab('ABC')
    l2 = Lab('DEF')
    l3 = Lab('XYZ')
    s._labs = {l1.number: l1, l2.number: l2}
    st1 = Stream('ABC')
    st2 = Stream('DEF')
    st3 = Stream("XYZ")
    s._streams = {st1.number: st1, st2.number: st2}
    t1 = Teacher("ABC", "Doe")
    t2 = Teacher("DEF", "Doe")
    t3 = Teacher("XYZ", "Doe")
    s._teachers = {t1.number: t1, t2.number: t2, t3.number: t3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("c3")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 11.0, 1)
    b4 = s3.add_block(WeekDay.Tuesday, 9.0, 1)
    b5 = s3.add_block(WeekDay.Tuesday, 10.0, 1)
    b6 = s4.add_block(WeekDay.Tuesday, 11.0, 1)

    c1.add_teacher(t1)
    c2.add_teacher(t2)

    s1.add_stream(st1)
    s3.add_stream(st1)
    s2.add_stream(st2)
    s4.add_stream(st2)

    c1.add_lab(l1)
    c2.add_lab(l2)

    assert len(s.get_blocks_for_stream(st1)) == 4
    assert b1 in s.get_blocks_for_stream(st1)
    assert b2 in s.get_blocks_for_stream(st1)
    assert b4 in s.get_blocks_for_stream(st1)
    assert b5 in s.get_blocks_for_stream(st1)

    assert isinstance(s.get_blocks_for_stream(st1), tuple)
    assert len(s.get_blocks_for_stream(st3)) == 0


def test_get_blocks_for_obj():
    s = Schedule()
    l1 = Lab('ABC')
    l2 = Lab('DEF')
    l3 = Lab('XYZ')
    s._labs = {l1.number: l1, l2.number: l2}
    st1 = Stream('ABC')
    st2 = Stream('DEF')
    st3 = Stream("XYZ")
    s._streams = {st1.number: st1, st2.number: st2, st3.number: st3}
    t1 = Teacher("ABC", "Doe")
    t2 = Teacher("DEF", "Doe")
    t3 = Teacher("XYZ", "Doe")
    s._teachers = {t1.number: t1, t2.number: t2, t3.number: t3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("c3")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 10.0, 1)
    b4 = s3.add_block(WeekDay.Monday, 9.0, 1)
    b5 = s3.add_block(WeekDay.Monday, 10.0, 1)
    b6 = s4.add_block(WeekDay.Monday, 10.0, 1)

    c1.add_teacher(t1)
    c2.add_teacher(t2)

    s1.add_stream(st1)
    s3.add_stream(st1)
    s2.add_stream(st2)
    s4.add_stream(st2)

    c1.add_lab(l1)
    c2.add_lab(l2)

    assert s.get_blocks_for_teacher(t1) == s.get_blocks_for_obj(t1)
    assert s.get_blocks_in_lab(l1) == s.get_blocks_for_obj(l1)
    assert s.get_blocks_for_stream(st1) == s.get_blocks_for_obj(st1)


def test_clear_all():
    s = Schedule()
    l1 = Lab('ABC')
    l2 = Lab('DEF')
    l3 = Lab('XYZ')
    s._labs = {l1.number: l1, l2.number: l2}
    st1 = Stream('ABC')
    st2 = Stream('DEF')
    st3 = Stream("XYZ")
    s._streams = {st1.number: st1, st2.number: st2, st3.number: st3}
    t1 = Teacher("ABC", "Doe")
    t2 = Teacher("DEF", "Doe")
    t3 = Teacher("XYZ", "Doe")
    s._teachers = {t1.number: t1, t2.number: t2, t3.number: t3}

    c1 = s.add_update_course("C1")
    c2 = s.add_update_course("c3")
    s1 = c1.add_section("1")
    s2 = c1.add_section("2")
    s3 = c2.add_section("1")
    s4 = c2.add_section("2")

    b1 = s1.add_block(WeekDay.Monday, 9.0, 1)
    b2 = s1.add_block(WeekDay.Monday, 10.0, 1)
    b3 = s2.add_block(WeekDay.Monday, 10.0, 1)
    b4 = s3.add_block(WeekDay.Monday, 9.0, 1)
    b5 = s3.add_block(WeekDay.Monday, 10.0, 1)
    b6 = s4.add_block(WeekDay.Monday, 10.0, 1)

    c1.add_teacher(t1)
    c2.add_teacher(t2)

    s1.add_stream(st1)
    s3.add_stream(st1)
    s2.add_stream(st2)
    s4.add_stream(st2)

    c1.add_lab(l1)
    c2.add_lab(l2)

    s.clear_all_from_course(c1)

    assert len(c1.teachers()) == 0
    assert len(c1.labs()) == 0
    assert len(c1.streams()) == 0


def test_calculate_conflicts():
    """too much trouble to test this right now"""
    # TODO: write this test
    assert True
