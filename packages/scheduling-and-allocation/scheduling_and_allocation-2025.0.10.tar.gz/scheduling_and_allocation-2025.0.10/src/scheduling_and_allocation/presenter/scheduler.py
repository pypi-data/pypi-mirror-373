"""
# ============================================================================
# Main entry point to the schedule application
#
# Events triggered by menus_main_menu toolbar and menu events
#       new_menu_event()
#       open_menu_event()
#       save_menu_event()
#       save_as_menu_event()
#       validate()
#       exit_event()
#       print_views(resource_type, canvas)
#       print_registrar()
#       auto_save_set(bool)
#
# Events triggered from the welcome page
#       exit_event()
#       open_menu_event()
#       new_menu_event()
#       open_previous_file_event()
#       semester_change()
#
# Notebook change events
#       update_course_text(frame)
#       update_teacher_text(frame)
#       update_choices_of_resource_views(frame)
#       update_overview(frame)
#       update_edit_courses(frame)
#       update_edit_teachers(frame)
#       update_edit_labs(frame)
#       update_edit_streams(frame)
#
# ============================================================================
"""


from __future__ import annotations

from enum import Enum
from functools import partial
from typing import Optional

from .edit_resources import EditResources
from .edit_courses import EditCourses
from .menus_main_menu_scheduler import set_menu_event_handler, main_menu
from .view import View
from .views_controller import ViewsController
from .notebook_tab_data import NBTabInfo

from ..Utilities import Preferences
from ..export.registrars_office import registrars_output
from ..gui_pages.scheduler_tk import SchedulerTk, set_main_page_event_handler
from ..model import Schedule, ResourceType
from ..model.exceptions import CouldNotReadFileError
from ..gui_generics.read_only_text_tk import ReadOnlyTextTk
from ..export.view_export_canvases import PDFCanvas, LatexCanvas
from ..gui_pages.view_canvas_tk import ViewCanvasTk

class CanvasType(Enum):
    latex = 1
    pdf = 2

# =====================================================================================
# Scheduler
# =====================================================================================

DIRECTORY = str


