"""Creates a horizontally scrollable grid with surrounding data frames that are not scrollable"""
from functools import partial
from typing import Optional, Literal, Callable, Any

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror

from ..modified_tk import get_fonts_and_colours
from ..modified_tk import Pane

from ..Utilities import Colour
from ..gui_generics.number_validations import entry_float
from ..modified_tk import Hovertip


# =====================================================================================================================
# globals
# =====================================================================================================================

# colours
HEADER_COLOUR1           = "#abcdef"
HEADER_COLOUR2           = Colour.lighten(HEADER_COLOUR1, 10)
VERY_LIGHT_GREY          = "#dddddd"
ROW_COL_INDICATOR_COLOUR = Colour.lighten("#cdefab", 5)
SUMMARY_HEADER_COLOUR    = Colour.string("lemonchiffon")
SUMMARY_COLOUR           = Colour.lighten(SUMMARY_HEADER_COLOUR, 5)
FG_COLOUR                = "black"
BG_COLOUR                = "white"
NOT_OK_COLOUR            = Colour.string("light salmon")
NOT_OK_DARK_COLOUR       = Colour.add(NOT_OK_COLOUR, VERY_LIGHT_GREY)
FRAME_BACKGROUND         = "black"  # provides the borders around the entry widgets

# layout properties
WIDTH = 5
ENTRY_PADDING = 1
TITLE_WIDTH = 12
SUMMARY_WIDTH = WIDTH + 2
PAD_COL_0 = 0
PAD_COL_1 = 0
PAD_COL_2 = 0
PAD_ROW_0 = 0
PAD_ROW_1 = 0
PAD_ROW_2 = 0

# entry widget properties
ENTRY_PROPS = {
    'width': WIDTH,
    'relief': 'ridge',
    'border': 0,
    'justify': 'center',
    'fg': FG_COLOUR,
    'disabledforeground': FG_COLOUR,
    'highlightbackground': BG_COLOUR,
    'bg': BG_COLOUR,
    'disabledbackground': BG_COLOUR
}


# trigger for data change
DATA_CHANGED: dict[tuple[int,int], tk.StringVar] = dict()
def on_var_change(v, row, col, *_):
    DATA_CHANGED[row,col] = v


