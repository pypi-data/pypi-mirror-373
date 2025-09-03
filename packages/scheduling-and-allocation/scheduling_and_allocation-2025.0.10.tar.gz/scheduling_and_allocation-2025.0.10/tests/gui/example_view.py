from dataclasses import dataclass
from tkinter import *
from typing import Optional

from src.scheduling_and_allocation.Utilities.id_generator import IdGenerator
from src.scheduling_and_allocation.gui_generics.menu_and_toolbars import MenuItem, MenuType
from src.scheduling_and_allocation.gui_pages.view_dynamic_tk import ViewDynamicTk
from src.scheduling_and_allocation.model import Lab, Stream, Teacher, ResourceType, Schedule, Block

mw = Tk()
frame = Frame(mw)
frame.pack(expand=1,fill='both')


RESOURCE = Lab | Stream | Teacher

_gui_block_ids = IdGenerator()

frame = Frame(mw)
frame.pack(expand=1, fill = 'both')
resource_type = ResourceType.teacher
schedule = Schedule("../unit_tests_presenter/silly_winter.csv")
gui_blocks: dict[str, Block] = {}
blocks: list[Block] = []

def draw_blocks():
    global blocks
    blocks = schedule.blocks()
    gui_blocks.clear()

    for block in blocks:
        gui_block_id: int = _gui_block_ids.get_new_id()
        gui_tag = f"gui_tag_{gui_block_id}"
        gui_blocks[gui_tag] = block

        view.draw_block(resource_type=resource_type,
                            day=block.day.value, start_time=block.start, duration=block.duration,
                            text=gui_tag,
                            gui_block_id=gui_tag,
                            movable=block.movable)
        view.colour_block(gui_tag, resource_type, block.movable, conflict=block.conflict)

def gui_block_is_moving(gui_id: str,  gui_block_day: float, gui_block_start_time: float):

    block: Block = gui_blocks.get(gui_id,None)
    block.start = gui_block_start_time
    block.snap_to_day(gui_block_day)
    block.snap_to_time()
    schedule.calculate_conflicts()
    for gui_tag, block in gui_blocks.items():
        view.colour_block(gui_tag, resource_type, is_movable=block.movable, conflict=block.conflict)

def gui_block_has_dropped(gui_id: str):
    print("block dropped")
    block: Block = gui_blocks.get(gui_id,None)
    view.move_gui_block(gui_id, block.day.value,block.start)


def tree_popup_menu( gui_id) -> Optional[list[MenuItem]]:
    menu_list: list[MenuItem] = [MenuItem(menu_type=MenuType.Command, label="Click me",
                                          command=lambda : print(f"menu for {gui_id}"))]
    return menu_list

# create the gui representation of the view
view = ViewDynamicTk( frame, "Testing View", ResourceType.teacher)

# Need to set handlers here, instead on constructor, so that it is easier for testing
view.get_popup_menu_handler = tree_popup_menu
view.refresh_blocks_handler = draw_blocks
view.on_closing_handler = lambda *_: print ("on closing")
view.double_click_block_handler = lambda x: print("double clicked",x)
view.gui_block_is_moving_handler = gui_block_is_moving
view.gui_block_has_dropped_handler = gui_block_has_dropped
view.undo_handler = lambda: print("undo")
view.redo_handler = lambda: print("redo")
view.draw()

mw.mainloop()