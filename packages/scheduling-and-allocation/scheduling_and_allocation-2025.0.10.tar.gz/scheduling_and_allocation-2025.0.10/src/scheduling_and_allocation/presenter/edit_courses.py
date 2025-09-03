"""
# ============================================================================
# Creates a tree of all the courses, and lists of all the resources
# - can add/modify/delete all objects through the tree object
# - can drag resources onto courses
#
# Events triggered by EditCoursesTk
#       button_event_create_new_course()
#       tree_event_edit_tree_obj(selected_obj, parent_obj, tree_id)
#       tree_event_create_tree_popup(selected_obj, parent_obj, tree_id, parent_id)->list[MenuItem]
#       resource_event_create_resource_popup(resource_type, object)->list[MenuItem]
#       resource_event_show_teacher_stat(teacher)
#       resource_drag_event_is_valid_drop(resource_type, tree_object) -> bool
#       resource_dropped_event(resource_obj, tree_obj, tree_id)
#
# Events triggered by CreateTreePopupMenuActions
#       edit_block_dialog(selected_object, tree_id)
#       add_blocks_dialog(selected_object, tree_id)
#       edit_section_dialog(selected_object, tree_id)
#       edit_course_dialog(selected_object, tree_id)
#       remove_selected_from_parent(parent_object, selected_object, tree_parent_id))
#       modify_course_needs_allocation(selected_object, true_false, tree_id)
#       add_section_dialog(selected_object, tree_id)
#       assign_selected_to_parent(selected_object, resource, tree_id)
#       remove_selected_from_parent(selected_object, resource, tree_id)
#       remove_all_types_from_selected_object(resource_type_string, selected_object, tree_id)
#
# ============================================================================
"""

from functools import partial
from typing import Optional, Callable, Any, TYPE_CHECKING, Literal

from ..gui_generics.menu_and_toolbars import MenuItem
from ..gui_dialogs.add_edit_block_dialog_tk import AddEditBlockDialogTk
from ..gui_dialogs.add_section_dialog_tk import AddSectionDialogTk
from ..gui_dialogs.edit_course_dialog_tk import EditCourseDialogTk
from ..gui_dialogs.edit_section_dialog_tk import EditSectionDialogTk
from ..model import Schedule, ResourceType, Section, Block, Teacher, Lab, Stream, Course, WeekDay
from ..gui_pages import EditCoursesTk
from ..presenter.edit_courses_popup_menus import CreateTreePopupMenuActions, CreateResourcePopupMenuActions

RESOURCE_OBJECT = Teacher | Lab | Stream
TREE_OBJECT = Any

# =====================================================================================================================
# model subroutine lookups
# =====================================================================================================================
REMOVE_SUBS = {
    "teacher": lambda parent, teacher: parent.remove_teacher(teacher),
    "lab": lambda parent, lab: parent.remove_lab(lab),
    "stream": lambda parent, stream: parent.remove_stream(stream),
    "course": lambda parent, course: parent.remove_course(course),
    "block": lambda parent, block: parent.remove_block(block),
    "section": lambda parent, section: parent.remove_section(section),
}
REMOVE_ALL_SUBS = {
    "teacher": lambda parent: parent.remove_all_teachers(),
    "lab": lambda parent: parent.remove_all_labs(),
    "stream": lambda parent: parent.remove_all_streams(),
    "block": lambda parent: parent.remove_all_blocks(),
    "section": lambda parent: parent.remove_all_sections(),
}
REFRESH_SUBS = {
    "schedule": lambda presenter, parent_id, obj1: presenter.refresh(),
    "course": lambda presenter, parent_id, obj1:  presenter.refresh_course_gui(parent_id, obj1, False),
    "block": lambda presenter, parent_id, obj1: presenter.refresh_block_gui(parent_id, obj1, False),
    "section": lambda presenter, parent_id, obj1: presenter.refresh_section_gui(parent_id, obj1, False),
}
ASSIGN_SUBS = {
    "teacher": lambda parent, teacher: parent.add_teacher(teacher),
    "lab": lambda parent, lab: parent.add_lab(lab),
    "stream": lambda parent, stream: parent.add_stream(stream),
}

def list_minus_list(all_list, other_list):
    other_list = set(other_list)
    minus_list = list(set(all_list).difference(other_list))
    minus_list.sort()
    return  minus_list, list(other_list)


