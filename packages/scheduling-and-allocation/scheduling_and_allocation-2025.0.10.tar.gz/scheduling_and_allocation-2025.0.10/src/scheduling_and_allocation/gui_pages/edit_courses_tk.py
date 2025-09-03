"""
# ============================================================================
# This module contains all the gui code that is related to the course tree view
# - There is a course tree
# - There is three lists of resources (for drag'n'dropping onto the tree)
#
# EVENT HANDLERS
#
#   double-click: edit the selected tree object
#       handler_tree_edit(selected_obj, parent_obj, tree_id, parent_id)
#
#   button: create a new course (button)
#       handler_new_course()
#
#   tree right-click: return drop-down menu info
#       handler_tree_create_popup(selected_obj, parent_obj, tree_id, parent_id)->list[MenuItem]
#
#   resource right-click: return drop-down menu info
#       handler_resource_create_menu(resource_type, object)->list[MenuItem]
#
#   teacher double-click:
#       handler_show_teacher_stat(teacher)
#
#   resource object being dragged over tree, return bool to indicate valid drop site
#       handler_drag_resource(resource_type, tree_object) -> bool
#
#   resource object dropped on tree object
#       handler_drop_resource(resource_obj, tree_obj, tree_id)
#
# ============================================================================
"""
from __future__ import annotations

import time
import tkinter as tk
from functools import partial
from tkinter.messagebox import showinfo
from typing import Callable, Any, TYPE_CHECKING
import re

from ..modified_tk import Scrolled
from ..modified_tk import AdvancedTreeview
from ..modified_tk import DragNDropManager
from ..modified_tk.InitGuiFontsAndColours import get_fonts_and_colours, set_default_fonts
from ..gui_generics.menu_and_toolbars import MenuItem, MenuType, generate_menu
from ..model import ResourceType

if TYPE_CHECKING:
    from ..model import Teacher, Lab, Stream

    RESOURCE_OBJECT = [Teacher | Lab | Stream]
    TREE_OBJECT = Any


# ====================================================================================================================
# default stuff
# ====================================================================================================================
def _default_menu(obj, parent_obj, iid, parent_iid) -> list[MenuItem]:
    menu = MenuItem(name=str(obj), label=str(obj), menu_type=MenuType.Command, command=lambda: None)
    return [menu, ]


def _default_resource_menu(resource_type: ResourceType, obj) -> list[MenuItem]:
    menu_title = MenuItem(name=str(resource_type), label=str(resource_type), menu_type=MenuType.Command,
                          command=lambda: None)
    menu = MenuItem(name=str(obj), label=str(obj), menu_type=MenuType.Command, command=lambda: None)
    return [menu_title, menu]


# ====================================================================================================================
# Edit courses GUI_Pages
# ====================================================================================================================

