"""
# ============================================================================
# This is the central control for launching any or all of the Views
# (the things that allow you to move blocks around)
#
# For each schedule item view, there will be:
#  * A button to open the view for that schedule item
#  * The button colour will reflect the Conflict status for that schedule item
#     * Due to the inability to change the background colour of a button on a MAC, we will use
#       borders around our button to indicate the various colour statuses of our scheduled items
#
# EVENT HANDLERS:
#    btn_callback(resource)
# ============================================================================
"""

from __future__ import annotations

import platform
from functools import partial
import tkinter as tk
from typing import Callable

from ..Utilities.Colour import is_light
from ..modified_tk import Scrolled, set_default_fonts_and_colours
from ..modified_tk import get_fonts_and_colours
from ..Utilities import Colour
from ..gui_generics.block_colours import RESOURCE_COLOURS
from ..model import ConflictType, ResourceType

class ViewsControllerTk:

    # ============================================================================
    # constructor
    # ============================================================================
    def __init__(self, parent: tk.Frame, resources:dict[ResourceType,list], btn_callback: Callable):
        """
        Initialize this manager
        :param parent: where to put the gui objects
        """

        # remove anything that was already in the frame
        self.parent = parent

        for widget in parent.winfo_children():
            widget.destroy()

        # set fonts
        self.colours, self.fonts = get_fonts_and_colours()
        if self.fonts is None:
            self.colours, self.fonts = set_default_fonts_and_colours(self.parent.winfo_toplevel())
        scrolled_frame = Scrolled(parent, "Frame").widget

        self._button_refs: dict[str, tk.Button] = {}

        tk.Label(scrolled_frame,text="Edit Class Times for ...", font=self.fonts.big, anchor='center').pack(expand=1,fill='both', pady=5)

        # for each resource, create a bunch of buttons that can launch views
        for resource_type in (ResourceType.teacher, ResourceType.lab, ResourceType.stream):
            l_frame = tk.LabelFrame(scrolled_frame, text=resource_type.name)
            l_frame.pack(expand=1,fill='both', padx=5,pady=15)

            for index,resource in enumerate(resources[resource_type]):
                row = int(index/4)
                col = index-row*4
                command = partial(btn_callback, resource)
                self._button_refs[resource.number] = tk.Button(l_frame, text=str(resource), highlightthickness=4, command=command, width=15)
                self._button_refs[resource.number].grid(column = col, row=row, sticky='nsew',ipadx=20, ipady=10, padx=2, pady=2)

    # ============================================================================
    # set button colour
    # ============================================================================
    def set_button_colour(self, button_id: str, resource_type, view_conflict: ConflictType = None):
        """
        set the colour of the button according to the conflict
        :param button_id:
        :param resource_type:
        :param view_conflict:
        """
        btn = self._button_refs.get(button_id, None)
        if btn is None:
            return

        # change the background colour of the button
        # ... (doesn't work on MAC) so also change the background colour of the highlighted area

        colour_highlight = self.parent.cget("background")
        colour = RESOURCE_COLOURS.get(resource_type, self.colours.ButtonBackground)
        active_colour = self.colours.ActiveBackground

        if view_conflict != ConflictType.NONE:
            colour = ConflictType.colours().get(view_conflict,'grey')
            active_colour = Colour.darken(colour, 10)

        if platform.system() == "Darwin":
            colour_highlight = colour
        else:
            if is_light(colour):
                btn.configure(foreground="black")
            else:
                btn.configure(foreground="white")

        btn.configure(background=colour, activebackground=active_colour,
                      highlightbackground=colour_highlight)



