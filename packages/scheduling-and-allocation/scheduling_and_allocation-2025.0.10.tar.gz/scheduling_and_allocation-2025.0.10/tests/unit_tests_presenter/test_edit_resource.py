from os import path
from typing import Callable, Any, Optional

import pytest

from src.scheduling_and_allocation.gui_pages import EditResourcesTk, DEColumnDescription
from src.scheduling_and_allocation.model import Schedule, ResourceType
from src.scheduling_and_allocation.presenter.edit_resources import EditResources

SCHEDULE_FILE = path.dirname(__file__) + "/test.csv"
BIN_DIR = path.dirname(__file__) + "/../../schedule"

# ============================================================================
# overload the gui
# ============================================================================
CURRENT_TEST_FILENAME = SCHEDULE_FILE


class EditResourcesTkTest(EditResourcesTk):
    def __init__(self,
                 parent,
                 event_delete_handler: Callable[[list[str], ...], None] = lambda x, *_: None,
                 event_save_handler: Callable[[...], None] = lambda *_: None,
                 colours=None,
                 ):
        self.frame = parent
        self.data_entry: list = list()
        self.delete_handler = event_delete_handler
        self.save_handler = event_save_handler

    def initialize_columns(self, column_descriptions: list[DEColumnDescription], disabled=[]):
        self.called_initialize_columns = True
        self.column_descriptions = column_descriptions

    def refresh(self, data: list[list[Any]]):
        self.called_refresh = True
        self.data_entry = data

    def get_all_data(self) -> list[list[str]]:
        self.called_get_all_data = True
        return self.data_entry


# ============================================================================
# tests
# ============================================================================
@pytest.fixture()
def gui():
    return EditResourcesTkTest(None, None, None)


dirty_flag = False


@pytest.fixture()
def dirty():
    global dirty_flag
    dirty_flag = False

    def set_dirty(value: Optional[bool] = None) -> bool:
        global dirty_flag
        if value is not None:
            dirty_flag = value
        return dirty_flag

    return set_dirty


@pytest.fixture()
def schedule_obj():
    schedule = Schedule()

    # teachers
    schedule.add_update_teacher("Jane", "Doe", "0.25")
    schedule.add_update_teacher("John", "Doe")
    schedule.add_update_teacher("Babe", "Ruth")

    # labs
    schedule.add_update_lab("P107", "C-Lab")
    schedule.add_update_lab("P322", "Mac Lab")
    schedule.add_update_lab("P325")

    # streams
    schedule.add_update_stream("1A", "calculus available")
    schedule.add_update_stream("1B", "no calculus")
    schedule.add_update_stream("2A")
    schedule.add_update_stream("2B")

    return schedule


def test_init_teacher(gui, dirty, schedule_obj):
    """init
    - initializes columns
    """
    # execute
    EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)

    # verify
    assert gui.called_initialize_columns
    columns = gui.column_descriptions
    assert columns[1].property == 'firstname'
    assert columns[2].property == 'lastname'
    assert columns[3].property == 'release'


def test_init_stream(gui, dirty, schedule_obj):
    """init
    - initializes columns
    """
    # execute
    EditResources(dirty, None, ResourceType.stream, schedule_obj, gui)

    # verify
    assert gui.called_initialize_columns
    columns = gui.column_descriptions
    assert columns[0].property == 'number'
    assert columns[1].property == 'description'


def test_init_lab(gui, dirty, schedule_obj):
    """init
    - initializes columns
    """
    # execute
    EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)

    # verify
    assert gui.called_initialize_columns
    columns = gui.column_descriptions
    assert columns[0].property == 'number'
    assert columns[1].property == 'description'


def test_init_no_change_dirty1(gui, dirty, schedule_obj):
    """init
    - no change in dirty flag
    """

    # prepare
    dirty_set_to = True
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to

    # execute
    EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)

    # verify
    assert dirty_flag == dirty_set_to


def test_init_no_change_dirty2(gui, dirty, schedule_obj):
    """init
    - no change in dirty flag
    """

    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to

    # execute
    EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)

    # verify
    assert dirty_flag == dirty_set_to


def test_refresh_no_data(gui, dirty, schedule_obj):
    """refresh data
    - calls gui refresh
    - purges delete queue
    """
    # prepare
    schedule_obj = Schedule()
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)

    # execute
    obj.refresh()

    # verify
    assert gui.called_refresh
    assert len(gui.data_entry) == 0
    assert len(obj.delete_queue) == 0


