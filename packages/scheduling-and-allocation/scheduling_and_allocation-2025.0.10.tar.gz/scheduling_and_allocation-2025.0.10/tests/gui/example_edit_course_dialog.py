from tkinter import *

from src.scheduling_and_allocation.gui_dialogs.edit_course_dialog_tk import EditCourseDialogTk
from src.scheduling_and_allocation.model import Schedule, Course, Section, WeekDay, SemesterType

mw=Tk()
frame = Frame(mw)
frame.pack()
mw.geometry("400x400")

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

# courses
c_001:Course = schedule.add_update_course("001", "Basket Weaving", SemesterType.fall)
s_001_1:Section = c_001.add_section("1", section_id=1)
s_001_1.add_stream(st1)
b_001_1_1 = s_001_1.add_block(WeekDay.Monday,8)
b_001_1_2 = s_001_1.add_block(WeekDay.Monday, 10)
b_001_1_1.add_teacher(t1)
b_001_1_2.add_teacher(t1)
b_001_1_1.add_lab(l1)
b_001_1_2.add_lab(l1)

s_001_2 = c_001.add_section("2", section_id=2)
s_001_2.add_stream(st2)
b_001_2_1 = s_001_2.add_block(WeekDay.Tuesday, 8)
b_001_2_2 = s_001_2.add_block(WeekDay.Tuesday, 10)
b_001_2_1.add_teacher(t2)
b_001_2_2.add_teacher(t3)
b_001_2_1.add_lab(l2)
b_001_2_2.add_lab(l3)


def go_edit():

    title = f"{s_001_1.course.name} ({s_001_1.hours} hrs)"
    text = s_001_1.title
    block_data = []

    if len(c_001.sections()) != 0:
        for b in c_001.sections()[0].blocks():
            block_data.append( (b.day.name, str(b.start), str(b.duration)))
    db = EditCourseDialogTk(frame,'edit',
                            course_number = c_001.number,
                            existing_course_numbers= [c_001.number],
                            course_name = c_001.name,
                            course_hours = s_001_1.course.hours_per_week,
                            num_sections= len(c_001.sections()),


                             assigned_teachers =[t1, t2, t3],
                             non_assigned_teachers = [t4],
                             assigned_labs = [l2],
                             non_assigned_labs = [l1, l3, l4],
                             current_blocks= block_data,
                             apply_changes=schedule.add_edit_course,
                            )

def go_add():
    pass
    block_data = []

    if len(c_001.sections()) != 0:
        for b in c_001.sections()[0].blocks():
            block_data.append( (b.day.name, str(b.start), str(b.duration)))
    db = EditCourseDialogTk(frame,'add',
                            course_number = c_001.number,
                            existing_course_numbers= [c_001.number],
                            course_name = c_001.name,
                            course_hours = s_001_1.course.hours_per_week,
                            num_sections= len(c_001.sections()),


                             assigned_teachers =[t1, t2, t3],
                             non_assigned_teachers = [t4],
                             assigned_labs = [l2],
                             non_assigned_labs = [l1, l3, l4],
                             current_blocks= block_data,
                             apply_changes=schedule.add_edit_course,
                            )

Button(frame, text="Edit Course", command=go_edit).pack()
Button(frame, text="Add Course", command=go_add).pack()
mw.mainloop()