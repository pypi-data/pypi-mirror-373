import tkinter as tk
from tkinter import ttk, messagebox

from src.scheduling_and_allocation.modified_tk import DragNDropManager


def lb_on_start(e: tk.Event, info_data: dict) -> str:
    # select the nearest item in the list
    w: tk.Listbox = e.widget
    index = w.nearest(e.y)
    w.select_clear(0, 'end')
    w.selection_set(index, index)

    # save some info for later use
    info_data["index"] = index

    # return string to be used in the drag indicator
    return w.get(index)


def lb_on_drag(e: tk.Event, info_data: dict, target: tk.Widget) -> bool:
    for s_iid in tv.selection():
        tv.selection_remove(s_iid)

    # if we are not dropping on the treeview, then it is no good
    if target != tv:
        return False

    # made up rule, just to demonstrate use of info_data
    if info_data["index"] < 0:
        return False

    # select item are we hovering over?
    tv_y_pos = e.y_root - tv.winfo_rooty()
    iid = tv.identify_row(tv_y_pos)
    if not iid:
        return False

    # if selected item doesn't have a parent, then it is not a valid drop site, but open branch
    if tv.parent(iid) == "":
        tv.item(iid, open=True)
        return False

    # finally, we have a valid drop site
    tv.selection_set(iid)
    tv.item(iid, open=True)
    return True


def lb_on_drop(e: tk.Event, info_data: dict, target: tk.Widget):
    tv.selection_clear()

    # if we are not dropping on the treeview, then it is no good
    if target != tv:
        return

    # select item are we hovering over?
    tv_y_pos = e.y_root - tv.winfo_rooty()
    iid = tv.identify_row(tv_y_pos)
    if not iid:
        return

    # if selected item doesn't have a parent, then it is not a valid drop site, but open branch
    if tv.parent(iid) == "":
        return

    # finally, we have a valid drop site
    messagebox.showinfo(title="Successful Drop", message=f"index {info_data['index']} dropped on {tv.item(iid)}")


mw = tk.Tk()
mw.geometry("300x500+30+40")
#colours, fonts = set_default_fonts_and_colours(mw)
tk.Label(mw, text="Drag from list one onto tree").pack()

lb = tk.Listbox()
lb.pack()
lb.insert('end', "one")
lb.insert('end', "two")
lb.insert('end', "three")
lb.insert('end', "four")

tv = ttk.Treeview()
tv.pack()
id1 = tv.insert(parent="", index="end", text="Not droppable", open=False)
id2 = tv.insert(parent=id1, index="end", text="can drop on me location 1", open=False)
id3 = tv.insert(parent=id2, index="end", text="can drop on me location 2", open=False)

tk.Button(mw, text="clear selection", command=lambda: tv.selection_clear()).pack()

dm = DragNDropManager()
dm.add_draggable(lb, on_start=lb_on_start, on_drop=lb_on_drop, on_drag=lb_on_drag)
mw.mainloop()