def test_refresh_with_data(gui, dirty, schedule_obj):
    """refresh data
    - calls gui refresh
    - purges delete queue
    """
    # prepare
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)

    # execute
    obj.refresh()

    # verify
    assert gui.called_refresh
    assert len(gui.data_entry) == 3
    assert len(obj.delete_queue) == 0


def test_refresh_no_change_dirty1(gui, dirty, schedule_obj):
    """refresh data
    - no change dirty flag
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)

    # execute
    obj.refresh()

    # verify
    assert dirty_flag == dirty_set_to


def test_refresh_no_change_dirty2(gui, dirty, schedule_obj):
    """refresh data
    - no change dirty flag
    """
    # prepare
    dirty_set_to = True
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)

    # execute
    obj.refresh()

    # verify
    assert dirty_flag == dirty_set_to


def test_adding_new_teacher(gui, dirty, schedule_obj):
    """save after teacher added
    - teacher is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)
    obj.refresh()
    gui.data_entry.append(["", "New", "Teacher", ".21"])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.teachers()) == 4
    new_teacher = schedule_obj.get_teacher_by_name("New", "Teacher")
    assert new_teacher is not None
    assert new_teacher.release == 0.21
    assert dirty_flag


def test_adding_new_teacher_no_release_specified(gui, dirty, schedule_obj):
    """save after teacher added
    - teacher is added to schedule, but use default release
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)
    obj.refresh()
    gui.data_entry.append([ "", "New", "Teacher"])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.teachers()) == 4
    new_teacher = schedule_obj.get_teacher_by_name("New", "Teacher")
    assert new_teacher is not None
    assert dirty_flag

def test_modifying_teacher_not_new_obj(gui, dirty, schedule_obj):
    """save after teacher release modified
    - teacher modification is added to schedule, without changing the actual object
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    teacher_obj_id = id(schedule_obj.get_teacher_by_number("Doe_Jane"))
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)
    obj.refresh()
    gui.data_entry[1][3] = "3"

    # execute
    obj.save(gui.data_entry)

    # validate
    teacher = schedule_obj.get_teacher_by_number("Doe_Jane")
    assert teacher is not None
    assert teacher.firstname == "Jane"
    assert teacher.release == 3.0
    assert id(teacher) == teacher_obj_id
    assert dirty_flag



def test_modifying_teacher(gui, dirty, schedule_obj):
    """save after teacher modified
    - teacher modification is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)
    obj.refresh()
    gui.data_entry[1][2] = "new name"
    teacher_id = gui.data_entry[1][0]

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.teachers()) == 3
    teacher = schedule_obj.get_teacher_by_number(teacher_id)
    assert teacher is not None
    assert teacher.firstname == "Jane"
    assert teacher.lastname == "new name"
    assert dirty_flag


def test_adding_new_lab(gui, dirty, schedule_obj):
    """save after lab added
    - lab is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)
    obj.refresh()
    gui.data_entry.append(["P000", "New"])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.labs()) == 4
    new_lab = schedule_obj.get_lab_by_number("P000")
    assert new_lab is not None
    assert dirty_flag


def test_adding_new_lab2(gui, dirty, schedule_obj):
    """save after lab added, not specifying description
    - lab is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)
    obj.refresh()
    gui.data_entry.append(["P000"])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.labs()) == 4
    new_lab = schedule_obj.get_lab_by_number("P000")
    assert new_lab is not None
    assert dirty_flag


def test_modifying_lab(gui, dirty, schedule_obj):
    """save after lab modified
    - lab modification is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)
    obj.refresh()
    gui.data_entry[1][1] = "new name"
    lab_id = gui.data_entry[1][0]

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.labs()) == 3
    lab = schedule_obj.get_lab_by_number(lab_id)
    assert lab is not None
    assert lab.description == "new name"
    assert dirty_flag

def test_modifying_lab_not_new_obj(gui, dirty, schedule_obj):
    """save after lab description modified
    - lab modification is added to schedule, without changing the actual object
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    lab_obj_id = id(schedule_obj.get_lab_by_number("P107"))
    obj = EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)
    obj.refresh()
    gui.data_entry[0][1] = "something else"

    # execute
    obj.save(gui.data_entry)

    # validate
    lab = schedule_obj.get_lab_by_number("P107")
    assert lab is not None
    assert lab.description == "something else"
    assert id(lab) == lab_obj_id
    assert dirty_flag


def test_adding_new_stream(gui, dirty, schedule_obj):
    """save after stream added
    - lab is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.stream, schedule_obj, gui)
    obj.refresh()
    gui.data_entry.append(["1C", "New"])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.streams()) == 5
    new_stream = schedule_obj.get_stream_by_number("1C")
    assert new_stream is not None
    assert dirty_flag