class Scheduler:
    """
    This is the main entry point for the Scheduler Program
    """

    NB_overview_course = "by Course"
    NB_overview_teacher = "by Teacher"
    NB_schedule = "Schedules"
    NB_overview = "Overview"
    NB_course = "Courses"
    NB_teacher = "Teachers"
    NB_lab = "Labs"
    NB_stream = "Streams"

    def __init__(self, bin_dir: DIRECTORY, gui: Optional[SchedulerTk] = None):
        """
        :param bin_dir: where this executable file exists
        :param gui: creates gui if not already defined
        """

        self.view_controller: Optional[ ViewsController] = None
        self.preferences: Preferences = Preferences()
        self.schedule: Optional[Schedule] = None
        self._dirty_flag = False
        self.current_tab: Optional[str] = None

        # gui is optional so that we can test the presenter more readily
        if gui:
            self.gui = gui
        else:
            self.gui: SchedulerTk = SchedulerTk('Scheduler', self.preferences, bin_dir)

        self._schedule_filename = ""
        self._previous_filename = self.preferences.previous_file()

        # --------------------------------------------------------------------
        # required notebook pages
        # --------------------------------------------------------------------
        by_course_page = NBTabInfo(label=self.NB_overview_course, name=self.NB_overview_course)
        by_teacher_page = NBTabInfo(label=self.NB_overview_teacher, name=self.NB_overview_teacher)

        self._required_tabs: list[NBTabInfo] = [
            NBTabInfo(label=self.NB_schedule, name=self.NB_schedule, is_default_page=True),
            NBTabInfo(label=self.NB_overview, name=self.NB_overview, subpages=[by_course_page, by_teacher_page]),
            NBTabInfo(label=self.NB_course, name=self.NB_course),
            NBTabInfo(label=self.NB_teacher, name=self.NB_teacher),
            NBTabInfo(label=self.NB_lab, name=self.NB_lab),
            NBTabInfo(label = self.NB_stream, name = self.NB_stream)
        ]

        # --------------------------------------------------------------------
        # create the Menu and Toolbars
        # --------------------------------------------------------------------
        set_menu_event_handler("file_new", self.new_menu_event)
        set_menu_event_handler("file_open", self.open_menu_event)
        set_menu_event_handler("file_save", self.save_menu_event)
        set_menu_event_handler("file_save_as", self.save_as_menu_event)
        set_menu_event_handler("validate", self.validate)
        set_menu_event_handler("file_exit", self.menu_exit_event)
        set_main_page_event_handler("file_exit", self.exit_event)
        set_main_page_event_handler("file_open", self.open_menu_event)
        set_main_page_event_handler("file_new", self.new_menu_event)
        set_main_page_event_handler("file_open_previous", self.open_previous_file_event)
        set_main_page_event_handler("semester_change", self.semester_change)
        set_menu_event_handler("print_pdf_teacher", partial(self.print_views, ResourceType.teacher, CanvasType.pdf))
        set_menu_event_handler("print_pdf_lab", partial(self.print_views, ResourceType.lab, CanvasType.pdf))
        set_menu_event_handler("print_pdf_streams", partial(self.print_views, ResourceType.stream, CanvasType.pdf))
        set_menu_event_handler("print_latex_teacher", partial(self.print_views, ResourceType.teacher, CanvasType.latex))
        set_menu_event_handler("print_latex_lab", partial(self.print_views, ResourceType.lab, CanvasType.latex))
        set_menu_event_handler("print_latex_streams", partial(self.print_views, ResourceType.stream, CanvasType.latex))
        set_menu_event_handler("print_registrar", self.print_registrar)

        self.gui.toggle_auto_save = self.auto_save_set

        # TODO
        set_menu_event_handler("print_text", self.menu_ignore)

        (self._toolbar_buttons, self._button_properties, self._menu) = main_menu()

        # --------------------------------------------------------------------
        # create the Gui Main Window
        # --------------------------------------------------------------------
        self.gui.create_menu_and_toolbars(self._toolbar_buttons, self._button_properties, self._menu)
        self.gui.create_welcome_page(self.preferences.semester())
        self.gui.create_status_bar()
        self.gui.notebook_tab_changed_handler = self.notebook_tab_has_changed
        self.set_dirty_indicator()

        self.gui.start_event_loop()

    # ============================================================================================
    #  Properties - filenames
    # ============================================================================================
    @property
    def schedule_filename(self):
        """The filename associated with this file"""
        return self._schedule_filename

    @schedule_filename.setter
    def schedule_filename(self, value: Optional[str]):
        self._schedule_filename = value
        self.gui.schedule_filename = value
        if value is not None and value != "":
            self.previous_filename = value

    @property
    def previous_filename(self):
        """what was the last opened file"""
        return self._previous_filename

    @previous_filename.setter
    def previous_filename(self, value):
        self.preferences.previous_file(value)
        self._previous_filename = value
        self.gui.previous_file = value
        self.preferences.save()

    @property
    def auto_save_text(self):
        if self.preferences.auto_save():
            return "AUTO SAVE ON"
        else:
            return ""

    # ============================================================================================
    # Properties - is data changed (dirty)
    # ============================================================================================
    @property
    def dirty_flag(self) -> bool:
        """is the data different than what was saved on disk?"""
        return self._dirty_flag

    @dirty_flag.setter
    def dirty_flag(self, value):
        self.set_dirty_method(value)

    # ============================================================================================
    # Event handler, auto save setting changed
    # ============================================================================================
    def set_dirty_indicator(self):
        if self.gui and self.dirty_flag:
            self.gui.dirty_text = "UNSAVED"
        else:
            self.gui.dirty_text = self.auto_save_text

    def auto_save_set(self, value):
        self.preferences.auto_save(value)
        self.set_dirty_indicator()
        self.preferences.save()

    # ============================================================================================
    # Event handlers - file open/close/save/new
    # ============================================================================================
    def new_menu_event(self):
        """create a new file"""
        self.schedule = Schedule()
        self.schedule_filename = ""
        self.dirty_flag = True
        self.refresh_for_newly_opened_file()

    def open_menu_event(self):
        """open a file"""
        filename = self.gui.select_file_to_open(f"Open Schedule")
        self._open_file(filename)

    def open_previous_file_event(self):
        """open previously opened file"""
        filename = self.preferences.previous_file()
        self._open_file(filename)

    def _open_file(self, filename: str):
        """generic open file method"""
        if filename:
            try:
                schedule = Schedule(filename)
                self.schedule = schedule
                self.schedule_filename = filename
                self.dirty_flag = False
                self.refresh_for_newly_opened_file()

            except CouldNotReadFileError as e:
                self.gui.show_custom_message("Read File Error", str(e))

    def save_menu_event(self):
        """save file"""
        self._save_schedule(self.schedule_filename)

    def save_as_menu_event(self):
        """save as file"""
        self._save_schedule(None)

    def _save_schedule(self, filename: Optional[str]):
        """generic save file method"""

        if self.schedule is None:
            self.gui.show_error("Save Schedule", "There is no schedule to save!")
            return
        if filename is None or filename == "":
            filename = self.gui.select_file_to_save()

        if filename is not None and filename != "":
            self.schedule.write_file(filename)
            self.schedule_filename = filename
            self.dirty_flag = False

    # ============================================================================================
    # Event handlers - semester change
    # ============================================================================================
    def semester_change(self, *_):
        """semester has been changed"""
        self.preferences.semester(self.gui.current_semester)
        self.previous_filename = self.preferences.previous_file()
        self.preferences.save()

    def refresh_for_newly_opened_file(self):
        pass
        if self.view_controller is not None:
            self.view_controller.kill_all_views()
        self.view_controller = None
        self.gui.create_standard_page(self._required_tabs, reset=True)

    # ============================================================================================
    # Event handlers - exit
    # ============================================================================================

    def exit_event(self):
        """program is exiting"""
        if self.dirty_flag:
            ans = self.gui.ask_yes_no("File", "Save File?")
            if ans:
                self.save_menu_event()

    def menu_exit_event(self):
        self.gui.exit_schedule()

    def menu_ignore(self):
        # print("still a To Do!!")
        pass

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
        if name == self.NB_overview_course:
            self.update_course_text(frame)
        elif name == self.NB_overview_teacher:
            self.update_teacher_text(frame)
        elif name == self.NB_schedule:
            self.update_choice_colours(frame)
        elif name == self.NB_overview:
            self.update_overview(frame)
        elif name == self.NB_course:
            self.update_edit_courses(frame)
        elif name == self.NB_teacher:
            self.update_edit_teachers(frame)
        elif name == self.NB_lab:
            self.update_edit_labs(frame)
        elif name == self.NB_stream:
            self.update_edit_streams(frame)

    # ==================================================================
    # update choice colours
    # ==================================================================
    def update_choice_colours(self, frame):
        """if not already created, create Views Controller, update colours"""
        if self.view_controller is None:
            self.view_controller = ViewsController(self.set_dirty_method, frame, self.schedule)
        self.view_controller.refresh()

    # ==================================================================
    # update_overview
    # A text representation of the schedules
    # ==================================================================
    def update_overview(self, frame):
        """not required to do anything"""
        pass

    def update_course_text(self, frame):
        """update text describing all the courses"""
        text: list[str] = list()
        if self.schedule is None:
            text.append('There is no schedule, please open one')
        else:
            if not self.schedule.courses:
                text.append('No courses defined in this schedule')
            else:
                for c in self.schedule.courses():
                    text.append(str(c))
        data_entry = ReadOnlyTextTk(frame, text)
        data_entry.write(text)

    def update_teacher_text(self, frame):
        """udpate the text describing all the teacher duties"""
        text = []
        if not self.schedule.teachers:
            text.append('No teachers defined in this schedule')
        else:
            for t in self.schedule.teachers():
                text.append(self.schedule.teacher_details(t))
        data_entry = ReadOnlyTextTk(frame, text)
        data_entry.write(text)

    # ==================================================================
    # update_edit_teachers
    # ==================================================================
    def update_edit_teachers(self, frame):
        """A page where teacher can be added/modified or deleted"""
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.teacher, self.schedule, self.preferences)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # update_edit_streams
    # ==================================================================
    def update_edit_streams(self, frame):
        """A page where stream_ids can be added/modified or deleted"""
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.stream, self.schedule, self.preferences)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # update_edit_labs
    # ==================================================================
    def update_edit_labs(self, frame):
        """A page where lab_ids can be added/modified or deleted"""
        data_entry = EditResources(self.set_dirty_method, frame, ResourceType.lab, self.schedule, self.preferences)
        data_entry.schedule = self.schedule
        data_entry.refresh()

    # ==================================================================
    # draw_edit_courses
    # ==================================================================
    def update_edit_courses(self, frame):
        """A page where courses can be added/modified or deleted"""
        data_entry = EditCourses(self.set_dirty_method, frame, self.schedule)
        data_entry.schedule = self.schedule
        data_entry.refresh()


    # ==================================================================
    # print_views
    # ==================================================================
    def print_views(self, resource_type, canvas_type: CanvasType):
        """
        print the schedule 'views'
        :param resource_type:
        :param canvas_type: pdf or latex
        :return:
        """

        # no schedule yet
        if not self.schedule:
            self.gui.show_error("Export", "Cannot export - There is no schedule")

        # should not print if the schedule is not saved
        if self.dirty_flag:
            self.gui.show_message(
                title="Unsaved Changes",
                msg="There are unsaved changes",
                detail="You cannot print schedules if the schedule is not saved"
                )
            return

        # gather info
        resources = ()
        match resource_type:
            case ResourceType.teacher:
                resources = self.schedule.teachers()
            case ResourceType.lab:
                resources = self.schedule.labs()
            case ResourceType.stream:
                resources = self.schedule.streams()

        # loop over each resource and create file
        save_dir = self.preferences.current_dir() or self.preferences.home_directory()
        for resource in resources:

            # pdf or latex
            if canvas_type == CanvasType.pdf:
                cn = PDFCanvas(title=str(resource), schedule_name=self.schedule.filename,
                               directory=save_dir)
                vc = ViewCanvasTk(cn, 0.8)
            else:
                cn = LatexCanvas(title=str(resource), schedule_name=self.schedule.filename,
                               directory=save_dir)
                vc = cn

            # get all the blocks
            blocks = ()
            match resource_type:
                case ResourceType.teacher:
                    blocks = self.schedule.get_blocks_for_teacher(resource)
                case ResourceType.lab:
                    blocks = self.schedule.get_blocks_in_lab(resource)
                case ResourceType.stream:
                    blocks = self.schedule.get_blocks_for_stream(resource)

            # draw the blocks
            for block in blocks:
                text = View.get_block_text(block, scale=1, resource_type=ResourceType.teacher)

                day, start_time, duration = View._block_to_floats(block)

                vc.draw_block(resource_type=ResourceType.teacher,
                              day=day, start_time=start_time, duration=duration,
                              text=text,
                              gui_tag="",
                              movable=True,
                              )
            # write to file
            cn.save()

    # ==================================================================
    # print the output needed for the registrar
    # ==================================================================
    def print_registrar(self):
        if self.schedule is None:
            self.gui.show_error("Save Schedule", "There is no schedule to write!")
            return
        filename = self.gui.select_file_to_save()
        try:
            registrars_output(self.schedule, filename)
        except Exception as e:
            self.gui.show_message(title="Registrar's Output", msg="Could not save file",
                                  detail=f"Error: {e}")


    # ==================================================================
    # validate
    # ==================================================================
    def validate(self):
        """check if the schedule is valid, show result to user"""
        msg = self.schedule.validate()
        if len(msg) != 0:
            self.gui.show_text(title="Validate", text=msg)
        else:
            self.gui.show_message(title="Validate", msg="Everything is ok!")


    # ==================================================================
    # schedule has been modified, update gui as required
    # ==================================================================
    def set_dirty_method(self, value: Optional[bool] = None) -> bool:

        # if value is true, update all the open views
        if value and self.current_tab != self.NB_schedule and self.view_controller is not None:
            self.view_controller.redraw_all()

        # if value is true, and autosave is on, save the file
        if value and self.preferences.auto_save():
            self._save_schedule(self.schedule_filename)
            value = False

        if value is not None:
            self._dirty_flag = value

        self.set_dirty_indicator()
        return self.dirty_flag

