import tkinter as tk
from functools import partial
from tkinter import ttk
import tkinter.messagebox as message_box

from ..gui_generics.number_validations import entry_float
from ..model import WeekDay


# ================================================================================================================
# class times?
# ================================================================================================================
def validate_class_times_equals_course_time(block_tk_variables, course_hours: float)-> bool:
    """
    Compares the total duration of all the blocks and compares to the hours assigned to the course
    :param block_tk_variables: list of tuples with string reprs of day, start_time, and duration
    :param course_hours: the hours assigned to this course
    :return: true if no blocks defined, or if duration is equal to assigned hours, or user oks the discrepancy
    """
    total = 0.0
    for block_info in block_tk_variables:
        duration = float(block_info[2].get().strip().split(" ")[0])
        if duration < 0:
            duration += 24
        total += duration

    if total == course_hours or total == 0.0:
        return True

    else:
        return message_box.askyesno("Class Times", f"Total allocated class times ({total})\n"
                                       f"does not equal course time ({course_hours})"
                                       f"\n\nDo you wish to continue?")


# ================================================================================================================
# get updated block information
# ================================================================================================================
def get_block_info_from_tk_widgets(block_tk_variables: list[tk.StringVar]) -> list[tuple[float,float,float]]:
    """
    Convert string (day, start_time, duration) to int(day), float(start_time), float(duration)
    :param block_tk_variables:
    :return: updated list
    """
    updated_blocks = []
    for i, b in enumerate(block_tk_variables):
        d = [x.get() for x in b]
        day = WeekDay[d[0]].value
        start = float(d[1].strip())
        duration = float(d[2].strip())
        updated_blocks.append((day,start,duration))

    return updated_blocks

# ================================================================================================================
# update the gui with block data
# ================================================================================================================
def refresh_gui_blocks(self,):
    """
    Create the drop-down and entry boxes etc for blocks
    :param self: the object that contains all the block info, frame, etc
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # remove any pre-existing stuff
    for w in self.block_frames.winfo_children():
        w.destroy()

    row_frames = []
    for index, block_info in enumerate(self.block_tk_variables):
        def remove_block(instance=self, i=index):
            instance.block_tk_variables.pop(i)
            instance.refresh()

        row_frame = tk.Frame(self.block_frames)
        if row_frame.winfo_toplevel().tk.call('tk', 'windowingsystem') == 'aqua':
            padx = 0
            pady = 0
        else:
            padx = 2
            pady = 0
        row_frames.append(row_frame)
        row_frame.pack(expand=1, fill='both', padx=10, pady=2)

        opt_day, opt_hour, opt_duration = block_info

        btn_delete = tk.Button(row_frame, text="remove",  command=remove_block, padx=2*padx)
        om_day = ttk.Combobox(row_frame, textvariable=opt_day,  values=days, state="readonly" )
        om_time = entry_float(row_frame, textvariable=opt_hour)
        om_duration = entry_float(row_frame, textvariable=opt_duration)

        om_day.config(width=8)
        om_time.config(width=5)
        om_duration.config(width=5)

        om_day.pack(side='left', pady=pady, padx=padx)
        tk.Label(row_frame, text="start:", anchor='e',width=5,).pack(side='left', expand=1, fill='x')
        om_time.pack(side='left', pady=pady, padx=padx, expand=1, fill='x')
        tk.Label(row_frame, text="duration:", anchor='e',width=8,).pack(side='left', expand=1, fill='x')
        om_duration.pack(side='left', pady=pady, padx=padx, expand=1, fill='x')
        btn_delete.pack(side='left', pady=pady, padx=padx, ipadx=padx, expand=1, fill='x')

        om_time.bind("<Leave>", partial(_validate_start_time, opt_hour))
        om_time.bind("<FocusOut>", partial(_validate_start_time, opt_hour))
        om_duration.bind("<Leave>", partial(_validate_duration, opt_duration))
        om_duration.bind("<FocusOut>",  partial(_validate_duration, opt_duration))

# ================================================================================================================
# validate that the start time is a float, and that it is within operating hours
# ================================================================================================================
def _validate_start_time(tkvar: tk.StringVar,  _: tk.Event):
    """
    Validates the start time is good, and rounds to the nearest 15 minutes
    :param tkvar: The tk variable to analyze
    """
    try:
        value = float(tkvar.get())
    except ValueError:
        tk.messagebox.showerror(message="Class Start Time", title="Invalid Float",
                                detail=f"'{tkvar.get()}' is not a valid number")
        tkvar.set("8.0")
        return

    if value < 8 or value > 18:
        tk.messagebox.showerror(title="Invalid Class Start Time", detail="Resetting to 8:00 am",
                                message=f"'{tkvar.get()}' is outside of operational hours")
        tkvar.set("8.0")
        return

    tkvar.set(str(round(4*value)/4))

# ================================================================================================================
# validate that the duration is a float, and that it is within operating constraints
# ================================================================================================================
def _validate_duration(tkvar: tk.StringVar, _: tk.Event):
    """
    Validates the duration length is good, and rounds to the nearest 15 minutes
    :param tkvar: The tk variable to analyze
    """

    try:
        value = float(tkvar.get())
    except ValueError:
        tk.messagebox.showerror(message="Class Duration", title="Invalid Float",
                                detail=f"'{tkvar.get()}' is not a valid number")
        return

    if value < 0.5 or value > 8:
        tk.messagebox.showerror(title="Invalid Class Duration", detail="Resetting to 1.5 hrs",
                                message=f"'{tkvar.get()}' is not a valid class duration")
        return

    tkvar.set(str(round(4*value)/4))






