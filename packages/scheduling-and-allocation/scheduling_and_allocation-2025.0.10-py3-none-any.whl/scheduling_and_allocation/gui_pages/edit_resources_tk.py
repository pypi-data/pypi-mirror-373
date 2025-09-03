"""
# ============================================================================
# Basically a Tk::TableEntry object with some restrictions
#
# The first column I<must> be a unique identifier for the corresponding data
# object, and can not be edited.
#
# EVENT HANDLERS
#
#   button-click: delete the data in this row (code is in Tk::TableEntry)
#       event_delete_handler(row_data)
#
#   leave form event: save the data (data is a 2d list of strings)
#       event_save_handler(all_data)
#
# ============================================================================

"""
from asyncio import sleep
from typing import *

from ..Utilities import Preferences
from ..modified_tk.TableEntry import TableEntry
from dataclasses import dataclass
import tkinter as tk
from ..modified_tk.InitGuiFontsAndColours import TkColours


# ============================================================================
# Class for describing properties for each column
# ============================================================================
@dataclass
class DEColumnDescription:
    title: str
    width: int
    property: str
    unique_id: bool


# ============================================================================
# class: EditResourcesTk
# ============================================================================
class EditResourcesTk:
    Currently_saving = 0

    # ------------------------------------------------------------------------
    # constructor
    # ------------------------------------------------------------------------
    def __init__(self,
                 parent: tk.Frame,
                 event_delete_handler: Callable[[list[str], ...], None] = lambda x, *_: None,
                 event_save_handler: Callable[[list[list[str]]], None] = lambda *_: None,
                 preferences: Optional[Preferences] = None,
                 colours: Optional[TkColours] = None,
                 ):
        """
        :param parent: the frame where to put the data
        :param event_delete_handler: function to call when something is deleted
        :param event_save_handler: function to call for saving data
        :param colours: colours
        """
        # remove anything that was already in the frame
        for widget in parent.winfo_children():
            widget.destroy()

        if colours is None:
            colours = TkColours(parent.winfo_toplevel(), preferences.dark_mode())
        self.colours = colours
        self.frame = parent
        self.data_entry: Optional[TableEntry] = None
        self.delete_handler = event_delete_handler
        self.save_handler = event_save_handler

    # ------------------------------------------------------------------------
    # initialize columns
    # ------------------------------------------------------------------------
    def initialize_columns(self, column_descriptions: list[DEColumnDescription], disabled_columns=None):
        """
        define the columns
        :param column_descriptions:
        :param disabled_columns:
        :return:
        """

        titles: list[str] = list()
        column_widths: list[int] = list()
        for cd in column_descriptions:
            titles.append(cd.title)
            column_widths.append(cd.width)

        if self.data_entry is not None:
            self.data_entry.destroy()

        self.data_entry = TableEntry(
            self.frame,
            rows=1,
            columns=len(column_descriptions),
            titles=titles,
            colwidths=column_widths,
            delete=self.delete_handler,
            colours=self.colours,
            disabled = disabled_columns
        )
        self.data_entry.pack(side='top', expand=True, fill='both')

        self.data_entry.bind('<Leave>', func=self.save)

    # ------------------------------------------------------------------------
    # refresh
    # ------------------------------------------------------------------------
    def refresh(self, data: list[list[Any]]):
        """
        refresh the data
        :param data: a list of lists (a 2-d array sort of)
        """
        self.data_entry.clear_data()
        for row, row_data in enumerate(data):
            for col, cell_data in enumerate(row_data):
                self.data_entry.put(row, col, str(cell_data))

        if self.data_entry.number_of_rows <= len(data):
            self.data_entry.add_empty_row()

        # stupid Tk won't update image unless I do this.  Oh well, at least it worked
        self.frame.focus_set()

    # ------------------------------------------------------------------------
    # get the data from the gui and return it
    # ------------------------------------------------------------------------
    def get_all_data(self) -> list[list[str]]:
        """
        reads the data stored in the TableEntry widget
        :return: a list of rows, which is a list of columns with the data
        """
        data: list = list()
        for row in range(self.data_entry.number_of_rows):
            data.append(self.data_entry.read_row(row))
        return data

    # ------------------------------------------------------------------------
    # save
    # ------------------------------------------------------------------------
    def save(self, *_):
        """save the data in the table"""
        # Just in case saving is already in progress, wait before continuing.
        if self.Currently_saving > 2:
            return  # 2 is too many.
        if self.Currently_saving:
            sleep(2)
        self.Currently_saving += 1

        # call event handler with data
        all_data = self.get_all_data()
        self.save_handler(all_data)

        # reset currently saving
        self.Currently_saving -= 1

