import tkinter
from functools import partial
from tkinter import *
from tkinter.simpledialog import Dialog

print("Testing simple dialog boxes")
mw = Tk()
mw.geometry('500x500')

class A(Dialog):
    # creates parent window
    def body(self, frame:Frame):
        """
        setup body, return widget that will have the initial focus
        :param frame:
        :return:
        """
        self.initialvalue = 3
        w = Label(frame, text="Enter Number", justify="left")
        w.grid(row=0, padx=5, sticky='w')

        self.entry = Entry(frame, name="entry")
        self.entry.grid(row=1, padx=5, sticky="we")

        if self.initialvalue is not None:
            self.entry.insert(0, str(self.initialvalue))
            self.entry.select_range(0, "end")

        return self.entry

    def validate(self):
        try:
            n = self.entry.getint(self.entry.get())
        except ValueError:
            self.entry.delete(0, "end")
            self.entry.insert(0, str(self.initialvalue))
            self.entry.select_range(0, "end")
            return False
        if n == 5:
            return False
        return True

    def ok(self, event=None):
        print("Called ok")
        super().ok(event)

    def apply(self):
        print("Called apply")
        super().apply()

    def cancel(self, event=None):
        print("Called cancel")
        super().cancel(event)

def show_dialog(*_):
    a=A(mw, "This Title")

def is_ok(number,*_):
    if number == "" or number == ".":
        return True
    try:
        float(number)
        return True
    except ValueError:
        duration_entry.winfo_toplevel().bell()
        return False


is_ok_tk = mw.register(is_ok)

Button(mw, text="press me for dialog box", command=show_dialog ).pack()
tk_duration=tkinter.StringVar()
duration_entry = Entry(mw, textvariable=tk_duration, validate='key', validatecommand=(is_ok_tk, '%P', '%s'))
duration_entry.pack()

def print_contents( event):
    print("Hi. The current entry content is:",
          tk_duration.get())

duration_entry.bind('<Key-Return>',
                             print_contents)


mainloop()