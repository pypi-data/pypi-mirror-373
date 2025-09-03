"""
# ============================================================================
# Create dynamic menus (dependent on the state of the Schedule object)
#
# NOTE: this module is dependent on functions in EditCourses
#       edit_block_dialog(selected_object, tree_id)
#       add_blocks_dialog(selected_object, tree_id)
#       edit_section_dialog(selected_object, tree_id)
#       edit_course_dialog(selected_object, tree_id)
#       remove_selected_from_parent(parent_object, selected_object, tree_parent_id)
#       modify_course_needs_allocation(selected_object, true_false, tree_id)
#       add_section_dialog(selected_object, tree_id)
#       assign_selected_to_parent(selected_object, resource, tree_id)
#       remove_selected_from_parent(selected_object, resource, tree_id)
#       remove_all_types_from_selected_object(resource_type_string, selected_object, tree_id)
#
# ============================================================================
"""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from ..gui_generics.menu_and_toolbars import MenuItem, MenuType
from ..model import Course, Teacher, ResourceType, Section, Block, Lab, Stream, Schedule

if TYPE_CHECKING:
    from .edit_courses import EditCourses


# ====================================================================================================================
# Creates all the pop menu items, and their sub-menus if required
# ... each menu type will then call the appropriate 'presenter' code that will manage the modifications to the
#     tree/list menus in the EditCourse gui
# ====================================================================================================================
class CreateTreePopupMenuActions:
    """Creates all the pop menu items, dependent on the selected object, and their sub-menus if required

        Each menu type will then call the appropriate 'presenter' code that will manage the modifications to the
        tree/list menus in the EditCourse gui
    """
    def __init__(self, presenter: EditCourses, selected_object, parent_object, tree_id: str, tree_parent_id: str):
        """
        :param presenter: The presenter that is handling all the logic
        :param selected_object: The object that is the target of this menu
        :param parent_object: The parent of the object (ex. which block this teacher is attached to)
        :param tree_id: the id of the selected tree object
        :param tree_parent_id: the id of the selected tree object
        """
        self.presenter = presenter
        self.selected_object = selected_object
        self.parent_object = parent_object if parent_object is not None else presenter.schedule
        self.tree_id = tree_id
        self.tree_parent_id = tree_parent_id

    # ================================================================================================================
    # Create pop up menu based on the selected object
    # ================================================================================================================
    def create_tree_popup_menus(self):
        """create popup menus for trees

        menus are dynamic, depending on the current schedule, and what tree item was selected
        """

        menu_list: list[MenuItem] = []

        # ------------------------------------------------------------------------------------------------------------
        # course
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Course):
            self._edit_course(menu_list)
            self._remove_item(menu_list, "Remove Course")

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._needs_allocation(menu_list)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._add_section( menu_list)
            self._sub_menu_add_items(menu_list, ResourceType.teacher)
            self._sub_menu_add_items(menu_list, ResourceType.lab)
            self._sub_menu_add_items(menu_list, ResourceType.stream)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._remove_all_items(menu_list, "course")

        # ------------------------------------------------------------------------------------------------------------
        # section
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Section):
            self._edit_section(menu_list)
            self._remove_item(menu_list, "Remove Section")

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._add_blocks(menu_list)
            self._sub_menu_add_items(menu_list, ResourceType.teacher)
            self._sub_menu_add_items(menu_list, ResourceType.lab)
            self._sub_menu_add_items(menu_list, ResourceType.stream)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))
            self._sub_menu_remove_items(menu_list, ResourceType.teacher)
            self._sub_menu_remove_items(menu_list, ResourceType.lab)
            self._sub_menu_remove_items(menu_list, ResourceType.stream)
            self._remove_all_items(menu_list, "section")

        # ------------------------------------------------------------------------------------------------------------
        # block
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Block):
            self._edit_block(menu_list)
            self._remove_item(menu_list, "Remove Class Time")

            menu_list.append(MenuItem(menu_type=MenuType.Separator))

            self._sub_menu_add_items(menu_list, ResourceType.teacher)
            self._sub_menu_add_items(menu_list, ResourceType.lab)

            menu_list.append(MenuItem(menu_type=MenuType.Separator))
            self._sub_menu_remove_items(menu_list, ResourceType.teacher)
            self._sub_menu_remove_items(menu_list, ResourceType.lab)
            self._remove_all_items(menu_list, "block")

        # ------------------------------------------------------------------------------------------------------------
        # lab/teacher
        # ------------------------------------------------------------------------------------------------------------
        if isinstance(self.selected_object, Teacher):
            self._remove_item(menu_list, "Remove Teacher")
        if isinstance(self.selected_object, Lab):
            self._remove_item(menu_list, "Remove Lab")

        return menu_list

    # ================================================================================================================
    # Private methods that create the MenuList items
    # ================================================================================================================

    def _edit_block(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Edit Class Time",
                     command=lambda *_: self.presenter.edit_block_dialog(self.selected_object, self.tree_id, self.tree_parent_id)
                     )
        )

    # ------------------------------------------------------------------------------------------------------------
    def _add_blocks(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Add Class Times",
                     command=lambda *_: self.presenter.add_blocks_dialog(self.selected_object, self.tree_id)
                     )

        )

    # ------------------------------------------------------------------------------------------------------------
    def _edit_section(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Edit Section",
                     command=lambda *_: self.presenter.edit_section_dialog(self.selected_object, self.tree_id)
                     )
        )

    # ------------------------------------------------------------------------------------------------------------
    def _edit_course(self, menu_list: list[MenuItem]):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label="Edit Course",
                     command=lambda *_: self.presenter.edit_course_dialog(self.selected_object, self.tree_id)
                     )
        )

    # ------------------------------------------------------------------------------------------------------------
    def _remove_item( self, menu_list: list[MenuItem], text):
        menu_list.append(
            MenuItem(menu_type=MenuType.Command, label=text,
                     command=lambda *_: self.presenter.remove_selected_from_parent(self.parent_object, self.selected_object, self.tree_parent_id))
        )

    # ------------------------------------------------------------------------------------------------------------
    def _needs_allocation(self, menu_list: list[MenuItem]):
        if self.selected_object.needs_allocation:
            menu_list.append(
                MenuItem(menu_type=MenuType.Command, label="Unset 'needs allocation'",
                         command=lambda *_: self.presenter.modify_course_needs_allocation(self.selected_object, False, self.tree_id))
            )
        else:
            menu_list.append(
                MenuItem(menu_type=MenuType.Command, label="Set 'needs allocation'",
                         command=lambda *_: self.presenter.modify_course_needs_allocation(self.selected_object, True, self.tree_id))
            )

    # ------------------------------------------------------------------------------------------------------------
    def _add_section(self, menu_list: list[MenuItem]):
        menu_list.append(MenuItem(menu_type=MenuType.Command, label="Add Sections",
                     command=lambda *_: self.presenter.add_section_dialog(self.selected_object, self.tree_id))
        )

    # ------------------------------------------------------------------------------------------------------------
    def _sub_menu_add_items(self, menu_list: list[MenuItem], view: ResourceType):
        match view:
            case ResourceType.lab:
                items = [o for o in self.presenter.schedule.labs() if not self.selected_object.has_lab(o)]
                text = "Add Lab"
            case ResourceType.teacher:
                items = [o for o in self.presenter.schedule.teachers() if not self.selected_object.has_teacher(o)]
                text = "Add Teacher"
            case ResourceType.stream:
                items = [o for o in self.presenter.schedule.streams() if not self.selected_object.has_stream(o)]
                text = "Add Stream"
            case _:
                items = []
                text = "Add generic item"

        sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label=text)

        # need to define new sub in each iteration, because otherwise the closures will get messed up
        # ... do NOT use lambda's in a loop, we need to bind the individual 'item' in loop rather than its last value
        # ... https://stackoverflow.com/questions/54288926/python-loops-and-closures
        for item in items:
            def f(item_closure= item):
                return  self.presenter.assign_selected_to_parent(self.selected_object, item_closure,
                                                                                               self.tree_id)
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label=str(item), command=f))
        menu_list.append(sub_menu)

    # ------------------------------------------------------------------------------------------------------------
    def _sub_menu_remove_items(self, menu_list: list[MenuItem], view: ResourceType):
        match view:
            case ResourceType.lab:
                items = [o for o in self.presenter.schedule.labs() if self.selected_object.has_lab(o)]
                text = "Remove Lab"
            case ResourceType.teacher:
                items = [o for o in self.presenter.schedule.teachers() if self.selected_object.has_teacher(o)]
                text = "Remove Teacher"
            case ResourceType.stream:
                items = [o for o in self.presenter.schedule.streams() if not self.selected_object.has_stream(o)]
                text = "Remove Stream"
            case _:
                items = []
                text = "Remove generic item"

        sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label=text)

        # ... do NOT use lambda's in a loop, we need to bind the individual 'item' in loop rather than its last value
        # ... or use partials
        # ... https://stackoverflow.com/questions/54288926/python-loops-and-closures
        for item in items:
            def f(item_closure=item):
                return self.presenter.remove_selected_from_parent(self.selected_object, item_closure,
                                                                self.tree_id)

            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label=str(item),
                                        command=f))
        menu_list.append(sub_menu)

    # ------------------------------------------------------------------------------------------------------------
    def _remove_all_items(self, menu_list: list[MenuItem], parent_type):
        sub_menu = MenuItem(menu_type=MenuType.Cascade, tear_off=False, label="Remove All")

        # NOTE: do not put the following in a loop, because the closures won't work properly if you do.
        #       If you don't know what a closure is... https://en.wikipedia.org/wiki/Closure_(computer_programming)
        if parent_type == "course":
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="sections",
                                        command=lambda *_: self.presenter.remove_all_types_from_selected_object("section",
                                                                                                           self.selected_object,
                                                                                                           self.tree_id)
                                        )
                           )

        if parent_type == "section":
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="class times",
                                        command=lambda *_: self.presenter.remove_all_types_from_selected_object("block",
                                                                                                           self.selected_object,
                                                                                                           self.tree_id)
                                        )
                           )

        if parent_type == "course" or parent_type == "section":
            sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="streams",
                                        command=lambda *_: self.presenter.remove_all_types_from_selected_object("stream",
                                                                                                           self.selected_object,
                                                                                                           self.tree_id)
                                        )
                               )
        sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="labs",
                                    command=lambda *_: self.presenter.remove_all_types_from_selected_object("lab",
                                                                                                       self.selected_object,
                                                                                                       self.tree_id)
                                    )
                           )
        sub_menu.add_child(MenuItem(menu_type=MenuType.Command, label="teachers",
                                    command=lambda *_: self.presenter.remove_all_types_from_selected_object("teacher",
                                                                                                       self.selected_object,
                                                                                                       self.tree_id)
                                    )
                           )
        menu_list.append(sub_menu)


