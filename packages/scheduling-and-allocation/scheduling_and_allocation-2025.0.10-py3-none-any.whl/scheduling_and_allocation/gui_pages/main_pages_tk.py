"""
# ============================================================================
# MAIN PAGE - Gui entry point to the application(s)
#
# - Forms base class for Scheduler and Allocation applications
#
# EVENT HANDLERS - None
# ============================================================================

"""
from __future__ import annotations

import platform
from functools import partial

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as tk_fd
from typing import Optional, TYPE_CHECKING, Callable

from tkinter.messagebox import showerror, showinfo, askyesno

from ..modified_tk import set_default_fonts_and_colours, TkColours, TkFonts
from ..gui_dialogs.change_font_tk import ChangeFont
from ..gui_pages.note_book_frame_tk import NoteBookFrameTk, TabInfoProtocol
from ..gui_generics.menu_and_toolbars import MenuItem, ToolbarItem, generate_menu, make_toolbar
from ..Utilities.Preferences import Preferences
from ..modified_tk.InitGuiFontsAndColours import set_system_colours

if TYPE_CHECKING:
    pass

Operating_system = platform.system().lower()

MAIN_FRAME_HEIGHT = 600
MAIN_FRAME_WIDTH = 800
WELCOME_WIDTH = 800
WELCOME_HEIGHT = 600


