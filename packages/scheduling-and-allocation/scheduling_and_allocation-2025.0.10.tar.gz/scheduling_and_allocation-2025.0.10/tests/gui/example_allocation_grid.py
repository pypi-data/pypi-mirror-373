import os
import tkinter as tk

from src.scheduling_and_allocation.model import Schedule
from src.scheduling_and_allocation.modified_tk import set_default_fonts_and_colours
from src.scheduling_and_allocation.presenter.allocation_editor import AllocationEditor

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
mw = tk.Tk()
mw.geometry("800x400")

_ = set_default_fonts_and_colours(mw)
file = f"{bin_dir}/../unit_tests_presenter/data_fall.csv"
s = Schedule(file)

f = tk.Frame(mw, background="pink")
f.pack(expand=1, fill="both")
def set_dirty_flag(flag=False): ...

ae = AllocationEditor(set_dirty_flag, frame =f, schedule = s)

tk.mainloop()

