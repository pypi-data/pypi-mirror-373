
import os.path
from functools import partial
from PIL import Image, ImageTk

from typing import Callable, Optional, Literal, get_args

from ..Utilities.Preferences import Preferences

from .main_pages_tk import MainPageBaseTk
import tkinter as tk
from ..model.enums import SemesterType

BUTTON_WIDTH = 50
MAX_LEN_OF_DISPLAYED_FILENAME = 60

# ============================================================================
# event handlers
# ============================================================================

EVENT_HANDLER_NAMES = Literal[
    "go",
    "exit",
]

MAIN_PAGE_EVENT_HANDLERS: dict[EVENT_HANDLER_NAMES, Callable[[], None]] = {}

for event_name in get_args(EVENT_HANDLER_NAMES):
    MAIN_PAGE_EVENT_HANDLERS[event_name] = lambda : print(f"'selected. {event_name}")


def set_main_page_event_handler(name: EVENT_HANDLER_NAMES, handler: Callable[[], None]):
    MAIN_PAGE_EVENT_HANDLERS[name] = handler

# ============================================================================
# class: AllocationManagerTk
# ============================================================================
class AllocationManagerTk(MainPageBaseTk):

    # ----------------------------------------------------------------------------------------------------------------
    # constructor
    # ----------------------------------------------------------------------------------------------------------------
    def __init__(self, title: str, preferences: Preferences = None, bin_dir: str = "."):
        """
        create object - starts with welcome page displayed
        :param title: Sir, Ma'am, Her Royal Highness
        :param preferences: what d'ya want, d'ya really really want?
        :param bin_dir: the directory that the logo for this app is located
        """
        self.preferences: Preferences = preferences
        self.chosen_file_labels: dict[SemesterType, Optional[tk.Label]] = {s: None for s in SemesterType}

        super().__init__(title, preferences)
        MainPageBaseTk.bin_dir = bin_dir

        # select previous files by default
        self.selected_files: dict[SemesterType, tk.StringVar] = {}
        for semester in SemesterType:
            if preferences is not None:
                self.preferences.semester(semester.name)
                self.selected_files[semester] =  tk.StringVar(value=str(self.preferences.previous_file()))
            else:
                self.selected_files[semester] =  tk.StringVar(value=None)

        # create icon for program
        ico = Image.open(f"{bin_dir}/allocation_ico.png")
        photo = ImageTk.PhotoImage(ico)
        self.mw.wm_iconphoto(True, photo)

    # ----------------------------------------------------------------------------------------------------------------
    # setting the schedule filename
    # ----------------------------------------------------------------------------------------------------------------
    def schedule_filename(self, semester:SemesterType = SemesterType.any, value:str =""):
        """
        the schedule file is saved as a Tk StringVar, and is trimmed down to a smaller size if necessary
        :param semester:
        :param value:
        :return: the current value of the Tk StringVar
        """

        # trim file name if necessary
        if value is not None and value != "":
            value = os.path.abspath(value)
            if len(value) > MAX_LEN_OF_DISPLAYED_FILENAME:
                value = "... " + value[len(value) - MAX_LEN_OF_DISPLAYED_FILENAME:]
            self.selected_files[semester].set(value)
        else:
            self.selected_files[semester].set(value="Create New")

        # save the filename
        if semester == SemesterType.winter:
            self.status_bar_winter_file_info = value
        else:
            self.status_bar_fall_file_info = value

        # return the value
        return self.selected_files[semester].get()

    # ----------------------------------------------------------------------------------------------------------------
    # override exit event
    # ----------------------------------------------------------------------------------------------------------------
    def _exit_schedule(self, *_):
        self.exit_schedule()

    def exit_schedule(self):
        MAIN_PAGE_EVENT_HANDLERS["exit"]()
        super()._exit_schedule()

    # ----------------------------------------------------------------------------------------------------------------
    # create welcome page
    # ----------------------------------------------------------------------------------------------------------------
    def create_welcome_page(self, valid_semesters:list[SemesterType]):
        """
        Creates the very first page that is shown to the user
        :param valid_semesters:
        """
        option_frame = super().create_welcome_page_base(
            os.path.join(self.bin_dir, 'allocation_logo.png'))

        # divide frame into semesters
        option_frames: dict[SemesterType, tk.LabelFrame] = {}
        for row,semester in enumerate(valid_semesters):
            option_frames[semester] = tk.LabelFrame(option_frame,text=semester.name,font=self.fonts.big)
            option_frames[semester].pack(expand=1, fill='y', side='top')

        for semester in valid_semesters:

            # open previous schedule file buttons
            self.chosen_file_labels[semester]= tk.Label(
                option_frames[semester],
                anchor="e",
                font=self.fonts.big,
                borderwidth=2,
                background=self.colours.ButtonBackground,
                foreground=self.colours.ButtonForeground,
                width=BUTTON_WIDTH,
                height=2,
                textvariable=self.selected_files[semester],
                state='disabled'
            )
            self.chosen_file_labels[semester].pack(side="top", fill="x", expand=1, padx=5, pady=5)

            # open schedule file option
            tk.Button(
                option_frames[semester],
                text=f"Browse",
                font=self.fonts.normal,
                borderwidth=2,
                background=self.colours.ButtonBackground,
                foreground=self.colours.ButtonForeground,
                command=partial(self.select_file,semester),
                width=8,
                height=2
            ).pack(side="top", fill="x", expand=1, padx=5, pady=5)

            # open schedule file option
            tk.Button(
                option_frames[semester],
                text=f"New",
                font=self.fonts.normal,
                borderwidth=2,
                background=self.colours.ButtonBackground,
                foreground=self.colours.ButtonForeground,
                command=partial(self.new_file,semester),
                width=8,
                height=2
            ).pack(side="top", fill="x", expand=1, padx=5, pady=5)

        # go
        tk.Button(option_frame, text="Go", font=self.fonts.big, padx=20,pady=5,
                  command=self.go).pack(expand=1, fill='x', side='top', pady=20)

    def select_file(self, semester):
        file = self.select_file_to_open(f"Open Schedule for {semester}")
        self.selected_files[semester].set(value=file)

    def new_file(self, semester):
        self.selected_files[semester].set(value=str(None))

    def go(self):
        MAIN_PAGE_EVENT_HANDLERS["go"]()