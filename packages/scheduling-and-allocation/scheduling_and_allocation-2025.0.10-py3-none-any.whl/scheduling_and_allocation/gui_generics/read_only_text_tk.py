from typing import Literal
import tkinter as tk
from ..modified_tk import Scrolled

SCROLLBAR_DIR = Literal["s", "w", "e", "n", "se", "sw", "ne", "nw"]

# =====================================================================================================================
# create some text info that is read only
# =====================================================================================================================
class ReadOnlyTextTk:
    def __init__(self, frame, text: list[str] = None,
                 height: int = 20, width: int = 50,
                 scrollbars: SCROLLBAR_DIR = 'se',
                 wrap="none"):
        """
        :param frame: the container where the text widget will be placed
        :param text: the text to display (list)
        :param height: height of text box
        :param width: width of text box
        :param scrollbars: scrollbars ?
        :param wrap: do you want the text to wrap-around?
        """

        # remove any pre-existing widgets in this frame
        for w in frame.winfo_children():
            w.destroy()

        s: Scrolled = Scrolled(
            frame,
            'Text',
            height=height,
            width=width,
            scrollbars=scrollbars,
            wrap=wrap
        )
        s.pack(expand=True, fill="both")
        self.textbox: tk.Text = s.widget
        if text is not None:
            self.write(text)
        self.textbox.config(state="disabled")

    def write(self, text):
        self.textbox.config(state="normal")
        self.textbox.delete("1.0", "end")
        for txt in text:
            self.textbox.insert('end', txt + "\n")
        self.textbox.config(state="disabled")
