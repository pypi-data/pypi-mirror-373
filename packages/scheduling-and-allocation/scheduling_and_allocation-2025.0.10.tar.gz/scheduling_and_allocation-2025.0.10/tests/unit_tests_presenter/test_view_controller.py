from __future__ import annotations
from typing import Callable

import pytest

from src.scheduling_and_allocation.Utilities.id_generator import IdGenerator
from src.scheduling_and_allocation.model import Lab, Stream, Teacher, Block, ResourceType, ConflictType, Schedule, \
    SemesterType, WeekDay
from src.scheduling_and_allocation.presenter.views_controller import ViewsController

# =====================================================================================================================
# Dummy classes
# =====================================================================================================================
"""Provides code to deal with user modifying the gui view.  Most actions are passed onto the View Controller"""


RESOURCE = Lab | Stream | Teacher

# =====================================================================================================================
# use an generator to always guarantee that the new id will be unique
# =====================================================================================================================
_gui_block_ids = IdGenerator()

# =====================================================================================================================
# ViewTest
# =====================================================================================================================
class GUI:
    def raise_to_top(self): pass

VIEW_TEST_CALLED = 0
REFRESH_COLOURS_CALLED = 0
MOVE_GUI_BLOCK_TO = 0
VIEW_DRAW_CALLED = 0
class ViewTest:

    def __init__(self, views_controller, frame, schedule, resource, gui=None):
        self.gui = GUI()
        global VIEW_TEST_CALLED
        VIEW_TEST_CALLED += 1
        self.gui_blocks = {}
        self.move_gui_block_args = []

    def move_gui_block_to(self, block: Block, day: float, start_time: float):
        global MOVE_GUI_BLOCK_TO
        self.move_gui_block_args.append((block, day, start_time))
        MOVE_GUI_BLOCK_TO += 1

    def refresh_block_colours(self):
        global REFRESH_COLOURS_CALLED
        REFRESH_COLOURS_CALLED += 1

    def get_block_text(self, block: Block):
        return "hi"

    def draw(self):
        global VIEW_DRAW_CALLED
        VIEW_DRAW_CALLED += 1

    def is_block_in_view(self, block):
        return True

# =====================================================================================================================
# ViewsControllerTestTkTest
# =====================================================================================================================

class ViewsControllerTkTest:
    def __init__(self, parent, resources:dict[ResourceType,list], btn_callback: Callable):
        self.btn_colours = []

    def set_button_colour(self, button_id: str, resource_type, view_conflict: ConflictType = None):
        self.btn_colours.append((button_id, resource_type, view_conflict))

# =====================================================================================================================
# fixtures
# =====================================================================================================================
@pytest.fixture()
def gui():
    return ViewsControllerTkTest("",{},lambda x: None)

@pytest.fixture()
def schedule_obj():
    schedule = Schedule()

    # teachers
    t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id="1")
    t2 = schedule.add_update_teacher("John", "Doe", teacher_id="2")
    t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id="3")
    t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id = "4")

    # labs
    l1 = schedule.add_update_lab("P107", "C-Lab")
    l2 = schedule.add_update_lab("P322", "Mac Lab")
    l3 = schedule.add_update_lab("P325")
    l4 = schedule.add_update_lab("BH311", "Britain Hall")

    # streams
    st1 = schedule.add_update_stream("1A", "calculus available")
    st2 = schedule.add_update_stream("1B", "no calculus")
    st3 = schedule.add_update_stream("2A")
    st4 = schedule.add_update_stream("2B")

    # courses
    c_001 = schedule.add_update_course("001","BasketWeaving", SemesterType.fall )
    s_001_1 = c_001.add_section("1", section_id=1)
    s_001_1.add_stream(st1)
    b_001_1_1 = s_001_1.add_block(WeekDay.Monday,  8 )
    b_001_1_2 = s_001_1.add_block(WeekDay.Monday,  10 )
    b_001_1_1.add_teacher(t1)
    b_001_1_2.add_teacher(t1)
    b_001_1_1.add_lab(l1)
    b_001_1_2.add_lab(l1)

    s_001_2 = c_001.add_section("2",section_id=2)
    s_001_2.add_stream(st2)
    b_001_2_1 = s_001_2.add_block(WeekDay.Tuesday,  8 )
    b_001_2_2 = s_001_2.add_block(WeekDay.Tuesday,  10 )
    b_001_2_1.add_teacher(t2)
    b_001_2_2.add_teacher(t3)
    b_001_2_1.add_lab(l2)
    b_001_2_2.add_lab(l3)


    c_002 = schedule.add_update_course("002","Thumb Twiddling", SemesterType.fall )
    s_002_1 = c_002.add_section("1",)
    b_002_1_1 = s_002_1.add_block(WeekDay.Monday,  8 )
    b_002_1_2 = s_002_1.add_block(WeekDay.Monday,  10 )
    s_002_2 = c_002.add_section("2",)
    b_002_2_1 = s_002_2.add_block(WeekDay.Tuesday,  8 )
    b_002_2_2 = s_002_2.add_block(WeekDay.Tuesday,  10 )



    return schedule

