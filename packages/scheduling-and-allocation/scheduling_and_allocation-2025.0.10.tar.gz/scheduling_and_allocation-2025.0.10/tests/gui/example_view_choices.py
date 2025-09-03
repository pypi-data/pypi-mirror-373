from tkinter import *

from src.scheduling_and_allocation.gui_pages.views_controller_tk import ViewsControllerTk
from src.scheduling_and_allocation.model import Schedule, ResourceType, ConflictType

schedule = Schedule()

# teachers
t1 = schedule.add_update_teacher("Jane", "Doe", "0.25", teacher_id="1")
t2 = schedule.add_update_teacher("John", "Doe", teacher_id="2")
t3 = schedule.add_update_teacher("Babe", "Ruth", teacher_id="3")
t4 = schedule.add_update_teacher("Bugs", "Bunny", teacher_id="4")

# labs
l1 = schedule.add_update_lab("P107", "C-Lab")
l2 = schedule.add_update_lab("P322", "Mac Lab")
l3 = schedule.add_update_lab("P325")
l4 = schedule.add_update_lab("BH311", "Britain Hall")

# streams
st1 = schedule.add_update_stream("1A", "Math Stream")
st2 = schedule.add_update_stream("1B")

mw = Tk()
frame = Frame()
frame.pack(expand=1, fill="both")
resources:dict[ResourceType, list] = {ResourceType.teacher:[t1,t2,t3,t4,t1,t2,t3,t4,t1,t2,t3,t4,],
                           ResourceType.stream:[st1,st2],
                           ResourceType.lab:[l1,l2,l3,l4]}
vm = ViewsControllerTk(frame, resources, lambda *_:print(*_))
vm.set_button_colour(t1.number, ResourceType.teacher, ConflictType.TIME)
vm.set_button_colour(t2.number, ResourceType.teacher, ConflictType.NONE)
mw.mainloop()