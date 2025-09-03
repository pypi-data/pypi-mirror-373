from __future__ import annotations
import pytest
import sys

from src.scheduling_and_allocation.model import TimeSlot, Course, Section, Block, Lab, Teacher, ConflictType

course = Course("123")
dummy_Section = Section(course)


@pytest.fixture(scope="module", autouse=True)
def before_and_after_module():
    pass


@pytest.fixture(autouse=True)
def run_before():
    pass


def test_generic():
    day = 1
    start1 = 8
    start2 = 12
    dur = 2
    block1 = Block(dummy_Section, day, start1, dur, True)
    assert block1.section is dummy_Section
    assert not block1.conflict.is_conflicted()


def test_hashable():
    day = 1
    start1 = 8
    start2 = 12
    dur = 2
    block1 = Block(dummy_Section, day, start1, dur, True)
    block2 = Block(dummy_Section, day, start1, dur, True)
    s = {block1, block2}
    assert len(s) == 2


def test_sortable():
    slot1 = Block(dummy_Section, 2, start=13.25, duration=1.5)
    slot2 = Block(dummy_Section, 2, start=11.25, duration=1.5)
    s = [slot1, slot2]
    s.sort()
    assert s[0] == slot2
    assert s[1] == slot1


def test_sync_day():
    """Verifies that the day setter works as intended, changing the day property of any Block
    synced_blocks to the current Block. """
    day = 1
    start1 = 8
    start2 = 12
    dur = 2
    block1 = Block(dummy_Section, day, start1, dur, True)
    block2 = Block(dummy_Section, 4, start2, dur, True)
    block1.sync_block(block2)
    block2.sync_block(block1)
    assert block2._time_slot == block2._time_slot


def test_id():
    """Verifies that the id property works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur, True)
    old_id = block.id
    block = Block(dummy_Section, day, start, dur, True)
    assert block.id == old_id + 1


def test_id_with_id_given():
    """Verifies that the id property works as intended."""

    day = 1
    start = 8.5
    dur = 2
    existing_id = 12
    block1 = Block(dummy_Section, day, start, dur, True, block_id=existing_id)
    assert block1.id == existing_id
    block2 = Block(dummy_Section, day, start, dur, True)
    assert block2.id == existing_id + 1
    block3 = Block(dummy_Section, day, start, dur, True, block_id=existing_id - 5)
    assert block3.id == existing_id - 5
    block4 = Block(dummy_Section, day, start, dur, True)
    assert block4.id == block2.id + 1


def test_assign_lab_good():
    """Verifies that the add_lab method can assign a valid Lab object to the Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur, True)
    lab = Lab()
    block.add_lab(lab)
    assert block.has_lab(lab)


def test_assign_lab_multiple():
    """Verifies that the assign_lab_by_id method can assign a valid Lab object to the Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    lab1 = Lab("P100")
    lab2 = Lab("P101")
    block.add_lab(lab1)
    block.add_lab(lab2)
    labs = block.labs()
    assert block.has_lab(lab1)
    assert block.has_lab(lab2)
    assert len(labs) == 2


def test_assign_lab_multiple_with_duplicate():
    """Verifies that the assign_lab_by_id method can assign a valid Lab object to the Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    lab1 = Lab("P100")
    lab2 = Lab("p101")
    block.add_lab(lab1)
    block.add_lab(lab1)
    block.add_lab(lab2)
    labs = block.labs()
    assert len(labs) == 2


def test_remove_lab_good():
    """Verifies that remove_lab() can successfully remove a valid Lab object from this Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    lab1 = Lab("P100")
    lab2 = Lab("101")
    block.add_lab(lab1)
    block.add_lab(lab2)
    block.remove_lab(lab1)
    labs = block.labs()
    assert not block.has_lab(lab1)
    assert block.has_lab(lab2)
    assert len(labs) == 1


def test_remove_lab_no_crash():
    """Verifies that remove_lab won't crash the program if the Block doesn't contain
    the specified valid Lab. """
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    lab = Lab()
    block.add_lab(lab)
    other_lab = Lab("R-101", "dummy")
    block.remove_lab(other_lab)
    assert block.has_lab(lab)


def test_remove_all_labs():
    """Verifies that remove_all_labs works as intended, removing all Labs from the current
    Block. """
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    this_lab = Lab("R-100", "the second-worst place in the world")
    other_lab = Lab("R-101", "the worst place in the world")
    block.add_lab(this_lab)
    block.add_lab(other_lab)
    assert len(block.labs()) == 2
    block.remove_all_labs()
    assert len(block.labs()) == 0
    assert not block.has_lab(this_lab)
    assert not block.has_lab(other_lab)


def test_labs():
    """Verifies that labs returns a list of all Lab objects assigned to this Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    this_lab = Lab("R-100", "the second-worst place in the world")
    other_lab = Lab("R-101", "the worst place in the world")
    block.add_lab(this_lab)
    block.add_lab(other_lab)
    labs = block.labs()
    assert len(labs) == 2 and this_lab in labs and other_lab in labs


