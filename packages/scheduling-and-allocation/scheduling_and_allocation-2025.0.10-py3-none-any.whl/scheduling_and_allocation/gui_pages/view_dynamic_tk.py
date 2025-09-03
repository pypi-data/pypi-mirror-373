"""
# ============================================================================
# Code that draws the View stuff.
#
# PURPOSE: Provides all the gui interactions with the View
#
#
# EVENT HANDLERS:
#         get_popup_menu_handler(gui_block_id)
#         refresh_blocks_handler()
#         on_closing_handler()
#         double_click_block_handler(gui_id)
#         gui_block_is_moving_handler(gui_id, day, start)
#         gui_block_has_dropped_handler(gui_id)
#         undo_handler()
#         redo_handler()
# ============================================================================
"""
from __future__ import annotations

from functools import partial
import tkinter as tk
from typing import Callable

from ..gui_generics.menu_and_toolbars import generate_menu, MenuItem, MenuType
from ..Utilities import Colour
from ..Utilities.id_generator import IdGenerator
from ..gui_generics.block_colours import get_conflict_colour_info, IMMOVABLE_COLOUR, RESOURCE_COLOURS
from ..gui_pages.view_canvas_tk import ViewCanvasTk
from ..model import ResourceType, ConflictType

DEFAULT_CANVAS_WIDTH = 700
DEFAULT_CANVAS_HEIGHT = 700


def _default_menu(*_) -> list[MenuItem]:
    menu = MenuItem(name="nothing", label="nothing", menu_type=MenuType.Command, command=lambda: None)
    return [menu, ]


