"""Create a scrollable frame, although it doesn't attach any scrollbars"""

from __future__ import annotations
import tkinter as tk

import sys
import traceback
from tkinter import ttk
from typing import Literal, Optional


def eprint(*args, **kwargs):
    print("\n", file=sys.stderr, **kwargs)
    print(*args, file=sys.stderr, **kwargs)
    print(traceback.format_stack()[0], file=sys.stderr, **kwargs)
    exit()


###############
# https://docstore.mik.ua/orelly/perl3/tk/ch06_03.htm
# Section 6.3.8
# http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/events.html
# https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html
###############

class Pane(tk.Frame):
    """
        ┌──────────────────────────────────────────────────────┐
        │ ┌──────────────────────────────────────────────────┐ │
        │ │ ┌──────────────────────────────────────────────┐ │ │
        │ │ │                                              │ │ │
        │ │ │                                              │ │ │
        │ │ │                                              │< ------- inner frame
        │ │ │             Inner frame                      │ │ │
        │ │ │          this is where you add stuff         │ │<------ scrollable canvas
        │ │ │                                              │ │ │
        │ │ └──────────────────────────────────────────────┘ │ │<---- self (Pane)
        │ └──────────────────────────────────────────────────┘ │
        └──────────────────────────────────────────────────────┘

    """

    # ==============================================================================================
    # properties
    # ==============================================================================================
    @property
    def frame(self)->tk.Widget:
        return self._widget

    @property
    def canvas(self):
        return self._scrollable_object

    # ==============================================================================================
    # constructor
    # ==============================================================================================
    def __init__(self, parent, **kwargs):
        background_colour = None
        if "bg" in kwargs:
            background_colour = kwargs['bg']
        if "background" in kwargs:
            background_colour = kwargs['background']

        tk.Frame.__init__(self, parent)

        self.horizontal_scrollbar: Optional[ttk.Scrollbar] = None
        self.vertical_scrollbar: Optional[ttk.Scrollbar] = None

        canvas = tk.Canvas(self, bg="red")
        canvas.pack(side="left", fill="both", expand=tk.TRUE)
        self._scrollable_object = canvas
        super().configure(background=background_colour)
        super().configure(highlightbackground=background_colour)
        canvas.configure(background=background_colour)
        canvas.configure(highlightbackground=background_colour)

        # Create a frame inside the canvas which will be scrolled with it.
        self._widget = tk.Frame(canvas, **kwargs)
        self._scrolled_id = canvas.create_window(0, 0, window=self._widget,
                                           anchor="nw")

        self._widget.bind('<Configure>', self.configure_interior)

    def configure_interior(self, *_):
        # Update canvas to match the size of the inner frame.
        width, height = (self._widget.winfo_reqwidth(), self._widget.winfo_reqheight())
        self.canvas.config(scrollregion=(0, 0, width, height), width=width, height=height)

    # ===============================================================================================================
    # pass on all 'configure' to the scrollable object
    # ===============================================================================================================
    def configure(self, **kwargs):
       self._widget.configure(**kwargs)

    def yview(self, *args):
        self.canvas.yview(*args)

    def xview(self, *args):
        self.canvas.xview(*args)

    # ===============================================================================================================
    # scrolling methods
    # ===============================================================================================================
    def see(self, widget, **_kwargs)->tuple[Optional[float], Optional[float]]:
        """Adjusts the view so that widget is visible.

        Additional parameters in options-value pairs can be passed,
        each option-value pair must be one of the following

        NOT IMPLEMENTED YET

        -anchor => anchor
        Specifies how to make the widget visible. If not given then as much of the widget as possible is made visible.

        Possible values are n, s, w, e, nw, ne, sw and se.
        This will cause an edge on the widget to be aligned with the corresponding edge on the pane.
        for example nw will cause the top left of the widget to be placed at the top left of the pane.
        s will cause the bottom of the widget to be placed at the bottom of the pane, and as much of
        the widget as possible made visible in the x direction.

        """
        delta_x = self.xview_widget(widget)
        delta_y = self.yview_widget(widget)
        return delta_x, delta_y

    def yview_moveto(self, fraction: Optional[float]):
        """
            Adjusts the view in the window so that fraction of the total width of the Scrollable object is off-screen
            to the top.

            fraction must be a fraction between 0 and 1.
        """
        if fraction is not None:
            if self.vertical_scrollbar is not None:
                self.canvas.yview_moveto(fraction)

    def xview_moveto(self, fraction: Optional[float]):
        """
            Adjusts the view in the window so that fraction of the total width of the Scrollable object is off-screen
            to the left.

            fraction must be a fraction between 0 and 1.
        """
        if fraction is not None:
            if self.horizontal_scrollbar is not None:
                self.canvas.xview_moveto(fraction)

    def xview_widget(self, widget=None) -> Optional[float]:
        """
        No parameters:
            Returns a list containing two elements, both of which are real fractions between 0 and 1.
            The first element gives the position of the left of the window, relative to the scrollable object as a whole
            (0.5 means it is halfway through the Frame, for example).
            The second element gives the position of the right of the window, relative to the scrollable object
            as a whole.

        Tk Widget defined
            Adjusts the view in the window so that widget is displayed.

         """

        # make sure idle tasks are finished (includes redrawing of changes in geometry)
        self.update_idletasks()
        pos: Optional[float] = None

        if self.horizontal_scrollbar is None:
            return pos

        if widget is not None:
            scrollable_object_width = self._widget.winfo_width()
            scrollable_object_left = self.frame.winfo_rootx()

            to_be_seen_left = widget.winfo_rootx()
            to_be_seen_width = widget.winfo_width()
            to_be_seen_right = to_be_seen_left + to_be_seen_width

            scroll_region_width = self._scrollable_object.winfo_width()
            scroll_region_left = self._scrollable_object.winfo_rootx()
            scroll_region_right = scroll_region_left + scroll_region_width

            if to_be_seen_left < scroll_region_left:
                dx = to_be_seen_left - scroll_region_left
                pos = (scroll_region_left - scrollable_object_left + dx) / scrollable_object_width
                self._scrollable_object.xview_moveto(pos)

            if to_be_seen_right > scroll_region_right:
                dx = to_be_seen_right - scroll_region_right + to_be_seen_width
                pos = (scroll_region_left - scrollable_object_left + dx) / scrollable_object_width
                self._scrollable_object.xview_moveto(pos)

        return pos

    def yview_widget(self, widget=None) -> Optional[float]:
        """
        No parameters:
            Returns a list containing two elements, both of which are real fractions between 0 and 1.
            The first element gives the position of the top of the window, relative to the scrollable object as a whole
            (0.5 means it is halfway through the Frame, for example).
            The second element gives the position of the bottom of the window, relative to the scrollable object
            as a whole.

        Tk Widget defined
            Adjusts the view in the window so that widget is displayed.

        """

        # make sure idle tasks are finished (includes redrawing of changes in geometry)
        self.update_idletasks()
        pos = None

        if self.vertical_scrollbar is None:
            return pos

        if widget is not None:
            scrollable_object_height = self._widget.winfo_height()
            scrollable_object_top = self.frame.winfo_rooty()

            to_be_seen_top = widget.winfo_rooty()
            to_be_seen_height = widget.winfo_height()
            to_be_seen_bottom = to_be_seen_top + to_be_seen_height

            scroll_region_height = self._scrollable_object.winfo_height()
            scroll_region_top = self._scrollable_object.winfo_rooty()
            scroll_region_bottom = scroll_region_top + scroll_region_height

            if to_be_seen_top < scroll_region_top:
                dy = to_be_seen_top - scroll_region_top
                pos = (scroll_region_top - scrollable_object_top + dy) / scrollable_object_height
                self._scrollable_object.yview_moveto(pos)

            if to_be_seen_bottom > scroll_region_bottom:
                dy = to_be_seen_bottom - scroll_region_bottom + to_be_seen_height
                pos = (scroll_region_top - scrollable_object_top + dy) / scrollable_object_height
                self._scrollable_object.yview_moveto(pos)

        return pos

    def xview_scroll(self, number: int, what: Literal["units", "pages"]) -> None:
        """ Shift the x-view according to NUMBER which is measured in "units" or "pages" (WHAT).

        'what' must be  Literal["units", "pages"]
        """
        if self.horizontal_scrollbar is not None:
            self._scrollable_object.xview_scroll(number, what)

    def yview_scroll(self, number: int, what: Literal["units", "pages"]) -> None:
        """ Shift the y-view according to NUMBER which is measured in "units" or "pages" (WHAT).

        'what' must be  Literal["units", "pages"]
        """
        if self.vertical_scrollbar is not None:
            self._scrollable_object.yview_scroll(number, what)