# ====================================================================================================================
# Creates all the pop menu items, and their sub-menus if required
# ... each menu type will then call the appropriate 'presenter' code that will manage the modifications to the
#     tree/list menus in the EditCourse gui
# ====================================================================================================================
class CreateResourcePopupMenuActions:
    """Creates all the pop menu items, dependent on the selected object, and their sub-menus if required

        Each menu type will then call the appropriate 'presenter' code that will manage the modifications to the
        tree/list menus in the EditCourse gui
    """
    def __init__(self, presenter: EditCourses, schedule: Schedule, resource_type:ResourceType, resource: Lab|Stream|Teacher):
        """
        :param presenter: The presenter that is handling all the logic
        :param resource_type
        :param resource: The object that is the target of this menu
        """
        self.presenter = presenter
        self.resource_type = resource_type
        self.resource = resource
        self.schedule = schedule

    # ================================================================================================================
    # Create pop up menu based on the selected object
    # ================================================================================================================
    def create_resource_popup_menus(self):
        """create popup menus for trees

        menus are dynamic, depending on the current schedule, and what tree item was selected
        """


        # ------------------------------------------------------------------------------------------------------------
        # create a menu for entire friggin course schedule (teacher and labs)
        # ------------------------------------------------------------------------------------------------------------
        menu_course = []
        if self.resource_type != ResourceType.stream:

            for course in self.schedule.courses():
                menu_section = [MenuItem(label=course.number, menu_type=MenuType.Command,
                                         command=partial(self._add_all_sections, self.resource, course))]

                for section in course.sections():
                    menu_block = [MenuItem(label=str(section), menu_type=MenuType.Command,
                                           command=partial(self._add_all_blocks, self.resource, course,
                                                           section))]

                    for block in section.blocks():
                        menu_block.append(MenuItem(label=str(block), menu_type=MenuType.Command,
                                                   command=partial(self._add_course_section_block, self.resource, course, section, block )))
                    menu_section.append(MenuItem(label=str(section), menu_type=MenuType.Cascade,
                                                 children=menu_block))
                menu_course.append(MenuItem(label=course.number, menu_type=MenuType.Cascade, children=menu_section))
            menu_list: list[MenuItem] = [MenuItem(label="Add to Course ...", menu_type=MenuType.Cascade, children=menu_course),]
        else:

            for course in self.schedule.courses():
                menu_section = []

                for section in course.sections():
                    menu_section.append(MenuItem(label=str(section), menu_type=MenuType.Command,
                                           command=partial(self._add_all_blocks, self.resource, course,
                                                           section)))
                menu_course.append(MenuItem(label=course.number, menu_type=MenuType.Cascade, children=menu_section))

            menu_list: list[MenuItem] = [
                MenuItem(label="Add to Course ...", menu_type=MenuType.Cascade, children=menu_course), ]

        return menu_list

    # ================================================================================================================
    # Private methods that create the MenuList items
    # ================================================================================================================

    def _add_all_sections(self, resource, course):
        self.presenter.assign_selected_to_parent(selected=resource, parent=course)

    def _add_all_blocks(self, resource, __course, section):
        self.presenter.assign_selected_to_parent(selected=resource, parent=section)

    def _add_course_section_block(self, resource, __course, __section, block):
        self.presenter.assign_selected_to_parent(selected=resource, parent=block)

