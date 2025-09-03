# https://www.pythontutorial.net/tkinter/tkinter-treeview/
import os
import sys
import tkinter as tk
from tkinter import ttk
import csv
bin_dir: str = os.path.dirname(os.path.realpath(__file__))
print (bin_dir)
sys.path.append(os.path.join(bin_dir, "../../"))

from schedule.Tk.Pane import Pane

# TODO: lost the horizontal scrollbar
# TODO: the vertical frames are not the same size (header vs data vs summary)
"""
┌─────────────────────────────────────────────────────────────────────┐
│       ┌──────────────────────────────────────────────────┐          │
│       │               header                             │          │
│       └──────────────────────────────────────────────────┘          │
│ ┌────┐┌──────────────────────────────────────────────────┐┌────┐    │
│ │ t  ││                                                  ││ s  │ ^  │
│ │ i  ││                                                  ││ u  │ |  │
│ │ t  ││                                                  ││ m  │ |  │
│ │ l  ││                data                              ││ m  │ |  │
│ │ e  ││                                                  ││ a  │ |  │
│ │ s  ││                                                  ││ r  │ |  │
│ │    ││                                                  ││ r  │ |  │
│ │    ││                                                  ││ y  │ v  │
│ └────┘└──────────────────────────────────────────────────┘└────┘    │
│       ┌──────────────────────────────────────────────────┐          │
│       │               footer                             │          │
│       └──────────────────────────────────────────────────┘          │
│        <────────────────────────────────────────────────>           │
└─────────────────────────────────────────────────────────────────────┘

horizontal scroll: header data footer
vertical scroll: titles data summary
"""
class AllocationLayout:
    def __init__(self, frame):

        # define the grid for managing this layout
        outer_frame = tk.Frame(frame, background="yellow", borderwidth=5, relief='raised')
        outer_frame.grid_columnconfigure(0, weight=1, pad=5, minsize=20)
        outer_frame.grid_columnconfigure(1, weight=100, pad=5)
        outer_frame.grid_columnconfigure(2, weight=1, pad=5, minsize=20)
        outer_frame.grid_columnconfigure(3, weight=1, pad=5)
        outer_frame.grid_rowconfigure(0, weight=1, pad=5)
        outer_frame.grid_rowconfigure(1, weight=100, pad=5)
        outer_frame.grid_rowconfigure(2, weight=1, pad=5)
        outer_frame.grid_rowconfigure(3, weight=1, pad=5)

        # Define the frames
        self.header_frame = self.scrollable_frame(outer_frame,0,1, height=20, width=None)
        self.title_frame = self.scrollable_frame(outer_frame,1,0)
        self.data_frame = self.scrollable_frame(outer_frame,1,1)
        self.summary_frame = self.scrollable_frame(outer_frame,1,2)
        self.footer_frame = self.scrollable_frame(outer_frame,2,1)

        # Define the scrollbars
        h_scrollbar = tk.Scrollbar(outer_frame, orient='horizontal')
        v_scrollbar = tk.Scrollbar(outer_frame, orient='vertical')
        h_scrollbar.grid(row=3,column=1, sticky='ew')
        v_scrollbar.grid(row=1,column=3, sticky='ns')

        # Link the scrollbars to the frames
        horizontal_scrollable:list[Pane] = [self.footer_frame, self.header_frame, self.data_frame]
        vertical_scrollable:list[Pane] = [self.title_frame, self.data_frame, self.summary_frame]

        def sync_vertical_scroll(*args):
            for w in vertical_scrollable:
                w.yview(*args)

        def sync_horizontal_scroll(*args):
            for w in horizontal_scrollable:
                w.xview(*args)

        h_scrollbar.config(command=sync_horizontal_scroll)
        v_scrollbar.config(command=sync_vertical_scroll)
        for f in horizontal_scrollable:
            f.canvas.config(xscrollcommand=h_scrollbar.set)
        for f in vertical_scrollable:
            f.canvas.config(yscrollcommand=v_scrollbar.set)

        # pack the outer frame
        outer_frame.pack(expand=1, fill="both")

    def scrollable_frame(self, outer_frame, row,col, width=None, height=None) -> Pane:
        sf = Pane(outer_frame)
        sf.grid(row=row, column=col, sticky='nsew')
        return sf


    def populate(self, columns, column_widths=150, num_rows=50 ):

        # header
        for i,c in enumerate(columns):
            tk.Label(self.header_frame.frame, text=c).grid(
                column=i,row=0,sticky='nsew', padx=1, pady=1)
            self.header_frame.frame.columnconfigure(i,minsize=column_widths, weight=0)

        # data frame has all entry boxes
        for r in range(num_rows):
            for c in range(len(columns)):
                tk.Entry(self.data_frame.frame).grid(column=c,row=r,sticky='nsew', padx=1, pady=1)
            self.data_frame.frame.rowconfigure(r, minsize=20)


        # titles
        for r in range(num_rows):
            tk.Label(self.title_frame.frame, text=f"Row {r}").grid(column=0,row=r,sticky='nsew', padx=1, pady=1)
            self.title_frame.frame.rowconfigure(r, minsize=20)

        # footer
        for c in range(len(columns)):
            tk.Label(self.footer_frame.frame, text=f"{c}").grid(column=c,row=2,sticky='nsew', padx=1, pady=1)
            self.footer_frame.frame.columnconfigure(c,minsize=column_widths, weight=0)

        # summary
        for r in range(num_rows):
            tk.Label(self.summary_frame.frame, text=f"Summary {r}").grid(column=0,row=r,sticky='nsew', padx=1, pady=1)
            self.summary_frame.frame.rowconfigure(r, minsize=20)






def main():
    root = tk.Tk()
    root.title("Employee List")
    columns = ("First Name","Last Name","Gender","City","Salary","Bonus")

    al = AllocationLayout(root)
    al.populate(columns,150)


    root.mainloop()


if __name__ == '__main__':
    main()