def test_labs_empty():
    """Verifies that lab_ids returns an empty list if called while no Labs are assigned to the
    Block. """
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    labs = block.labs()
    assert len(labs) == 0


def test_has_lab_good():
    """Verifies that has_lab_with_id() returns true when the specified Lab is assigned to this Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    lab = Lab()
    block.add_lab(lab)
    assert block.has_lab(lab)


def test_has_lab_false():
    """"Verifies that has_lab_with_id() returns false when the Lab isn't assigned to this Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    lab = Lab()
    assert block.has_lab(lab) is False


def test_assign_teacher_good():
    """Verifies that the add_teacher() method works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach = Teacher("John", "Smith")
    block.add_teacher(teach)
    assert block.has_teacher(teach)


def test_assign_teacher_multiple():
    """Verifies that the assign_teacher_by_id() method works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach1 = Teacher("John", "Smith")
    teach2 = Teacher("Jane", "Smith")
    block.add_teacher(teach1)
    block.add_teacher(teach2)
    assert block.has_teacher(teach1)
    assert block.has_teacher(teach2)
    assert len(block.teachers()) == 2


def test_assign_teacher_multiple_with_duplicates():
    """Verifies that the assign_teacher_by_id() method works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach1 = Teacher("John", "Smith")
    teach2 = Teacher("Jane", "Smith")
    block.add_teacher(teach1)
    block.add_teacher(teach1)
    block.add_teacher(teach2)
    print(teach1, teach2, block.teachers())
    assert len(block.teachers()) == 2


def test_remove_teacher_good():
    """Verifies that remove_teacher_by_id() works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach = Teacher("John", "Smith")
    block.add_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    block.add_teacher(other_teach)
    block.remove_teacher(teach)
    assert len(block.teachers()) == 1
    assert block.has_teacher(teach) is not True
    assert block.has_teacher(other_teach)


def test_remove_teacher_no_crash():
    """Verifies that remove_teacher doesn't crash the program when attempting to remove a
    Teacher that isn't assigned to this Block. """
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach = Teacher("John", "Smith")
    block.add_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    block.remove_teacher(other_teach)
    assert len(block.teachers()) == 1


def test_remove_all_teachers():
    """Verifies that remove_all_teachers() works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach = Teacher("John", "Smith")
    other_teach = Teacher("Jane", "Doe")
    block.add_teacher(teach)
    block.add_teacher(other_teach)
    block.remove_all_teachers()
    assert block.has_teacher(teach) is not True
    assert block.has_teacher(other_teach) is not True
    assert len(block.teachers()) == 0


def test_teachers():
    """Verifies that teacher_ids() returns a list of all the Teachers assigned to this Block."""
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach = Teacher("John", "Smith")
    other_teach = Teacher("Jane", "Doe")
    block.add_teacher(teach)
    block.add_teacher(other_teach)
    teachers = block.teachers()
    assert len(teachers) == 2 and teach in teachers and other_teach in teachers


def test_teachers_empty_list():
    """Verifies that teacher_ids will return an empty list if no Teachers are assigned to this
    Block. """
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teachers = block.teachers()
    assert len(teachers) == 0


def test_has_teacher_true():
    """Verifies that has_teacher returns true when the specified Teacher has been assigned
    to this Block. """
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach = Teacher("John", "Smith")
    block.add_teacher(teach)
    assert block.has_teacher(teach)


def test_has_teach_false():
    """Verifies that has_teacher returns false when the specified Teacher isn't assigned to
    this Block. """
    day = 1
    start = 8.5
    dur = 2
    block = Block(dummy_Section, day, start, dur)
    teach = Teacher("John", "Smith")
    block.add_teacher(teach)
    other_teach = Teacher("Jane", "Doe")
    assert block.has_teacher(other_teach) is False


def test_reset_conflicted():
    """Verifies that reset_conflicted works as intended, setting the value of conflicted_number to
    False. """
    day = 1
    start = 8.5
    dur = 2

    block1 = Block(dummy_Section, day, start, dur)
    block1.clear_conflicts()
    assert not block1.conflict.is_conflicted()


def test_conflicted_getter():
    """Verifies that the conflicted_number getter works as intended, returning a default value of
    False. """
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    assert not block1.conflict.is_conflicted()


def test_conflicted_setter_good():
    """Verifies that the conflicted_number setter works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block1.clear_conflicts()
    block1.add_conflict(ConflictType.LUNCH)
    assert block1.conflict == ConflictType.LUNCH


def test_is_conflicted_true():
    """Verifies that is_conflicted() returns true if the conflicted number is not zero."""
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block1.add_conflict(ConflictType.LUNCH)
    assert block1.conflict.is_conflicted()


