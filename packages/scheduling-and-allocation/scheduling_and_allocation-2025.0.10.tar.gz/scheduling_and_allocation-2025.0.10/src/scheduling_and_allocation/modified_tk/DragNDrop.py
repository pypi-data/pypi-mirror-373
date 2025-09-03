from __future__ import annotations

import tkinter as tk
from functools import partial
from typing import Callable, Any, Optional
from .InitGuiFontsAndColours import TkColours



class DragNDropManager:
    _currently_dragging: bool = False  # are we currently dragging something?
    _info_data: dict[Any, Any] = dict()  # dictionary so calling program can exchange data between event handlers
    _drag_indicator: Optional[tk.Toplevel] = None  # a top level window that moves around with the mouse
    _default_cursor: str = ""  # the cursor of associated with the source widget before dragging begins
    _label: tk.Label = None  # the content of the drag_indicator
    _current_target: Optional[tk.Widget] = None  # the current, valid, cb_drop-site widget
    _drag_indicator_text: str = ""  # the text in the label in the drag_indicator

    def __init__(self, colours = TkColours()):
        self.colours = colours

    # ========================================================================
    # add a widget to the 'draggable' list
    # ========================================================================
    def add_draggable(self, source: tk.Widget,
                      on_start: Callable[[tk.Event, dict], str] = lambda e, info_data: str(e.widget),
                      on_drag: Callable[[tk.Event, dict, tk.Widget], bool] = lambda e, info_data, target: bool,
                      on_drop: Callable[[tk.Event, dict, tk.Widget], None] = lambda e, info_data, target: None):
        """
        Add the specified widget to the list of widgets that can be dragged and dropped.

        Details
        -------

        * When the widget is selected, the `on_start` function will be called, where any information required during
          the drag-n-drop phase can be stored in the `info_data` dictionary.  This method should return a string
          which will be used to label the little square that physical indicates where things are being dropped

        * When the widget is being moved about, the `on_drag` method will be called, with the current event,
          the data saved in `info_data`, and a widget that is under the mouse.  Must return true or false to indicate
          if it is a valid drop-site

        * When the widget is dropped, if the mouse is hovering over another widget (target) that has been
          set as a drop-site, the `on_drop` method will be called, again passing in any information stored in
          `info_data`

        * The widget that is being dragged about is available through the `tk.Event` object, (event.widget)

        Parameters
        ----------

        :param source: the widget which will be selected for dropping
        :param on_start:
        :param on_drag:
        :param on_drop:
        :return: Nothing
        """
        source.bind("<ButtonPress-1>", partial(self._on_start, on_start, on_drag, on_drop))

    # ========================================================================
    # Prepare for dragging the widget
    # ========================================================================
    def _on_start(self,
                  cb_start: Callable[[tk.Event, dict], str],
                  cb_drag: Callable[[tk.Event, dict, tk.Event], None],
                  cb_drop: Callable[[tk.Event, dict], None],
                  event: tk.Event):
        """Start the drag'n'drop process"""

        # prevent multiple dragging and dropping
        if self._currently_dragging:
            return

        # call user's 'time_start' method defined for this source widget
        self._info_data.clear()
        self._drag_indicator_text = cb_start(event, self._info_data)
        if not self._drag_indicator_text:
            self._drag_indicator_text = str(event.widget)

        # setup for dragging and dropping object
        self._current_target = None
        self._default_cursor = event.widget.cget("cursor")
        source = event.widget
        source.bind("<B1-Motion>", partial(self._on_drag, cb_drag))
        source.bind("<ButtonRelease-1>", partial(self._on_drop, cb_drop))

    # ========================================================================
    # Drag the widget
    # ========================================================================
    def _on_drag(self, cb_drag: Callable[[tk.Event, dict, tk.Widget], None], event: tk.Event):

        # create a popup window for dragging
        if not self._drag_indicator:
            tl = tk.Toplevel(background = self.colours.DataBackground)
            self._label = tk.Label(tl, text=self._drag_indicator_text, foreground=self.colours.DataForeground)
            self._label.pack(expand=1, fill="both")
            tl.update_idletasks()
            tl.overrideredirect(True)
            tl.transient()
            self._drag_indicator = tl
            event.widget.configure(cursor="hand2")

        self._label.configure(bg=self.colours.DragNDropBackground)
        self._label.configure(fg=self.colours.DragNDropForeground)
        tl = self._drag_indicator

        # move the indicator by specifying the geometry
        tl.geometry(f"100x20+{event.x_root + 5}+{event.y_root - 5}")

        # find the target under the cursor
        target = event.widget.winfo_containing(event.x_root, event.y_root)

        # call user's 'drag' method, which returns 'true' if mouse over valid drop-site
        if cb_drag(event, self._info_data, target):
            self._label.configure(bg=self.colours.DragNDropAllowedBackground)

    # ========================================================================
    # Drop the widget
    # ========================================================================
    def _on_drop(self, cb_drop: Callable[[tk.Event, dict, tk.Widget], None], event: tk.Event):

        # find the target under the cursor
        target = event.widget.winfo_containing(event.x_root, event.y_root)

        # call user's 'drop' method
        cb_drop(event, self._info_data, target)

        # clean up after dropping
        if self._drag_indicator:
            self._drag_indicator.destroy()
        self._drag_indicator = None
        self._currently_dragging = False
        event.widget.configure(cursor=self._default_cursor)
        event.widget.unbind("<B1-Motion>")
        event.widget.unbind("<ButtonRelease-1>")