# =====================================================================================================================
# EditCourse
# =====================================================================================================================
class EditCourses:
    """
    Creates the page for editing courses, with a tree view, lists of resources, drag'n'drop, etc.
    """

    def __init__(self,
                 dirty_flag_method: Callable[[Optional[bool]], bool],
                 frame,
                 schedule: Optional[Schedule],
                 gui: EditCoursesTk=None):
        """
        :param dirty_flag_method: a function that is used to set the flag if schedule has been changed
        :param frame: the frame to put all the gui stuff in
        :param schedule: the model
        :param gui: the gui page
        """

        if not gui:
            self.gui = EditCoursesTk(frame)
        else:
            self.gui = gui

        self.set_dirty_flag = dirty_flag_method
        self.frame = frame
        self.schedule = schedule
        self.tree_ids: dict[str, str] = {}


        # set all the event required handlers for EditResourcesTk
        self.gui.handler_tree_edit = self.tree_event_edit_tree_obj
        self.gui.handler_new_course = self.button_event_create_new_course
        self.gui.handler_tree_create_popup = self.tree_event_create_tree_popup
        self.gui.handler_resource_create_menu = self.resource_event_create_resource_popup
        self.gui.handler_show_teacher_stat = self.resource_event_show_teacher_stat
        self.gui.handler_drag_resource = self.resource_drag_event_is_valid_drop
        self.gui.handler_drop_resource = self.resource_dropped_event

    # -----------------------------------------------------------------------------------------------------------------
    # tree - refresh everything
    # -----------------------------------------------------------------------------------------------------------------
    def refresh(self):
        """ updates the gui with the data from schedule"""
        self.gui.clear_tree()
        self.tree_ids.clear()
        for course in self.schedule.courses():
            name = " ".join((course.number, course.name))
            course_id = self.gui.add_tree_item("", name, course)
            self.refresh_course_gui(course_id, course, True)
        self.gui.update_resource_type_objects(ResourceType.teacher, self.schedule.teachers())
        self.gui.update_resource_type_objects(ResourceType.lab, self.schedule.labs())
        self.gui.update_resource_type_objects(ResourceType.stream, self.schedule.streams())


    # -----------------------------------------------------------------------------------------------------------------
    # tree - refresh course
    # -----------------------------------------------------------------------------------------------------------------
    def refresh_course_gui(self, course_id, course: Course, hide:bool = True):
        """
        refresh the contents of the course (sections) on the tree structure
        :param course_id: the id of the Course tree item
        :param course:
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(course_id)
        for section in course.sections():
            name = str(section)
            section_id = self.gui.add_tree_item(course_id, name, section, hide)
            self.refresh_section_gui(section_id, section, hide)

    # -----------------------------------------------------------------------------------------------------------------
    # tree - refresh gui
    # -----------------------------------------------------------------------------------------------------------------
    def refresh_section_gui(self, section_id, section: Section, hide: bool = True):
        """
        adds the contents of the section (blocks) on the tree structure
        :param section_id: the id of the Section tree item
        :param section: course section
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(section_id)

        # change the name of the parent text if stream exists for this section
        name = str(section)
        if len(section.streams()):
            name += "  (" + ",".join([str(stream) for stream in section.streams()]) + ")"
            self.gui.update_tree_text(section_id, name)

        for block in section.blocks():
            name = "Class Time: " + block.description()
            block_id = self.gui.add_tree_item(section_id, name, block, hide)
            self.refresh_block_gui(block_id, block, hide)


    # -----------------------------------------------------------------------------------------------------------------
    # tree - refresh block
    # -----------------------------------------------------------------------------------------------------------------
    def refresh_block_gui(self, block_id, block: Block, hide: bool=True):
        """
        adds the contents of the block (resources) onto the tree structure
        :param block_id: the id of the Block tree item
        :param block: course section block
        :param hide: leave the parent (and everything under it hidden?)
        :return:
        """
        self.gui.remove_tree_item_children(block_id)
        for teacher in block.teachers():
            self.gui.add_tree_item(block_id, f"teacher: {str(teacher)}", teacher, hide)
        for lab in block.labs():
            self.gui.add_tree_item(block_id, f"lab: {str(lab)}", lab, hide)

    # -------------------------------------------------------------------------------------------------------------
    # Tree - edit object
    # -------------------------------------------------------------------------------------------------------------
    def tree_event_edit_tree_obj(self, obj: Any, parent_obj: Any, tree_id: str, parent_id: str):
        """
        Given a particular tree object, edit it (Blocks, Section, Course)
        :param obj: Any tree object, but will ignore it if it is not a Block, Section or Course
        :param parent_obj: Who is the parent of this object
        :param tree_id: What is the tree_id of this object
        :param parent_id: What is the tree_id of this object's parent object
        :return:
        """
        if isinstance(obj, Block):
            self.edit_block_dialog(obj,parent_obj, parent_id)
        if isinstance(obj, Section):
            self.edit_section_dialog(obj, tree_id)
        if isinstance(obj, Course):
            self.edit_course_dialog(obj, tree_id)

    # -------------------------------------------------------------------------------------------------------------
    # Tree - popup menu
    # -------------------------------------------------------------------------------------------------------------
    def tree_event_create_tree_popup(self, selected_obj: Any, parent_object, tree_path:str, tree_parent_path) -> list[MenuItem]:
        """
        Create a pop-up menu based on the selected object

        :param selected_obj: object that was selected on the tree
        :param parent_object: parent of selected object
        :param tree_path: the id of the tree item that was selected
        :param tree_parent_path: the id of the tree item that is the parent of the selected
        :return:
        """
        popup = CreateTreePopupMenuActions(self, selected_obj, parent_object, tree_path, tree_parent_path)
        return popup.create_tree_popup_menus()

    # -------------------------------------------------------------------------------------------------------------
    # Course - add dialog
    # -------------------------------------------------------------------------------------------------------------
    def button_event_create_new_course(self):
        """
        Create a new course
        """
        self._add_edit_course_dialog('add', None, None)

    # -------------------------------------------------------------------------------------------------------------
    # Course - edit dialog
    # -------------------------------------------------------------------------------------------------------------
    def edit_course_dialog(self, course: Course, tree_id:str):
        """
        Create and use the edit course dialog to modify the selected course
        :param course:
        :param tree_id:
        """
        self._add_edit_course_dialog('edit',course,tree_id)

    # -------------------------------------------------------------------------------------------------------------
    # Course - add or edit dialog
    # -------------------------------------------------------------------------------------------------------------
    def _add_edit_course_dialog(self, add_or_edit: Literal['add','edit'], course: Optional[Course], tree_id:Optional[str]):
        """
        Create and use the edit course dialog to modify the selected course
        :param course:
        :param tree_id:
        """

        # set defaults
        block_data = []

        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), [])
        non_assigned_labs, assigned_labs = list_minus_list( self.schedule.labs(), [])

        course_number = ""
        number_sections = 1
        hours_per_week = 3
        course_name = ""
        course_allocation = True

        # if course exists, get info from course
        if course is not None:
            course_number = course.number
            number_sections = len(course.sections())
            hours_per_week = course.hours_per_week
            course_name = course.name
            course_allocation = course.needs_allocation

            if len(course.sections()) != 0:
                for b in course.sections()[0].blocks():
                    block_data.append((b.day.name, b.start, b.duration))

            non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), course.teachers())
            non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(), course.labs())

        # open the dialog box
        EditCourseDialogTk(self.frame,
                                course_number=course_number,
                                edit_or_add=add_or_edit,
                                existing_course_numbers=[c.number for c in self.schedule.courses()],
                                course_name=course_name,
                                course_hours=hours_per_week,
                                course_allocation= course_allocation,
                                num_sections=number_sections,

                                assigned_teachers=assigned_teachers,
                                non_assigned_teachers=non_assigned_teachers,
                                assigned_labs=assigned_labs,
                                non_assigned_labs=non_assigned_labs,
                                current_blocks=block_data,
                                apply_changes=self.schedule.add_edit_course,
                                )

        # refresh
        if add_or_edit == 'edit':
            REFRESH_SUBS['course'](self, tree_id, course)
        else:
            REFRESH_SUBS['schedule'](self, None, None)
        self.set_dirty_flag(True)


    # -------------------------------------------------------------------------------------------------------------
    # Section - add dialog
    # -------------------------------------------------------------------------------------------------------------
    def add_section_dialog(self, course: Course, tree_id: str):
        """Add section to Course
        :param course:
        :param tree_id:
        """
        title = f"{course.name} ({course.hours_per_week} hrs)"
        AddSectionDialogTk(self.frame,
                                course_description=title,
                                apply_changes=partial(self.schedule.add_sections,course),
                                course_hours=course.hours_per_week),
        REFRESH_SUBS["course"](self, tree_id, course)
        self.set_dirty_flag(True)

    # -------------------------------------------------------------------------------------------------------------
    # Section - edit dialog
    # -------------------------------------------------------------------------------------------------------------
    def edit_section_dialog(self, section: Section, tree_id: str):
        """Modify an existing section
        :param section:
        :param tree_id:
        """

        title = f"{section.course.name} ({section.course.hours_per_week} hrs)"
        text = section.title
        block_data = []
        for b in section.blocks():
            block_data.append((b.day.name, b.start, b.duration))
        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(),section.teachers())
        non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(),section.labs())
        non_assigned_streams, assigned_streams = list_minus_list(self.schedule.streams(), section.streams())

        EditSectionDialogTk(self.frame,
                                 course_description=title,
                                 section_description=text,
                                 assigned_teachers=list(section.teachers()),
                                 non_assigned_teachers=non_assigned_teachers,
                                 assigned_labs=list(section.labs()),
                                 non_assigned_labs=non_assigned_labs,
                                 assigned_streams=list(section.streams()),
                                 non_assigned_streams=non_assigned_streams,
                                 current_blocks=block_data,
                                 apply_changes=partial(self.schedule.update_section, section),
                                 course_hours=section.course.hours_per_week)
        REFRESH_SUBS["section"](self, tree_id, section)

        self.set_dirty_flag(True)

    # -------------------------------------------------------------------------------------------------------------
    # Blocks - add dialog
    # -------------------------------------------------------------------------------------------------------------
    def add_blocks_dialog(self, section: Section, tree_id: str):
        """
        :param section: the section to add a block to
        :param tree_id: the id of the section
        """
        AddEditBlockDialogTk(self.frame, "add", 1.5, [], list(self.schedule.teachers()),
                             [], list(self.schedule.labs()), partial(self.schedule.add_blocks, section))

        REFRESH_SUBS["section"](self, tree_id, section)
        self.set_dirty_flag(True)

    # -------------------------------------------------------------------------------------------------------------
    # Blocks - edit dialog
    # -------------------------------------------------------------------------------------------------------------
    def edit_block_dialog(self, block, section: Any, parent_id: str):
        """
        Modify the block
        :param block:
        :param section:
        :param parent_id: the id of the section
        """
        non_assigned_teachers, assigned_teachers = list_minus_list(self.schedule.teachers(), block.teachers())
        non_assigned_labs, assigned_labs = list_minus_list(self.schedule.labs(), block.labs())

        AddEditBlockDialogTk(
            frame = self.frame,
            add_edit_type = "edit",
            duration = block.duration,
            assigned_teachers = list(block.teachers()),
            non_assigned_teachers= non_assigned_teachers,
            non_assigned_labs=non_assigned_labs,
            assigned_labs=assigned_labs,
            apply_changes= partial(self.schedule.edit_block, block),
        )

        REFRESH_SUBS["section"](self,parent_id, block.section)
        self.set_dirty_flag(True)


    # -------------------------------------------------------------------------------------------------------------
    # Tree Popup - remove selected element from its parent
    # -------------------------------------------------------------------------------------------------------------
    def remove_selected_from_parent(self, parent, selected, parent_id):
        """
        Tree Popup - remove selected element from its parent
        :param parent:  the parent object
        :param selected: the selected object
        :param parent_id: the tree id of the parent
        """
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REMOVE_SUBS[key](parent,selected)

        obj_type = str(type(parent)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REFRESH_SUBS[key](self,parent_id, parent)
        self.set_dirty_flag(True)

    # -------------------------------------------------------------------------------------------------------------
    # Tree Popup - needs allocation
    # -------------------------------------------------------------------------------------------------------------
    def modify_course_needs_allocation(self, course:Course, value: bool, tree_path):
        """
        set the 'needs allocation' property of the course
        :param course:
        :param value:
        :param tree_path:
        """
        course.needs_allocation = value
        self.refresh_course_gui(tree_path, course)
        self.set_dirty_flag(True)

    # -------------------------------------------------------------------------------------------------------------
    # Tree Popup or dropped object - assign resource to selected tree item
    # -------------------------------------------------------------------------------------------------------------
    def assign_selected_to_parent(self, parent, selected, parent_id = -1):
        """
        assign selected resource object to the parent
        :param parent: Course/Section/block object
        :param selected: Lab/Stream/Teacher object
        :param parent_id: tree id of the parent object
        :return:
        """
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        ASSIGN_SUBS[key](parent,selected)

        if parent_id == -1:
            key = 'schedule'
        else:
            obj_type = str(type(parent)).lower()
            key = obj_type.split(".")[-1][0:-2]
        REFRESH_SUBS[key](self,parent_id, parent)
        self.set_dirty_flag(True)


    # -------------------------------------------------------------------------------------------------------------
    # remove all resources from a selected object
    # -------------------------------------------------------------------------------------------------------------
    def remove_all_types_from_selected_object(self, obj_type, selected, selected_id):
        """
        remove all resources from a selected object
        :param obj_type: the type of the object (Course/Section/Block)
        :param selected: the object
        :param selected_id: the tree id of the selected object
        :return:
        """
        REMOVE_ALL_SUBS[obj_type](selected)
        obj_type = str(type(selected)).lower()
        key = obj_type.split(".")[-1][0:-2]
        REFRESH_SUBS[key](self, selected_id, selected)
        self.set_dirty_flag(True)

    # -------------------------------------------------------------------------------------------------------------
    # create a pop-up menu for the resource list item
    # -------------------------------------------------------------------------------------------------------------
    def resource_event_create_resource_popup(self, resource_type: ResourceType, resource: RESOURCE_OBJECT) -> list[MenuItem]:
        """
        Create a pop-up menu based on the selected resource object

        :param resource_type: is it a teacher/lab/stream?
        :param resource: selected object
        """
        popup = CreateResourcePopupMenuActions(self, self.schedule, resource_type, resource)
        return popup.create_resource_popup_menus()


    # -------------------------------------------------------------------------------------------------------------
    # respond to a double click on a teacher resource
    # -------------------------------------------------------------------------------------------------------------
    def resource_event_show_teacher_stat(self, teacher: Teacher):
        text = []
        days = set()
        hours = 0
        for course in self.schedule.get_courses_for_teacher(teacher):
            for block in course.blocks():
                if block.has_teacher(teacher):
                    days.add(block.day)
                    hours = hours + block.duration

        text.append(f"Release: {teacher.release}")
        text.append( f"Total Class Time: {hours}")
        day_str = []
        for day in WeekDay:
            if day in days:
                day_str.append(day.name[0:3])
        text.append( f"Days: "+", ".join(day_str))
        self.gui.show_message(title = "Teacher Stats", msg=str(teacher), detail="\n".join(text))

    # -------------------------------------------------------------------------------------------------------------
    # can the resource object be added to the selected tree object?
    # -------------------------------------------------------------------------------------------------------------
    def resource_drag_event_is_valid_drop(self, resource_type: ResourceType, destination: TREE_OBJECT) -> bool:
        """
        is the destination object a legitimate object to accept as a parent for this resource type?
        :param resource_type:
        :param destination:
        """
        match resource_type:
            case ResourceType.teacher:
                if isinstance(destination, Course) or isinstance(destination, Section) or isinstance(destination, Block):
                    return True
                else:
                    return False
            case ResourceType.stream:
                if isinstance(destination, Section):
                    return True
                else:
                    return False
            case ResourceType.lab:
                if isinstance(destination, Course) or isinstance(destination, Section) or isinstance(destination, Block):
                    return True
                else:
                    return False

        return False

    # -------------------------------------------------------------------------------------------------------------
    # a resource object has been dropped on a course object
    # -------------------------------------------------------------------------------------------------------------
    def resource_dropped_event(self, resource: RESOURCE_OBJECT, destination: TREE_OBJECT, tree_id):
        """
        a resource object has been dropped onto a course object, so assign this resource to this object
        :param resource:
        :param destination:
        :param tree_id:
        :return:
        """
        self.assign_selected_to_parent(destination, resource,tree_id)
