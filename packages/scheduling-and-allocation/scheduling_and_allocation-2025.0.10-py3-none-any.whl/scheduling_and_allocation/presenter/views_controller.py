"""
# ============================================================================
# The controller of all the views
#
# Events triggered by ViewsControllerTk
#   call_view(resource)
#
# Events triggered by ViewDynamicTk
#   undo()
#   redo()
#
# Feedback from Views
#   open_companion_view(block)
#
#   notify_block_movable_toggled( block)
#   notify_move_block_to_resource(resource_type,block,from_resource,resource)
#   notify_block_move(self.resource.number, block, gui_block_day, gui_block_start_time)
#
#   save_action_block_movable_toggled(block, not block.movable)
#   save_action_block_move(block, from_day, to_day, from_start, to_start)
#   save_action_block_resource_changed(resource_type, block,from_resource,to_resource)
#
#   remove_all_redoes()
#   view_is_closing(self.resource)
# ============================================================================
"""

from typing import Callable, Optional, Literal

from ..gui_pages.views_controller_tk import ViewsControllerTk
from ..model import ResourceType, Schedule, Stream, Teacher, Lab, Block
from .view import View

RESOURCE = Teacher | Lab | Stream

# =====================================================================================================================
# Actions
# =====================================================================================================================

class Action:
    def __init__(self, block: Block, action: Literal['move', 'change_resource', 'toggle_movable'],
            from_day: Optional[float] = None,
            from_time: Optional[float] = None,
            to_day: Optional[float] = None,
            to_time: Optional[float] = None,
            from_resource: Optional[RESOURCE] = None,
            to_resource: Optional[RESOURCE] = None,
            resource_type:Optional[ResourceType] = None,
            was_movable: bool = None,
                 ):
        self.action = action
        self.block = block
        self.to_day = to_day
        self.to_time = to_time
        self.from_day = from_day
        self.from_time = from_time
        self.from_resource = from_resource
        self.to_resource = to_resource
        self.resource_type = resource_type
        self.was_movable = was_movable

    def __str__(self):
        if self.action == 'move':
            return f"move {self.block} from {self.from_day} to {self.to_day} and from {self.from_time} to {self.to_time}"
        elif self.action == "change_resource":
            return f"{self.block} change from {self.from_resource} to {self.to_resource}"
        elif self.action == "toggle_movable":
            return f"{self.block} movable has been toggled"
        else:
            return "Action with no action"