def test_is_conflicted_false():
    """Verifies that is_conflicted() returns the false if the conflicted number is zero."""
    day = 1
    start = 8.5
    dur = 2

    block1 = Block(dummy_Section, day, start, dur)
    block1.add_conflict(ConflictType.LUNCH)
    assert block1.conflict.is_conflicted()
    block1.clear_conflicts()
    assert not block1.conflict.is_conflicted()


def test_adjusting_conflict_sets_appropriate_bits():
    """Verifies that is_conflicted() returns the false if the conflicted number is zero."""
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block1.clear_conflicts()
    block1.add_conflict(ConflictType.LUNCH)
    block1.add_conflict(ConflictType.LUNCH)
    block1.add_conflict(ConflictType.TIME_LAB)
    block1.add_conflict(ConflictType.TIME_LAB)
    assert block1.conflict.is_time_lab()
    assert block1.conflict.is_time_lunch()


# ====================================================================================================================
# Synchronization
# ====================================================================================================================
def test_start_setter_synced_2_blocks_check_block1_moves_block2():
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block2 = Block(dummy_Section, 3, start, dur)
    block1.sync_block(block2)
    assert block2._time_slot == block2._time_slot


def test_start_setter_synced_2_blocks_check_block2_moves_block1():
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block2 = Block(dummy_Section, 3, start, dur)
    block1.sync_block(block2)
    assert block2._time_slot == block2._time_slot
    block1._time_slot.day = 2
    assert block2._time_slot == block2._time_slot


def test_start_setter_synced_4_blocks():
    """Same as previous test, but with 4 blocks instead of 2."""
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block2 = Block(dummy_Section, 3, start, dur)
    block3 = Block(dummy_Section, 4, start, dur)
    block4 = Block(dummy_Section, 5, start, dur)
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)

    new_start = "10:00"
    block1._time_slot.time_start = new_start
    assert block2._time_slot == block3._time_slot == block4._time_slot


def test_start_setter_synced_4_blocks_move_block3():
    """Same as previous test, but with 4 blocks instead of 2."""
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block2 = Block(dummy_Section, 3, start, dur)
    block3 = Block(dummy_Section, 4, start, dur)
    block4 = Block(dummy_Section, 5, start, dur)
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)

    new_start = "10:00"
    block3._time_slot.time_start = new_start
    assert block2._time_slot.time_start == new_start == block3._time_slot.time_start == block4._time_slot.time_start


def test_sync_block_good():
    """Verifies that sync_block() synchronizes a passed Block with this Block."""
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block2 = Block(dummy_Section, 2, start, dur)
    block1.sync_block(block2)
    assert block2 in block1.synced_blocks()
    assert block1 in block2.synced_blocks()


def test_unsync_block1_from_block2():
    """Verifies that unsync_block() works as intended."""
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block2 = Block(dummy_Section, 2, start, dur)
    block1.sync_block(block2)
    assert block1 in block2.synced_blocks()
    assert block2 in block1.synced_blocks()

    block2.unsync_block(block1)
    assert block1 not in block2.synced_blocks()
    assert block2 not in block1.synced_blocks()


def test_synced():
    """Verifies that synced_blocks returns a tuple of all the Blocks that are synced_blocks with this
    Block. """
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    block2 = Block(dummy_Section, 2, start, dur)
    block3 = Block(dummy_Section, 3, start, dur)
    block1.sync_block(block2)
    block1.sync_block(block3)
    blocks = block1.synced_blocks()

    assert len(blocks) == 2 and block2 in blocks and block3 in blocks


def test_synced_empty_tuple():
    """Verifies that synced_blocks() returns an empty tuple if called when no Blocks are synced_blocks with
    this Block. """
    day = 1
    start = 8.5
    dur = 2
    block1 = Block(dummy_Section, day, start, dur)
    blocks = block1.synced_blocks()
    assert len(blocks) == 0


def test_synced_blocks_interdependence_works_as_expected():
    block1 = Block(dummy_Section, 1, 8.5, 2)
    block2 = Block(dummy_Section, 2, 8.5, 2)
    block3 = Block(dummy_Section, 3, 8.5, 2)
    block4 = Block(dummy_Section, 5, 8.5, 2)

    # make all blocks dependent on block1, and vice versa
    block1.sync_block(block2)
    block1.sync_block(block3)
    block1.sync_block(block4)

    # disconnect blocks 1 from blocks 3,
    block3.unsync_block(block1)

    # changing blocks 3 should affect on anybody block2 and block4, but not block1
    block3._time_slot.time_start = 11.5
    assert block1._time_slot == TimeSlot(1, 8.5, 2)
    assert block3._time_slot.time_start == block2._time_slot.time_start == block4._time_slot.time_start == 11.5

    # changing block 1 should not affect any other block
    block1._time_slot.time_start = 9.5
    assert block3._time_slot.time_start == block2._time_slot.time_start == block4._time_slot.time_start == 11.5
    assert block1._time_slot.time_start == 9.5