class MainPageBaseTk:
    """Generic main page for Scheduler and Allocation Manager apps"""
    bin_dir = None

    # ===================================================================================
    # constructor
    # ===================================================================================
    def __init__(self, title, preferences: Preferences):
        """
        main page
        :param title:
        :param preferences: a preference object (color scheme, last opened file, etc)
        """

        # public properties
        self.dark_mode = preferences.dark_mode()
        self.theme = preferences.theme()
        self.colours: Optional[TkColours] = None
        self.fonts: Optional[TkFonts] = None
        self.dict_of_frames: dict[str, tk.Frame] = dict()
        self.logo: Optional[tk.PhotoImage] = None
        self.mw: Optional[tk.Tk] = None
        self.notebook_tab_changed_handler: Callable[[str,tk.Frame], None] = lambda a,b: None

        # autosave handler
        self.toggle_auto_save: Callable[ [bool], None] = lambda flag: print("Auto set has been set to", flag)

        # private properties
        self._preferences = preferences
        self._notebook_frame: Optional[NoteBookFrameTk] = None
        self._wait = None
        self.notebook_tabs_info: list[TabInfoProtocol] | None = None
        self._front_page_frame: Optional[tk.Frame] = None
        self._toolbar = None
        self._default_notebook_page: int = 0
        self._top_level_notebook: Optional[ttk.Notebook] = None
        self._main_page_frame: Optional[tk.Frame] = None

        # Create the Tk main window
        self.mw = self._create_toplevel(title)

        # colors and fonts
        font_size = None
        if self._preferences is not None:
            font_size = self._preferences.font_size()
        self.colours, self.fonts = set_default_fonts_and_colours(self.mw,
                                                                 font_size=font_size,
                                                                invert=self.dark_mode)
        set_system_colours(self.mw, self.colours, self.theme)

        # set the filename so that it can be bound later
        self._status_bar_fall_file_info: tk.StringVar = tk.StringVar(value="None")

        # set the filename so that it can be bound later
        self._status_bar_winter_file_info: tk.StringVar = tk.StringVar(value="None")

        # set the dirty text so it can be bound later
        self._status_bar_dirty: tk.StringVar = tk.StringVar(value="")

    # ===================================================================================
    # properties
    # ===================================================================================
    @property
    def status_bar_fall_file_info(self):
        return self._status_bar_fall_file_info.get()

    @status_bar_fall_file_info.setter
    def status_bar_fall_file_info(self, value: str):
        self._status_bar_fall_file_info.set(value)

    @property
    def status_bar_winter_file_info(self):
        return self._status_bar_winter_file_info.get()

    @status_bar_winter_file_info.setter
    def status_bar_winter_file_info(self, value: str):
        self._status_bar_winter_file_info.set(value)

    @property
    def dirty_text(self):
        return self._status_bar_dirty.get()

    @dirty_text.setter
    def dirty_text(self, value):
        self._status_bar_dirty.set(value)

    # ===================================================================================
    # menu and toolbars
    # ===================================================================================
    def create_menu_and_toolbars(self, buttons: list[str], toolbar_info: dict[str:ToolbarItem],
                                 menu_details: list[MenuItem]):
        """
        Using the info, create menu and toolbar for this app
        :param buttons: a list of buttons for the toolbar
        :param toolbar_info: information about buttons/callbacks for the toolbar
        :param menu_details: all the details required for the menu
        """

        menu_bar = tk.Menu(self.mw)

        # create application specific menu
        generate_menu(self.mw, menu_details, menu_bar)
        self.mw.configure(menu=menu_bar)

        # create the auto-save part of menu
        auto_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Auto Save", menu=auto_menu)

        tk_auto_save = tk.BooleanVar(value=bool(self._preferences.auto_save()))
        auto_menu.add_radiobutton(label="Auto Save ON", value=True, variable=tk_auto_save,
                                  command=partial(self.toggle_auto_save, True))
        auto_menu.add_radiobutton(label="Auto Save OFF", value=False, variable=tk_auto_save,
                                  command=partial(self.toggle_auto_save, False))

        # create preferences menu
        preference_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="Preferences", menu=preference_menu)
        preference_menu.add_command(label="Font Size",
                                    command=lambda: ChangeFont(self.mw, self._preferences))

        theme_menu = tk.Menu(preference_menu, tearoff=False)
        s = ttk.Style(self.mw)
        dark = 'dark' if self._preferences.dark_mode() else 'light'
        preference_menu.add_cascade(label=f"Themes ({s.theme_use()} {dark})", menu=theme_menu)
        themes = list(set(self._preferences.available_themes()).intersection(set(s.theme_names())))
        themes.sort()
        for theme in themes:
            for dark in ("light","dark"):
                theme_menu.add_command(label=f"{theme} {dark}",
                                        command=partial(self.change_theme, theme, dark))

        # create _toolbar
        self._toolbar = make_toolbar(self.mw, buttons, toolbar_info)
        self._toolbar.pack(side='top', expand=0, fill='x')

    # ===================================================================================
    # Change Theme
    # ===================================================================================
    def change_theme(self, theme, dark):
        """change the theme of the Tk"""
        self._preferences.theme(theme)
        self._preferences.dark_mode(True if dark == "dark" else False)
        self.show_message("Changing themes", msg="Changing themes will not take affect until "
                                                 "you close and re-open application")
        self._preferences.save()

    # ===================================================================================
    # status bar
    # ===================================================================================
    def create_status_bar(self):
        """Create a status bar for current filename and dirty flag"""

        mw = self.mw

        # draw frame and labels for current filename and dirty flag
        status_frame = tk.Frame(mw, borderwidth=0, relief='flat')
        status_frame.pack(side='bottom', expand=0, fill='x')

        tk.Label(status_frame, textvariable=self._status_bar_fall_file_info, borderwidth=1, relief='ridge',
              anchor='w',
              ).pack(side='left', expand=1, fill='x')

        tk.Label(status_frame, textvariable=self._status_bar_winter_file_info, borderwidth=1, relief='ridge',
              anchor='w',
              ).pack(side='left', expand=1, fill='x')

        tk.Label(status_frame, textvariable=self._status_bar_dirty, borderwidth=1, relief='ridge', width=15,
              foreground=self.colours.DirtyColour).pack(side='right', fill='x')

    # ===================================================================================
    # welcome page
    # ===================================================================================
    def create_welcome_page_base(self, logo: str) -> tk.Frame:
        """
        Creates the very first page that is shown to the user
        :param logo: image to use as part of the front page header
        :return: the frame for the super class to use to add whatever they want
        """
        mw = self.mw
        self._front_page_frame = tk.Frame(mw, borderwidth=10, relief='flat', background=self.colours.DataBackground)
        self._front_page_frame.pack(side='top', expand=1, fill='both')

        # create an image object of the _logo
        # ... for some weird reason, if logo is not part of 'self', then it doesn't work
        # Weird, right?
        self.logo = tk.PhotoImage(file=logo)

        # frame and label
        tk.Label(self._front_page_frame, image=self.logo, borderwidth=0, relief='flat') \
            .pack(side='left', expand=0)

        # --------------------------------------------------------------
        # frame for holding buttons for starting the scheduling/allocation tasks
        # --------------------------------------------------------------
        option_frame = tk.Frame(
            self._front_page_frame,
            background=self.colours.DataBackground,
            borderwidth=10,
            relief='flat')
        option_frame.pack(side='left', expand=1, fill='both')

        tk.Frame(option_frame, background=self.colours.DataBackground).pack(expand=1, fill='both')
        center_frame = tk.Frame(option_frame, background=self.colours.DataBackground)
        center_frame.pack(expand=0, fill='both')
        tk.Frame(option_frame, background=self.colours.DataBackground).pack(expand=1, fill='both')

        return center_frame

    # ===================================================================================
    # standard page with notebook
    # ===================================================================================
    def create_standard_page(self, notebook_pages_info: Optional[list[TabInfoProtocol]] = None, reset=False):
        """
        Create the 'welcome' page after the main page has fulfilled its purpose
        :param notebook_pages_info: which tabs, and callbacks, etc are in the notebook being created
        :param reset: should the notebook be re-drawn
        """

        # if the page is already created, do not recreate it
        if self._notebook_frame is not None and not reset:
            if self._notebook_frame.main_notebook_frame:
                self._notebook_frame.main_notebook_frame.select(self._default_notebook_page)
                self._notebook_frame.main_notebook_frame.event_generate("<<NotebookTabChanged>>")
                return

        # create the page
        mw = self.mw
        self._front_page_frame.destroy()

        # frame
        if self._main_page_frame is not None:
            self._main_page_frame.destroy()
        self._main_page_frame = tk.Frame(mw, borderwidth=1, relief='ridge')
        self._main_page_frame.pack(side='top', expand=1, fill='both')
        self._notebook_frame = NoteBookFrameTk(self.mw, self._main_page_frame, notebook_pages_info,
                                               self.weird_mac_crap_tab_change_handler)

    def _exit_schedule(self, *_):
        self.mw.destroy()

    def weird_mac_crap_tab_change_handler(self, name, frame):
        self.recursive_expose(frame)
        self.notebook_tab_changed_handler(name, frame)

    def recursive_expose(self, widget):
        for w in widget.winfo_children():
            self.recursive_expose(w)
            widget.update()

    def select_tab(self, name):
        for notebook in self._notebook_frame.notebooks:
            tab_names = {notebook.tab(i, option="text"):i for i in notebook.tabs()}
            if name in tab_names.keys():
                notebook.select(tab_names[name])
                self._notebook_frame.tab_changed(notebook,tab_names[name] )

    # ========================================================================
    # choose file
    # ========================================================================
    def select_file_to_save(self, title:str="Save File As") -> str:
        return self._select_file(partial(tk_fd.asksaveasfilename,
                                         defaultextension="csv",
                                         title=title))

    def select_file_to_open(self, title = "Open Schedule") -> str:
        return self._select_file(partial(tk_fd.askopenfilename,
                                         title=title))

    def _select_file(self, select_gui) -> str:
        current_dir = self._preferences.current_dir() or self._preferences.home_directory()
        kwargs = {"filetypes": (
            ('schedule files', '*.csv'),
            ('All files', '*.*')
        )}

        if current_dir is not None:
            kwargs["initialdir"] = current_dir

        filename = select_gui(**kwargs)
        return filename

    # ========================================================================
    # message boxes
    # ========================================================================
    def show_error(self, title: str, msg: str, detail: str = ""):
        showerror(title=title, message=msg, detail=detail, icon='error')

    def show_message(self, title: str, msg: str, detail: str = ""):
        showinfo(title=title, message=msg, detail=detail, icon='info')

    def ask_yes_no(self, title: str, msg: str, detail: str = ""):
        return askyesno(title=title, message=msg, detail=detail, icon='info')

    def show_custom_message(self, title="", msg=""):
        dialog = tk.Tk()
        dialog.title(title)

        label = tk.Label(dialog, text=msg, justify='left')
        label.pack(pady=20,padx=20)

        ok_button = tk.Button(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(padx=20,pady=20, expand=1)

        dialog.transient(self.mw)  # Make it a child of the main window
        dialog.grab_set()      # Make it modal
        self.mw.wait_window(dialog) # Wait for the dialog to close

    # ===================================================================================
    # create top level
    # ===================================================================================
    def _create_toplevel(self, title):
        """Create the top level window, specify fonts and colors"""
        # create main window and frames
        """Create the top level window, specify fonts and colors"""
        # create main window and frames
        mw = tk.Tk()
        mw.title(title)
        mw.geometry(f"{WELCOME_WIDTH}x{WELCOME_HEIGHT}")
        #mw.geometry("100x100")

        # when clicking the 'x' in the corner of the window, call _exit_schedule
        mw.protocol("WM_DELETE_WINDOW", self._exit_schedule)

        # have main window pop-up and have focus
        # https://stackoverflow.com/questions/8691655/how-to-put-a-tkinter-window-on-top-of-the-others/8691795
        mw.lift()
        mw.call('wm', 'attributes', '.', '-topmost', True)
        mw.after_idle(mw.call, 'wm', 'attributes', '.', '-topmost', False)
        mw.focus_force()

        return mw

    # ===================================================================================
    # start event loop
    # ===================================================================================
    def start_event_loop(self):
        """time_start the Tk event main event loop"""
        self.mw.mainloop()

    # ===================================================================================
    # waiting routines
    # ===================================================================================
    def wait_for_it(self, title, msg):
        self.stop_waiting()

        self._wait = self.mw.winfo_toplevel()
        self._wait.title = title
        tk.Label(self._wait, text=msg).pack(expand=1, fill='both')

        self._wait.geometry('300x450')
        self.mw.update()

    def stop_waiting(self):
        if self._wait:
            self._wait.destroy()
        self._wait = None
