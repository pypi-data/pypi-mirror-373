from functools import partial
from tkinter import *

from src.scheduling_and_allocation.modified_tk import Scrolled


class AddRemove:
    def __init__(self, frame: Frame,
                 get_add_list,
                 get_remove_list,
                 to_add_function,
                 to_remove_function,
                 add_text="Add to",
                 remove_text="Remove from"):
        self.frame = frame
        self.to_add_function = to_add_function
        self.to_remove_function = to_remove_function
        self.add_text = add_text
        self.remove_text = remove_text
        self.add_listbox = None
        self.remove_listbox = None
        self.adds = []
        self.removes = []
        self.get_add_list = get_add_list
        self.get_remove_list = get_remove_list

        f = Frame(self.frame)
        f.grid(column=0, stick='nsew', row=0)
        Label(f, text=self.add_text).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='oe')
        self.add_listbox = s.widget
        self.add_listbox.configure(borderwidth="5", relief="sunken")
        s.widget.bind('<Button-1>', partial(self._cmd_double, 'add'))

        f = Frame(self.frame)
        f.grid(column=1, stick='nsew', row=0)
        Label(f, text=self.remove_text).pack()
        sf = Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='oe')
        self.remove_listbox = s.widget
        self.remove_listbox.configure(borderwidth="5", relief="sunken")
        s.widget.bind('<Button-1>',  partial(self._cmd_double, 'remove'))

        self.refresh()

    def _cmd_double(self, which: str, e: Event):
        if which == "add":
            widget = self.add_listbox
            index = widget.nearest(e.y)
            if index < len(self.adds):
                self.to_add_function(self.adds[index])
        else:
            widget = self.add_listbox
            index = widget.nearest(e.y)
            if index < len(self.removes):
                self.to_remove_function(self.removes[index])
        self.refresh()

    def refresh(self):
        self.adds = self.get_add_list()
        self.removes = self.get_remove_list()
        self.add_listbox.delete(0, "end")
        self.remove_listbox.delete(0, "end")
        for item in self.adds:
            self.add_listbox.insert("end", str(item))
        for item in self.removes:
            self.remove_listbox.insert("end", str(item))


to_add = [1,3,5,7,11,13,15,17,19,21,23,25,27,29,31,33]
to_remove = [2,4,6,8]
def get_add_list():
    return to_add
def get_remove_list():
    return to_remove
def add_function(obj):
    to_remove.append(obj)
    to_remove.sort()
    to_add.remove(obj)
def remove_function(obj):
    to_add.append(obj)
    to_add.sort()
    to_remove.remove(obj)





mw=Toplevel()
frame = Frame(mw)
frame.pack()
mw.geometry("400x400")
AddRemove(frame, get_add_list,get_remove_list, add_function, remove_function)

mw.mainloop()

