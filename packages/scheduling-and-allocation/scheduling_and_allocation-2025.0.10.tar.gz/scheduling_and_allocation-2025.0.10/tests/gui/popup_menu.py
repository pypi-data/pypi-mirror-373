# creating popup menu in tkinter
import tkinter
import os
import sys

from src.scheduling_and_allocation.gui_generics.menu_and_toolbars import MenuItem, MenuType, generate_menu

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../../"))


class A:
    # creates parent window
    def __init__(self):

        self.popup_menu = None
        self.root = tkinter.Tk()
        self.root.geometry('500x500')

        self.frame1 = tkinter.Label(self.root,
                                    width=400,
                                    height=400,
                                    text = "Hi",)
        self.frame1.pack()

    # create menu
    def popup(self):
        menu = list()
        menu.append(MenuItem(menu_type=MenuType.Command,
                                     label='say hi',
                                     command=lambda: self.hey("hi")
                                     )
                    )
        menu.append(MenuItem(menu_type=MenuType.Command,
                                     label='say hello',
                                     command=lambda: self.hey("hello")
                                     )
                    )
        menu.append(MenuItem(menu_type=MenuType.Command,
                                     label='say bye',
                                     command=lambda: self.hey("bye")
                                     )
                    )

        self.popup_menu = tkinter.Menu(self.root,
                                        tearoff=0)
        generate_menu(self.root, menu, self.popup_menu)

    # display menu on right click
    def do_popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root,
                                     event.y_root)
        finally:
            self.popup_menu.grab_release()

    def hey(self, s):
        self.frame1.configure(text=s)

    def run(self):
        self.popup()
        self.root.bind("<Button-2>", self.do_popup)
        tkinter.mainloop()


a = A()
a.run()
