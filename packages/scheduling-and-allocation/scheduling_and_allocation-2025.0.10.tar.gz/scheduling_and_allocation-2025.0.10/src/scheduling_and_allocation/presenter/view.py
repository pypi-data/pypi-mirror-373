"""
# ============================================================================
# A view of the class times for a specific resource
#
# Events triggered by ViewDynamicTk
#   tree_popup_menu(gui_id)
#   draw_blocks()
#   on_closing(_*)
#   open_companion_view(gui_id)
#   gui_block_is_moving(gui_id,  gui_block_day, gui_block_start_time)
#   gui_block_has_dropped(gui_id)
#
# From pop-up menu
#   is_movable(block,gui_id)
#   move_resource(block,resource)
#
# Methods called from ViewsController
#   close()
#   draw()
#   is_block_in_view(moved_block)
#   move_gui_block_to(moved_block, day, start_time)
#   refresh_block_colours()
#
# ============================================================================
"""
from __future__ import annotations
import re
from functools import partial
from typing import TYPE_CHECKING, Optional, Callable

from ..gui_generics.menu_and_toolbars import MenuItem, MenuType
from ..Utilities.id_generator import IdGenerator
from ..gui_pages.view_dynamic_tk import ViewDynamicTk
from ..model import Block, Teacher, Stream, Lab, Schedule
from ..model.enums import ResourceType
if TYPE_CHECKING:
    from ..presenter.views_controller import ViewsController

RESOURCE = Lab | Stream | Teacher

# =====================================================================================================================
# use an generator to always guarantee that the new id will be unique
# =====================================================================================================================
_gui_block_ids = IdGenerator()

