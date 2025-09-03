from __future__ import annotations
from tkinter import *
import tkinter as tk
from typing import Any, Callable
from functools import partial
import os

from ..modified_tk.Scrolled import Scrolled
from ..modified_tk.FindImages import get_image_dir
from ..modified_tk.InitGuiFontsAndColours import TkColours

# TODO:  Maybe refactor the method for config_specs, etc.
#        Check DynamicTree methods (if was coded after this was)
# =================================================================================================
# NOTES TO DEVELOPERS
# =================================================================================================
# 1. columns and rows:
#    the 0th grid row is the label row, and the data row starts at 0, but is in grid row 1
#    the 0th grid column is the delete button, and the data column starts at 0, but is in grid column 1
#    if there is a button at the end of the row, the grid column will be the data column + 1
#    i.e.
#           grid_row = data_row + 1
#           grid_column = data_column + 1
#           del_button_column = 0
#           button_column = self.number_of_columns + 2
# -------------------------------------------------------------------------------------------------

class TableEntry(tk.Frame):
    """
    Creates a spreadsheet-ish widget, inside a frame

Inputs
------
    notebook: Frame
        the notebook widget that will contain the TableEntry widget

Additional TableEntry Options
-----------------------------
    rows: int
        The number of data rows in TableEntry, should not be modified after TableEntry is created
    columns: int
        The number of data columns in TableEntry, should not be modified after TableEntry is created
    titles: list
        A list of column titles
    colwidths: list
        A list of widths for each column (default = defwidth), should not be modified after TableEntry is created
    disabled: list
        A list containing a '1' for each column that is made 'disabled'.  Do not modify after TableEntry is created
    defwidth: int
        The default width of the columns (defaults to 8 if not defined). Do Not modify after TableEntry is created
    buttontext: str
        If buttoncmd is defined, then a button will be added to the row.  The text will be 'buttontext'.
        Do not modify after TableEntry is created
    delete: callable
        A function that will be called if the row is deleted.  The data in that row will be passed to the
        function as a list
    buttoncmd: callable
        If defined, a button will be created at the end of each row.  This function that will be called
        The data in that row will be passed to the function as a list

Public Methods
--------------

    add_empty_row()
        Adds a new row at the end of the DateEntry
    read_row(row:int)->List[Str]
        Reads the data in the row, and returns the data in a list (note that all data will be a string)
    put(row:int, col:int, datum:Any)
        Puts the string version of the data into the Entry widget at row,col
    cget(option:str)
        Returns the value of that particular option
    configure(option_name=value, ...)
        Sets the option. NB: Modifying some options will have no effect (see above)

Examples
--------

Example::

    data = [
        [1, "datum 1", "m1"],
        [2, "datum 2", "m2"],
        [3, "datum 3", "m3"],
    ]

    # make a Tk window
    mw = Tk()
    mw.geometry("500x300")
    frame = Frame(mw)
    frame.pack(expand=1, fill="both")

    # add the TableEntry object
    titles = ["one", "two", "three"]
    col_widths = [10, 20, 5]

    # note that buttoncmd must be here, it cannot be entered later via config
    de = TableEntry(frame, rows=0, columns=len(data[0]), colwidths=col_widths, titles=titles,buttoncmd=on_button_click)
    de.pack(side="top", expand=1, fill="both")
    de.configure(borderwidth=3)

    # disable the first column, but not the rest
    disabled = [1]
    de.configure(disabled=disabled)

    # callback for deleting a row
    de.configure(delete=on_delete)

    # populate with data
    for r in range(len(data)):
        for c in range(len(data[r])):
            de.put(r, c, data[r][c])

    de.add_empty_row();

    mw.mainloop()

    def on_delete(data: list):
        print(f"Deleted row, {data}")

    def on_button_click(data: list):
        print(f"Button clicked, {data}")
    """

    # ===================================================================
    # properties
    # ===================================================================

    # number of data rows
    @property
    def number_of_rows(self) -> int:
        """Gets and sets the number of rows in the table"""
        return self.cget("rows")

    # number of data columns
    @property
    def number_of_columns(self) -> int:
        """Gets and sets the number of columns in the table"""
        return self.cget("columns")

    # ===================================================================
    # Constructor
    # ===================================================================
    def __init__(self, parent: Frame, colours: TkColours, **kwargs):
        """Create a TableEntry widget inside 'notebook'"""
        tk.Frame.__init__(self, parent)
        self.colours = colours
        self._cget = dict()
        self.frame = None
        self.__scrolled_frame = None
        self.__delete_photo = None

        # ---------------------------------------------------------------
        # configuration and defaults
        # ---------------------------------------------------------------
        # this is a table of all the additional options available to
        # TableEntry, and the methods used to set those options
        self.__config_specs: dict[str:Callable[[TableEntry, Any], None]] = {
            'rows': self.__set_rows,
            'columns': self.__set_columns,
            'titles': self.__set_titles,
            'disabled': self.__set_disabled_columns,
            'delete': self.__set_delete_callback,
            'buttoncmd': self.__set_button_callback,
            'buttontext': self.__set_button_text,
            'colwidths': self.__set_column_widths,
            'defwidth': self.__set_default_width,
        }

        # this is a table of all the additional options available to
        # TableEntry, and their default values
        self._defaults: dict[str, Any] = {
            "rows": 10,
            "columns": 10,
            "titles": list(),
            "colwidths": list(),
            "disabled": list(),
            "defwidth": 8,
            "width": 100,
            "height": 200,
            "relief": 'flat',
            "buttontext": "Go",
            "delete": None,
            "buttoncmd": None,
        }

        # time_start the creation of the widget
        self.__populate_the_frame(**kwargs)

    # ====================================================================================
    # add empty_row
    # ====================================================================================
    def add_empty_row(self):
        """Add an empty row at the end of the 'spreadsheet'"""
        column_widths = self.cget("colwidths")
        columns_enabled_disabled = self.cget("disabled")
        if columns_enabled_disabled is None:
            columns_enabled_disabled = []

        # make sure lists are long enough
        while len(column_widths) < self.number_of_columns + 1:
            column_widths.append(0)
        while len(columns_enabled_disabled) < self.number_of_columns + 1:
            columns_enabled_disabled.append(False)

        # --------------------------------------------------------------------------------
        # add the grid_row
        # --------------------------------------------------------------------------------
        # always add new grid_row at the end of the existing EditResources widget
        grid_row = self.number_of_rows + 1

        # for each column, add an entry box
        for data_col in range(0, self.number_of_columns):

            # set the column width if defined, else use the default width
            column_widths[data_col] = column_widths[data_col] if column_widths[data_col] else self.cget("defwidth")

            # if there is something already there, delete it
            old = self.__get_widget_in_row_col(grid_row, data_col + 1)
            if old:
                old.destroy()

            # make entry widget
            w = Entry(self.frame,
                      width=column_widths[data_col],
                      bg=self.colours.DataBackground,
                      fg=self.colours.DataForeground,
                      disabledbackground=self.colours.DisabledBackground,
                      disabledforeground=self.colours.DataForeground,
                      relief="ridge",
                      )

            # if the column has been set to disabled, disable it
            if columns_enabled_disabled[data_col]:
                w.configure(state="disabled")

            # put widget in appropriate grid column and row
            w.grid(column=data_col + 1, sticky="nsew", row=grid_row)

            # key bindings for this entry widget
            w.bind("<Tab>", partial(self.__next_cell, w))
            w.bind("<Key-Return>", partial(self.__next_cell, w))
            w.bind("<Shift-Tab>", partial(self.__prev_cell, w))
            w.bind("<Key-Left>", partial(self.__prev_cell, w))
            w.bind("<Key-leftarrow>", partial(self.__prev_cell, w))
            w.bind("<Key-Up>", partial(self.__prev_row, w))
            w.bind("<Key-uparrow>", partial(self.__prev_row, w))
            w.bind("<Key-Down>", partial(self.__next_row, w))
            w.bind("<Key-downarrow>", partial(self.__next_row, w))
            w.bind("<Key-Right>", partial(self.__next_cell, w))
            w.bind("<Key-rightarrow>", partial(self.__next_cell, w))
            w.bind("<Button>", partial(self.__select_all, w))

            # I want my bindings to happen BEFORE the class bindings
            # TODO: This is not working properly, <TAB> still behaves weirdly
            bindtags = w.bindtags()
            w.bindtags((bindtags[1], bindtags[0], bindtags[2], bindtags[3]))

        # keep our grid_row count up to date
        self.configure(rows=grid_row)

        # add a `delete button` in the first column
        self.__add_delete_btn_to_row(grid_row)

        # if we need a grid_row button, add that to the last column
        self.__add_btn_to_end_of_row(grid_row)

        # we've added a new grid_row, so we need to adjust the size of the scrollable frame
        self.__adjust_size_of_frame()

    # ====================================================================================
    # read row
    # ====================================================================================
    def read_row(self, data_row: int) -> list[str]:
        """Get the data from the specified row"""
        data = list()
        grid_row = data_row + 1

        # cannot select the data from the title row
        if grid_row < 1:
            return data

        # get all the data from all the Entry widgets
        for data_col in range(0, self.number_of_columns):
            w = self.__get_widget_in_row_col(grid_row, data_col + 1)
            if w:
                value = w.get()
                value = value.strip()
                data.append(value)
        return data

    # ===================================================================
    # put data
    # ===================================================================
    def put(self, data_row: int, data_col: int, data: Any):
        """Put data into a cell specified by row and col"""
        if data_row < 0:
            return

        grid_row = data_row + 1
        grid_col = data_col + 1

        # add rows, if required
        if grid_row > self.number_of_rows:
            for _ in range(grid_row - self.number_of_rows):
                self.add_empty_row()

        # get the entry widget
        w = self.__get_widget_in_row_col(grid_row, grid_col)
        if not w or not isinstance(w, Entry):
            return

        # we have to disable Entry widgets before this can work
        disabled_flag = w.cget("state") == "disabled"
        if disabled_flag:
            w.configure(state="normal")

        # remove what was there and insert the data
        w.delete(0, 'end')
        w.insert(0, data)

        # if entry widget was disabled, set it back to disabled
        if disabled_flag:
            w.configure(state="disabled")

    # ===================================================================
    # clear data
    # ===================================================================
    def clear_data(self):
        """Put data into a cell specified by row and col"""
        for data_row in range(self.number_of_rows):
            grid_row = data_row + 1
            for data_col in range(self.number_of_columns):
                grid_col = data_col + 1

                # get the entry widget
                w = self.__get_widget_in_row_col(grid_row, grid_col)
                if not w or not isinstance(w, Entry):
                    return

                # we have to disable Entry widgets before this can work
                disabled_flag = w.cget("state") == "disabled"
                if disabled_flag:
                    w.configure(state="normal")

                # remove what was there and insert the data
                w.delete(0, 'end')

                # if entry widget was disabled, set it back to disabled
                if disabled_flag:
                    w.configure(state="disabled")

    # =================================================================================================
    # configure, cget, etc
    # =================================================================================================
    def cget(self, option: str) -> Any:
        if option in self._cget:
            return self._cget[option]
        else:
            return super().cget(option)

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._cget:
                self.__config_specs[k](v)
            else:
                super().configure(**{k: v})

    # ====================================================================================
    # add the user defined button at end of row
    # ====================================================================================
    def __add_btn_to_end_of_row(self, grid_row):
        if self.cget("buttoncmd"):
            b = Button(self.frame,
                       text=self.cget("buttontext"),
                       )
            b.configure(command=partial(self.__button_cmd, b))
            b.grid(column=self.number_of_columns + 1, sticky="nsew", row=grid_row)

    # ====================================================================================
    # add the "delete" button at the beginning of a row
    # ====================================================================================
    def __add_delete_btn_to_row(self, grid_row):
        b = Button(self.frame,
                   relief="flat",
                   highlightbackground=self.colours.HighlightBackground,
                   bg=self.colours.ButtonBackground,
                   )
        if self.delete_photo:
            b.configure(image=self.delete_photo)
        else:
            b.configure(text="del")
        b.configure(command=partial(self.__delete_row, b))
        b.grid(column=0, sticky="nsew", row=grid_row)

        # disable button?
        if self.__are_all_columns_disabled():
            b.configure(state='disabled')

    # ====================================================================================
    # after a row add or row delete, adjust the size of the frame
    # ====================================================================================
    def __adjust_size_of_frame(self):
        # --------------------------------------------------------------------------------
        # adjust height of pane
        # --------------------------------------------------------------------------------
        height = 0
        for row in range(self.number_of_rows + 1):
            w = self.__get_widget_in_row_col(row, 1)
            if not w:
                continue
            height += w.winfo_height()

        height += 2 * self.cget('border')
        height += self.__scrolled_frame.Subwidget("xscrollbar").winfo_height()
        self.frame.configure(height=height)
        self.update()

    # =================================================================================================
    # Generic function that applies calls a function for all Entry widgets
    # =================================================================================================
    def __apply_to_all_entry_widgets(self, func: callable):
        if self.number_of_columns and self.number_of_rows:
            for grid_col in range(1, self.number_of_columns + 1):
                for grid_row in range(1, self.number_of_rows + 1):
                    w = self.__get_widget_in_row_col(grid_row, grid_col)
                    if w is not None:
                        func(w, grid_row, grid_col)

    # ====================================================================================
    # are all columns disabled?
    # ====================================================================================
    def __are_all_columns_disabled(self) -> bool:
        disabled_columns = self.cget("disabled")
        if not disabled_columns:
            return False
        flag = True
        for col in disabled_columns:
            flag = flag and col
        return flag

    # ====================================================================================
    # callback for button at end of row being clicked
    # ====================================================================================
    def __button_cmd(self, btn, **kwargs):
        if self.cget("buttoncmd"):
            grid_row, grid_col = self.__get_row_col_of_widget(btn)
            data_row = grid_row - 1
            data = self.read_row(data_row)
            self.cget("buttoncmd")(data)

    # ====================================================================================
    # change focus to next cell (bound to Entry widgets)
    # ====================================================================================
    def __change_focus_to_new_cell(self, w: Entry, x_dir: int, y_dir: int, e:Event=None):

        if w:
            w.selection_clear()

        (grid_row, grid_col) = self.__get_row_col_of_widget(w)
        grid_col = grid_col + x_dir
        grid_row = grid_row + y_dir

        # if at end of row, scroll around to beginning of next row,
        # ignoring the 'delete' button
        if grid_col > self.number_of_columns:
            grid_row = grid_row + 1
            grid_col = 1

        # if at beginning of row, go to the end of the previous row
        if grid_col < 1:
            grid_row = grid_row - 1
            grid_col = self.number_of_columns

        # if we have exceeded the number of rows, create a new empty row
        if grid_row > self.number_of_rows:
            self.add_empty_row()
            #self.__scrolled_frame.update_scrollbars()

        # can't go less than zero
        if grid_row < 0:
            grid_row = 0

        # set the focus, and move the scrollbars appropriately
        w2 = self.__get_widget_in_row_col(grid_row, grid_col)
        if w2:
            self.__scrolled_frame.see(w2)
            self.update()
            if isinstance(w2, Entry):
                w2.focus_set()
                w2.selection_range(0, 'end')

                # if we land on a disabled widget, keep moving
                disabled_list = self.cget("disabled")
                if disabled_list[grid_col - 1]:
                    self.winfo_toplevel().after(20,lambda:self.__change_focus_to_new_cell(w2, x_dir, y_dir))

        self.update()

        # According to the documentation, this should prevent the event
        # from propagating to the next internal event handlers
        # (see bindtags), but it doesn't appear to work
        return "break"

    # ===================================================================
    # save the additional TableEntry options in a list
    # ===================================================================
    def __configure_save(self, **kwargs):
        for k, v in kwargs.items():
            self._cget[k] = v

    # ===================================================================
    # insert header_row
    # ===================================================================
    def __create_header_row(self):
        titles = self.cget("titles")
        col_widths = self.cget("colwidths")

        # make sure lists are long enough
        while len(titles) < self.number_of_columns + 1:
            titles.append("")

        while len(col_widths) < self.number_of_columns + 1:
            col_widths.append(0)

        # add labels to the top row
        for data_col in range(0, self.number_of_columns):
            col_widths[data_col] = col_widths[data_col] if col_widths[data_col] else self.cget("defwidth")
            w = Label(self.frame, text=titles[data_col], width=col_widths[data_col])
            w.grid(column=data_col + 1, sticky='nsew', row=0)

        self.__configure_save(colwidths=col_widths)

    # ====================================================================================
    # delete a row
    # ====================================================================================
    def __delete_row(self, b):
        grid_row, _ = self.__get_row_col_of_widget(b)
        if grid_row == 0:
            return  # cannot delete the header row
        data_row = grid_row - 1

        # run user supplied callback first
        delete_callback = self.cget("delete")
        if delete_callback:
            data = self.read_row(data_row)
            delete_callback(data)


        # we want to move everything up
        for grid_row in range(grid_row + 1, self.number_of_rows + 1):
            for grid_col in range(1, self.number_of_columns + 2):
                w1 = self.__get_widget_in_row_col(grid_row-1, grid_col)
                w2 = self.__get_widget_in_row_col(grid_row, grid_col)
                if w1:
                    was_state = w1.cget('state')
                    w1.configure(state="normal")
                    w1.delete(0, 'end')
                    if w2:
                        w1.insert(0, w2.get())
                    w1.configure(state=was_state)

        # adjust the number of rows
        self.configure(rows=self.number_of_rows - 1)

    # ===================================================================
    # draw the widgets onto the scrollable frame
    # ===================================================================
    def __draw(self):

        # create header row
        self.__create_header_row()

        # add rows
        num_of_rows = self.number_of_rows
        self.configure(rows=0)
        for r in range(0, num_of_rows):
            self.add_empty_row()

        # calculate the width of the row, to set the pane width
        width_total = 0
        for c in range(self.number_of_columns + 1):
            w = self.__get_widget_in_row_col(1, c)
            if w is not None:
                width_total += w.winfo_width() + 12

            if self.cget("buttoncmd"):
                width_total += 100

            width_total += 2 * self.cget("border")
            self.frame.configure(width=width_total)

    # ===================================================================
    # get row/col of a widget
    # ===================================================================
    def __get_row_col_of_widget(self, w: Entry):
        if w:
            i = w.grid_info()
            return i["row"], i["column"]
        return 0, 0

    # ===================================================================
    # get widget in row/col
    # ===================================================================
    def __get_widget_in_row_col(self, r, c) -> Entry | None:
        """get the widget in the row/col"""
        w = self.frame.grid_slaves(r, c)
        if w:
            return w[0]
        return None

    # ===================================================================
    def __next_cell(self, w: Any, *args, **kwargs):
        self.__change_focus_to_new_cell(w, 1, 0)

    # ===================================================================
    def __next_row(self, w: Any, *args, **kwargs):
        self.__change_focus_to_new_cell(w, 0, 1)

    # ===================================================================
    # populate the frame
    # ===================================================================
    def __populate_the_frame(self, **kwargs):

        # ---------------------------------------------------------------
        # create a scrolled pane
        # ---------------------------------------------------------------
        scrolled_frame = Scrolled(self, "Frame", scrollbars="se", border=2, relief="flat")
        scrolled_frame.pack(side='left', fill='both')
        self.__scrolled_frame = scrolled_frame
        self.frame = scrolled_frame.Subwidget("Frame")

        # ---------------------------------------------------------------
        # define the 'delete' image
        # ---------------------------------------------------------------
        image_dir = get_image_dir()
        self.delete_photo = PhotoImage(format='gif', file=os.path.join(image_dir, "ex.gif"))

        # ---------------------------------------------------------------
        # configure this table entry & draw
        # ---------------------------------------------------------------
        to_configure = self._defaults.copy()
        to_configure.update(kwargs)
        self.__configure_save(**to_configure)
        self.__draw()

    # ====================================================================================
    def __prev_cell(self, w: Any, *args, **kwargs):
        self.__change_focus_to_new_cell(w, -1, 0)

    # ====================================================================================
    def __prev_row(self, w: Any, *args, **kwargs):
        self.__change_focus_to_new_cell(w, 0, -1)

    # ====================================================================================
    # binding subroutine for clicking mouse button on entry widget
    # ====================================================================================
    def __select_all(self, w: Entry, *args, **kwargs):
        if w:
            w.focus()
            w.selection_clear()
            w.selection_range(0, 'end')

    # ====================================================================================
    # set the titles for each column
    # ====================================================================================
    def __set_titles(self, title_list: list):
        if title_list is None:
            return self.cget('titles')
        while len(title_list) < self.number_of_columns:
            title_list.append("")
        self.__configure_save(titles=title_list)
        self.__apply_to_all_entry_widgets(lambda w, r, c: w.configure(text=title_list[c - 1]))
        return self.cget('titles')

    # ====================================================================================
    # set which columns of entry widgets are disabled
    # ====================================================================================
    def __set_disabled_columns(self, column_disabled_list: list):
        if column_disabled_list is None:
            return self.cget("disabled")
        while len(column_disabled_list) < self.number_of_columns:
            column_disabled_list.append(0)
        self.__configure_save(disabled=column_disabled_list)

        def _disable_widget(w, r, c):
            if column_disabled_list[c - 1]:
                w.configure(state='disabled')
                w.configure(takefocus=0)
            else:
                w.configure(state='normal')

        self.__apply_to_all_entry_widgets(_disable_widget)
        return self.cget('disabled')

    # ====================================================================================
    # set the callback for the button at the end of the row
    # NB:  If this is not set during the __init__, there will NOT be a button at the end
    #      of the row
    # ====================================================================================
    def __set_button_callback(self, button_callback: callable):
        self.__configure_save(buttoncmd=button_callback)
        return self.cget("buttoncmd")

    # ====================================================================================
    # define the button's text (the button at the end of the row)
    # ====================================================================================
    def __set_button_text(self, button_text: str):
        self.__configure_save(buttontext=button_text)
        return self.cget("buttontext")

    # ====================================================================================
    # set the number of columns
    # ====================================================================================
    def __set_columns(self, columns: list):
        self.__configure_save(columns=columns)
        return self.cget("columns")

    # ====================================================================================
    # set the widths for each column
    # ====================================================================================
    def __set_column_widths(self, colwidths_list: list):
        if not colwidths_list:
            return self.cget("colwidths")
        self.__configure_save(colwidths=colwidths_list)

        def _colwidths(w, r, c):
            width = colwidths_list[c - 1] or self.cget("defwidth") or 8
            w.configure(width=width)

        self.__apply_to_all_entry_widgets(_colwidths)
        return self.cget('colwidths')

    # ====================================================================================
    # set the callback function for the delete button
    # ====================================================================================
    def __set_delete_callback(self, delete_callback: callable):
        self.__configure_save(delete=delete_callback)
        return self.cget("delete")

    # ====================================================================================
    # set the number of rows
    # ====================================================================================
    def __set_rows(self, rows: list):
        self.__configure_save(rows=rows)
        return self.cget("rows")

    # ====================================================================================
    # set the default width of a column
    # ====================================================================================
    def __set_default_width(self, default_width: int):
        self.__configure_save(defwidth=default_width)
        return self.cget("width")
