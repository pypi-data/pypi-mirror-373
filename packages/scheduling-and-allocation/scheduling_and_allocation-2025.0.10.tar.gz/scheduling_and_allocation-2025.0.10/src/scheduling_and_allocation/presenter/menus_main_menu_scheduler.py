"""
# ============================================================================
# Gathers info for main menus and toolbars for scheduler, and gives them default commands
# - to set the commands, use methods 'set_menu_event_handler'
#
# NOTE: this does not actually create the gui menu, it just gathers the info
# ============================================================================
"""
from __future__ import annotations

from typing import Callable, Literal, get_args
from ..gui_generics.menu_and_toolbars import MenuItem, MenuType, ToolbarItem

MAIN_MENU_EVENT_HANDLER_NAMES = Literal[
    "file_new",
    "file_open",
    "file_save",
    "file_save_as",
    "file_exit",
    "print_pdf_teacher",
    "print_pdf_lab",
    "print_pdf_streams",
    "print_text",
    "print_latex_teacher",
    "print_latex_lab",
    "print_latex_streams",
    "print_registrar",
    "validate",
]



MAIN_MENU_EVENT_HANDLERS: dict[MAIN_MENU_EVENT_HANDLER_NAMES, Callable[[], None]] = {}
for event_name in get_args(MAIN_MENU_EVENT_HANDLER_NAMES):
    MAIN_MENU_EVENT_HANDLERS[event_name] = lambda: print(f"'{event_name}' selected. ")


def set_menu_event_handler(name: MAIN_MENU_EVENT_HANDLER_NAMES, handler: Callable[[], None]):
    MAIN_MENU_EVENT_HANDLERS[name] = handler


def main_menu() -> tuple[list[str], dict[str, ToolbarItem], list[MenuItem]]:
    menu = list()
    # NOTE:  if these events are bound, the first parameter passed will be the event.
    #        - we want to ignore these events, because the event handlers don't need this info
    # -----------------------------------------------------------------------------------------
    # File menu
    # -----------------------------------------------------------------------------------------
    file_menu = MenuItem(name='file', menu_type=MenuType.Cascade, label='File')
    file_menu.add_child(MenuItem(name='new', menu_type=MenuType.Command,
                                 label='New', accelerator='Control-n',
                                 command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_new"]()
                                 )
                        )
    file_menu.add_child(MenuItem(name='open', menu_type=MenuType.Command,
                                 label='Open', accelerator='Control-o',
                                 command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_open"]()
                                 )
                        )

    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(name='save', menu_type=MenuType.Command,
                                 label='Save',
                                 accelerator='Control-s',
                                 underline=False,
                                 command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_save"]()
                                 )
                        )
    file_menu.add_child(MenuItem(name='save_as', menu_type=MenuType.Command,
                                 label='Save As',
                                 command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_save_as"]()
                                 )
                        )

    file_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    file_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                 label='Validate',
                                 command=lambda *_: MAIN_MENU_EVENT_HANDLERS["validate"]()
                                 )
                        )
    file_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                 label='Exit',
                                 accelerator='Control-e',
                                 command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_exit"]()
                                 )
                        )

    # -----------------------------------------------------------------------------------------
    # Print menu
    # -----------------------------------------------------------------------------------------
    print_menu = MenuItem(name='print', menu_type=MenuType.Cascade, label='Print')
    pdf_menu = MenuItem(menu_type=MenuType.Cascade, label='PDF')
    latex_menu = MenuItem(menu_type=MenuType.Cascade, label='Latex')

    print_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                  label="Registrar's Output",
                                  command = lambda *_: MAIN_MENU_EVENT_HANDLERS["print_registrar"]()
                                  )
                         )

    print_menu.add_child(pdf_menu)
    print_menu.add_child(latex_menu)

    # pdf sub-menu
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                label='Teacher Schedules',
                                command=lambda *_: MAIN_MENU_EVENT_HANDLERS["print_pdf_teacher"]()
                                )
                       )
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                label='Lab Schedules',
                                command=lambda *_: MAIN_MENU_EVENT_HANDLERS["print_pdf_lab"]()
                                )
                       )
    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                label='Stream Schedules',
                                command=lambda *_: MAIN_MENU_EVENT_HANDLERS["print_pdf_streams"]()
                                )
                       )

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Separator))

    pdf_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                label='Text Output',
                                command=lambda *_: MAIN_MENU_EVENT_HANDLERS["print_text"]()
                                )
                       )

    # latex sub menu
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                  label='Teacher Schedules',
                                  command=lambda *_: MAIN_MENU_EVENT_HANDLERS["print_latex_teacher"]()
                                  )
                         )
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command,
                                  label='Lab Schedules',
                                  command=lambda *_: MAIN_MENU_EVENT_HANDLERS["print_latex_lab"]()
                                  )
                         )
    latex_menu.add_child(MenuItem(menu_type=MenuType.Command, label='Stream Schedules',
                                  command=lambda *_: MAIN_MENU_EVENT_HANDLERS["print_latex_streams"]()
                                  )
                         )
    # -----------------------------------------------------------------------------------------
    # Auto Save & Preferences - taken care of if main_tk
    # -----------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------
    # _toolbar
    # -----------------------------------------------------------------------------------------
    toolbar_info = dict()
    toolbar_info['new'] = ToolbarItem(command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_new"](),
                                      hint='Create new Schedule File')

    toolbar_info['open'] = ToolbarItem(command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_open"](),
                                       hint='Open Schedule File')

    toolbar_info['save'] = ToolbarItem(command=lambda *_: MAIN_MENU_EVENT_HANDLERS["file_save"](),
                                       hint='Save Schedule File')
    toolbar_order = ['new', 'open', '', 'save']

    # return list of top level menu items
    menu.append(file_menu)
    menu.append(print_menu)

    return toolbar_order, toolbar_info, menu
