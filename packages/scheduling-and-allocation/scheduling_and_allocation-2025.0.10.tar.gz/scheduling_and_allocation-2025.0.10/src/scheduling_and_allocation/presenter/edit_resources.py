"""
# ============================================================================
# Create a list of all resources
# - edit properties
# - create new resource
# - delete resource
#
# Events triggered by EditResourcesTk
#       delete_obj(row_data)
#       save(all_data)
#
# ============================================================================
"""

from typing import Optional, Callable

from ..Utilities import Preferences
from ..model import Schedule, ResourceType
from ..gui_pages import EditResourcesTk, DEColumnDescription

property_conversions_from_str = {
    "firstname": lambda x: x,
    "lastname": lambda x: x,
    "release": lambda x: float(x) if x else 0,
    "teacher_id": lambda x: x,
    "description": lambda x: x,
    "number": lambda x: x,
}


# =====================================================================================================================
# Class Edit Resources
# =====================================================================================================================
class EditResources:

    # -----------------------------------------------------------------------------------------------------------------
    # constructor
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 dirty_flag_method: Callable[[Optional[bool]], bool],
                 frame,
                 view_type: ResourceType,
                 schedule: Optional[Schedule],
                 preferences: Preferences = None,
                 gui=None):
        """
        Creates the basic EditResources (a simple matrix)
        :dirty_flag_method: function that gets/sets the dirty flag
        :param frame: gui container object
        :param view_type: Is it a lab, stream or teacher
        :param schedule: The Schedule object
        :gui: the gui object that shows data (optional)
        """

        self.preferences = preferences
        # Resource type specifics
        match view_type:
            case ResourceType.teacher:
                self.column_descriptions: list[DEColumnDescription] = [
                    DEColumnDescription(title="ID", width=5, property="teacher_id", unique_id=True),
                    DEColumnDescription(title="First Name", width=15, property="firstname", unique_id=False),
                    DEColumnDescription(title="Last Name", width=15, property="lastname", unique_id=False),
                    DEColumnDescription(title="RT", width=8, property="release", unique_id=False),
                ]
                self._get_resources = schedule.teachers
                self._get_resource_by_number = schedule.get_teacher_by_number
                self._delete_resource = schedule.remove_teacher
                self._update_resource = schedule.add_update_teacher

            case ResourceType.lab:
                self.column_descriptions: list[DEColumnDescription] = [
                    DEColumnDescription(title="Room", width=14, property="number", unique_id=True),
                    DEColumnDescription(title="Description", width=50, property="description", unique_id=False),
                ]
                self._get_resources = schedule.labs
                self._get_resource_by_number = schedule.get_lab_by_number
                self._delete_resource = schedule.remove_lab
                self._update_resource = schedule.add_update_lab

            case ResourceType.stream:
                self.column_descriptions: list[DEColumnDescription] = [
                    DEColumnDescription(title="Room", width=14, property="number", unique_id=True),
                    DEColumnDescription(title="Description", width=50, property="description", unique_id=False),
                ]
                self._get_resources = schedule.streams
                self._get_resource_by_number = schedule.get_stream_by_number
                self._delete_resource = schedule.remove_stream
                self._update_resource = schedule.add_update_stream

            case _:
                self.column_descriptions: list[DEColumnDescription] = [
                    DEColumnDescription(title="", width=10, property="", unique_id=True),
                ]
                self._get_resources = lambda: []
                self._get_resource_by_number = lambda x: None
                self._delete_resource = lambda x: None
                self._update_resource = lambda *args, **kwargs: None

        # other initializations
        if not gui:
            self.gui = EditResourcesTk(
                parent=frame,
                event_delete_handler=self.delete_obj,
                event_save_handler=self.save,
                preferences=self.preferences,
            )
        else:
            self.gui = gui

        disabled_columns = [True,] if view_type == ResourceType.teacher else []

        self.dirty_flag_method: Callable[[Optional[bool]], bool] = dirty_flag_method
        self.delete_queue: list = list()
        self.view_type: ResourceType = view_type
        self.schedule: Optional[Schedule] = schedule
        self.gui.initialize_columns(self.column_descriptions, disabled_columns)

    # -----------------------------------------------------------------------------------------------------------------
    # refresh the tables
    # -----------------------------------------------------------------------------------------------------------------
    def refresh(self):
        """update the table to represent the 'new' data"""

        # get the data
        objs = self._get_resources()

        # Create a 2-d array of the data that needs to be displayed.
        data = [[str(getattr(obj, col.property, None)) for col in self.column_descriptions] for obj in objs]

        # refresh the GUI_Pages
        self.gui.refresh(data)

        # purge the delete queue
        self.delete_queue.clear()

    # -----------------------------------------------------------------------------------------------------------------
    # Save updated data
    # -----------------------------------------------------------------------------------------------------------------
    def save(self, all_data: list[list[str]]):
        """
        Save any changes that the user entered in the GUI_Pages form.
        :param all_data: a 2-d array of string values in columns and rows
        """

        needs_updating = self._check_for_changed_resources(all_data)

        # do we need to change anything?
        changes = False
        changes = len(needs_updating) or changes
        changes = len(self.delete_queue) or changes
        if not changes:
            return

        # Update or add changes.
        for obj in self.delete_queue:
            self._delete_resource(obj)
        for init_arguments in needs_updating:
            self._update_resource(**init_arguments)

        # all done saving
        self.dirty_flag_method(changes)
        self.refresh()

    # -----------------------------------------------------------------------------------------------------------------
    # delete object
    # -----------------------------------------------------------------------------------------------------------------
    def delete_obj(self, data: list[str], *_):
        """Save delete requests, to be processed later. Note that all data is given in string representation"""
        obj = None
        for index, column in enumerate(self.column_descriptions):
            if column.unique_id and data[index]:
                unique_id = property_conversions_from_str[column.property](data[index])
                obj = self.schedule.get_view_type_obj_by_id(self.view_type, unique_id)
                break
        if obj:
            self.delete_queue.append(obj)

    # -----------------------------------------------------------------------------------------------------------------
    # Check if any of the resources have been modified
    # -----------------------------------------------------------------------------------------------------------------
    def _check_for_changed_resources(self, all_data) -> list[dict]:
        """Go through data that is in gui, and compare to existing objects
        :return dictionary: key/value pairs required for this resource type's constructor
        """

        changed_objects: list[dict] = []

        # Read data from the data object (ignore lines with no data in them).
        for data in (d for d in all_data if len([x for x in d if x])):

            obj = None
            constructor_inputs = dict()

            # get all inputs required for the constructor
            for index, column in enumerate(self.column_descriptions):
                if column.unique_id and data[index]:
                    unique_id = property_conversions_from_str[column.property](data[index])
                    obj = self.schedule.get_view_type_obj_by_id(self.view_type, unique_id)
                    constructor_inputs[column.property] = unique_id
                elif not column.unique_id:
                    if index < len(data):
                        constructor_inputs[column.property] = property_conversions_from_str[column.property](
                            data[index])

            # if object is modified or new, save constructor inputs
            if obj is not None and self._object_changed(obj, data):
                changed_objects.append(constructor_inputs)
            if obj is None:
                changed_objects.append(constructor_inputs)

        return changed_objects

    # -----------------------------------------------------------------------------------------------------------------
    # does an object need to be updated?
    # -----------------------------------------------------------------------------------------------------------------
    def _object_changed(self, obj, data) -> bool:
        """compares each column data with the attribute for the object and returns true if any of them are different"""

        for col, column in enumerate(self.column_descriptions):
            if hasattr(obj, column.property):
                if str(getattr(obj, column.property, None)) != data[col]:
                    return True
        return False
