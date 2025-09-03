from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from functools import partial
from typing import Callable, Optional, ClassVar, Any
from enum import Enum

import re
from os import path
try:
    from ..modified_tk import FindImages, ToolBar, TkColours
except ImportError:
    from src.scheduling_and_allocation.modified_tk import FindImages, ToolBar, TkColours

# =====================================================================================================================
# Valid Menu type items
# =====================================================================================================================
class MenuType(Enum):
    """ensure that the MenuItem resource_type is valid"""
    Command = 'command'
    Separator = 'separator'
    Radiobutton = 'radiobutton'
    Checkbutton = 'checkbutton'
    Cascade = 'cascade'


# =====================================================================================================================
# A class to define a single menu item (menu items can have children though)
# =====================================================================================================================
@dataclass
class MenuItem:
    """Define a menu_item (resource_type, options, etc)"""

    # a dictionary of all menu_items that were created.  Key is the 'name' property of the menu item
    all_menu_items: ClassVar[dict[str, MenuItem]] = {}

    # -----------------------------------------------------------------------------------------------------------------
    # properties
    # -----------------------------------------------------------------------------------------------------------------
    label: str = ""                             # what is shown to the user
    tear_off: bool = 0                          # menu can be detached from window?
    menu_type: MenuType = MenuType.Command      # type of menu item
    name: str = ""                              # unique name to define your menu item
    accelerator: str = ""                       # just a string that defines short-cuts... JUST A STRING!
    command: Callable = lambda *_: None         # which function to call when menu item is clicked
    children: list[MenuItem] = field(default_factory=list)  # any kids?
    underline: bool = False                     # underline a character based on accelerator
    bool_variable: bool = True                  # if a checkbutton type, what is the default value

    # -----------------------------------------------------------------------------------------------------------------
    # can't remember what this is for... too scared to delete it
    # -----------------------------------------------------------------------------------------------------------------
    def __post_init__(self):
        MenuItem.all_menu_items[self.name] = self

    # -----------------------------------------------------------------------------------------------------------------
    # define which options are valid depending on the menu item type
    # -----------------------------------------------------------------------------------------------------------------
    def options_dict(self) -> dict[str, str]:
        """return a dictionary of options, appropriate to the menu resource_type"""
        options = dict()
        if self.menu_type != MenuType.Separator:
            options = {'label': self.label, 'accelerator': self.accelerator,
                       'command': self.command, 'underline': self.underline}
        return options

    # -----------------------------------------------------------------------------------------------------------------
    # add a child to this menu item
    # -----------------------------------------------------------------------------------------------------------------
    def add_child(self, menu_item: MenuItem):
        """add a new menu item as a sub-child of on existing menu item"""

        # if self is not a cascade resource_type menu item, then it should not have
        # children (i.e. non-cascade menu-items should not be parents)
        if self.menu_type != MenuType.Cascade:
            msg = f"Menu '{self.name}' is of resource_type '{self.menu_type}' and cannot support children"
            raise TypeError(msg)

        # procreate
        self.children.append(menu_item)


# =====================================================================================================================
# A tool bar item (names, commands, hints, etc)
# =====================================================================================================================
@dataclass
class ToolbarItem:
    """data defining a _toolbar item, command, hint, image, etc"""
    command: Optional[Callable] = lambda *_: None
    hint: Optional[str] = None
    image: Optional[str] = None


# =====================================================================================================================
# Generate a menu
# =====================================================================================================================
def generate_menu(mw, menu_details: Optional[list[MenuItem]], parent: tk.Menu):
    """
    Create a gui menu bar based off of the menu_details
    :param mw: main window to attach the menu to
    :param menu_details: list of menu items
    :param parent: the tk Menu (you have to have one of these first before you can attach menu items)
    :return:
    """

    if menu_details is None:
        return

    for menu_item in menu_details:

        # accelerator depends on window type
        if menu_item.accelerator:
            menu_item.accelerator = menu_item.accelerator.replace("Ctrl", "Control")
            if mw.tk.call('tk', 'windowingsystem') == 'aqua':
                if menu_item.accelerator:
                    menu_item.accelerator = menu_item.accelerator.replace("Control", "Command")

        # Cascading menu
        if menu_item.menu_type == MenuType.Cascade:
            new_menu = tk.Menu(parent, tearoff=menu_item.tear_off)
            generate_menu(mw, menu_item.children, new_menu)
            parent.add_cascade(label=menu_item.label, menu=new_menu)

        # simple separator
        elif menu_item.menu_type == MenuType.Separator:
            parent.add_separator()

        # button or command or radiobutton or...
        elif menu_item.menu_type == MenuType.Checkbutton:
            options: dict = menu_item.options_dict()
            options["variable"] = tk.BooleanVar(value= menu_item.bool_variable)
            options["command"] = partial(options["command"], options["variable"])
            parent.add_checkbutton(**options)

        else:
            options: dict = menu_item.options_dict()
            parent.add(menu_item.menu_type.value, **options)

        # bind accelerators
        if menu_item.accelerator:
            x = re.match(r'Control-(.)', menu_item.accelerator, re.RegexFlag.IGNORECASE)
            if x:
                binding = f"<Control-{x.group(1).lower()}>"
                mw.bind(binding, menu_item.command)

            x = re.match(r'Command-(.)', menu_item.accelerator, re.RegexFlag.IGNORECASE)
            if x:
                binding = f"<Command-{x.group(1).lower()}>"
                mw.bind(binding, menu_item.command)


# =====================================================================================================================
# Make a toolbar ( a bunch of buttons in a frame)
# =====================================================================================================================
def make_toolbar(mw, button_names: list[str], actions: dict[str:ToolbarItem],
                 colours: TkColours = TkColours(), **kwargs) -> ToolBar:
    """
    Create a toolbar described by the actions
    :param mw: the main window, or top level object, that the toolbar sits in
    :param button_names: name of the buttons
    :param actions: list of Toolbar items (name/tooltip/function)
    :param colours: default colours
    :param kwargs: any extra arguments that will passed to the toolbar widget
    :return:
    """
    image_dir = FindImages.get_image_dir()
    toolbar = ToolBar(mw, colours, **kwargs)

    # create all the buttons
    for button_name in button_names:
        if not button_name:  # if button not defined, insert a divider
            toolbar.bar()
        else:
            image = actions[button_name].image if actions[button_name].image else f'{button_name}.gif'
            full_image_path = path.join(image_dir, image)
            toolbar.add(
                name=button_name,
                image=full_image_path,
                command=actions[button_name].command,
                hint=actions[button_name].hint,
            )
    return toolbar