# =====================================================================================================================
# Views Controller
# =====================================================================================================================
class ViewsController:
    """Controls all of the views and their inter-view communication"""

    # -----------------------------------------------------------------------------------------------------------------
    # init
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, dirty_flag_method: Callable[[Optional[bool]], bool], frame, schedule: Schedule,
                 gui:ViewsControllerTk = None):
        """
        :param dirty_flag_method: method used to indicate that data has changed
        :param frame: where the view choices will be displayed
        :param schedule:
        """
        self.dirty_flag_method=dirty_flag_method
        self.frame = frame
        self.schedule = schedule
        self._views: dict[str, View] = {}
        self._undo: list[Action] = []
        self._redo: list[Action] = []


        self.resources = {
            ResourceType.teacher: list(self.schedule.teachers()),
            ResourceType.lab: list(self.schedule.labs()),
            ResourceType.stream: list(self.schedule.streams())
        }

        if gui is not None:
            self.gui = gui
        else:
            self.gui = ViewsControllerTk(frame, self.resources, self.call_view)


    # -----------------------------------------------------------------------------------------------------------------
    # refresh
    # -----------------------------------------------------------------------------------------------------------------
    def refresh(self):
        """
        sets the button colours for view choices depending on the most severe conflict for that resource
        """

        # if resources have changed, then we need to close all the views, and create a new gui
        resources = {
            ResourceType.teacher: list(self.schedule.teachers()),
            ResourceType.lab: list(self.schedule.labs()),
            ResourceType.stream: list(self.schedule.streams())
        }
        redrawing = False
        for resource_type in ResourceType.teacher, ResourceType.lab, ResourceType.stream:
            if (len(set(self.resources[resource_type]) - set(resources[resource_type])) != 0
                or len(set(resources[resource_type]) - set(self.resources[resource_type])) != 0):
                redrawing = True
                break
        if redrawing:
            self.resources = resources
            self.gui = ViewsControllerTk(self.frame, self.resources, self.call_view)

        # update the colours
        self.schedule.calculate_conflicts()
        for resource_type in self.resources:
            for resource in self.resources[resource_type]:
                conflict = self.schedule.resource_conflict(resource)
                conflict = conflict.most_severe(resource_type)
                self.gui.set_button_colour(resource.number, resource_type, conflict)


    # -----------------------------------------------------------------------------------------------------------------
    # call view
    # -----------------------------------------------------------------------------------------------------------------
    def call_view(self, resource):
        """
        creates the view for this resource, or if it already exists, makes it visible
        :param resource:
        """
        if resource.number in self._views:
            self._views[resource.number].gui.raise_to_top()
            return

        self._views[resource.number] = View(self, self.frame, self.schedule, resource, self.dirty_flag_method)


    # -----------------------------------------------------------------------------------------------------------------
    # notify block move
    # -----------------------------------------------------------------------------------------------------------------
    def notify_block_move(self, resource_number: Optional[str], moved_block: Block, day: float, start_time:float):
        """A GUI block has been modified in a view, so propagate this information to the other views"""

        self.refresh()

        # update any view that has the same block that was moved
        for view_id, view in self._views.items():
            if resource_number is None or view_id != resource_number:
                if view.is_block_in_view(moved_block):
                    view.move_gui_block_to(moved_block, day, start_time)
            view.refresh_block_colours()

    # -----------------------------------------------------------------------------------------------------------------
    # notify block movable toggled
    # -----------------------------------------------------------------------------------------------------------------
    def notify_block_movable_toggled(self, modified_block: Block):
        """A block has been modified in a view, so propagate this information to the other views"""

        self.refresh()

        # update any view that has the same block that was moved
        for view_id, view in self._views.items():
            view.refresh_block_colours()

    # ----------------------------------------------------------------------------------------------------------------
    # notify move block to a different resource
    # ----------------------------------------------------------------------------------------------------------------
    def notify_move_block_to_resource(self, resource_type: ResourceType, block: Block, from_resource: RESOURCE, to_resource: RESOURCE):
        """
        a block has been moved from one resource to another
        :param resource_type:
        :param block:
        :param from_resource:
        :param to_resource:
        """
        match resource_type:
            case ResourceType.teacher:
                block.remove_teacher(from_resource)
                block.add_teacher(to_resource)
            case ResourceType.lab:
                block.remove_lab(from_resource)
                block.add_lab(to_resource)
        self.schedule.calculate_conflicts()

        if from_resource.number in self._views.keys():
            self._views[from_resource.number].draw()
        else:
            self.call_view(from_resource)

        if to_resource.number in self._views.keys():
            self._views[to_resource.number].draw()
        else:
            self.call_view(to_resource)

        self.refresh()

        self.dirty_flag_method(True)


    # ----------------------------------------------------------------------------------------------------------------
    # open companion view (double_click_handler)
    # ----------------------------------------------------------------------------------------------------------------
    def open_companion_view(self, block: Block):
        """
        Based on the resource_type open other views which have this Block.
        :param block:
        """
        teachers = block.teachers()
        labs = block.labs()
        streams = block.streams()

        for resource in (*teachers, *labs, *streams):
            self.call_view(resource)

    # ----------------------------------------------------------------------------------------------------------------
    # view is closing
    # ----------------------------------------------------------------------------------------------------------------
    def view_is_closing(self, resource: RESOURCE):
        """view for resource has been closed, update our internal database"""
        try:
            self._views.pop(resource.number)
        except KeyError:
            pass

    # -----------------------------------------------------------------------------------------------------------------
    # save changes to undo db
    # -----------------------------------------------------------------------------------------------------------------
    def save_action_block_move(self, block: Block, from_day:float, to_day:float, from_time:float, to_time:float):

        # add to undo list
        self._undo.append(Action(block=block, action="move", from_day=from_day, from_time=from_time,
                                 to_day = to_day, to_time = to_time))

    def save_action_block_resource_changed(self, resource_type: ResourceType, block: Block, from_resource, to_resource):

        # add to undo list
        self._undo.append(Action(block=block, action="change_resource",
                                 from_resource=from_resource,
                                 to_resource=to_resource,
                                 resource_type=resource_type))

    def save_action_block_movable_toggled(self, block: Block, was: bool):

        # add to undo list
        self._undo.append(Action(block=block, action="toggle_movable", was_movable=was))


    # ----------------------------------------------------------------------------------------------------------------
    # undo/redo last actions
    # ----------------------------------------------------------------------------------------------------------------
    def undo(self):
        """
        undo whatever action remains in the undo list
        """
        if len(self._undo) == 0:
            return

        action = self._undo.pop()
        self._process_action(action, self._redo)
        self.dirty_flag_method(True)

    def redo(self):
        """
        redo whatever action remains in the redo list
        """
        if len(self._redo) == 0:
            return

        action = self._redo.pop()
        self._process_action(action, self._undo)
        self.dirty_flag_method(True)

    # ----------------------------------------------------------------------------------------------------------------
    # process the undo/redo action
    # ----------------------------------------------------------------------------------------------------------------
    def _process_action(self, action, other_list):
        """
        process the undo/redo action
        :param action: the action to do
        :param other_list: what list to move this action to... undo->redo and vice versa
        :return:
        """
        match action.action:
            case 'move':
                other_list.append(Action(action='move', block= action.block,
                                         from_day = action.to_day, from_time=action.to_time,
                                         to_day = action.from_day, to_time=action.from_time,
                                         ))
                action.block.start = action.from_time
                action.block.snap_to_day(action.from_day)
                self.schedule.calculate_conflicts()
                self.notify_block_move(None, action.block, action.from_day, action.from_time)

            case 'change_resource':
                other_list.append(Action(action='change_resource', block=action.block,
                                         from_resource=action.to_resource,
                                         to_resource=action.from_resource,
                                         resource_type=action.resource_type,
                                  ))
                self.schedule.calculate_conflicts()
                self.notify_move_block_to_resource(resource_type=action.resource_type, block=action.block,
                                                    from_resource=action.to_resource,
                                                    to_resource=action.from_resource)
            case 'toggle_movable':
                other_list.append(Action(action='toggle_movable', block=action.block, was_movable=not action.was_movable))
                action.block.movable = action.was_movable
                self.notify_block_movable_toggled(action.block)



    # ----------------------------------------------------------------------------------------------------------------
    # no more redoes
    # ----------------------------------------------------------------------------------------------------------------
    def remove_all_redoes(self):
        """Remove all redoes from the redo list"""
        self._redo.clear()

    # ----------------------------------------------------------------------------------------------------------------
    # redraw all the views and update button choices
    # ----------------------------------------------------------------------------------------------------------------
    def redraw_all(self):
        """redraw all the views and update button choices"""
        self.schedule.calculate_conflicts()

        for resource, view in self._views.items():
            teacher_numbers = (x.number for x in self.schedule.teachers())
            lab_numbers = (x.number for x in self.schedule.labs())
            stream_numbers = (x.number for x in self.schedule.streams())

            # if the resource for this view has been deleted from the schedule, then close the view
            if resource not in teacher_numbers and resource not in stream_numbers and resource not in lab_numbers:
                view.close()
            else:
                view.draw()

    # ----------------------------------------------------------------------------------------------------------------
    # kill bill!
    # ----------------------------------------------------------------------------------------------------------------
    def kill_all_views(self):
        """vicious!"""
        for view in self._views.values():
            view.close()
