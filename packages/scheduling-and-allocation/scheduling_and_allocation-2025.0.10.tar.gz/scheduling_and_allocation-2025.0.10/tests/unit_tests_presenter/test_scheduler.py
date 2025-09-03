import inspect
import os
import tkinter
from os import path

import pytest

from src.scheduling_and_allocation.Utilities import Preferences
from src.scheduling_and_allocation.gui_pages.scheduler_tk import SchedulerTk, MAIN_PAGE_EVENT_HANDLERS
from src.scheduling_and_allocation.presenter.menus_main_menu_scheduler import MAIN_MENU_EVENT_HANDLERS
from src.scheduling_and_allocation.presenter.scheduler import Scheduler

SCHEDULE_FILE = path.dirname(__file__) + "/data_test.csv"
PREVIOUS_FILE = path.dirname(__file__) + "/data_test_prev.csv"
BIN_DIR = path.dirname(__file__) + "/../../schedule"
BAD_SCHEDULE_FILE = path.dirname(__file__) + "/data_bad_test.csv"
CREATED_SCHEDULE_FILE = path.dirname(__file__) + "/data_new_test.csv"

# ============================================================================
# overload the gui
# ============================================================================
CURRENT_TEST_FILENAME = SCHEDULE_FILE


class SchedulerTkTest(SchedulerTk):
    def __init__(self, *args, **kwargs):
        self.called: dict[str, bool] = {}
        preferences: Preferences = Preferences()
        super().__init__("Testing", preferences, BIN_DIR)

    def clear(self):
        self.called.clear()

    def show_custom_message(self, title="", msg=""):
        self.called["show_error"] = True

    def start_event_loop(self):
        self.called["start_event_loop"] = True

    def show_error(self, title: str, msg: str, detail: str = ""):
        self.called["show_error"] = True

    def show_message(self, title: str, msg: str, detail: str = ""):
        self.called["show_message"] = True

    def select_file_to_open(self, title:str) -> str:
        self.called["select_file_to_open"] = True
        return CURRENT_TEST_FILENAME

    def select_file_to_save(self) -> str:
        self.called["select_file_to_save"] = True
        return CREATED_SCHEDULE_FILE

    def ask_yes_no(self, title: str, msg: str, detail: str = ""):
        return True

    def create_menu_and_toolbars(*args, **kwargs): ...

    def create_front_page(*args, **kwargs): ...

    def create_standard_page(*args, **kwargs): ...

    def create_status_bar(*args, **kwargs): ...

    def create_welcome_page(self, semester): ...


# ============================================================================
# tests
# ============================================================================
@pytest.fixture()
def gui():
    gui_test = SchedulerTkTest()
    gui_test.clear()
    return gui_test


def test_init(gui):
    obj = Scheduler(BIN_DIR, gui)
    assert gui.called["start_event_loop"]
    assert obj.schedule is None
    assert obj.schedule_filename is ''


# =============================================================================
# verify that menu event handlers have an 'event=None' as part of their signature
# =============================================================================
def test_menu_event_handlers_have_correct_signature(gui):
    Scheduler(BIN_DIR, gui)
    print("")
    for name, handler in MAIN_MENU_EVENT_HANDLERS.items():
        print(name)
        sig = inspect.signature(handler)
        print(sig)
        assert len(sig.parameters) == 0


# =============================================================================
# new, open
# =============================================================================
def test_new_from_menu(gui):
    """open new file from menu
    a) dirty flag set
    b) schedule filename set to ''
    c) gui schedule filename set  to ''
    d) gui previous filename remains unchanged
    """

    # prepare
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    obj.dirty_flag = False

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_new"]()

    # verify
    assert obj.dirty_flag
    assert obj.schedule is not None
    assert gui.schedule_filename == ""
    assert len(obj.schedule.teachers()) == 0


def test_new_button_press_event(gui):
    """same event handling for button press and menu"""

    # prepare
    Scheduler(BIN_DIR, gui)

    # verify
    assert MAIN_PAGE_EVENT_HANDLERS["file_new"] == MAIN_MENU_EVENT_HANDLERS["file_new"]


