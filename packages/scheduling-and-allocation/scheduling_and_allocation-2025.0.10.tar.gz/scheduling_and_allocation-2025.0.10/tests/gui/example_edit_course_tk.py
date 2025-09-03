from tkinter import *
from tkinter import messagebox
from typing import Any

from src.scheduling_and_allocation.gui_generics.menu_and_toolbars import MenuItem, MenuType
from src.scheduling_and_allocation.gui_pages import EditCoursesTk
from src.scheduling_and_allocation.model import ResourceType


# ----------------------------------------------------------------------------
# generic objects for putting in listbox and trees
# ----------------------------------------------------------------------------
class Nothing:
    def __init__(self, a):
        self.a = a

    def checking(self):
        print(f"object: a = {self.a}")

    def __str__(self):
        return str(self.a)

    def __repr__(self):
        return str(self.a)

    def __lt__(self, other):
        return self.a < other.a


# ----------------------------------------------------------------------------
# methods for use in callback methods
# ----------------------------------------------------------------------------
def tree_menu(obj) -> list[MenuItem]:
    menu = MenuItem(name=str(obj),
                    label=f"Testing: {str(obj)}",
                    menu_type=MenuType.Command,
                    command=lambda: None)
    return [menu, ]


def resource_menu(resource_type: ResourceType, obj) -> list[MenuItem]:
    menu_title = MenuItem(name=str(resource_type),
                          label=f"Testing: {str(resource_type)}",
                          menu_type=MenuType.Command,
                          command=lambda: None)
    menu = MenuItem(name=str(obj),
                    label=f"Testing: {str(obj)}",
                    menu_type=MenuType.Command,
                    command=lambda: None)
    return [menu_title, menu]


def edit_dialog(obj: Any, parent_obj: Any, tree_id: str, parent_id: str):
    messagebox.showinfo(title="Testing", message=f"selected obj: {obj}\n"
                                                 f"parent obj: {parent_obj}\n"
                                                 f"tree id: {tree_id}\n"
                                                 f"parent id: {parent_id}")


def new_course_dialog():
    messagebox.showinfo(title="Testing", message="New Course dialog")


def teacher_stat_dialog(obj: Any):
    messagebox.showinfo(title="Testing", message=f"Teacher stat for {str(obj)}")


def valid_drop_site(resource_type: ResourceType, target: Any) -> bool:
    if str(target) == "Sandy":
        return False
    if str(target).startswith("P"):
        return False
    return True


def item_dropped(source: Any, target: Any, id):
    messagebox.showinfo(title="Testing",
                        message=f"'{str(source)}' dropped on '{str(target)}' tree id '{str(id)}'")


# ----------------------------------------------------------------------------
# setup for creating the EditCourseTk page
# ----------------------------------------------------------------------------
mw = Tk()
f = Frame(mw)
f.pack(expand=1, fill="both")

test_page = EditCoursesTk(f)
t1 = Nothing("Sandy")
t2 = Nothing("Bob")
t3 = Nothing("Sandy1")
t4 = Nothing("Bob1")
t5 = Nothing("Sandy2")
t6 = Nothing("Bob2")
t7 = Nothing("Sandy3")
t8 = Nothing("Bob3")
t9 = Nothing("Sandy4")
t10 = Nothing("Bob4")
t11 = Nothing("Sandy5")
t12 = Nothing("Bob5")
l1 = Nothing("P325")
l2 = Nothing("P322")
l3 = Nothing("P326")
l4 = Nothing("P323")
s1 = Nothing("1A")
s2 = Nothing("1B")
s3 = Nothing("2A")
s4 = Nothing("2B")
s5 = Nothing("3A")
s6 = Nothing("3B")

test_page.update_resource_type_objects(ResourceType.teacher, [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12])
test_page.update_resource_type_objects(ResourceType.stream, [s1, s2, s3, s4, s5, s6])
test_page.update_resource_type_objects(ResourceType.lab, [l1, l2, l3, l4])


c1 = Nothing("Operating Systems")
c1_id = test_page.add_tree_item("", str(c1), c1)
s1_id = test_page.add_tree_item(c1_id, f"Section 1 ({s1})", Nothing("Section 1"))
s2_id = test_page.add_tree_item(c1_id, f"Section 2 ({s2})", Nothing("Section 2"))
b1_id = test_page.add_tree_item(s1_id, "Block 1", Nothing("Block 1"))
b2_id = test_page.add_tree_item(s1_id, "Block 2", Nothing("Block 2"))
test_page.add_tree_item(b1_id, "Teacher: " + str(t1), t1)
test_page.add_tree_item(b1_id, "Lab: " + str(l1), l1)

# ----------------------------------------------------------------------------
# add all the callback routines
# ----------------------------------------------------------------------------
# call back routines
test_page.handler_tree_edit = edit_dialog
test_page.handler_new_course = new_course_dialog
test_page.handler_tree_create_popup = tree_menu
test_page.handler_resource_create_menu = resource_menu
test_page.handler_show_teacher_stat = teacher_stat_dialog
test_page.handler_drag_resource = valid_drop_site
test_page.handler_drop_resource = item_dropped

mw.mainloop()
