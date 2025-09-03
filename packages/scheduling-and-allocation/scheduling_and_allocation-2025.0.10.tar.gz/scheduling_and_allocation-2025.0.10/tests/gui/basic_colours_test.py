from tkinter import *
from src.scheduling_and_allocation.modified_tk import set_default_fonts_and_colours


# TODO: background button Colour changes don't work on mac, not yet tested on windows

def main():
    mw: Tk = Tk()
    colours = set_default_fonts_and_colours(mw, invert=True)
    mw.geometry('400x450')
    mw.title('Button Background Example')

    button = Button(mw, text='Submit', bg='blue', fg='pink', activebackground="red")
    button.pack()

    b1 = Button(mw, width=20, text='Button', bg='red')
    b2 = Text(mw, width=40, height=20)
    b2.insert('end', 'background colours of buttons have been set to blue and red')

    b1.pack()
    b2.pack()
    # b1.configure({'bg':"#000000"})

    print(f"Button background : {b1.cget('background')}")
    print(f"Button foreground : {b1.cget('foreground')}")

    mw.mainloop()


main()