def test_adding_new_stream2(gui, dirty, schedule_obj):
    """save after stream added, not specifying description
    - lab is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.stream, schedule_obj, gui)
    obj.refresh()
    gui.data_entry.append(["1C"])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.streams()) == 5
    new_stream = schedule_obj.get_stream_by_number("1C")
    assert new_stream is not None
    assert dirty_flag


def test_modifying_stream(gui, dirty, schedule_obj):
    """save after stream modified
    - lab modification is added to schedule
    - dirty flag is set
    """
    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    obj = EditResources(dirty, None, ResourceType.stream, schedule_obj, gui)
    obj.refresh()
    gui.data_entry[1][1] = "new name"
    stream_id = gui.data_entry[1][0]

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.streams()) == 4
    stream = schedule_obj.get_stream_by_number(stream_id)
    assert stream is not None
    assert stream.description == "new name"
    assert dirty_flag


def test_save_with_no_changes1(gui, dirty, schedule_obj):
    """no changes, then save
    - dirty flag unchanged
    """
    dirty_set_to = False
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)

    # execute
    obj.save(gui.data_entry)

    # validate
    assert dirty_flag == dirty_set_to


def test_save_with_no_changes2(gui, dirty, schedule_obj):
    """no changes, then save
    - dirty flag unchanged
    """
    dirty_set_to = True
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)

    # execute
    obj.save(gui.data_entry)

    # validate
    assert dirty_flag == dirty_set_to


def test_save_with_handle_empty_rows1(gui, dirty, schedule_obj):
    """add empty rows
    - no changes
    - dirty flag unchanged
    """

    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)
    gui.data_entry.append(["", "", "", ""])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.streams()) == 4
    assert dirty_flag == dirty_set_to


def test_save_with_handle_empty_rows2(gui, dirty, schedule_obj):
    """add empty rows
    - no changes
    - dirty flag unchanged
    """

    # prepare
    dirty_set_to = True
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)
    gui.data_entry.append(["", "", "", ""])

    # execute
    obj.save(gui.data_entry)

    # validate
    assert len(schedule_obj.streams()) == 4
    assert dirty_flag == dirty_set_to


def test_delete_teacher(gui, dirty, schedule_obj):
    """delete teacher
    - teacher is removed
    - dirty flag is set
    """

    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.teacher, schedule_obj, gui)
    obj.refresh()
    teacher_id = gui.data_entry[1][0]

    # execute
    obj.delete_obj(gui.data_entry[1])
    obj.save(gui.data_entry)

    # validate
    assert obj.schedule.get_teacher_by_number(teacher_id) is None
    assert dirty_flag


def test_delete_lab(gui, dirty, schedule_obj):
    """delete lab
    - lab is removed
    - dirty flag is set
    """

    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)
    obj.refresh()
    lab_id = gui.data_entry[1][0]

    # execute
    obj.delete_obj(gui.data_entry[1])
    obj.save(gui.data_entry)

    # validate
    assert obj.schedule.get_lab_by_number(lab_id) is None
    assert dirty_flag


def test_delete_stream(gui, dirty, schedule_obj):
    """delete stream
    - stream is removed
    - dirty flag is set
    """

    # prepare
    dirty_set_to = False
    dirty(dirty_set_to)
    assert dirty_flag == dirty_set_to
    obj = EditResources(dirty, None, ResourceType.stream, schedule_obj, gui)
    obj.refresh()
    stream_id = gui.data_entry[1][0]

    # execute
    obj.delete_obj(gui.data_entry[1])
    obj.save(gui.data_entry)

    # validate
    assert obj.schedule.get_stream_by_number(stream_id) is None
    assert dirty_flag


def test_delete_happens_before_resource_update(gui, dirty, schedule_obj):
    """delete obj with id 'a', add new obj with id 'a'
    - an object with id 'a' exists, and has new properties
    Reasoning: if resource updates first, then deletes, the object will be deleted and no longer exist,
               if resource deletes first, then updates, new object will be created
    """

    # prepare
    obj = EditResources(dirty, None, ResourceType.lab, schedule_obj, gui)
    obj.refresh()
    lab_id = gui.data_entry[1][0]

    # execute
    obj.delete_obj(gui.data_entry[1])
    gui.data_entry.append([lab_id, "new object"])
    obj.save(gui.data_entry)

    # validate
    assert obj.schedule.get_lab_by_number(lab_id) is not None
    lab = obj.schedule.get_lab_by_number(lab_id)
    assert lab.description == "new object"