# =====================================================================================================================
# Allocation Grid Tk
# =====================================================================================================================
class AllocationGridTk:

    @property
    def num_summary_col(self):
        return len(self.summary_header_widgets)

    @property
    def num_summary_sub_col(self):
        return len(self.summary_sub_header_widgets)

    @property
    def num_rows(self):
        return len(self.title_widgets)

    @property
    def num_cols(self):
        return len(self.sub_header_widgets)


    # -----------------------------------------------------------------------------------------------------------------
    # constructor
    # -----------------------------------------------------------------------------------------------------------------
    def __init__(self, frame: tk.Frame, rows,
                 col_merge: list[int],
                 summary_merge: list[int],
                 cb_process_data_change = lambda *_, **__: True,
                 bottom_cell_valid: Callable[[Any], bool] = lambda *_: True
                 ):
        """

        :param frame: where to put this grid
        :param rows: number of rows in the grid
        :param col_merge: list, each item represents a group of columns (affects colouring)
        :param summary_merge: list, each item represents a group of columns in the totals sections
        :param cb_process_data_change:


        Column Merge Example: if you want this for your 2 heading rows
    
        +-------------+----------+--------------------+
        | heading1    | heading2 | heading3           |
        +------+------+----------+------+------+------+
        | sub1 | sub2 | sub1     | sub1 | sub2 | sub3 |
        +------+------+----------+------+------+------+

        use col_merge = [2,1,3]

        """

        # get rid of anything that is currently on this frame
        for w in frame.winfo_children():
            w.destroy()

        # keep this for later
        self.frame = frame
        self.process_data_change_handler = cb_process_data_change
        self.panes = []
        self.bottom_cell_valid = bottom_cell_valid

        # set up the font for the entry widgets
        _, self.fonts = get_fonts_and_colours()

        ENTRY_PROPS['font'] = self.fonts.normal

        # make the frames
        self._layout(frame)

        # make the other stuff
        self.header_widgets: list[tk.Entry] = []
        self.sub_header_widgets: list[tk.Entry] = []
        self.summary_sub_header_widgets: list[tk.Entry] = []

        self.title_widgets: list[tk.Entry] = []
        self.widgets_row_col: dict[tk.Entry, tuple[int,int]] = dict()
        self.entry_widgets: dict[tuple[int,int], tk.Entry] = dict()
        self.summary_widgets: dict[tuple[int,int], tk.Entry] = dict()
        self.summary_header_widgets: list[tk.Entry] = []

        self.bottom_title_widget: Optional[tk.Entry] = None

        self.bottom_widgets: list[tk.Entry] = []
        self.column_colours: dict[int, str] = dict()

        self.make_header_columns(col_merge)
        self.make_summary_header(summary_merge)
        self.make_row_titles(rows)
        self.make_data_grid(rows, col_merge)
        self.make_summary_grid(rows, summary_merge)
        self.make_bottom_header()
        self.make_bottom(col_merge)


    # -----------------------------------------------------------------------------------------------------------------
    # layout
    # -----------------------------------------------------------------------------------------------------------------
    def _layout(self, frame):
        """
        ┌──────────────────────────────────────────────────────────────────┐
        │       ┌──────────────────────────────────────────────────┐┌────┐ │
        │       │               header                             ││  1 │ │
        │       └──────────────────────────────────────────────────┘└────┘ │
        │ ┌────┐┌──────────────────────────────────────────────────┐┌────┐ │
        │ │ t  ││                                                  ││ s  │ │
        │ │ i  ││                                                  ││ u  │ │
        │ │ t  ││                                                  ││ m  │ │
        │ │ l  ││                data                              ││ m  │ │
        │ │ e  ││                                                  ││ a  │ │
        │ │ s  ││                                                  ││ r  │ │
        │ │    ││                                                  ││ y  │ │
        │ │    ││                                                  ││    │ │
        │ └────┘└──────────────────────────────────────────────────┘└────┘ │
        │ ┌────┐┌──────────────────────────────────────────────────┐       │
        │ │  2 ││               bottom                             │       │
        │ └────┘└──────────────────────────────────────────────────┘       │
        │        <────────────────────────────────────────────────>        │
        └──────────────────────────────────────────────────────────────────┘
        1 = summary header
        2 = bottom title
        """
        
        # NOTE: weird shit happens if outer_frame is a 'Pane' (it's a pain... get it?)
        self.outer_frame = tk.Frame(frame, background="white")
        self.outer_frame.pack(expand=1, fill='both')

        # make the frames
        self.header_pane = Pane(self.outer_frame, background=FRAME_BACKGROUND)
        self.header_frame = self.header_pane.frame
        self.panes.append(self.header_pane)
        self.header_pane.canvas.config(background="white")

        summary_header_pane = Pane(self.outer_frame, background=FRAME_BACKGROUND)
        self.summary_header_frame = summary_header_pane.frame
        self.panes.append(summary_header_pane)

        titles_pane = Pane(self.outer_frame, background=FRAME_BACKGROUND)
        self.titles_frame = titles_pane.frame
        self.panes.append(titles_pane)

        data_pane = Pane(self.outer_frame, background=FRAME_BACKGROUND)
        self.data_pane = data_pane
        self.data_frame = data_pane.frame
        self.data_pane.canvas.config(background="white")
        self.panes.append(data_pane)

        summary_pane = Pane(self.outer_frame, background=FRAME_BACKGROUND)
        self.summary_frame = summary_pane.frame
        self.panes.append(summary_pane)

        bottom_title_pane = Pane(self.outer_frame, background=FRAME_BACKGROUND)
        self.bottom_title_frame = bottom_title_pane.frame
        self.panes.append(bottom_title_pane)

        self.bottom_pane = Pane(self.outer_frame, background=FRAME_BACKGROUND)
        self.bottom_frame = self.bottom_pane.frame
        self.panes.append(self.bottom_pane)
        self.bottom_pane.canvas.config(background="white")


        # make the scrollbars
        scrollbar = ttk.Scrollbar(self.outer_frame, orient="horizontal")
        horizontal_scrollable = (self.header_pane, titles_pane, data_pane, self.bottom_pane)

        self.data_pane.horizontal_scrollbar = scrollbar
        self.header_pane.horizontal_scrollbar = scrollbar
        self.bottom_pane.horizontal_scrollbar = scrollbar

        def sync_horizontal_scroll(*args):
            for w in horizontal_scrollable:
                w.xview(*args)

        scrollbar.config(command=sync_horizontal_scroll)
        for f in horizontal_scrollable:
            f.canvas.config(xscrollcommand=scrollbar.set)


        # configure the layout
        self.outer_frame.columnconfigure(0,weight=0)
        self.outer_frame.columnconfigure(1,weight=100)
        self.outer_frame.columnconfigure(2,weight=0)

        self.header_pane.grid(row=0, column=1, sticky='nsew', pady=PAD_ROW_0, padx=PAD_COL_1)
        summary_header_pane.grid(row=0, column=2, sticky='nsew', pady=PAD_ROW_0, padx=PAD_COL_2)
        titles_pane.grid(row=1, column=0, sticky='nsew', pady=PAD_ROW_1, padx=PAD_COL_0)
        data_pane.grid(row=1, column=1, sticky='nsew', pady=PAD_ROW_1, padx=PAD_COL_1)
        summary_pane.grid(row=1, column=2, sticky='nsew', pady=PAD_ROW_1, padx=PAD_COL_2)
        bottom_title_pane.grid(row=2, column=0, sticky='nsew', pady=PAD_ROW_2, padx=PAD_COL_0)
        self.bottom_pane.grid(row=2, column=1, sticky='nsew', pady=PAD_ROW_2,padx=PAD_COL_1)
        scrollbar.grid(row=3, column=1, sticky='nsew', padx=PAD_COL_1)

    # -----------------------------------------------------------------------------------------------------------------
    # make the header columns
    # -----------------------------------------------------------------------------------------------------------------
    def make_header_columns(self, col_merge: list):
        """
        Create disabled entry widgets for the columns (scrollable horizontally).

        Stores widgets in self.header_widgets and self.sub_header_widgets (lists)

        :param col_merge: a list of number of subheadings per heading
        """
        prop = ENTRY_PROPS.copy()
        prop['state'] = 'disabled'

        # merged header
        for i, header in enumerate(col_merge):

            prop['disabledbackground'] = HEADER_COLOUR2 if i % 2 else HEADER_COLOUR1
            prop['highlightbackground'] = HEADER_COLOUR2 if i % 2 else HEADER_COLOUR1

            # frame to hold the merged header, and the subheadings
            mini_frame = tk.Frame(self.header_frame)
            mini_frame.pack(side='left')
            mini_frame.configure(background=self.header_frame.cget("background"))

            # widget
            me = tk.Entry(mini_frame, **prop)
            me.pack(side='top', expand=0, fill='both', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

            # keep these widgets so that they can be configured later
            self.header_widgets.append(me)

            # subsections
            for sub_section in range(header):
                # frame within the mini-frame, so we can stack 'left'
                (hf2 := tk.Frame(mini_frame)).pack(side='left')
                hf2.configure(background=self.header_frame.cget("background"))

                # widget
                (se := tk.Entry(hf2, **prop)).pack(side='left', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

                # keep these widgets so that they can be configured later
                self.sub_header_widgets.append(se)

    # -----------------------------------------------------------------------------------------------------------------
    # summary header
    # -----------------------------------------------------------------------------------------------------------------
    def make_summary_header(self, summary_merge):
        """
        Create disabled entry widgets for summary header

        Stores widgets in self.summary_header_widgets and self.summary_sub_header_widgets (lists)

        :param summary_merge: a list of number of subheadings per heading
        """
        prop = ENTRY_PROPS.copy()
        prop['width'] = SUMMARY_WIDTH
        prop['disabledbackground'] = SUMMARY_HEADER_COLOUR
        prop['highlightbackground'] = SUMMARY_HEADER_COLOUR
        prop['state'] = 'disabled'

        for header in summary_merge:

            # frame to hold the totals header, and the subheadings
            (mini_frame := tk.Frame(self.summary_header_frame)).pack(side='left')
            mini_frame.configure(background=self.header_frame.cget("background"))

            # widget
            (me := tk.Entry(mini_frame, **prop)).pack(side='top', expand=0, fill='both', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

            # keep these widgets so that they can be configured later
            self.summary_header_widgets.append(me)

            for sub_section in range(header):
                # frame within the mini-frame so we can stack left
                (hf2 := tk.Frame(mini_frame)).pack(side='left')
                hf2.configure(background=self.header_frame.cget("background"))

                # widget
                (se := tk.Entry(hf2, **prop)).pack(side='left', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

                # keep these widgets so that they can be configured later
                self.summary_sub_header_widgets.append(se)

    # -----------------------------------------------------------------------------------------------------------------
    # row titles
    # -----------------------------------------------------------------------------------------------------------------
    def make_row_titles(self, rows):
        """
        For each row, create a disabled entry widget to describe each row

        Stores widgets in self.title_widgets (list)

         :param rows: number of rows
        """
        prop = ENTRY_PROPS.copy()
        prop['width'] = TITLE_WIDTH
        prop['justify'] = 'left'
        for _ in range(rows):
            re = tk.Entry(self.titles_frame, **prop, state='disabled', )
            re.pack(side='top', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

            self.title_widgets.append(re)

    # -----------------------------------------------------------------------------------------------------------------
    # data grid
    # -----------------------------------------------------------------------------------------------------------------
    def make_data_grid(self, rows, col_merge: list):
        """
        For each row and column, create an entry widget to hold data

        Stores widgets in self.entry_widgets                (dict[tuple[row,col], tk.Entry])
        Conversely stores row, col in self.widget_row_col   (dict[tk.Entry], tuple[row,col])

        :param rows: number of rows
        :param col_merge: a list of number of subheadings per heading
        """
        prop = ENTRY_PROPS.copy()

        for row in range(rows):
            (df1 := tk.Frame(self.data_frame)).pack(side='top', expand=1, fill='x')
            df1.configure(background=self.data_frame.cget("background"))

            # foreach header
            col: int = 0
            for column_index, header in enumerate(col_merge):
                prop['background'] = VERY_LIGHT_GREY if column_index%2 == 0 else BG_COLOUR
                prop['highlightbackground'] = VERY_LIGHT_GREY if column_index%2 == 0 else BG_COLOUR

                # subsections
                for subsection in range(header):
                    self.column_colours[col] = prop['highlightbackground']

                    # data entry box
                    de = entry_float(df1, textvariable=tk.StringVar(value=""), **prop)
                    de.pack(side='left', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

                    # save row/column with data entry, and vice versa
                    self.entry_widgets[row,col] = de
                    self.widgets_row_col[de] = row, col

                    # binding
                    de.bind("<Tab>", partial(self._move, 'nextCell'))
                    de.bind("<Key-Return>", partial(self._move, 'nextRow'))
                    de.bind("<Shift-Tab>", partial(self._move, 'prevCell'))
                    de.bind("<Key-Up>", partial(self._move, 'prevRow'))
                    de.bind("<Key-uparrow>", partial(self._move, 'prevRow'))
                    de.bind("<Key-Down>", partial(self._move, 'nextRow'))
                    de.bind("<Key-downarrow>", partial(self._move, 'nextRow'))

                    de.bind("<FocusIn>", partial(self.focus_changed, 'focusIn', colour=ROW_COL_INDICATOR_COLOUR))
                    de.bind("<Leave>", self.process_data_change)
                    de.bind("<FocusOut>", partial(self.focus_changed, 'focusOut'))
                    de.bindtags([*de.bindtags(), 1, 0, 2, 3])

                    col += 1

    # -----------------------------------------------------------------------------------------------------------------
    # summary
    # -----------------------------------------------------------------------------------------------------------------
    def make_summary_grid(self, rows, summary_merge):
        """
        create a list of disabled entry widgets to hold summary data per row

        Stores widgets in self.summary_widget (dict[tuple[row,col], tk.Entry]

        :param rows: number of rows
        :param summary_merge: a list of number of subheadings per heading
        """
        prop = ENTRY_PROPS.copy()
        prop['disabledbackground'] = SUMMARY_COLOUR
        prop['highlightbackground'] = SUMMARY_COLOUR
        prop['width'] = SUMMARY_WIDTH
        prop['state'] = 'disabled'

        for row in range(rows):
            (df1 := tk.Frame(self.summary_frame)).pack(side='top', expand=1, fill='x')
            df1.configure(background=self.header_frame.cget("background"))

            # foreach header
            col = 0
            for header in range(len(summary_merge)):

                # subsections
                for _ in range( summary_merge[header]):

                    # data entry box
                    (de := tk.Entry(df1, **prop)).pack(side='left', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

                    # save row/column with totals entry
                    self.summary_widgets[row,col] = de
                    col += 1

    # -----------------------------------------------------------------------------------------------------------------
    # bottom row header
    # -----------------------------------------------------------------------------------------------------------------
    def make_bottom_header(self):
        """
        Create ONE widget to store the title for the bottom row
        """
        prop = ENTRY_PROPS.copy()
        prop['width'] = TITLE_WIDTH

        # widget
        se = tk.Entry(self.bottom_title_frame, **prop, state='disabled')
        se.pack(side='left', expand=1,fill='both', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

        # keep these widgets so that they can be configured later
        self.bottom_title_widget = se


    # -----------------------------------------------------------------------------------------------------------------
    # bottom
    # -----------------------------------------------------------------------------------------------------------------
    def make_bottom(self, col_merge):
        """
        create a list of disabled widgets to hold the summary of the columns

        Stores widgets in self.bottom_widgets (list)

        :param col_merge: a list of number of subheadings per heading
        """

        # merged header
        prop = ENTRY_PROPS.copy()
        col = 0
        for column_index, header in enumerate(col_merge):
            for sub_section in range(header):

                # widget
                prop['disabledbackground'] = HEADER_COLOUR2 if column_index % 2 == 0 else HEADER_COLOUR1
                prop['highlightbackground'] = HEADER_COLOUR2 if column_index % 2 == 0 else HEADER_COLOUR1
                # change Colour every second merged header

                se = tk.Entry(self.bottom_frame, **prop, state='disabled', validate='key')
                se.pack(side='left', padx=ENTRY_PADDING,pady=ENTRY_PADDING)

                # keep these widgets so that they can be configured later
                self.bottom_widgets.append(se)
            col+=1

    # -----------------------------------------------------------------------------------------------------------------
    # populate: assign text variables to each of the entry widgets
    # -----------------------------------------------------------------------------------------------------------------
    def populate(self, header_text: list[str], balloon_text: list[str],
                 sub_header_text: list[str], title_text: list[str],
                 data_vars: dict[tuple[int,int],float], summary_header_texts: list[str],
                 summary_sub_texts: list[str], summary_vars: list[list[str]],
                 bottom_header_text: str, bottom_row_vars: list[str]):
        """
        Enter data into the entry widgets
        :param header_text: A list of major headings in the header frame
        :param balloon_text: A list of text giving further information about the heading
        :param sub_header_text: Sub headings of the header frame
        :param title_text: a list of text describing the title of the row
        :param data_vars: a dictionary where the key is the row,col and the value is the data
        :param summary_header_texts: a list of texts for the summary frame
        :param summary_sub_texts: a list of sub-texts for the summary frame
        :param summary_vars: a 2-d list of variables for the summary data
        :param bottom_header_text: a single string for a title defining the bottom row
        :param bottom_row_vars: a list of data for the bottom row
        :return:
        """
        balloon_text = list(balloon_text)

        # add the tool tips to the header
        for w,text in zip(self.header_widgets, balloon_text):
            if text != "":
                Hovertip(w,text=text)

        # bottom row
        self.bottom_title_widget.configure(textvariable=tk.StringVar(value=bottom_header_text))

        for c in range(len(self.bottom_widgets)):
            self.update_data('bottom',row=0, col=c, value=bottom_row_vars[c])

        # the summary header
        for col in range(self.num_summary_col):
            self.summary_header_widgets[col].configure(textvariable=tk.StringVar(value=summary_header_texts[col]))

        # the summary sub header
        for col in range(self.num_summary_sub_col):
            self.summary_sub_header_widgets[col].configure(textvariable=tk.StringVar(value=summary_sub_texts[col]))

            # the summary data
            for row in range(self.num_rows):
                self.update_data('summary', row, col, summary_vars[row][col])

        # the data grid
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                self.update_data('data', row, col, data_vars[row,col])


        # the header data
        i = 0
        for ht in header_text:
            self.header_widgets[i].configure(textvariable=tk.StringVar(value=ht))
            Hovertip(self.header_widgets[i], balloon_text[i])
            i += 1

        # the sub header data
        i = 0
        for sht in sub_header_text:
            if len(self.sub_header_widgets) > i:
                self.sub_header_widgets[i].configure(textvariable=tk.StringVar(value=sht))
                i += 1
            else:
                break

        # the row titles
        i = 0
        for rht in title_text:
            self.title_widgets[i].configure(textvariable=tk.StringVar(value=rht))
            i += 1

        # get the panes to match their internal structure
        for pane in self.panes:
            pane.after(10, lambda *_: pane.configure_interior(*_))

    # -----------------------------------------------------------------------------------------------------------------
    # navigation routines
    # -----------------------------------------------------------------------------------------------------------------
    def _move(self, where, ev):
        w: tk.Entry = ev.widget

        w.selection_clear()
        row, col = self.widgets_row_col.get(w, (0,0))

        if where == 'nextRow':
            row = min(max(row+1, 0), self.num_rows - 1)
        elif where == 'prevRow':
            row = min(max(row-1, 0), self.num_rows - 1)
        elif where == 'nextCell':
            col = min(max(col+1, 0), self.num_cols - 1)
        elif where == 'prevCell':
            col = min(max(col-1, 0), self.num_cols - 1)

        e = self.entry_widgets.get((row,col), None)
        if e is not None:
            self.set_focus(e)

        # forces Tk to not continue applying any binding routines after this
        return "break"

    # -----------------------------------------------------------------------------------------------------------------
    # what to do when the widget gets the focus
    # -----------------------------------------------------------------------------------------------------------------
    def set_focus(self, e):
        dx, dy = self.data_pane.see(e)
        self.bottom_pane.xview_moveto(dx)
        self.header_pane.xview_moveto(dx)

        e.focus()

    # -----------------------------------------------------------------------------------------------------------------
    # focus has changed - indicate what row/col we are on, callback process change
    # -----------------------------------------------------------------------------------------------------------------
    def focus_changed(self, inout, e, *_, colour = None):
        w: tk.Entry = e.widget
        if inout == "focusIn":
            w.selection_range(0, 'end')
        else:
            w.selection_clear()

        # set Colour and totals Colour
        dcolour = colour or BG_COLOUR
        tcolour = colour

        # get the widget
        r, c = self.widgets_row_col.get(w, (0,0))

        # set colors for rows (data)
        col_colour = Colour.add(dcolour, self.column_colours.get(c))
        for row in range(self.num_rows):
            wid = self.entry_widgets.get((row,c), None)
            if wid is not None:
                wid.configure(bg=col_colour)
                wid.configure(highlightbackground=col_colour)

        # set colors for cols (data)
        for col in range(self.num_cols):
            wid = self.entry_widgets.get((r,col), None)
            if wid is not None:
                col_colour = Colour.add(dcolour, self.column_colours.get(col))
                wid.configure(bg=col_colour)
                wid.configure(highlightbackground=col_colour)

        # set Colour for row header
        widget = self.title_widgets[r]
        widget.configure(disabledbackground=dcolour)
        widget.configure(highlightbackground=dcolour)

        # set colors for summary row
        if tcolour:
            tcolour = Colour.add(tcolour, SUMMARY_COLOUR)
        else:
            tcolour = SUMMARY_COLOUR

        for col in range(self.num_summary_sub_col):
            widget = self.summary_widgets[r,col]
            widget.configure(disabledbackground=tcolour)
            widget.configure(highlightbackground=dcolour)

        self.process_data_change()

    # -----------------------------------------------------------------------------------------------------------------
    # process a data change
    # -----------------------------------------------------------------------------------------------------------------
    def process_data_change(self, *_):
        if len(DATA_CHANGED) == 0:
            return

        for loc, v in DATA_CHANGED.items():
            r,c = loc
            w = self.entry_widgets.get((r, c), None)
            v_str = v.get().strip()
            try:
                if v_str == "":
                    self.process_data_change_handler(r,c,0)
                else:
                    value = float(v_str)
                    self.process_data_change_handler(r,c,value)
                    if value == 0:
                        v.set(value="")
                if w:
                    w.config(foreground=FG_COLOUR)

            except ValueError:
                print ("oh no", v_str)
                if w:
                    w.winfo_toplevel().bell()
                    w.after(100, lambda *args: w.winfo_toplevel().bell(), ())
                    w.after(200, lambda *_: w.winfo_toplevel().bell(), ())
                    w.after(300, lambda *_: w.winfo_toplevel().bell(), ())
                    w.config(foreground="red")
                    showerror("Bad input: ", message="You need to enter a valid float! ", detail=f" '{v_str}' is not a float",
                              icon='error')
                    v.set("")
                    w.focus_set()
                return

        DATA_CHANGED.clear()

    # -----------------------------------------------------------------------------------------------------------------
    # process a data update (can only update widgets in the data/summary/bottom panes
    # -----------------------------------------------------------------------------------------------------------------
    def update_data(self, which: Literal['data','summary','bottom'], row, col, value):
        if which == 'bottom':
            bw = self.bottom_widgets[col]
            bw.configure(textvariable=tk.StringVar(value=value))
            if self.bottom_cell_valid(value):
                bw.configure(highlightbackground=HEADER_COLOUR2)
                bw.configure(disabledbackground = HEADER_COLOUR2)
                if self.column_colours[col] == VERY_LIGHT_GREY:
                    bw.configure(highlightbackground=HEADER_COLOUR1)
                    bw.configure(disabledbackground=HEADER_COLOUR1)
            else:
                bw.configure(highlightbackground=NOT_OK_COLOUR)
                bw.configure(disabledbackground=NOT_OK_COLOUR)
                if self.column_colours[col] == VERY_LIGHT_GREY:
                    bw.configure(highlightbackground=NOT_OK_DARK_COLOUR)
                    bw.configure(disabledbackground=NOT_OK_DARK_COLOUR)

        elif which == 'data':
                widget = self.entry_widgets.get((row, col), None)
                if widget is not None:
                    value = value if float(value) != 0.0 else ""
                    var = tk.StringVar(value=value)
                    widget.configure(textvariable=var)
                    var.trace_add('write', partial(on_var_change, var, row, col))

        elif which == 'summary':
            widget = self.summary_widgets.get((row, col), None)
            if widget:
                widget.configure(textvariable=tk.Variable(value=value))
