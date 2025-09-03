from tkinter import *
from tkinter.ttk import Notebook

# ISSUE: when changing notebook tabs, the notebook page doesn't redraw
mw = Tk()
mw.title("Notebook Test")
mw.geometry(f"{800}x{800}")

main_page_frame = Frame(mw, borderwidth=1, relief='ridge')
main_page_frame.pack(side='top', expand=1, fill='both')

notebook = Notebook(main_page_frame)
notebook.pack(expand=1, fill='both')
frames = []

def tab_change(*_):
    index = notebook.index(notebook.select())
    print(index, frames[index])
    for widget in frames[index].winfo_children():
        print(widget)
        # widget.update()
        # widget.tkraise()
        # widget.event_generate("<FocusOut>")
        # widget.event_generate("<FocusIn>")
        # widget.event_generate("<MouseWheel>")
        # widget.event_generate("<Create>")
        widget.event_generate("<Expose>")
        # widget.event_generate("<Configure>")
        # widget.event_generate("<Key>")
        # widget.event_generate("<Motion>")
        # widget.event_generate("<Reparent>")
        # widget.event_generate("<Property>")
        # widget.event_generate("<Visibility>")
        # widget.event_generate("<Leave>")
        # widget.event_generate("<Enter>")
        # widget.event_generate("<Map>")
        # widget.event_generate("<KeyRelease>")
        # widget.event_generate("<Gravity>")
        # widget.event_generate("<Circulate>")

        # for widget1 in widget.winfo_children():
        #     widget1.update()
        #     widget1.focus()
    mw.update()
    mw.update_idletasks()


for index, info in enumerate(("one", "two", "three")):
    frame = Frame(mw)
    frames.append(frame)
    Label(frame, text=info).pack()
    notebook.add(frame, text=info)

notebook.bind("<<NotebookTabChanged>>", tab_change)

mw.mainloop()