DIRTY_FLAG = False
def dirty_flag_method(value=None):
    global DIRTY_FLAG
    if value is not None:
        DIRTY_FLAG = value
    return DIRTY_FLAG

# =====================================================================================================================
# Testing
# =====================================================================================================================
def test_init(schedule_obj, gui):
    """create views controller
    1. all resources are saved in object
    """
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    assert vc.resources[ResourceType.teacher] == list(schedule_obj.teachers())
    assert vc.resources[ResourceType.lab] == list(schedule_obj.labs())
    assert vc.resources[ResourceType.stream] == list(schedule_obj.streams())

def test_create_view_only_once(schedule_obj, gui, monkeypatch):
    """create multiple views, but only end up with single view for each resource"""

    # prepare
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher1: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John","Doe")

    # execute
    vc.call_view(teacher1)
    vc.call_view(teacher2)
    vc.call_view(teacher1)
    vc.call_view(teacher2)
    vc.call_view(teacher1)
    vc.call_view(teacher2)

    # validate
    assert len(vc._views) == 2


def test_refresh(schedule_obj, gui):
    """refresh views controller
    1. conflicts are recalculated
    2. all buttons in resources have their colour updated
    """

    # prepare
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1 = blocks[0]
    block2 = blocks[1]
    block1.day = block2.day
    block1.start = block2.start
    assert not block1.conflict
    assert not block2.conflict

    # execute
    vc.refresh()

    # validate
    assert block1.conflict
    assert block2.conflict
    assert (len(gui.btn_colours) == len(vc.resources[ResourceType.teacher])
            + len(vc.resources[ResourceType.lab])
            + len(vc.resources[ResourceType.stream])
            )


def test_block_moved(schedule_obj, gui, monkeypatch):
    global REFRESH_COLOURS_CALLED
    """block has moved
    1. dirty flag has not been reset (it is reset when the block is dropped)
    2. refresh was called (which recalculates conflicts)
    3. all currently open views colours are updated 
    4. views are told to update their gui_block positions (not tested)
    """
    # prepare
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher1: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John","Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1 = blocks[0]
    block2 = blocks[1]
    dirty_flag_method(False)
    vc.call_view(teacher1)
    vc.call_view(teacher2)
    assert not block1.conflict
    assert not block2.conflict

    # execute
    REFRESH_COLOURS_CALLED = 0
    vc.notify_block_move("", block1, block1.day.value, block1.start)

    # verify
    assert not dirty_flag_method()
    assert block1.conflict
    assert block2.conflict
    assert REFRESH_COLOURS_CALLED == 2

def test_block_moved_view_updated(schedule_obj, gui, monkeypatch):
    global MOVE_GUI_BLOCK_TO
    """block has moved
    1. views are told to update their gui_block positions (but not the one that triggered it)
    """

    # prepare
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)

    # both teacher and stream share the same blocks
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    stream: Stream = schedule_obj.get_stream_by_number("1A")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks
    vc.call_view(teacher)
    vc.call_view(stream)

    # execute
    MOVE_GUI_BLOCK_TO = 0
    vc.notify_block_move(teacher.number, block1, block1.day.value, block1.start)

    # verify
    assert MOVE_GUI_BLOCK_TO == 1

def test_block_movable_changed(schedule_obj, gui, monkeypatch):
    """block movable has been changed
    1. NOTE: dirty flag is updated in the view where the event happened
    2. update colours on all the views
    3. update colors on view choices
    4. conflicts are recalculated
    """
    global REFRESH_COLOURS_CALLED
    REFRESH_COLOURS_CALLED = 0

    # prepare
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    stream: Stream = schedule_obj.get_stream_by_number("1A")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks
    vc.call_view(teacher)
    vc.call_view(stream)
    assert not block1.conflict

    # execute
    block1.movable = not block1.movable
    vc.notify_block_movable_toggled(block1)

    # validate
    assert block1.conflict

    # ... validate update colours on all the open views
    assert REFRESH_COLOURS_CALLED == 2

    # ... validate update colours on all the views
    assert (len(gui.btn_colours) == len(vc.resources[ResourceType.teacher])
            + len(vc.resources[ResourceType.lab])
            + len(vc.resources[ResourceType.stream])
            )


def test_block_moved_to_different_resource1(schedule_obj, gui, monkeypatch):
    """block is to be moved to a different resource
    1. block is removed from original resource
    2. block is added to the other resource
    3. dirty flag is set
    4. conflicts are updated
    5. conflicts are recalculated
    """
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)

    # prepare
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John", "Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks

    # execute
    dirty_flag_method(False)
    block2.conflict = ConflictType.NONE
    vc.notify_move_block_to_resource(ResourceType.teacher, block1, teacher, teacher2)

    # validate
    assert block1 not in schedule_obj.get_blocks_for_teacher(teacher)
    assert block1 in schedule_obj.get_blocks_for_teacher(teacher2)
    assert dirty_flag_method()
    assert block2.conflict

