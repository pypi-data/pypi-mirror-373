"""
# ============================================================================
# MAIN PAGE - Gui entry point to the Scheduler Program
#
# - inherits from class MainPageTk
#
# EVENT HANDLERS - to set handlers, use 'set_main_page_event_handler'
#   file_open
#   file_new
#   file_open_previous
#   file_exit
#   semester changed
# ============================================================================
"""
import os.path
from PIL import Image, ImageTk

from typing import Callable, Optional, Literal, get_args

from ..Utilities.Preferences import Preferences

from .main_pages_tk import MainPageBaseTk
import tkinter as tk

from ..gui_generics.read_only_text_tk import ReadOnlyTextTk

BUTTON_WIDTH = 50
MAX_LEN_OF_DISPLAYED_FILENAME = 60

# ============================================================================
# event handlers
# ============================================================================

EVENT_HANDLER_NAMES = Literal[
    "file_open",
    "file_new",
    "file_open_previous",
    "file_exit",
    "semester_change"
]
MAIN_PAGE_EVENT_HANDLERS: dict[EVENT_HANDLER_NAMES, Callable[[], None]] = {}
for event_name in get_args(EVENT_HANDLER_NAMES):
    MAIN_PAGE_EVENT_HANDLERS[event_name] = lambda: print(f"'selected. {event_name}")


def set_main_page_event_handler(name: EVENT_HANDLER_NAMES, handler: Callable[[], None]):
    MAIN_PAGE_EVENT_HANDLERS[name] = handler