def test_file_open_from_menu(gui):
    """open file CURRENT_TEST_FILENAME from menu
    a) dirty flag is unset
    b) schedule filename set to file name that was opened
    b) gui schedule filename set to file that was opened
    c) schedule was read
    """

    # prepare
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    obj.dirty_flag = True

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_open"]()

    # verify
    assert not obj.dirty_flag
    assert gui.called.get("select_file_to_open", None)
    assert gui.schedule_filename == CURRENT_TEST_FILENAME
    assert not gui.called.get("show_error", None)
    assert obj.schedule_filename == CURRENT_TEST_FILENAME
    assert obj.schedule is not None
    assert len(obj.schedule.teachers()) != 0


def test_bad_file_open_from_menu(gui):
    """open non-existent file from menu (after a previous file was opened)
    a) dirty flag unchanged (not unset)
    b) schedule filename is unchanged
    c) schedule object is unchanged
    """

    # prepare
    global CURRENT_TEST_FILENAME
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_open"]()
    obj.dirty_flag = True
    old_schedule = obj.schedule
    old_filename = obj.schedule_filename
    old_dirty_flag = obj.dirty_flag
    CURRENT_TEST_FILENAME = BAD_SCHEDULE_FILE
    MAIN_MENU_EVENT_HANDLERS["file_open"]()

    # verify
    assert obj.dirty_flag == old_dirty_flag
    assert gui.called.get("select_file_to_open", None)
    assert gui.schedule_filename == old_filename
    assert gui.called.get("show_error", None) is True
    assert obj.schedule_filename == old_filename
    assert obj.schedule is old_schedule


def test_bad_file_open_from_menu2(gui):
    """open non-existent file from menu (no previous file opened)
    a) dirty flag unchanged (not unset)
    b) schedule filename is unchanged
    c) schedule object is unchanged
    """

    # prepare
    global CURRENT_TEST_FILENAME
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    obj.dirty_flag = True

    # execute
    old_schedule = obj.schedule
    old_filename = obj.schedule_filename
    old_dirty_flag = obj.dirty_flag
    old_gui_filename = obj.gui.schedule_filename
    CURRENT_TEST_FILENAME = BAD_SCHEDULE_FILE
    MAIN_MENU_EVENT_HANDLERS["file_open"]()

    # verify
    assert obj.dirty_flag == old_dirty_flag
    assert gui.called.get("select_file_to_open", None)
    assert gui.schedule_filename == old_gui_filename
    assert gui.called.get("show_error", None) is True
    assert obj.schedule_filename == old_filename
    assert obj.schedule is old_schedule


def test_open_from_menu_user_cancels(gui):
    """start to open a schedule, but then user cancels (no previous file open)
    a) dirty flag unchanged (not unset)
    b) schedule filename is unchanged
    c) schedule object is unchanged
    """

    # prepare
    global CURRENT_TEST_FILENAME
    CURRENT_TEST_FILENAME = SCHEDULE_FILE
    obj = Scheduler(BIN_DIR, gui)
    obj.dirty_flag = True
    old_dirty_flag = obj.dirty_flag
    old_schedule = obj.schedule
    old_filename = obj.schedule_filename
    old_gui_filename = obj.gui.schedule_filename

    # execute
    CURRENT_TEST_FILENAME = None
    MAIN_MENU_EVENT_HANDLERS["file_open"]()

    # verify
    assert obj.dirty_flag == old_dirty_flag  # didn't open new file, dirty flag unchanged
    assert gui.called.get("select_file_to_open", None)
    assert gui.schedule_filename == old_gui_filename
    assert not gui.called.get("show_error", None)
    assert obj.schedule_filename == old_filename  # didn't open new file, old file still valid
    assert obj.schedule == old_schedule  # didn't open new file, schedule is the old one


