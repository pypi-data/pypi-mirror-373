"""
# ============================================================================
# Gathers info for main menus and toolbars for scheduler, and gives them default commands
# - to set the commands, use methods 'set_menu_event_handler'
#
# NOTE: this does not actually create the gui menu, it just gathers the info
# ============================================================================
"""
from __future__ import annotations

from functools import partial
from typing import Callable, Literal, get_args
from ..gui_generics.menu_and_toolbars import MenuItem, MenuType, ToolbarItem
from ..model import SemesterType

MAIN_MENU_EVENT_HANDLER_NAMES_ALLOCATION = Literal[
    "file_new",
    "file_open",
    "file_save",
    "file_save_as",
    "file_exit",
    "auto_save",
]


MAIN_MENU_EVENT_HANDLERS_ALLOCATION: dict[MAIN_MENU_EVENT_HANDLER_NAMES_ALLOCATION, Callable[[SemesterType], None]] = {}
for event_name in get_args(MAIN_MENU_EVENT_HANDLER_NAMES_ALLOCATION):
    MAIN_MENU_EVENT_HANDLERS_ALLOCATION[event_name] = lambda semester: print(f"'{event_name}' selected. ")


def set_menu_event_handler_allocation(name: MAIN_MENU_EVENT_HANDLER_NAMES_ALLOCATION,
                                      handler: Callable[[SemesterType], None]):
    MAIN_MENU_EVENT_HANDLERS_ALLOCATION[name] = handler


def main_menu_allocation(semesters:list[SemesterType]) -> tuple[list[str], dict[str, ToolbarItem], list[MenuItem]]:

    menu = list()
    # -----------------------------------------------------------------------------------------
    # File menu
    # -----------------------------------------------------------------------------------------
    file_menu = MenuItem(name='file', menu_type=MenuType.Cascade, label='File')
    for semester in semesters:
        file_menu.add_child(MenuItem(name=f"new_{semester.name}", menu_type=MenuType.Command,
                                 label=f'New {semester.name} Schedule',
                                 command=partial( MAIN_MENU_EVENT_HANDLERS_ALLOCATION["file_new"],semester)
                                 )
                        )
        file_menu.add_child(MenuItem(name=f'open_{semester.name}', menu_type=MenuType.Command,
                                     label=f'Open {semester.name} Schedule',
                                     command=partial( MAIN_MENU_EVENT_HANDLERS_ALLOCATION["file_open"],semester)
                                     )
                            )

        file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(name=f'save', menu_type=MenuType.Command,
                                 label=f'Save Schedule',
                                 command=partial( MAIN_MENU_EVENT_HANDLERS_ALLOCATION["file_save"],None)
                                 )
                        )
    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                 label='Exit',
                                 accelerator='Ctrl-e',
                                 command=partial( MAIN_MENU_EVENT_HANDLERS_ALLOCATION["file_exit"],None)
                                 )
                        )
    # -----------------------------------------------------------------------------------------
    # Auto Save - coding is in the main-tk
    # -----------------------------------------------------------------------------------------



    # -----------------------------------------------------------------------------------------
    # _toolbar
    # -----------------------------------------------------------------------------------------
    toolbar_info = dict()
    toolbar_order = []

    # return list of top level menu items
    menu.append(file_menu)

    return toolbar_order, toolbar_info, menu