def test_block_moved_to_different_resource2(schedule_obj, gui, monkeypatch):
    """block is to be moved to a different resource, both views are already opened
    1. both views are redrawn
    """
    global VIEW_DRAW_CALLED
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)

    # prepare
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane","Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John", "Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks
    vc.call_view(teacher)
    vc.call_view(teacher2)
    VIEW_DRAW_CALLED = 0

    # execute
    vc.notify_move_block_to_resource(ResourceType.teacher, block1, teacher, teacher2)

    # validate
    assert VIEW_DRAW_CALLED == 2


def test_block_moved_to_different_resource3(schedule_obj, gui, monkeypatch):
    """block is to be moved to a different resource, only one view is already open
    1. one view is redrawn, the other is created
    """
    global VIEW_DRAW_CALLED
    global VIEW_TEST_CALLED
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)

    # prepare
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane", "Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John", "Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks
    vc.call_view(teacher)
    VIEW_DRAW_CALLED = 0
    VIEW_TEST_CALLED = 0

    # execute
    vc.notify_move_block_to_resource(ResourceType.teacher, block1, teacher, teacher2)

    # validate
    assert VIEW_DRAW_CALLED == 1
    assert VIEW_TEST_CALLED == 1

def test_undos_from_saved_actions(schedule_obj, gui, monkeypatch):
    """create 3 actions of type move, change resource, change movability
    1. undo list should have three actions saved
    2. redo list should have no actions saved
    """
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane", "Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John", "Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks

    # execute
    vc.save_action_block_move(block1, from_day=5, to_day=block1.day.value,
                              from_time=0, to_time=block1.start)
    vc.save_action_block_resource_changed(ResourceType.teacher, block1, from_resource=teacher2, to_resource=teacher)
    vc.save_action_block_movable_toggled(block2,  block2.movable)

    # validate
    undos = vc._undo
    assert len(undos) == 3
    assert len(vc._redo) == 0
    a1,a2,a3 = undos
    assert a1.action == "move"
    assert a1.from_day == 5
    assert a1.to_day == block1.day.value
    assert a1.from_time == 0
    assert a1.to_time == block1.start

    assert a2.action == "change_resource"
    assert a2.to_resource == teacher
    assert a2.from_resource == teacher2

    assert a3.action == "toggle_movable"
    assert a3.was_movable == block2.movable

def test_undos_actual_undo(schedule_obj, gui, monkeypatch):
    """create 3 actions, then undo all changes, one by one
    1. undo action is done
    2. undo action is saved in redo
    """
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane", "Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John", "Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks

    original_movable = block2.movable
    block2.movable = not block2.movable

    vc.save_action_block_move(block1, from_day=5, to_day=block1.day.value,
                              from_time=14, to_time=block1.start)
    vc.save_action_block_resource_changed(ResourceType.teacher, block1, from_resource=teacher2, to_resource=teacher)
    vc.save_action_block_movable_toggled(block2,  original_movable)

    # execute
    vc.undo()

    # validate
    assert len(vc._undo) == 2
    assert len(vc._redo) == 1
    assert block2.movable == original_movable

    # execute
    vc.undo()

    # validate
    assert len(vc._undo) == 1
    assert len(vc._redo) == 2
    assert block1 in schedule_obj.get_blocks_for_teacher(teacher2)

    # execute
    vc.undo()

    # validate
    assert len(vc._undo) == 0
    assert len(vc._redo) == 3
    assert block1.day.value == 5
    assert block1.start == 14

def test_redos(schedule_obj, gui, monkeypatch):
    """create 3 actions, then undo all changes, and then redo them
    1. after, everything is back to the original
    2. redo action is saved in 'undo'
    """
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)
    teacher: Teacher = schedule_obj.get_teacher_by_name("Jane", "Doe")
    teacher2: Teacher = schedule_obj.get_teacher_by_name("John", "Doe")
    blocks = schedule_obj.get_blocks_for_teacher(teacher)
    block1, block2 = blocks

    original_time = block1.start
    original_movable = block2.movable
    block2.movable = not block2.movable

    vc.save_action_block_move(block1, from_day=5, to_day=block1.day.value,
                              from_time=14, to_time=block1.start)
    vc.save_action_block_resource_changed(ResourceType.teacher, block1, from_resource=teacher2, to_resource=teacher)
    vc.save_action_block_movable_toggled(block2,  original_movable)

    # execute
    vc.undo()
    vc.undo()
    vc.undo()
    vc.redo()
    vc.redo()
    vc.redo()

    # validate
    assert len(vc._undo) == 3
    assert len(vc._redo) == 0
    assert block2.movable != original_movable
    assert block1 in schedule_obj.get_blocks_for_teacher(teacher)
    assert block1.start == original_time

def test_undo_redo_no_action_required(schedule_obj, gui, monkeypatch):
    """no pending actions,
    1. redo/undo do not crash the program
    """
    monkeypatch.setattr("src.scheduling_and_allocation.presenter.views_controller.View", ViewTest)
    vc = ViewsController(dirty_flag_method, "", schedule_obj, gui)

    # execute
    vc.undo()
    vc.undo()
    vc.undo()
    vc.redo()
    vc.redo()
    vc.redo()