def test_open_from_menu_user_cancels2(gui):
    """start to open a schedule, but then user cancels (previous file open)
    a) dirty flag unchanged
    b) schedule filename is unchanged
    c) schedule object is unchanged
    """

    # prepare
    global CURRENT_TEST_FILENAME
    CURRENT_TEST_FILENAME = SCHEDULE_FILE
    obj = Scheduler(BIN_DIR, gui)
    MAIN_MENU_EVENT_HANDLERS["file_open"]()
    obj.dirty_flag = True
    old_dirty_flag = obj.dirty_flag
    old_schedule = obj.schedule
    old_filename = obj.schedule_filename
    old_gui_filename = obj.gui.schedule_filename

    # execute
    CURRENT_TEST_FILENAME = None
    MAIN_MENU_EVENT_HANDLERS["file_open"]()

    # verify
    assert not gui.called.get("show_error", None)
    assert gui.called.get("select_file_to_open", None)

    assert obj.dirty_flag == old_dirty_flag  # didn't open new file, dirty flag unchanged
    assert gui.schedule_filename == old_filename
    assert obj.gui.schedule_filename == old_gui_filename
    assert obj.schedule == old_schedule  # didn't open new file, schedule is the old one


def test_open_from_main_page_event(gui):
    """same event handling for button press and menu"""

    # prepare
    Scheduler(BIN_DIR, gui)

    # verify
    assert MAIN_PAGE_EVENT_HANDLERS["file_open"] == MAIN_MENU_EVENT_HANDLERS["file_open"]


def test_open_previous(gui):
    """Using the preferences, get previous file that was opened, and open that
    - filename set to PREVIOUS FILE
    - dirty flag unset
    - schedule has 18 teachers
    """

    # prepare
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    obj.dirty_flag = True

    # execute
    print(PREVIOUS_FILE)
    obj.preferences.previous_file(PREVIOUS_FILE)
    obj.preferences.save()
    MAIN_PAGE_EVENT_HANDLERS["file_open_previous"]()

    # verify
    assert not obj.dirty_flag
    assert gui.schedule_filename == PREVIOUS_FILE
    assert not gui.called.get("show_error", None)
    assert obj.schedule_filename == PREVIOUS_FILE
    assert obj.schedule is not None
    assert len(obj.schedule.teachers()) == 18

    # prepare
    global CURRENT_TEST_FILENAME
    CURRENT_TEST_FILENAME = SCHEDULE_FILE
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    obj.dirty_flag = False

    # execute
    MAIN_PAGE_EVENT_HANDLERS["file_open"]()

    # verify
    assert not obj.dirty_flag
    assert gui.schedule_filename == SCHEDULE_FILE
    assert not gui.called.get("show_error", None)
    assert obj.schedule_filename == SCHEDULE_FILE
    assert obj.schedule is not None
    assert len(obj.schedule.teachers()) != 0


# =============================================================================
# save, save as
# =============================================================================
def test_save_from_menu(gui):
    """open file, and save
    - dirty flag is unset
    - new file is created
    """

    # prepare
    global CURRENT_TEST_FILENAME
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    obj._open_file(SCHEDULE_FILE)
    assert obj.schedule is not None
    before = len(obj.schedule.teachers())
    last_modified_time = os.path.getmtime(SCHEDULE_FILE)
    obj.dirty_flag = True

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_save"]()

    # verify
    assert not obj.dirty_flag
    assert os.path.getmtime(SCHEDULE_FILE) > last_modified_time
    assert obj.schedule_filename == SCHEDULE_FILE
    obj._open_file(SCHEDULE_FILE)
    assert len(obj.schedule.teachers()) == before


def test_save_as_from_menu(gui):
    """open file, save as
    - dirty flag is unset
    - ask user for filename
    - filename is changed
    """

    # prepare
    global CURRENT_TEST_FILENAME
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    obj._open_file(SCHEDULE_FILE)
    assert obj.schedule is not None
    before = len(obj.schedule.teachers())
    obj.dirty_flag = True
    try:
        os.remove(CREATED_SCHEDULE_FILE)
    except FileNotFoundError:
        pass

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_save_as"]()

    # verify
    assert not obj.dirty_flag
    assert gui.called.get("select_file_to_save", None)
    assert os.path.exists(CREATED_SCHEDULE_FILE)
    assert obj.schedule_filename == CREATED_SCHEDULE_FILE
    assert obj.gui.schedule_filename == CREATED_SCHEDULE_FILE
    obj._open_file(CREATED_SCHEDULE_FILE)
    assert len(obj.schedule.teachers()) == before


