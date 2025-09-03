from dataclasses import dataclass
from tkinter import *

from src.scheduling_and_allocation.gui_pages.view_canvas_tk import ViewCanvasTk
from src.scheduling_and_allocation.model import ResourceType

mw = Tk()
cn = Canvas(mw, height=700, width=700, background="white")
cn.pack()

vc = ViewCanvasTk(cn)

@dataclass
class ExampleBlock:
    start_time: float = 8.0
    day: int = 1
    duration: float = 1.5
    resource_type: ResourceType = ResourceType.teacher
bl1 = ExampleBlock()
bl2 = ExampleBlock(start_time=9.5, day=1)
vc.draw_block(ResourceType.teacher, bl1.day, bl1.start_time, bl1.duration,"Block1","g01",movable=True)
vc.draw_block(ResourceType.teacher, bl2.day, bl2.start_time, bl2.duration,"Block2","g02", movable=True)


mw.mainloop()

