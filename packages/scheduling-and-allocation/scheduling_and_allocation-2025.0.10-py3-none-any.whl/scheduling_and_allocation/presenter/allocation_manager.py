
"""Entry point for the GUI_Pages Allocation Management Tool"""
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Optional

from .allocation_editor import AllocationEditor
from .edit_courses import EditCourses
from .edit_resources import EditResources
from .menus_main_menu_allocation import set_menu_event_handler_allocation, main_menu_allocation
from .student_numbers import StudentNumbers

from ..Utilities import Preferences
from ..gui_pages.allocation_manager_tk import AllocationManagerTk, set_main_page_event_handler
from ..model import SemesterType, Schedule, ResourceType, CouldNotReadFileError

# =====================================================================================
# Notebook book-keeping
# =====================================================================================
@dataclass
class NBTabInfo:
        name: str
        label: str
        subpages: list = field(default_factory=list)
        frame_args: dict[str, Any] =  field(default_factory=dict)
        creation_handler: Callable = lambda *_: None
        is_default_page: bool = False

DIRECTORY = str
PATH = str
VALID_SEMESTERS = [SemesterType.fall, SemesterType.winter]


# =====================================================================================
# Allocation Manager
# =====================================================================================
class AllocationManager:
    NB_course = "Courses"
    NB_teacher = "Teachers"
    NB_students = "Students"
    NB_allocation = "Allocation"


    def __init__(self, bin_dir: DIRECTORY, gui: Optional[AllocationManagerTk] = None):

        self.preferences: Preferences = Preferences()
        self.schedules: dict[SemesterType, Optional[Schedule]] = {s:None for s in VALID_SEMESTERS}
        self._previous_filenames: dict[SemesterType, str] = {s:"" for s in VALID_SEMESTERS}
        self._dirty_flag = False
        self.current_tab: Optional[str] = None
        self.standard_page = None

        # gui is optional so that we can test the presenter more readily
        if gui:
            self.gui = gui
        else:
            self.gui: AllocationManager = AllocationManagerTk('Allocation', self.preferences, bin_dir)

        self._schedule_filenames: dict[SemesterType, PATH] = {s:"" for s in VALID_SEMESTERS}

        self._allocation_manager_already_open = False

        # --------------------------------------------------------------------
        # required notebook pages
        # --------------------------------------------------------------------
        course_tab = {}
        teacher_tab = {}
        student_tab = {}
        allocation_tab = {}
        for semester in VALID_SEMESTERS:
            allocation_tab[semester] = NBTabInfo(label=f"{semester.name} {self.NB_allocation}",
                                             name=f"{semester.name} {self.NB_allocation}")
            course_tab[semester] = NBTabInfo(label=f"{semester.name} {self.NB_course}",
                                             name=f"{semester.name} {self.NB_course}")
            teacher_tab[semester] = NBTabInfo(label=f"{semester.name} {self.NB_teacher}",
                                             name=f"{semester.name} {self.NB_teacher}")
            student_tab[semester] = NBTabInfo(label=f"{semester.name} {self.NB_students}",
                                             name=f"{semester.name} {self.NB_students}")

        self._notebook_tabs = []
        for semester in VALID_SEMESTERS:
            self._notebook_tabs.append(
                NBTabInfo(label=semester.name, name=semester.name,
                      subpages=[allocation_tab[semester], course_tab[semester],
                                teacher_tab[semester], student_tab[semester]]
                          )
            )

        # --------------------------------------------------------------------
        # create the Menu and Toolbars
        # --------------------------------------------------------------------
        set_menu_event_handler_allocation("file_new", self.new_menu_event)
        set_menu_event_handler_allocation("file_open", self.open_menu_event)
        set_menu_event_handler_allocation("file_save", self.save_schedule)
        set_menu_event_handler_allocation("file_exit", self.menu_exit_event)

        self.gui.toggle_auto_save = self.auto_save_set

        set_main_page_event_handler("go", self.go)
        set_main_page_event_handler("exit", self.exit_event)

        (self._toolbar_buttons, self._button_properties, self._menu) = main_menu_allocation(VALID_SEMESTERS)

        # --------------------------------------------------------------------
        # create the Gui Main Window
        # --------------------------------------------------------------------
        self.gui.create_menu_and_toolbars(self._toolbar_buttons, self._button_properties, self._menu)
        self.gui.create_welcome_page(VALID_SEMESTERS)
        self.gui.create_status_bar()
        self.gui.notebook_tab_changed_handler = self.notebook_tab_has_changed

        self._previous_filenames: dict[SemesterType, PATH] = {}
        for semester in VALID_SEMESTERS:
            self.preferences.semester(semester.name)
            self.previous_filename(semester, self.preferences.previous_file())

        self.set_dirty_indicator()
        self.gui.start_event_loop()


    # ============================================================================================
    #  getters/setters - filenames
    # ============================================================================================
    def schedule_filename(self, semester: SemesterType=SemesterType.any, value=None) -> str:
        if value is not None:
            self._schedule_filenames[semester] = value
            self.gui.schedule_filename(semester,value)
            if value != "":
                self.previous_filename(semester,value)
        return self._schedule_filenames[semester]


    def previous_filename(self, semester:SemesterType=SemesterType.any, value=None)->str:
        if value is not None:
            self.preferences.semester(semester.name)
            self.preferences.previous_file(value)
            self._previous_filenames[semester] = value
            self.preferences.save()

        return self._previous_filenames.get(semester,"")

    # ============================================================================================
    # Properties - is data changed (dirty)
    # ============================================================================================
    @property
    def dirty_flag(self) -> bool:
        """is the data different from what was saved on disk?"""
        return self._dirty_flag

    @dirty_flag.setter
    def dirty_flag(self, value):
        self._dirty_flag = value
        self.set_dirty_indicator()

    # ============================================================================================
    # Events ... open
    # ============================================================================================
    def open_menu_event(self, semester):
        """open a file"""
        self.open_menu_event_from_main_page(semester)
        self.gui.create_standard_page(self._notebook_tabs, reset=True)

    def open_menu_event_from_main_page(self, semester):
        """open a file"""
        self.preferences.semester(semester.name)
        filename = self.gui.select_file_to_open(f"Open Schedule ({semester.name.upper()})")
        self._open_file(filename, semester)

    def open_previous_file_event(self, semester):
        """open previously opened file"""
        self.open_previous_file_event_from_main_page(semester)
        self.gui.create_standard_page(self._notebook_tabs, reset=True)

    def open_previous_file_event_from_main_page(self, semester):
        """open previously opened file"""
        self.preferences.semester(semester.name)
        filename = self.preferences.previous_file()
        self._open_file(filename, semester)

    def _open_file(self, filename: str, semester):
        """generic open file method"""
        if filename:
            try:
                schedule = Schedule(filename)
                self._allocation_manager_already_open = False
                self.schedules[semester] = schedule
                self.schedule_filename(semester, filename)
                self.dirty_flag = False
                if self.standard_page is not None:
                    self.gui.create_standard_page(self._notebook_tabs)


            except CouldNotReadFileError as e:
                self.gui.show_error("Read File", str(e))

    # ============================================================================================
    # Event handlers - new
    # ============================================================================================
    def new_menu_event(self, semester: SemesterType):
        """create a new file"""
        schedule = Schedule()
        self.schedules[semester] = schedule
        self.schedule_filename(semester, "")
        self.dirty_flag = True
        self.gui.create_standard_page(self._notebook_tabs, reset=True)

    # ============================================================================================
    # Event handlers - save
    # ============================================================================================
    def save_schedule(self, *_):
        """generic save file method"""

        for semester in self.schedules.keys():
            if self.schedules[semester] is None:
                continue
            filename = self._schedule_filenames.get(semester, None)

            if filename is None or filename == "":
                filename = self.gui.select_file_to_save(f"Save Schedule As ({semester.name.upper()})")

            if filename is not None and filename != "":
                self.schedules[semester].write_file(filename)
                self.dirty_flag = False
                self.schedule_filename(semester,filename)

    # ============================================================================================
    # Event handlers - exit
    # ============================================================================================
    def exit_event(self, *_):
        """program is exiting"""
        if self.dirty_flag:
            ans = self.gui.ask_yes_no("File", "Save File?")
            if ans:
                self.save_schedule()

    def menu_exit_event(self, _:SemesterType):
        self.gui.exit_schedule()

    # ============================================================================================
    # Event handlers - go
    # ============================================================================================
    def go(self):

        for semester in VALID_SEMESTERS:
            if (self.gui.selected_files[semester].get() == "" or
                self.gui.selected_files[semester].get() == str(None)):
                self.new_menu_event(semester)
                self.set_dirty_method(False)
            else:
                self._open_file(self.gui.selected_files[semester].get(), semester)
        self.standard_page = self.gui.create_standard_page(self._notebook_tabs)
        self.set_dirty_indicator()

    # ==================================================================
    # notebook tab has changed
    # ==================================================================
    def notebook_tab_has_changed(self, name: str, frame):
        """
        the standard page notebook tab has been change
        :param name: name of the tab
        :param frame: container where the gui is stored
        """
        self.current_tab = name
        if name == "fall":
            self.gui.select_tab(f"fall {self.NB_allocation}")
            self._allocation_manager_already_open = False
        if name == "winter":
            self.gui.select_tab(f"winter {self.NB_allocation}")
            self._allocation_manager_already_open = False
        for semester in VALID_SEMESTERS:
            if name == f"{semester.name} {self.NB_allocation}":
                self.update_allocation(frame, semester)
            if name == f"{semester.name} {self.NB_course}":
                self.update_edit_courses(frame, semester)
                self._allocation_manager_already_open = False
            elif name == f"{semester.name} {self.NB_teacher}":
                self.update_edit_teachers(frame, semester)
                self._allocation_manager_already_open = False
            elif name == f"{semester.name} {self.NB_students}":
                self.update_edit_students(frame, semester)
                self._allocation_manager_already_open = False

    # ==================================================================
    # update the allocation frame
    # ==================================================================
    def update_allocation(self, frame, semester):
        if not self._allocation_manager_already_open:
            other_schedules = [self.schedules[s] for s in VALID_SEMESTERS if s != semester]
            AllocationEditor(
                self.set_dirty_method,
                frame,
                schedule=self.schedules[semester],
                other_schedules = other_schedules
            )
        self._allocation_manager_already_open = True

    # ==================================================================
    # draw_edit_courses
    # ==================================================================
    def update_edit_courses(self, frame, semester):
        """A page where courses can be added/modified or deleted"""
        data_entry = EditCourses(self.set_dirty_method, frame, self.schedules[semester])
        data_entry.schedule = self.schedules[semester]
        data_entry.refresh()

    # ==================================================================
    # update_edit_teachers
    # ==================================================================
    def update_edit_teachers(self, frame, semester):
        """A page where teacher can be added/modified or deleted"""
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.teacher,
                                   self.schedules[semester], self.preferences)
        data_entry.schedule = self.schedules[semester]
        data_entry.refresh()

    # ==================================================================
    # update_edit_students
    # ==================================================================
    def update_edit_students(self, frame, semester):
        data_entry = StudentNumbers(self.set_dirty_method, frame, self.schedules[semester])
        data_entry.refresh()

    # ==================================================================
    # schedule has been modified, update gui as required
    # ==================================================================
    def set_dirty_method(self, value: Optional[bool] = None) -> bool:

        # if value is true, and autosave is on, save the file
        if value and self.preferences.auto_save():
            self.save_schedule()
            value = False

        if value is not None:
            self.dirty_flag = value
        return self.dirty_flag

    # ============================================================================================
    # Event handler, auto save setting changed
    # ============================================================================================
    def set_dirty_indicator(self):
        if self.gui and self.dirty_flag:
            self.gui.dirty_text = "UNSAVED"
        else:
            self.gui.dirty_text = self.auto_save_text

    def auto_save_set(self, value, *_):
        self.preferences.auto_save(value)
        self.set_dirty_indicator()
        self.preferences.save()

    @property
    def auto_save_text(self):
        if self.preferences.auto_save():
            return "AUTO SAVE ON"
        else:
            return ""