class ViewDynamicTk:
    """ Provide the dynamic view for all calls times for a specific resource."""

    view_ids = IdGenerator()

    # =================================================================================================================
    # Init
    # =================================================================================================================
    def __init__(self, frame: tk.Frame, title: str, resource_type: ResourceType,):
        """
        creates a dynamic view to see all the blocks, where they are, movable, changeable, etc.
        :param frame: where to put the view
        :param title: title of the toplevel window (displayed in the top bar)
        :param resource_type: What type of view is this
        """

        self.mw = frame.winfo_toplevel()
        self.view_id = self.view_ids.get_new_id()

        # ------------------------------------------------------------------------------------------------------------
        # handlers
        # ------------------------------------------------------------------------------------------------------------
        # returns menu info for gui block popup menu
        self.get_popup_menu_handler: Callable[[str], list[MenuItem]] = _default_menu

        # redraws all the appropriate blocks on the canvas
        self.refresh_blocks_handler: Callable[[], None] = lambda: None

        # handles the closing of this view
        self.on_closing_handler: Callable = lambda *_: None

        # handles a double click on a gui block
        self.double_click_block_handler: Callable[[str], None] = lambda gui_id: None

        # handles the movement of a gui block
        self.gui_block_is_moving_handler: Callable[[str, float, float], None] = lambda gui_id, day, start: None

        # handles the dropping of a gui block
        self.gui_block_has_dropped_handler: Callable[[str], None] = lambda gui_id: None

        # undo/redo handlers
        self.undo_handler: Callable[[], None] = lambda: None
        self.redo_handler: Callable[[], None] = lambda: None

        # ------------------------------------------------------------------------------------------------------------
        # create a new toplevel window for this view
        # ------------------------------------------------------------------------------------------------------------
        tl = tk.Toplevel(self.mw)
        self.toplevel = tl
        tl.protocol('WM_DELETE_WINDOW', self.destroy)
        tl.resizable(False, False)
        tl.title(title)

        # ------------------------------------------------------------------------------------------------------------
        # Create bar at top to show Colour coding of conflicts
        # ------------------------------------------------------------------------------------------------------------
        f = tk.Frame(tl)
        f.pack(expand=1, fill="x")

        for c in get_conflict_colour_info(resource_type):
            label_text = c["text"]
            label_text = label_text.replace("_"," ")
            label_text = label_text.capitalize()
            tk.Label(f, text=label_text, width=10, background=c['bg'], foreground=c['fg']) \
                .pack(side='left', expand=1, fill="x")

        # ------------------------------------------------------------------------------------------------------------
        # add canvas
        # ------------------------------------------------------------------------------------------------------------
        cn = tk.Canvas(tl, height=DEFAULT_CANVAS_HEIGHT, width=DEFAULT_CANVAS_WIDTH, background="white")
        cn.pack()
        self.cn = cn

        # create the view_canvas
        self.view_canvas = self._draw_view_canvas()

        # ------------------------------------------------------------------------------------------------------------
        # create scale menu and redo/undo menu
        # ------------------------------------------------------------------------------------------------------------
        main_menu = tk.Menu(tl)
        tl.configure(menu=main_menu)

        scale_menu = MenuItem(name='view', menu_type=MenuType.Cascade, label='View')
        scale_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                      label='50%', command=partial(self.draw, 0.50) )
                             )
        scale_menu.add_child(MenuItem( menu_type=MenuType.Command,
                                      label='75%', command=partial(self.draw, 0.75))
                             )
        scale_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                      label='100%', command=partial(self.draw, 1.0))
                             )
        undo_menu = MenuItem(name='undo_redo', menu_type=MenuType.Cascade, label='Undo/Redo')
        undo_menu.add_child(MenuItem( menu_type=MenuType.Command, label='Undo',
                                     accelerator="Control-z", command=self._undo )
                            )
        undo_menu.add_child(MenuItem( menu_type=MenuType.Command, label='Redo',
                                     accelerator="Control-y", command=self._redo )
                            )

        # return list of top level menu items
        generate_menu(tl, [scale_menu, undo_menu], main_menu)

    # =================================================================================================================
    # draw the view canvas (the static drawing of the view)
    # =================================================================================================================
    def _draw_view_canvas(self, scale_factor: float = 1.0) -> ViewCanvasTk:
        """
        Clears the canvas of all blocks and redraws the background, followed by a call
        to an event handler that will update all the required blocks
        :param scale_factor: Allows smaller views to be drawn, 1=100%
        """

        self.cn.delete('all')

        # remove any binding to the canvas itself.
        self.cn.bind("<1>", "")
        self.cn.bind("<B1-Motion>", "")
        self.cn.bind("<ButtonRelease-1>", "")

        # set height and width of canvas and toplevel
        self.cn.configure(width=DEFAULT_CANVAS_WIDTH * scale_factor,
                          height=DEFAULT_CANVAS_WIDTH * scale_factor)

        # redraw background (things that don't change, like time, etc.)
        self.view_canvas = ViewCanvasTk(self.cn, scale_factor)

        # update size of window
        self.toplevel.update_idletasks()  # Update widget layout and dimensions
        width = self.toplevel.winfo_reqwidth()  # Get required width based on content
        height = self.toplevel.winfo_reqheight()  # Get required height based on content
        self.toplevel.geometry(f"{width}x{height}")

        return self.view_canvas

    # =================================================================================================================
    # draw the view (the view with all the gui interactions) (called by view, and if resized from menu)
    # =================================================================================================================
    def get_scale(self):
        return self.view_canvas.scale.current_scale

    def draw(self, scale_factor: float = 1.0):
        """
        Draw the view, calls event handler refresh_blocks_handler to get info about the blocks
        :param scale_factor:
        :return:
        """
        self._draw_view_canvas(scale_factor)

        # update blocks
        self.refresh_blocks_handler()

        # reset binding to canvas objects
        self.cn.tag_bind(self.view_canvas.Movable_Tag_Name, "<Button-1>", self._select_gui_block_to_move)
        self.cn.tag_bind(self.view_canvas.Clickable_Tag_Name, '<3>', self._post_menu)
        self.cn.tag_bind(self.view_canvas.Clickable_Tag_Name, '<2>', self._post_menu)
        self.cn.tag_bind(self.view_canvas.Clickable_Tag_Name, "<Double-1>", self._double_clicked)

    # =================================================================================================================
    # draw an individual block
    # =================================================================================================================
    def draw_block(self, resource_type: ResourceType, day: int, start_time: float,
                   duration: float, text: str, gui_block_id, movable=True):
        """
        Draws the specific block on the gui canvas
        :param resource_type:
        :param day:
        :param start_time:
        :param duration:
        :param text:  the text to display on the block
        :param gui_block_id:  the unique identifier for all gui objects that comprise this block
        :param movable: is this block allowed to be moved?
        """
        # draw the block
        self.view_canvas.draw_block(
            resource_type=resource_type,
            day = day, start_time = start_time, duration=duration,
            text=text,
            gui_tag=gui_block_id,
            movable=movable)

    # =================================================================================================================
    # modify movability of gui block
    # =================================================================================================================
    def modify_movable(self, gui_tag: str, movable: bool):
        """
        modify movability of gui block
        :param gui_tag:
        :param movable:
        :return:
        """
        self.view_canvas.modify_movable(gui_tag, movable)

    # =================================================================================================================
    # colour an individual block
    # =================================================================================================================
    def colour_block(self, gui_block_id: str, resource_type: ResourceType, is_movable=True,
                     conflict: ConflictType = None):
        """
        Set the colour of the block, base on its resource, conflict, etc.
        :param is_movable:
        :param conflict:
        :param gui_block_id:
        :param resource_type:
        :return:
        """

        conflict = ConflictType.most_severe(conflict, resource_type)
        colour = RESOURCE_COLOURS[resource_type]

        if conflict != ConflictType.NONE:
            colour = ConflictType.colours().get(conflict, "pink")

        if not is_movable:
            colour = IMMOVABLE_COLOUR

        cn = self.cn

        colour = Colour.string(colour)
        text_colour = "black"
        if not Colour.is_light(colour):
            text_colour = "white"

        # if tag name doesn't exist, then don't do anything
        try:
            cn.itemconfigure(f"{self.view_canvas.Rectange_Tag_Name} && {gui_block_id}", fill=colour)
            cn.itemconfigure(f"{self.view_canvas.Text_Tag_Name} && {gui_block_id}", fill=text_colour)
        except tk.TclError:
            pass

    # =================================================================================================================
    # put this gui window on top of every one else
    # =================================================================================================================
    def raise_to_top(self):
        """put this gui window on top of every one else"""
        self.toplevel.lift()

    # =================================================================================================================
    # the window is being closed (event handler for the little 'x' in top-level window)
    # =================================================================================================================
    def destroy(self):
        """Close/destroy the gui window."""
        self.on_closing_handler(self)
        self.toplevel.destroy()

    def kill(self):
        self.toplevel.destroy()
        self.mw.update_idletasks()

    # =================================================================================================================
    # menus, popups and double-clicks
    # =================================================================================================================
    def _post_menu(self, e: tk.Event):
        """
        Display pop up menu for specific gui block
        :param e: the Tk event that triggered this handler
        """
        gui_block_id = self.view_canvas.get_gui_block_id_from_selected_item()

        # get menu info from callback routine
        menu_details = self.get_popup_menu_handler(gui_block_id)
        if menu_details is None:
            return

        # create the menu and display
        menu = tk.Menu(self.toplevel, tearoff=0)
        generate_menu(self.toplevel, menu_details, menu)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _double_clicked(self, _: tk.Event):
        """
        call event handler because gui block was double-clicked
        """
        gui_block_id = self.view_canvas.get_gui_block_id_from_selected_item()
        self.double_click_block_handler(gui_block_id)


    # =================================================================================================================
    # undo/ redo
    # =================================================================================================================
    def _undo(self, _: tk.Event = None):
        """calls the "undo" handler"""
        self.undo_handler()

    def _redo(self, _: tk.Event = None):
        """calls the "redo" handler"""
        self.redo_handler()

    # ============================================================================
    # Moving Gui blocks around in response to changes in the schedule block
    # ============================================================================
    def move_gui_block(self, gui_block_id: str, day_number, start_number):
        """
        Move the gui block to a new location based on day
        :param gui_block_id: this tag specifies the gui tag associated with the drawn images
        :param day_number:
        :param start_number:
        """

        new_coords = self.view_canvas.get_coords(day_number, start_number)
        old_coords = self.view_canvas.gui_block_coords(gui_block_id)
        if old_coords is None:
            return

        (cur_x_pos, cur_y_pos, _, _) = old_coords
        self.cn.lift(gui_block_id)
        self.cn.move(gui_block_id, new_coords[0] - cur_x_pos, new_coords[1] - cur_y_pos)


    # ============================================================================
    # Dragging Guiblocks around
    # ============================================================================
    def _select_gui_block_to_move(self, event: tk.Event):

        gui_block_id = self.view_canvas.get_gui_block_id_from_selected_item()
        self.cn.tag_raise(gui_block_id, 'all')

        # unbind any previous binding for clicking and motion, just in case
        self.cn.bind("<Motion>", "")
        self.cn.bind("<ButtonRelease-1>", "")
        self.cn.tag_bind(self.view_canvas.Movable_Tag_Name, "<Button-1>", "")

        # bind for mouse motion
        self.cn.bind("<Motion>", partial(self._gui_block_is_moving, gui_block_id, event.x, event.y))

        # bind for release of mouse up
        self.cn.bind("<ButtonRelease-1>", partial(self._gui_block_has_stopped_moving, gui_block_id))

    def _gui_block_is_moving(self, gui_block_id, original_x, original_y, event: tk.Event):

        # unbind moving while we process
        self.cn.bind("<Motion>", "")

        # move the widget
        self.cn.move(gui_block_id, event.x - original_x, event.y - original_y)

        # get the information about the movement and call event handler
        info = self.view_canvas.gui_block_to_day_time_duration(gui_block_id)
        if info is not None:
            day, start_time, _ = info
            self.gui_block_is_moving_handler(gui_block_id, day, start_time)

        # rebind for motion
        self.cn.bind("<Motion>", partial(self._gui_block_is_moving, gui_block_id, event.x, event.y))

    def _gui_block_has_stopped_moving(self, gui_block_id, _: tk.Event):
        self.cn.tag_bind(self.view_canvas.Movable_Tag_Name, "<Button-1>", self._select_gui_block_to_move)
        self.cn.bind("<Motion>", "")
        self.cn.bind("<ButtonRelease-1>", "")
        info = self.view_canvas.gui_block_to_day_time_duration(gui_block_id)
        if info is not None:
            self.gui_block_has_dropped_handler(gui_block_id)