def test_save_no_schedule(gui):
    """no schedule, save
    - error message is displayed
    - dirty change remains same as before
    """
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    last_modified_time = os.path.getmtime(SCHEDULE_FILE)
    assert obj.schedule_filename == ""
    obj.dirty_flag = True

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_save"]()

    # verify
    assert obj.dirty_flag  # no schedule to save, no change to dirty flag
    assert os.path.getmtime(SCHEDULE_FILE) == last_modified_time
    assert obj.schedule_filename == ''
    assert gui.called.get("show_error")


def test_save_as_no_schedule(gui):
    """no schedule, save as
    - error message is displayed
    - dirty change remains same as before
    """
    obj = Scheduler(BIN_DIR, gui)
    assert obj.schedule is None
    last_modified_time = os.path.getmtime(SCHEDULE_FILE)
    assert obj.schedule_filename is ''
    obj.dirty_flag = True

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_save"]()

    # verify
    assert obj.dirty_flag  # no file to save, so dirty flag not updated
    assert os.path.getmtime(SCHEDULE_FILE) == last_modified_time
    assert obj.schedule_filename is ''
    assert gui.called.get("show_error", None)
    assert not gui.called.get("select_file_to_save", None)


def test_save_no_filename(gui):
    """new schedule, save
    - asks user for filename
    - dirty flag unset
    """
    # prepare
    obj = Scheduler(BIN_DIR, gui)
    MAIN_MENU_EVENT_HANDLERS["file_new"]()
    assert obj.schedule_filename == ''
    obj.dirty_flag = True
    try:
        os.remove(CREATED_SCHEDULE_FILE)
    except FileNotFoundError:
        pass

    # execute
    MAIN_MENU_EVENT_HANDLERS["file_save"]()

    # verify
    assert not obj.dirty_flag
    assert os.path.exists(CREATED_SCHEDULE_FILE)
    assert obj.schedule_filename == CREATED_SCHEDULE_FILE
    assert not gui.called.get("show_error", None)
    assert gui.called.get("select_file_to_save", None)


# =============================================================================
# exit
# =============================================================================
def test_exit_with_new_schedule(gui):
    """new schedule, exit
    - asks user save?
    - asks user for filename
    """
    # prepare
    obj = Scheduler(BIN_DIR, gui)
    MAIN_MENU_EVENT_HANDLERS["file_new"]()
    assert obj.schedule_filename == ''
    obj.dirty_flag = True
    try:
        os.remove(CREATED_SCHEDULE_FILE)
    except FileNotFoundError:
        pass

    # execute
    MAIN_PAGE_EVENT_HANDLERS["file_exit"]()

    # verify
    assert os.path.exists(CREATED_SCHEDULE_FILE)
    assert obj.schedule_filename == CREATED_SCHEDULE_FILE
    assert not gui.called.get("show_error", None)
    assert gui.called.get("select_file_to_save", None)


# =============================================================================
# changing semesters
# =============================================================================
def test_semester_switch(gui):
    """switch semesters
    - previous filename is modified
    """

    # prepare
    obj = Scheduler(BIN_DIR, gui)
    obj.preferences.semester("fall")
    obj.preferences.previous_file("data_fall.csv")
    obj.preferences.save()
    obj.preferences.semester("winter")
    obj.preferences.previous_file("data_winter.csv")
    obj.preferences.save()

    # execute
    obj.gui.current_semester = "fall"
    MAIN_PAGE_EVENT_HANDLERS["semester_change"]()

    # validate
    assert os.path.basename(obj.previous_filename) == "data_fall.csv"

    # execute
    obj.gui.current_semester = "winter"
    MAIN_PAGE_EVENT_HANDLERS["semester_change"]()

    # validate
    assert os.path.basename(obj.previous_filename) == "data_winter.csv"
