"""
# ============================================================================
# Create a Notebook
#
# EVENT HANDLERS
#
#   tab_changed_handler(tab_name, frame)
#
# ============================================================================

"""
from dataclasses import dataclass, field
from functools import partial
import tkinter.ttk as ttk
import tkinter as tk
from typing import Optional, Callable, Protocol, Any


@dataclass
class TabInfoProtocol(Protocol):
    name: str
    label: str
    subpages: list = field(default_factory=list)
    frame_args: dict[str, Any] = field(default_factory=dict)
    creation_handler: Callable = lambda *_: None
    is_default_page: bool = False


def _expose_widgets(widget):
    """weird shit happens on MAC in that widgets are not shown in tab... this forces them to be shown"""
    widget.event_generate("<Expose>")

    for child in widget.winfo_children():
        _expose_widgets(child)


class NoteBookFrameTk:
    """creates notebook, recursively, until all notebook tabs are created"""

    # ===================================================================================
    # constructor
    # ===================================================================================
    def __init__(self, mw: tk.Toplevel, main_page_frame: tk.Frame,
                 tabs_info: Optional[list[TabInfoProtocol]] = None,
                 tab_changed_handler: Callable[[str, tk.Frame], None] = lambda *_: None):
        """
        create the notebook(s)
        :param mw: toplevel window
        :param main_page_frame: where the current notebook frame should be placed
        :param tabs_info: what tabs do you need
        :param tab_changed_handler: who you gonna call?... ghost busters!
        """

        self._default_notebook_page = None
        self.tabs_info = tabs_info
        self.mw = mw
        self.frame = main_page_frame
        self.tab_frames: dict[tuple[ttk.Notebook, int], tuple[str, tk.Frame]] = {}
        self.tab_changed_handler = tab_changed_handler
        self.main_notebook_frame = None
        self.notebooks: list[ttk.Notebook] = []

        self.recursive_notebook_creation(self.frame, tabs_info)
        self.notebooks[0].select(self._default_notebook_page)
        self.mw.after(20, lambda: self.tab_changed(self.notebooks[0]))
        self.mw.after(10, lambda *_: self.mw.geometry(
            f"{max(975, self.mw.winfo_width())}x{max(700, self.mw.winfo_height())}"))


    # ===================================================================================
    # create notebook pages
    # ===================================================================================
    def recursive_notebook_creation(self, notebook_frame: tk.Frame, tabs_info: list[TabInfoProtocol]):
        """
        recursive calling of notebook creation
        :param notebook_frame:
        :param tabs_info:
        """

        if tabs_info is None:
            return

        # Create notebook if required
        if self.notebooks is None:
            self.notebooks: list[ttk.Notebook] = []
        notebook = ttk.Notebook(notebook_frame)
        self.notebooks.append(notebook)
        notebook.pack(expand=1, fill='both')

        if self.main_notebook_frame is None:
            self.main_notebook_frame = notebook

        for info in tabs_info:

            # create a frame and add to the notebook
            frame = tk.Frame(self.mw, **info.frame_args)
            notebook.add(frame, text=info.label)
            notebook_index = notebook.index(frame)

            # save the frame and name for this tab index
            self.tab_frames[(notebook, notebook_index)] = (info.name, frame)

            # set the page that should be shown by default
            if info.is_default_page:
                self._default_notebook_page = notebook_index

            # if this notebook page has sub-pages, then set them up as well
            if info.subpages:
                self.recursive_notebook_creation(frame, info.subpages)

            # call the 'create handler' for this page
            if info.creation_handler:
                info.creation_handler(info.name, frame)

        # add the binding for changing of events, and include a list of events for each tab change
        notebook.bind("<<NotebookTabChanged>>", partial(self.tab_changed, notebook))

    # ===================================================================================
    # tab has changed
    # ===================================================================================
    def tab_changed(self, notebook: ttk.Notebook, *_):
        """
        calls the tab changed callback when the tab has changed
        :param notebook:
        :param _: tk events?
        """
        try:
            index = notebook.index(notebook.select())
            tab_name, frame = self.tab_frames.get((notebook, index), None)
            self.tab_changed_handler(tab_name, frame)

            # have to delay to get this to work properly,
            # maybe using 'after_idle' works, but haven't tired it
            notebook.after(10, lambda *_:_expose_widgets(frame))
            notebook.after(20,lambda *_: notebook.event_generate("<Leave>"))

        except tk.TclError:
            """just in case tk has a problem with this as the notebook is being created"""
            pass