class EditCoursesTk:
    """A page that allows user to edit courses, assign resources, sections, blocks, etc
    :param frame: the frame to hold all the gui elements

    """

    # -----------------------------------------------------------------------------------------------------------------
    # constructor
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, frame: tk.Frame):
        """create the EditCourse page
        :param frame: container object for the gui stuff
        """
        self.frame = frame

        # setup fonts if they have not already been set up
        self.colours, self.fonts = get_fonts_and_colours()
        if self.fonts is None:
            self.colours, self.fonts = set_default_fonts(self.frame.winfo_toplevel())

        # call backs (should be defined by presenter)
        self.handler_tree_edit: Callable[[TREE_OBJECT, TREE_OBJECT, str, str], None] \
            = lambda obj, parent_obj, tree_id, parent_id: print(f"Edit {str(obj)}")
        self.handler_new_course: Callable[[], None] = lambda: None
        self.handler_tree_create_popup: Callable[[TREE_OBJECT, TREE_OBJECT, str, str], list[MenuItem]] = _default_menu
        self.handler_resource_create_menu: Callable[
            [ResourceType, RESOURCE_OBJECT], list[MenuItem]] = _default_resource_menu
        self.handler_show_teacher_stat: Callable[[RESOURCE_OBJECT], None] = lambda obj: print(f"Teacher stat: {obj}")
        self.handler_drag_resource: Callable[[ResourceType, TREE_OBJECT], bool] = \
            lambda resource_type, target_obj: True
        self.handler_drop_resource: Callable[[ RESOURCE_OBJECT, TREE_OBJECT, str], None] = \
            lambda source_obj, target_obj, tree_id: None

        # create lists to keep track of widgets and objects for all resources
        # (teachers/streams/labs)
        self.resource_Listbox: dict[ResourceType, tk.Listbox] = dict()
        self.resource_objects: dict[ResourceType, list[RESOURCE_OBJECT]] = dict()
        for rt in ResourceType:
            self.resource_objects[rt] = list()

        # remove anything that is already in the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # make panels
        right_panel = tk.Frame(frame)
        right_panel.grid(row=0, column=1, sticky='nsew')
        left_panel = tk.Frame(frame)
        left_panel.grid(row=0, column=0, sticky='nsew')

        # calculate min_width of left panel based on screen size
        width = 975
        height = 800
        if match:= re.match(r"^=?(\d+)x(\d+)?([+-]\d+[+-]\d+)?$", frame.winfo_toplevel().geometry()):
            width, height, _ = match.groups()

        # relative weights etc. to widths
        frame.grid_columnconfigure(0, minsize=int(0.5 * int(width)), weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # make the gui contents
        self.course_ttkTreeView = self._make_treeview(left_panel)
        self._make_resource_list_widgets(right_panel)
        self._make_button_row(right_panel)

        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=10, minsize=int(0.45 * int(height)))
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_rowconfigure(3, weight=0)


        # is the user hovering over a tree element when dragging a resource?
        self._hover_time = None
        self._hover_tree_element = None


    # -----------------------------------------------------------------------------------------------------------------
    # Public Methods for manipulating the tree object
    # -----------------------------------------------------------------------------------------------------------------
    def update_resource_type_objects(self, resource_type: ResourceType, objs: tuple[RESOURCE_OBJECT, ...]):
        """
        Updates the Listbox widget with Labs/Teachers/Streams string representations
        :param resource_type: what view resource_type are you updating?
        :param objs: all the objects that you want in the list
        """
        widget: tk.Listbox = self.resource_Listbox[resource_type]
        widget.delete(0, 'end')
        self.resource_objects[resource_type].clear()
        for obj in objs:
            widget.insert('end', str(obj))
            self.resource_objects[resource_type].append(obj)

    def add_tree_item(self, parent_id: str, name: str, child: TREE_OBJECT, hide: bool = True) -> str:
        """add an object to the tree, as a child of the parent
        :param parent_id: an existing tree object that will become the parent of this new child
        :param name: the name of
        :param child: the child
        :param hide: hide the children?
        :return: The id of the tree element
        """
        tag = "bold" if parent_id is None or parent_id == "" else "normal"
        parent_id = "" if parent_id is None else parent_id
        iid = self.course_ttkTreeView.insert_sorted(parent_id, child, text=name, tag=tag)
        self.course_ttkTreeView.after(20,lambda *_: self.course_ttkTreeView.item(parent_id, open=not hide))
        return iid

    def remove_tree_item(self, tree_iid: str):
        """remove an item from the tree
        :param tree_iid: the id of the item to be removed"""
        return self.course_ttkTreeView.delete(tree_iid)

    def remove_tree_item_children(self, tree_iid: str):
        """remove all children from the specified parent
        :param tree_iid: the id of the parent whose items are to be removed"""
        for child in self.course_ttkTreeView.get_children(tree_iid):
            self.course_ttkTreeView.delete(child)

    def update_tree_text(self, tree_iid: str, text: str):
        if self.course_ttkTreeView.exists(tree_iid):
            self.course_ttkTreeView.item(tree_iid, text=text)

    def clear_tree(self):
        """clear the tree of all items"""
        for child in self.course_ttkTreeView.get_children():
            self.course_ttkTreeView.delete(child)

    # -----------------------------------------------------------------------------------------------------------------
    # Resource Event - pop-up menu for teacher/stream/lab
    # -----------------------------------------------------------------------------------------------------------------
    def _cmd_show_resource_type_menu(self, resource_type: ResourceType, e: tk.Event):
        """bound method for right click on resource list
                calls handler: handler_resource_create_menu
        """

        if resource_type is ResourceType.none:
            return
        widget: tk.Listbox = self.resource_Listbox[resource_type]
        index = widget.nearest(e.y)
        widget.select_clear(0, 'end')
        widget.selection_set(index, index)
        obj = self.resource_objects[resource_type][index]

        # get menu info from callback routine
        menu = tk.Menu(self.frame.winfo_toplevel(), tearoff=0)
        menu_details = self.handler_resource_create_menu(resource_type, obj)
        generate_menu(self.frame.winfo_toplevel(), menu_details, menu)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    # -----------------------------------------------------------------------------------------------------------------
    # Resource Event - double click teacher on resource view
    # -----------------------------------------------------------------------------------------------------------------
    def _cmd_double_click_teacher(self, e: tk.Event):
        """bound method for double-click on a teacher object,
                calls handler: handler_show_teacher_stat
        """
        widget: tk.Listbox = self.resource_Listbox[ResourceType.teacher]
        index = widget.nearest(e.y)
        widget.select_clear(0, 'end')
        widget.selection_set(index, index)
        obj = self.resource_objects[ResourceType.teacher][index]
        self.handler_show_teacher_stat(obj)

    # -----------------------------------------------------------------------------------------------------------------
    # Tree Event - show editor for selected element (course, stream, block)
    # -----------------------------------------------------------------------------------------------------------------
    def _cmd_edit_selection(self, *_):
        """bound method for <keypress Enter> or <double click> on treeview, or clicking 'Edit Selection' button
                calls handler: handler_tree_edit
        """

        # get the tree selected item
        iid_list = self.course_ttkTreeView.selection()
        if not iid_list:
            return
        obj = self.course_ttkTreeView.get_obj_from_id(iid_list[0])
        iid = iid_list[0]
        parent_iid = self.course_ttkTreeView.parent(iid)

        # get object associated with this item
        obj = self.course_ttkTreeView.get_obj_from_id(iid)
        parent_obj = self.course_ttkTreeView.get_obj_from_id(parent_iid)

        self.handler_tree_edit(obj,parent_obj,  iid, parent_iid)

    # -----------------------------------------------------------------------------------------------------------------
    # Tree Events - pop-up menu for course/stream/block
    # -----------------------------------------------------------------------------------------------------------------
    def _cmd_show_tree_menu(self, e: tk.Event):
        """bound method for right click on tree item
                calls handler: handler_tree_create_popup
        """

        tv = self.course_ttkTreeView

        # which item was selected?
        iid = tv.identify_row(e.y)
        if not iid:
            return
        tv.selection_set(iid)
        parent_iid = tv.parent(iid)

        # get object associated with this item
        obj = tv.get_obj_from_id(iid)
        parent_obj = tv.get_obj_from_id(parent_iid)

        # get menu info from callback routine
        menu = tk.Menu(self.frame.winfo_toplevel(), tearoff=0)
        menu_details = self.handler_tree_create_popup(obj, parent_obj, iid, parent_iid)
        generate_menu(self.frame.winfo_toplevel(), menu_details, menu)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    # -----------------------------------------------------------------------------------------------------------------
    # Event Drag 'n' Drop start
    # -----------------------------------------------------------------------------------------------------------------
    def _resource_on_start_drag(self, e: tk.Event, info_data: dict) -> str:
        """bound event if a resource widget is about to be dragged from a resource listbox"""

        # what resource type is it?
        info_data["resource_type"] = ResourceType.none
        lb: tk.Listbox = e.widget
        rtype: ResourceType = ResourceType.none
        for rt in self.resource_Listbox:
            if lb == self.resource_Listbox[rt]:
                rtype = rt

        # select the nearest item in the list
        index = lb.nearest(e.y)
        lb.select_clear(0, 'end')
        lb.selection_set(index, index)

        # save some info for later use
        info_data["source_obj"] = self.resource_objects[rtype][index]
        info_data["resource_type"] = rtype

        # return string to be used in the drag indicator
        return lb.get(index)

    # -----------------------------------------------------------------------------------------------------------------
    # Event Drag 'n' Drop moving
    # -----------------------------------------------------------------------------------------------------------------
    def _hovering_response(self, iid):
        tv = self.course_ttkTreeView
        tv.item(iid, open=True)

    def _resource_on_drag(self, e: tk.Event, info_data: dict, target: tk.Widget) -> bool:
        """bound event while the resource list object is being dragged around
                calls handler: handler_drag_resource"""

        tv = self.course_ttkTreeView
        for s_iid in tv.selection():
            tv.selection_remove(s_iid)

        tv_y_pos = e.y_root - tv.winfo_rooty()

        # a resource widget can only be dropped on the self.course_ttkTreeView
        if target == tv:

            # get position of mouse within the treeview widget, and identify item in treeview under mouse
            tv_y_pos = e.y_root - tv.winfo_rooty()
            iid = tv.identify_row(tv_y_pos)

            # if we have a valid id...
            if iid:
                target_obj: TREE_OBJECT = tv.get_obj_from_id(iid)
                resource_type: ResourceType = info_data["resource_type"]

                # check with 'user' if this is a valid item for dropping source onto target
                if self.handler_drag_resource(resource_type, target_obj):

                    # if we are hovering, then open the tree element
                    if (self._hover_time is not None and self._hover_tree_element is not None
                            and self._hover_tree_element != iid):
                        self.frame.after_cancel(self._hover_time)

                    if self._hover_tree_element is None or self._hover_tree_element != iid:
                        self._hover_tree_element = iid
                        self._hover_time = self.frame.after(500, self._hovering_response, iid)

                    info_data["target_obj"] = target_obj
                    info_data["tree_id"] = iid
                    tv.selection_set(iid)
                    return True

        # if mouse above or below tv view, then force scroll, but have a time delay to make it more
        # manageable
        elif tv_y_pos < 0:
            if info_data.get('start_time', None) is not None and time.time() - info_data['start_time'] < 0.05:
                return False
            info_data['start_time'] = time.time()
            n1,n2 = self.tree_scrolled.yview_widget()
            self.tree_scrolled.yview_moveto(max(7/8*n1 - 1/8*n2,0))
        elif tv_y_pos > 0:
            if info_data.get('start_time', None) is not None and time.time() - info_data['start_time'] < 0.05:
                return False
            info_data['start_time'] = time.time()
            n1,n2 = self.tree_scrolled.yview_widget()
            self.tree_scrolled.yview_moveto(min(7/8*n1 + 1/8*n2,1))

        return False

    # -----------------------------------------------------------------------------------------------------------------
    # Event Drag 'n' Drop end
    # -----------------------------------------------------------------------------------------------------------------
    def _resource_on_drop(self, e: tk.Event, info_data: dict, target: tk.Widget):
        """bound event when a resource item is dropped
                calls handler: handler_drop_resource"""

        if self._resource_on_drag(e, info_data, target):
            target_obj: TREE_OBJECT = info_data["target_obj"]
            source_obj: RESOURCE_OBJECT = info_data["source_obj"]
            tree_id: str = info_data["tree_id"]
            self.handler_drop_resource(source_obj, target_obj, tree_id )
        if self._hover_time is not None:
            self.frame.after_cancel(self._hover_time)
        self._hover_time = None
        self._hover_tree_element = None

    # -----------------------------------------------------------------------------------------------------------------
    # Button Events - new course
    # -----------------------------------------------------------------------------------------------------------------
    def _new_course_btn_pressed(self, *_):
        """bound method for clicking 'new course' button
                calls handler: handler_new_course"""

        self.handler_new_course()

    # =================================================================================================================
    # Private Methods
    # =================================================================================================================

    def _make_treeview(self, left_panel: tk.Frame):
        """
        make tree representing all courses, sections, blocks, resource
        :param left_panel: where to put stuff
        """
        self.tree_scrolled: Scrolled = Scrolled(left_panel, 'AdvancedTreeview', scrollbars='se')
        self.tree_scrolled.pack(expand=1, fill='both', side='left')
        tv: AdvancedTreeview = self.tree_scrolled.widget
        tv.bind('<Double-1>', self._cmd_edit_selection)
        tv.bind('<Key-Return>', self._cmd_edit_selection)
        tv.tag_configure("bold", font=self.fonts.big)
        tv.tag_configure("normal", font=self.fonts.normal)

        # mac vs windows methods for getting pop up menus
        if self.frame.winfo_toplevel().tk.call('tk','windowingsystem') == 'aqua':
            tv.bind('<2>', self._cmd_show_tree_menu)
            tv.bind('<Control-1>', self._cmd_show_tree_menu)
        else:
            tv.bind('<3>', self._cmd_show_tree_menu)

        return tv

    def _make_resource_list_widgets(self, panel):
        """make a list widget for teachers/labs/streams"""

        # the scrolled method requires an empty frame, or else, it messes up.
        f = tk.Frame(panel)
        f.grid(column=0, stick='nsew', row=0)
        tk.Label(f, text="Teachers", font=self.fonts.bold).pack()
        sf = tk.Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='e')
        s.widget.bind('<Double-Button-1>', self._cmd_double_click_teacher)
        self.resource_Listbox[ResourceType.teacher] = s.widget

        f = tk.Frame(panel)
        f.grid(column=0, stick='nsew', row=1)
        tk.Label(f, text="Labs", font=self.fonts.bold).pack()
        sf = tk.Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='e')
        self.resource_Listbox[ResourceType.lab] = s.widget

        f = tk.Frame(panel)
        f.grid(column=0, stick='nsew', row=2)
        tk.Label(f, text="Streams", font=self.fonts.bold).pack()
        sf = tk.Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='e')
        self.resource_Listbox[ResourceType.stream] = s.widget

        # Set up binding for menus and dragging-n-dropping
        dm = DragNDropManager()

        for resource_type in ResourceType:
            if resource_type not in self.resource_Listbox:
                continue
            dm.add_draggable(self.resource_Listbox[resource_type],
                             on_start=self._resource_on_start_drag,
                             on_drop=self._resource_on_drop,
                             on_drag=self._resource_on_drag)

            # mac vs windows methods for getting pop up menus
            if self.frame.winfo_toplevel().tk.call('tk', 'windowingsystem') == 'aqua':
                self.resource_Listbox[resource_type].bind(
                    '<Button-2>',
                    partial(self._cmd_show_resource_type_menu, resource_type))
                self.resource_Listbox[resource_type].bind(
                    '<Control-1>',
                    partial(self._cmd_show_resource_type_menu, resource_type))
            else:
                self.resource_Listbox[resource_type].bind(
                    '<Button-3>',
                    partial(self._cmd_show_resource_type_menu, resource_type))

            self.resource_Listbox[resource_type].unbind('<Motion>')

    def _make_button_row(self, panel: tk.Frame):
        """make the button row for creating new courses, editing selections, etc"""
        button_row = tk.Frame(panel)
        button_row.grid(column=0, sticky='nsew', row=3)
        btn_new_course = tk.Button(button_row, text="New Course", width=11,
                                command=lambda: self._new_course_btn_pressed())
        btn_new_course.pack(side='left', ipadx=10)
        btn_edit_selection = tk.Button(button_row, text="Edit Selection", width=11,
                                    command=lambda: self._cmd_edit_selection())
        btn_edit_selection.pack(side='left', ipadx=10)

    # ================================================================================================================
    # show a message
    # ================================================================================================================
    def show_message(self, title: str, msg: str, detail: str = ""):
        showinfo(title=title, message=msg, detail=detail, icon='info')
