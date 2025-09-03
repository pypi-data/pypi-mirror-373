"""
# ============================================================================
# Code that draws the View stuff.  No other functionality.
#
# PURPOSE: To provide a simple class that can be used to draw schedules where the canvas object can
#          be a generic canvas:  PDF, Tk.Canvas, HTML, etc.
#
# EVENT HANDLERS: None
# ============================================================================
"""

import tkinter as tk
from typing import Protocol, Optional

from ..Utilities import Colour
from ..gui_generics.block_colours import RESOURCE_COLOURS
from ..model import ResourceType
from ..gui_generics.drawing_scale import DrawingScale
from ..modified_tk.InitGuiFontsAndColours import get_fonts_and_colours

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
Times: dict[int, str] = {
    8: "8am",
    9: "9am",
    10: "10am",
    11: "11am",
    12: "12pm",
    13: "1pm",
    14: "2pm",
    15: "3pm",
    16: "4pm",
    17: "5pm",
    18: "6pm"
}
RECTANGLE_X1_OFFSET = 3
RECTANGLE_Y1_OFFSET = 2
RECTANGLE_X2_OFFSET = -2
RECTANGLE_Y2_OFFSET = -3

EARLIEST_TIME = min(Times.keys())
LATEST_TIME = max(Times.keys())

# =====================================================================================================================
# what is the minimal requirements for the canvas object to have if we want to draw
# =====================================================================================================================
class GenericCanvas(Protocol):
    def __init__(self, title="Title", schedule_name="sub_title", filename=None):...
    def create_line(self, x1:float, y1:float, x2:float, y2:float, fill:str="grey", dash="", tags: str|tuple=""):...
    def addtag_withtag(self,*args,**kwargs):...
    def create_text(self, x:float, y:float, text:str="", fill:str='black', tags:str|tuple="")->int:...
    def create_rectangle(self, coords:tuple[float,float,float,float], fill:str='grey', outline:str='grey',
                                        tags:str|tuple="")->int:...
    def save(self):...