# =====================================================================================================================
# View
# =====================================================================================================================
class View:
    """View - describes the visual representation of a Schedule."""
    def __init__(self, views_controller: ViewsController, frame, schedule: Schedule,
                 resource: RESOURCE, dirty_flag_method:Callable, gui:ViewDynamicTk=None,
                 ):
        """
        :param views_controller: somebody needs to be in control
        :param frame: container
        :param schedule:
        :param resource:
        :param gui: doesn't need to be set except when setting up for a test suite
        """
        self.views_controller = views_controller
        self.frame = frame
        self.resource = resource
        self.schedule = schedule
        self.gui_blocks: dict[str, Block] = {}
        self.dirty_flag_method = dirty_flag_method

        # get the resource type from the resource object, and all its blocks
        resource_type = ResourceType.none
        if isinstance(resource, Teacher):
            resource_type = ResourceType.teacher
        elif isinstance(resource, Stream):
            resource_type = ResourceType.stream
        elif isinstance(resource, Lab):
            resource_type = ResourceType.lab
        self.resource_type = resource_type

        self.blocks: list[Block] = []

        # create the gui representation of the view
        if gui is None:
            self.gui: ViewDynamicTk = ViewDynamicTk(self.frame, str(resource), resource_type= self.resource_type)
        else:
            self.gui = gui

        # Need to set handlers here, instead on constructor, so that it is easier for testing
        self.gui.get_popup_menu_handler = self.tree_popup_menu
        self.gui.refresh_blocks_handler = self.draw_blocks
        self.gui.on_closing_handler = self.on_closing
        self.gui.double_click_block_handler = self.open_companion_view
        self.gui.gui_block_is_moving_handler = self.gui_block_is_moving
        self.gui.gui_block_has_dropped_handler = self.gui_block_has_dropped
        self.gui.undo_handler = self.views_controller.undo
        self.gui.redo_handler = self.views_controller.redo

        self._block_original_start_time: Optional[float]= None
        self._block_original_day: Optional[float] = None
        self.gui.draw()

    # ----------------------------------------------------------------------------------------------------------------
    # get popup menu (get_popup_menu_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def toggle_is_movable(self, block: Block, gui_id:str):
        """
        toggle movability for block, and inform View Controller
        :param block: the block that needs its 'movable' option toggled
        """
        block.movable = not block.movable
        self.gui.modify_movable(gui_id, block.movable)

        # very important, let the gui controller _know_ that the gui block has been modified
        self.views_controller.notify_block_movable_toggled( block)
        self.dirty_flag_method(True)

        # new action by user, so clear all 'redo'
        self.views_controller.remove_all_redoes()

        # save the action so that it can be undone
        self.views_controller.save_action_block_movable_toggled(block, not block.movable)


    # ----------------------------------------------------------------------------------------------------------------
    # get all the blocks for this resource/schedule (refresh_blocks_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def draw_blocks(self):
        """
        draw blocks onto Canvas
        """

        # get all the blocks for this resource/schedule
        blocks = []
        match self.resource_type:
            case ResourceType.teacher:
                blocks = self.schedule.get_blocks_for_teacher(self.resource)
            case ResourceType.stream:
                blocks = self.schedule.get_blocks_for_stream(self.resource)
            case ResourceType.lab:
                blocks = self.schedule.get_blocks_in_lab(self.resource)

        # create all the gui blocks and draw them
        self.gui_blocks.clear()

        for block in blocks:

            gui_block_id: int = _gui_block_ids.get_new_id()
            gui_tag = f"gui_tag_{gui_block_id}"
            self.gui_blocks[gui_tag] = block

            text = self.get_block_text(block, scale = self.gui.get_scale(),resource_type = self.resource_type)
            day, start_time, duration = self._block_to_floats(block)

            self.gui.draw_block(resource_type=self.resource_type,
                                day=day, start_time=start_time, duration=duration,
                                text=text,
                                gui_block_id=gui_tag,
                                movable=block.movable)
            self.gui.colour_block(gui_tag, self.resource_type, block.movable, conflict=block.conflict)

    # ----------------------------------------------------------------------------------------------------------------
    # is block in this view?
    # ----------------------------------------------------------------------------------------------------------------
    def is_block_in_view(self, block):
        return block in self.gui_blocks.values()

    # ----------------------------------------------------------------------------------------------------------------
    # important tidy-up stuff (on_closing_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def on_closing(self, *_):
        """When the view closes, clean up"""
        self.views_controller.view_is_closing(self.resource)

    def close(self):
        self.gui.kill()

    # ----------------------------------------------------------------------------------------------------------------
    # open companion view (double_click_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def open_companion_view(self, gui_tag: str):
        """
        Based on the resource_type of this view, will open another view which has this Block.
        :param gui_tag:
        """
        block = self.gui_blocks[gui_tag]
        self.views_controller.open_companion_view(block)

    # ----------------------------------------------------------------------------------------------------------------
    # gui_block_is_moving (gui_block_is_moving_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def gui_block_is_moving(self, gui_id: str,  gui_block_day: float, gui_block_start_time: float):
        """
        Update block and conflict information as the user is dragging the gui block
        :param gui_id: the id of the gui representation of the block
        :param gui_block_day: the position of the gui block
        :param gui_block_start_time: the start time of the gui block
        """

        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return

        # capture the info about the block before it starts moving
        if self._block_original_start_time is None and self._block_original_day is None:
            self._block_original_start_time = block.start
            self._block_original_day = block.day.value

        # update the block by snapping to time and day, although it doesn't update the gui block
        block.start = gui_block_start_time
        block.snap_to_day(gui_block_day)
        block.snap_to_time()
        self.schedule.calculate_conflicts()
        self.refresh_block_colours()
        #self.gui.colour_block(gui_id, self.resource_type, is_movable=block.movable, conflict = block.conflict)

        # very important, let the gui controller _know_ that the gui block has been moved
        self.views_controller.notify_block_move(self.resource.number, block, gui_block_day, gui_block_start_time)

        # don't set dirty flag until block has dropped!

    # ----------------------------------------------------------------------------------------------------------------
    # gui_block_has_dropped (gui_block_has_dropped_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def gui_block_has_dropped(self, gui_id: str):
        """
        User has stopped dragging the gui block, so adjust gui block to block's new location and
        inform View Controller
        :param gui_id: the id of the gui representation of the block
        """
        block: Block = self.gui_blocks.get(gui_id,None)
        if block is None:
            return

        # set the gui block coordinates to match the block
        # (which is constantly being snapped to grid during the move process)
        self.gui.move_gui_block(gui_id, block.day.value,block.start)

        # has the block actually moved?
        if self._block_original_start_time is None or self._block_original_day is None:
            return

        if (self._block_original_start_time == block.start and
            self._block_original_day == block.day):
            return

        # very important, let the gui controller _know_ that the gui block has been moved
        self.views_controller.notify_block_move(self.resource.number, block, block.day.value,
                                                block.start)

        # new action by user, so clear all 'redo'
        self.views_controller.remove_all_redoes()

        # save the action so that it can be undone
        self.views_controller.save_action_block_move(block, self._block_original_day, block.day.value,
                                                     self._block_original_start_time, block.start)

        # reset the 'start move' info
        self._block_original_start_time = None
        self._block_original_day = None

        self.dirty_flag_method(True)

    # ----------------------------------------------------------------------------------------------------------------
    # get popup menu (get_popup_menu_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def tree_popup_menu(self, gui_id) -> Optional[list[MenuItem]]:
        """
        Create a pop-up menu that is unique to this gui_id
        :param gui_id:
        """
        block = self.gui_blocks.get(gui_id, None)

        if block is None:
            return

        # get the resources (note we cannot swap blocks between streams)
        resources = set()
        match self.resource_type:
            case ResourceType.teacher:
                resources = set(self.schedule.teachers()) - set(block.teachers())
            case ResourceType.lab:
                resources = set(self.schedule.labs()) - set(block.labs())

        # create the menu
        toggle_str = "Unset 'movable' option" if block.movable else "Set 'movable' option"
        menu_list: list[MenuItem] = [MenuItem(menu_type=MenuType.Command, label=toggle_str,
                                              command=partial(self.toggle_is_movable, block, gui_id))]

        if len(resources):
            menu_list.append(MenuItem(menu_type=MenuType.Separator))

        resource_list = []
        for resource in sorted(resources):
            resource_list.append(MenuItem(menu_type=MenuType.Command, label=f"{resource}",
                                      command=partial(self.move_resource, block, resource)
                                      ))
        menu_list.append(MenuItem(menu_type=MenuType.Cascade, label=f"Move class to {self.resource_type.name} ...",
                         children=resource_list))

        return menu_list

    # ----------------------------------------------------------------------------------------------------------------
    # modify the resource (from pop-up menu)
    # ----------------------------------------------------------------------------------------------------------------
    def move_resource(self, block: Block, resource: RESOURCE):
        """
        move resource (ask Views Controller to do it for us)
        :param block:
        :param resource:
        """

        # let gui controller handle this because it involves more than one resource
        self.views_controller.notify_move_block_to_resource(resource_type = self.resource_type,
                                                            block=block,
                                                            from_resource= self.resource,
                                                            to_resource= resource)

        # new action by user, so clear all 'redo'
        self.views_controller.remove_all_redoes()

        # save the action so that it can be undone
        self.views_controller.save_action_block_resource_changed(resource_type = self.resource_type,
                                                                 block=block,
                                                                 from_resource= self.resource,
                                                                 to_resource= resource)

    # ----------------------------------------------------------------------------------------------------------------
    # move_gui_block_to (used by Views Controller)
    # ----------------------------------------------------------------------------------------------------------------
    def move_gui_block_to(self, block: Block, day: float, start_time: float):
        """
        move the gui block (associated with block) to a new position (used by Views Controller)
        :param block: block that is associated with the gui image
        :param day: the day that the **gui block** needs to be moved to (not necessarily the same as the block)
        :param start_time: the time that the **gui block** needs to be moved to (not necessarily the same as the block)
        """
        gui_id = self._get_gui_id_from_block(block.number)
        self.gui.move_gui_block(gui_id, day, start_time)


    # ----------------------------------------------------------------------------------------------------------------
    # refresh block colour (used by Views Controller & View)
    # ----------------------------------------------------------------------------------------------------------------
    def refresh_block_colours(self):
        """Go through all blocks, and adjust colours as required"""

        for gui_tag, block in self.gui_blocks.items():
            self.gui.colour_block(gui_tag, self.resource_type, is_movable=block.movable, conflict = block.conflict)

    # ----------------------------------------------------------------------------------------------------------------
    # get block text
    # ----------------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_block_text( block: Block, resource_type, scale=1):
        """
        :param block: The block object
        :param scale: the scale of the view
        :param resource_type: Teacher | Stream | Lab
        """

        # course & section & streams
        course_number = ""
        section_number = ""
        if block.section:
            course_number = block.section.course.number if scale > 0.5 else re.split("[-*]", block.section.course.number)
            section_number = block.section.title

        # labs
        lab_numbers = ", ".join(l.number for l in block.labs())
        lab_numbers = lab_numbers if scale > .75 else lab_numbers[0:16] + "..."
        lab_numbers = lab_numbers if scale > .50 else lab_numbers[0:7] + "..."
        if resource_type == ResourceType.lab and (scale <= .75 or block.duration <= 1):
                lab_numbers = ""
        lab_numbers = "" if resource_type == ResourceType.lab and block.duration <= 1 else lab_numbers

        # streams
        stream_numbers = ",".join(s.number for s in block.streams())
        stream_numbers = stream_numbers if scale > .75 else stream_numbers[0:11] + "..."
        stream_numbers = stream_numbers if scale > .50 else stream_numbers[0:7] + "..."
        if resource_type == ResourceType.stream and (scale <= .75 or block.duration <= 1):
                stream_numbers = ""

        # teachers
        teachers_name = ""
        if len(block.teachers()) <= 2:
            for t in block.teachers():
                if len(str(t)) > 12:
                    teachers_name = teachers_name + f"{t.firstname} {t.lastname[0:1]}.\n"
                else:
                    teachers_name = teachers_name + f"{str(t)}\n"
        teachers_name = teachers_name.rstrip()
        teachers_name = teachers_name if scale > .75 else teachers_name[0:11] + "..."
        teachers_name = teachers_name if scale > .50 else teachers_name[0:7] + "..."
        if resource_type == ResourceType.teacher:
            if scale < .75 or block.duration <= 1:
                teachers_name = ""

        # define what to display
        block_text = f"{course_number}\n{section_number}\n"
        block_text = block_text + teachers_name + "\n" if teachers_name else block_text
        block_text = block_text + lab_numbers + "\n" if lab_numbers else block_text
        block_text = block_text + stream_numbers + "\n" if stream_numbers else block_text

        block_text = block_text.rstrip()
        return block_text

    # ----------------------------------------------------------------------------------------------------------------
    # draw - called by Views Controller
    # ----------------------------------------------------------------------------------------------------------------
    def draw(self):
        self.gui.draw()

    # ----------------------------------------------------------------------------------------------------------------
    # block to floats
    # ----------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _block_to_floats( block) -> tuple[int,float,float]:
        """take a block and return number representations of its properties"""
        return block.day.value, block.start, block.duration

    # ----------------------------------------------------------------------------------------------------------------
    # get gui id from block
    # ----------------------------------------------------------------------------------------------------------------
    def _get_gui_id_from_block(self, block_number: str) -> Optional[str]:
        for g,b in self.gui_blocks.items():
            if b.number == block_number:
                return g
        return None