# ============================================================================
# class: SchedulerTk
# ============================================================================
class SchedulerTk(MainPageBaseTk):
    """
    GUI_Pages Code for the main Scheduling application window. Inherits from MainPageBaseTk.
    """

    # ========================================================================
    # constructor
    # ========================================================================
    def __init__(self, title: str, preferences: Preferences, bin_dir: str):
        """
        create object - starts with welcome page displayed
        :param title: Sir, Ma'am, Her Royal Highness
        :param preferences: what d'ya want, what d'ya really really want?
        :param bin_dir: the directory that the logo for this app is located
        """
        self.preferences: Preferences = preferences
        self.previous_file_button: Optional[tk.Button] = None
        self._schedule_filename = ""

        super().__init__(title, preferences)
        MainPageBaseTk.bin_dir = bin_dir
        self._current_semester: tk.StringVar = tk.StringVar()  # bound to semester_frame radio buttons
        self._previous_file: tk.StringVar = tk.StringVar(value="None")  # bound to previous_file_button

        # create icon for program
        if title != "Testing":
            ico = Image.open(f"{bin_dir}/schedule_ico.png")
            photo = ImageTk.PhotoImage(ico)
            self.mw.wm_iconphoto(True, photo)

    @property
    def current_semester(self):
        return self._current_semester.get()

    @current_semester.setter
    def current_semester(self, value):
        self._current_semester.set(value)

    @property
    def previous_file(self):
        return self._previous_file.get()

    @previous_file.setter
    def previous_file(self, value):
        if value is not None and value != "":
            basename = os.path.basename(str(value))
            if len(basename) > MAX_LEN_OF_DISPLAYED_FILENAME:
                basename = "..." + basename[len(basename) - MAX_LEN_OF_DISPLAYED_FILENAME:]
            self._previous_file.set(basename)
        else:
            self._previous_file.set("None")

    @property
    def schedule_filename(self):
        return self._schedule_filename

    @schedule_filename.setter
    def schedule_filename(self, value: str):
        self._schedule_filename = value
        if value is not None and value != "":
            value = os.path.abspath(value)
            if len(value) > MAX_LEN_OF_DISPLAYED_FILENAME:
                value = "... " + value[len(value) - MAX_LEN_OF_DISPLAYED_FILENAME:]
        if self.preferences.semester() == "winter":
            self.status_bar_winter_file_info = value
        else:
            self.status_bar_fall_file_info = value

    # ========================================================================
    # override exit event
    # ========================================================================
    def _exit_schedule(self, *_):
        self.exit_schedule()

    def exit_schedule(self):
        MAIN_PAGE_EVENT_HANDLERS["file_exit"]()
        super()._exit_schedule()

    # ========================================================================
    # create Welcome page
    # ========================================================================
    def create_welcome_page(self, semester):
        """Creates the very first page that is shown to the user."""
        option_frame = super().create_welcome_page_base(os.path.join(self.bin_dir, 'schedule_logo.png'))

        # --------------------------------------------------------------
        # which semester?
        # --------------------------------------------------------------
        self._current_semester.set(str(semester))
        semester_frame = tk.Frame(option_frame, background=self.colours.DataBackground)
        semester_frame.pack(side="top", fill="y", expand=1)
        radio_fall = tk.Radiobutton(semester_frame, text='Fall',
                                 background=self.colours.DataBackground, variable=self._current_semester,
                                 font=self.fonts.big,
                                 value='fall')
        radio_winter = tk.Radiobutton(semester_frame, text='Winter',
                                   background=self.colours.DataBackground, variable=self._current_semester,
                                   font=self.fonts.big,
                                   value='winter')

        radio_fall.grid(row=0, column=0, sticky="nsew", padx=25, pady=15)
        radio_winter.grid(row=0, column=1, sticky="nsew", padx=25, pady=15)

        # place a watch on changing bound variables
        self._current_semester.trace('w', MAIN_PAGE_EVENT_HANDLERS["semester_change"])

        def _previous_file_change_event(*_):
            try:
                if self._previous_file != "None":
                    self.previous_file_button.configure(state='normal')
                else:
                    self.previous_file_button.configure(state='disabled')
            except tk.TclError:
                pass
        self._previous_file.trace('w', _previous_file_change_event)

        # --------------------------------------------------------------
        # open previous schedule file buttons
        # -------------------------------------------------------------
        self.previous_file_button = tk.Button(
            option_frame,
            justify="right",
            font=self.fonts.big,
            borderwidth=2,
            background=self.colours.ButtonBackground,
            foreground=self.colours.ButtonForeground,
            command=MAIN_PAGE_EVENT_HANDLERS["file_open_previous"],
            width=BUTTON_WIDTH,
            height=3,
            textvariable=self._previous_file
        )
        self.previous_file_button.pack(side="top", fill="y", expand=0, padx=5, pady=5)

        # --------------------------------------------------------------
        # create new schedule file option
        # --------------------------------------------------------------
        tk.Button(
            option_frame,
            text="Create NEW Schedule File",
            font=self.fonts.big,
            borderwidth=2,
            background=self.colours.ButtonBackground,
            foreground=self.colours.ButtonForeground,
            command=MAIN_PAGE_EVENT_HANDLERS["file_new"],
            width=BUTTON_WIDTH,
            height=3
        ).pack(side="top", fill="y", expand=0, padx=5, pady=5)

        # --------------------------------------------------------------
        # open schedule file option
        # --------------------------------------------------------------
        tk.Button(
            option_frame,
            text="Browse for Schedule File",
            font=self.fonts.big,
            borderwidth=2,
            background=self.colours.ButtonBackground,
            foreground=self.colours.ButtonForeground,
            command=MAIN_PAGE_EVENT_HANDLERS["file_open"],
            width=BUTTON_WIDTH,
            height=3
        ).pack(side="top", fill="y", expand=0, padx=5, pady=5)

        # a growable and shrinkable frame which makes resizing look better
        tk.Frame(
            option_frame, background=self.colours.DataBackground
        ).pack(expand=1, fill="both")

        # --------------------------------------------------------------
        # update the current file and/or button
        # --------------------------------------------------------------
        MAIN_PAGE_EVENT_HANDLERS["semester_change"]()

    # ========================================================================
    # show a text box
    # ========================================================================
    def show_text(self, title, text:list[str]):
        tl = tk.Toplevel(self.mw)
        tl.protocol('WM_DELETE_WINDOW', tl.destroy)
        tl.title(title)
        ro = ReadOnlyTextTk(tl, text, height=20, width=50, scrollbars='e')

