from src.scheduling_and_allocation.model import TimeSlot, WeekDay, \
    MINIMUM_DURATION, DEFAULT_DAY, DEFAULT_START, DEFAULT_DURATION, MINUTE_BLOCK_SIZE, MAXIMUM_DURATION, MAX_END_TIME


def test_defaults():
    slot = TimeSlot()
    assert slot.day == DEFAULT_DAY
    assert slot.start == DEFAULT_START
    assert slot.duration == DEFAULT_DURATION
    assert slot.movable


def test_calculate_end_time():
    slot = TimeSlot(WeekDay.Tuesday, start=13.25, duration=1.5)
    assert slot.day == WeekDay.Tuesday
    assert slot.start == 13.25
    assert slot.duration == 1.5
    assert slot.end == 14.75


def test_equality():
    slot1 = TimeSlot(WeekDay.Tuesday, start=13.25, duration=1.5)
    slot2 = TimeSlot(WeekDay.Tuesday, start=13.25, duration=1.5)
    assert slot1 == slot2


def test_hashable():
    slot1 = TimeSlot(WeekDay.Tuesday, start=13.25, duration=1.5)
    slot2 = TimeSlot(WeekDay.Tuesday, start=13.25, duration=1.5)
    s = {slot1, slot2}
    assert len(s) == 1


def test_sortable():
    slot1 = TimeSlot(WeekDay.Tuesday, start=13.25, duration=1.5)
    slot2 = TimeSlot(WeekDay.Monday, start=13.25, duration=1.5)
    s = [slot1, slot2]
    s.sort()
    assert s[0] == slot2
    assert s[1] == slot1


def test_duration_not_allowed_less_than_zero():
    slot = TimeSlot(WeekDay.Tuesday, start=13.25, duration=-3)
    assert abs(slot.duration - MINUTE_BLOCK_SIZE / 60) < 0.001


def test_duration_not_allowed_greater_than_eight():
    slot = TimeSlot(WeekDay.Tuesday, start=13.5, duration=MAXIMUM_DURATION + .5)
    assert slot.duration == MAXIMUM_DURATION


def test_duration_rounded_up_to_minimum_half_hour():
    slot = TimeSlot(WeekDay.Tuesday, 13.5, duration=0.1)
    assert slot.duration == MINIMUM_DURATION


def test_duration_setter_changes_end():
    slot = TimeSlot(WeekDay.Tuesday, 13.5, duration=1)
    assert slot.end == 14.5
    slot.duration = 3
    assert slot.end == 16.5


def test_no_snapping_required():
    slot = TimeSlot(start=13)
    assert not slot.snap_to_time()


def test_snap_to_time():
    slot = TimeSlot(start=13.25)
    slot.snap_to_time()
    expected_start =13
    assert slot.start == expected_start


def test_snap_to_time_adjust_duration():
    slot = TimeSlot(duration=1.2, start=13)
    slot.snap_to_time()
    assert slot.duration == 1


def test_snap_to_time_bad_value_to_minimum():
    slot = TimeSlot(start=5)
    slot.snap_to_time()
    expected_start = 8
    print()
    print(slot)
    assert slot.start == expected_start


def test_snap_to_time_bad_value_to_maximum():
    slot = TimeSlot(start=19)
    slot.snap_to_time()
    assert slot.start + slot.duration <= MAX_END_TIME


def test_snap_to_day_with_args():
    """Verifies that TimeSlot's snap_to_day method adjusts its day property to the correct value
    when it is outside a specified date range. """
    slot = TimeSlot()
    slot.day = WeekDay.Friday
    assert slot.snap_to_day(slot.day.value, WeekDay.Tuesday, WeekDay.Wednesday)
    assert slot.day == WeekDay.Wednesday


def test_snap_to_day_with_fractional_day():
    slot = TimeSlot()
    slot.day = WeekDay.Friday
    assert slot.snap_to_day(2.3)
    assert slot.day == WeekDay.Tuesday


def test_snap_to_day_returns_false_no_change():
    slot = TimeSlot()
    slot.day = WeekDay.Tuesday
    assert not slot.snap_to_day(2)
    assert slot.day == WeekDay.Tuesday


def test_conflicts_time1():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday,8, 1.5)
    slot2 = TimeSlot(WeekDay.Monday, 9, 1)
    assert slot1.conflicts_time(slot2)


def test_conflicts_time2():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday, 8, 1)
    slot2 = TimeSlot(WeekDay.Monday, 9, 1)
    assert not slot1.conflicts_time(slot2)


def test_conflicts_time3():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday,9.5, 1)
    slot2 = TimeSlot(WeekDay.Monday,9, 1)
    assert slot1.conflicts_time(slot2)


def test_conflicts_time4():
    """Verifies that conflicts_time works as intended."""
    slot1 = TimeSlot(WeekDay.Monday, 9.5, 1)
    slot2 = TimeSlot(WeekDay.Monday, 10.5, 1)
    assert not slot1.conflicts_time(slot2)


def test_conflicts_time_different_days():
    """Verifies that conflicts_time registers no conflict when two TimeSlots are on different
    days. """
    slot1 = TimeSlot(WeekDay.Tuesday, 9.5, 1)
    slot2 = TimeSlot(WeekDay.Monday, 9, 1)
    assert slot1.conflicts_time(slot2) is False

def test_conflicts_time_one_inside_another1():
    slot1 = TimeSlot(WeekDay.Tuesday, 9.5, 1)
    slot2 = TimeSlot(WeekDay.Tuesday, 9.5, 4)
    assert slot1.conflicts_time(slot2) is True
    assert slot2.conflicts_time(slot1) is True

def test_conflicts_time_one_inside_another2():
    slot1 = TimeSlot(WeekDay.Tuesday, 9.5, 4)
    slot2 = TimeSlot(WeekDay.Tuesday, 10, 1)
    assert slot1.conflicts_time(slot2) is True
    assert slot2.conflicts_time(slot1) is True

def test_conflicts_time_one_inside_another3():
    slot1 = TimeSlot(WeekDay.Tuesday, 9.5, 4)
    slot2 = TimeSlot(WeekDay.Tuesday, 9.5, 4)
    assert slot1.conflicts_time(slot2) is True
    assert slot2.conflicts_time(slot1) is True
