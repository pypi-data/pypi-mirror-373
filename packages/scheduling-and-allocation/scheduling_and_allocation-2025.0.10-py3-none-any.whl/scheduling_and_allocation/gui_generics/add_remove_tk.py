"""
AddRemoveTk

Creates two list boxes where you can transfer items from one list to another, just by clicking on an item

"""
import tkinter as tk

from ..modified_tk import Scrolled
from functools import partial

# ====================================================================================================================
# Move objects between two lists
# ====================================================================================================================
class AddRemoveTk:
    def __init__(self, frame: tk.Frame,
                 add_list: list,
                 remove_list: list,
                 add_text="Add to",
                 remove_text="Remove from",
                 height = 10):
        """
        :param frame: the frame to put the widgets in
        :param add_list: the list of objects that can be added
        :param remove_list: the list of objects that can be removed
        :param add_text: text over the 'add' list
        :param remove_text: text over the 'remove' list
        """
        self.frame = frame
        self.add_text = add_text
        self.remove_text = remove_text
        self.add_listbox = None
        self.remove_listbox = None
        self.adds = add_list
        self.removes = remove_list

        f = tk.Frame(self.frame)
        f.grid(column=0, stick='nsew', row=0)
        tk.Label(f, text=self.add_text).pack()
        sf = tk.Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='oe', height=height)
        self.add_listbox = s.widget
        self.add_listbox.configure(borderwidth="5", relief="ridge")
        s.widget.bind('<Button-1>', partial(self._cmd_click, 'add'))

        f = tk.Frame(self.frame)
        f.grid(column=1, stick='nsew', row=0)
        tk.Label(f, text=self.remove_text).pack()
        sf = tk.Frame(f)
        sf.pack(fill='both', expand=1)
        s: Scrolled = Scrolled(sf, 'Listbox', scrollbars='oe', height=height)
        self.remove_listbox = s.widget
        self.remove_listbox.configure(borderwidth="5", relief="ridge")
        s.widget.bind('<Button-1>', partial(self._cmd_click, 'remove'))

        self.refresh()

    # ----------------------------------------------------------------------------------------------------------------
    # move object from 'remove' list to 'add' list
    # ----------------------------------------------------------------------------------------------------------------
    def to_add_function(self, obj):
        self.removes.append(obj)
        try:
            self.removes.sort()
        except ValueError:
            pass
        self.adds.remove(obj)

    # ----------------------------------------------------------------------------------------------------------------
    # move object from 'add' list to 'remove' list
    # ----------------------------------------------------------------------------------------------------------------
    def to_remove_function(self, obj):
        self.adds.append(obj)
        try:
            self.adds.sort()
        except ValueError:
            pass
        self.removes.remove(obj)

    # ----------------------------------------------------------------------------------------------------------------
    # what to do when a list box is clicked (... move object)
    # ----------------------------------------------------------------------------------------------------------------
    def _cmd_click(self, which: str, e: tk.Event):
        """
        move object from one list to another
        :param which: which is the 'starting' list
        :param e: the tk event (which can give us the nearest widget to the mouse click)
        :return:
        """
        if which == "add":
            widget = self.add_listbox
            index = widget.nearest(e.y)
            if 0 <= index < len(self.adds):
                self.to_add_function(self.adds[index])
        else:
            widget = self.remove_listbox
            index = widget.nearest(e.y)
            if 0 <= index < len(self.removes):
                self.to_remove_function(self.removes[index])
        self.refresh()

    # ----------------------------------------------------------------------------------------------------------------
    # refrest the two list boxes
    # ----------------------------------------------------------------------------------------------------------------
    def refresh(self):
        """updates the two list boxes"""
        self.add_listbox.delete(0, "end")
        self.remove_listbox.delete(0, "end")
        for item in self.adds:
            self.add_listbox.insert("end", str(item))
        for item in self.removes:
            self.remove_listbox.insert("end", str(item))
