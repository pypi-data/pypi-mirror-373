from tkinter import *

from src.scheduling_and_allocation.gui_pages import DEColumnDescription, EditResourcesTk
from src.scheduling_and_allocation.modified_tk import set_default_fonts_and_colours


# TODO: button Colour changes don't work on mac, not yet tested on windows

def main():
    mw = Tk()
    colours, fonts = set_default_fonts_and_colours(mw, invert=True)
    mw.geometry('400x450')
    mw.title('Edit Resources Generic')
    frame = Frame(mw)
    frame.pack(expand=1, fill='both')

    col_descr = DEColumnDescription("Column 1", 30, "", False)
    col2_descr = DEColumnDescription("Column 2", 20, "", False)
    col3_descr = DEColumnDescription("Column 3", 15, "", False)

    columns = [col_descr, col2_descr, col3_descr]
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    data2 = [[21, 22, 23], [24, 25, 26], [27, 28, 29]]

    de = EditResourcesTk(frame,
                         lambda *args: print("delete", [*args]),
                         lambda *args: print("save", [*args]),
                         colours,
                         )
    de.initialize_columns(columns)
    de.refresh(data)

    Button(mw, text="clear", command=lambda *_: de.data_entry.clear_data(),
           bg=colours.ButtonBackground,
           fg=colours.ButtonForeground,
           highlightbackground=colours.HighlightBackground,
           ).pack()
    Button(mw, text="refresh", command=lambda *_: de.refresh(data2)).pack()
    Button(mw, text="get data", command=lambda *_: print(de.get_all_data())).pack()

    print ("testing delete callback", de.delete_handler())
    print ("testing save callback", de.save_handler())
    mw.mainloop()


main()