# =====================================================================================================================
# ViewCanvasTk: this is where we draw stuff :)
# =====================================================================================================================
class ViewCanvasTk:

    Movable_Tag_Name = "movable"
    Rectange_Tag_Name = "rectangle"
    Text_Tag_Name = "text"
    Clickable_Tag_Name  = "clickable"

    # =================================================================
    # __init__
    # =================================================================
    def __init__(self, canvas: tk.Canvas | GenericCanvas, scale_factor: float = 1,
                 fg_colour=None, bg_colour=None):
        """Draws the Schedule timetable on the specified canvas.
            :param canvas: what to draw on
            :param scale_factor: scaling factors
            :param bg_colour: the colour used to draw the objects
        """
        self.colours, self.fonts = get_fonts_and_colours()

        self.canvas = canvas
        self.scale = DrawingScale(scale_factor)
        self.scale_factor = DrawingScale(scale_factor)
        scale = self.scale
        self.bg_colour = self.colours.DataBackground if bg_colour is None else bg_colour
        self.fg_colour = self.colours.WindowForeground if fg_colour is None else fg_colour
        self.canvas.config(background=self.bg_colour)

        # --------------------------------------------------------------------
        # draw hourly lines
        # --------------------------------------------------------------------
        (dummy_x, x_max) = self._days_x_coords(len(DAYS))
        (x_min, dummy_y) = self._days_x_coords(1)

        for time in Times.keys():

            # Draw each hour line.
            (y_hour, y_half) = self._time_y_coords(time, 0.5)
            canvas.create_line(
                x_min, y_hour, x_max, y_hour,
                fill="dark grey",
                dash="-",
                tags="baseline",
            )

            # Hour text.
            canvas.create_text(
                (x_min + scale.x_origin) / 2,
                y_hour, text=Times[time],
                fill=self.fg_colour,
                tags="baseline",
            )

            # for all inner times, draw a dotted line for the half hour.
            if time != LATEST_TIME:
                canvas.create_line(
                    x_min, y_half, x_max, y_half,
                    fill="grey",
                    dash=".",
                    tags="baseline",
                )

                # Half-hour text.
                if scale.current_scale > 0.5:
                    canvas.create_text(
                        (x_min + scale.x_origin) / 2,
                        y_half, text=":30",
                        fill=self.fg_colour,
                        tags="baseline",
                    )

        # --------------------------------------------------------------------
        # draw day lines
        # --------------------------------------------------------------------
        (y_min, y_max) = self._time_y_coords(EARLIEST_TIME, (LATEST_TIME - EARLIEST_TIME))

        for i in range(len(DAYS) + 1):
            (x_day, x_day_end) = self._days_x_coords(i + 1)
            canvas.create_line(x_day, scale.y_height_scale, x_day, y_max, fill=self.fg_colour,tags="baseline",)

            # day text
            if i < len(DAYS):
                if scale.current_scale <= 0.5:
                    canvas.create_text(
                        (x_day + x_day_end) / 2,
                        (y_min + scale.y_origin) / 2,
                        text=DAYS[i][0:1],
                        fill=self.fg_colour,
                        tags=("baseline",),
                    )
                else:
                    canvas.create_text(
                        (x_day + x_day_end) / 2,
                        (y_min + scale.y_origin) / 2,
                        text=DAYS[i],
                        fill=self.fg_colour,
                        tags=("baseline",),
                    )

    # =================================================================
    # draw_block
    # =================================================================
    def draw_block(self, resource_type: ResourceType, day: int, start_time: float,
                   duration: float, text:str, gui_tag, movable):
        """
        Draws the specific block on the gui canvas
        :param resource_type:
        :param day:
        :param start_time:
        :param duration:
        :param text:  the text to display on the block
        :param gui_tag:  the unique identifier for all gui objects that comprise this block
        :return:
        """

        # colour
        colour = RESOURCE_COLOURS[resource_type]
        colour = Colour.string(colour)
        text_colour = "black"
        if not Colour.is_light(colour):
            text_colour = "white"

        # coordinates
        x1,y1,x2,y2 = self.get_coords(day, start_time, duration)

        # draw
        self.canvas.create_rectangle(
            (x1 + RECTANGLE_X1_OFFSET,
             y1 + RECTANGLE_Y1_OFFSET,
             x2 + RECTANGLE_X2_OFFSET,
             y2 + RECTANGLE_Y2_OFFSET),
            fill=colour, outline=colour,
            tags=(self.Rectange_Tag_Name, self.Clickable_Tag_Name, gui_tag))

        self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2, text=text, fill=text_colour,
            tags=(self.Text_Tag_Name, self.Clickable_Tag_Name, gui_tag)
        )
        #self.canvas.addtag_withtag(self.Movable_Tag_Name, gui_tag)
        if movable:
            self.canvas.addtag_withtag(self.Movable_Tag_Name, gui_tag)
        else:
            self.canvas.tag_raise(gui_tag,"baseline")

    # =================================================================
    # modify movability of gui block
    # =================================================================
    def modify_movable(self, gui_tag:str, movable: bool):
        """
        modify movability of gui block
        :param gui_tag:
        :param movable:
        :return:
        """
        if movable:
            self.canvas.addtag_withtag(self.Movable_Tag_Name, gui_tag)
        else:
            self.canvas.dtag(gui_tag, self.Movable_Tag_Name)

    # =================================================================
    # get the gui id from tags
    # =================================================================
    def get_gui_block_id_from_selected_item(self) -> Optional[str]:
        """
        From the currently selected item, return the gui block tag
        :return: None if none can be found, else remaining tags, anded together
        """
        selected_objects: tuple[int, ...] = self.canvas.find_withtag(f"current && {self.Clickable_Tag_Name}")
        if len(selected_objects) == 0:
            return None

        selected_object = selected_objects[0]

        all_tags = set(self.canvas.gettags(selected_object)) - {'current', self.Rectange_Tag_Name,
                                                            self.Text_Tag_Name,
                                                            self.Movable_Tag_Name,
                                                            self.Clickable_Tag_Name}
        if len(all_tags) == 0:
            return ""
        if len(all_tags) > 1:
            print("SOMETHING IS WRONG IN VIEW_CANVAS_TK", all_tags)
        gui_id = list(all_tags)[0]
        return gui_id

    # =================================================================
    # get coordinates for a gui block
    # =================================================================
    def gui_block_coords(self, gui_block_id) -> Optional[list[float]]:
        """
        returns the coordinates of the gui block, None if gui block doesn't exist
        :param gui_block_id:
        :return: a list of 4 floats, or 'None'
        """
        obj_id = self.canvas.find_withtag(f"{ViewCanvasTk.Rectange_Tag_Name} && {gui_block_id}")
        if len(obj_id) < 1:
            return None
        else:
            coords = self.canvas.coords(obj_id[0])
            return [coords[0]-RECTANGLE_X1_OFFSET, coords[1]-RECTANGLE_Y1_OFFSET,
                    coords[2]-RECTANGLE_X2_OFFSET, coords[3]-RECTANGLE_Y2_OFFSET]

    # =================================================================
    # coords_to_day_time_duration
    # =================================================================
    def coords_to_day_time_duration(self, x, y, y2) -> tuple[float, float, float]:
        """
        Determines the day, time_start time, and duration based on canvas coordinates.
        :param x: x position (determines day)
        :param y: y position (determines time_start)
        :param y2: y2 position (with y - determines duration)
        :return: day, time, duration
        """
        scale = self.scale
        day = x / scale.x_width_scale - scale.x_offset + 1 - scale.x_origin
        time = y / scale.y_height_scale - scale.y_offset + EARLIEST_TIME - scale.y_origin
        duration = (y2 + 1 - y) / scale.y_height_scale

        return day, time, duration

    # =================================================================
    # gui block to day, time, duration (float)
    # =================================================================
    def gui_block_to_day_time_duration(self, gui_block_id) ->Optional[tuple[float,float,float]]:
        """
        Gets day/time/duration for given gui block if block exists
        :param gui_block_id:
        :return: day, start_time, duration if gui block exists, else None
        """

        coords = self.gui_block_coords(gui_block_id)
        if coords is not None:
            x1, y1, _, y2 = coords
            return self.coords_to_day_time_duration(x1, y1, y2)
        return None

    # =================================================================
    # get_coords
    # =================================================================
    def get_coords(self, day:float, start: float, duration: float=1.0):
        """Determines the canvas coordinates based on day, time_start time, and duration.
            :param start:
            :param day:
            :param duration:
        """
        (x, x2) = self._days_x_coords(round(day))
        (y, y2) = self._time_y_coords(start, duration)

        return x, y, x2, y2

    # =================================================================
    # using scale info, get the y limits for a specific time period
    # =================================================================
    def _time_y_coords(self, start, duration):
        """using scale info, get the y limits for a specific time period."""

        y_offset = self.scale.y_offset * self.scale.y_height_scale + self.scale.y_origin
        y = y_offset + (start - EARLIEST_TIME) * self.scale.y_height_scale
        y2 = duration * self.scale.y_height_scale + y - 1

        return y, y2


    # =================================================================
    # using scale info, get the x limits for a specific day
    # =================================================================
    def _days_x_coords(self, day: int) -> tuple[float,float]:
        """
        what can be the maximum and minimum number for day
        :param day:
        :return: minimum_x, maximum_x
        """

        x_offset = self.scale.x_offset * self.scale.x_width_scale + self.scale.x_origin
        x = x_offset + (day - 1) * self.scale.x_width_scale
        x2 = x_offset + day * self.scale.x_width_scale - 1

        return x, x2


    # ==================================================================
    # update scale
    # ==================================================================
    def adjust_scale(self, factor):
        """change the scale information based on the scaling factor"""
        self.scale = DrawingScale(factor)

