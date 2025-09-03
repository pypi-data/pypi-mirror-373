from typing import Optional

from . import FindImages
from tkinter import Frame, PhotoImage, Button, Label
import os
from functools import partial
from .idlelib_tooltip import Hovertip
from .InitGuiFontsAndColours import TkColours
import os

BUTTON_SIZE=24
BUTTON_BORDERWIDTH = 1


# TODO: Standardize the method for cget/configure between TableEntry,
#       dynamic entry, and ToolBar.  (Best? is DynamicTree)

class ToolBar(Frame):
    def __init__(self, parent, colours: Optional[TkColours] = None, **kwargs):
        super().__init__(master=parent, **kwargs)

        # define top level for this frame
        mw = self.master.winfo_toplevel()

        # set up default colours
        self.mw = mw
        if colours is not None:
            self.colours = colours
        else:
            self.colours = TkColours(mw)

        # default configuration
        self.config_options = ['button_hover_highlight', 'button_highlight', 'button_fg', 'button_bg']
        self.configure(bg=colours.WorkspaceColour)
        self.configure(button_hover_highlight=colours.ButtonHoverHighlight)
        self.configure(button_highlight=colours.WorkspaceColour)
        self.configure(button_bg=colours.ButtonBackground)
        self.configure(button_fg=colours.ButtonForeground)

        # user configuration
        for k,v in kwargs.items():
            self.configure(**{k:v})

        self.images = list()

        # some defaults
        image_dir = FindImages.get_image_dir()

        self.defaults = {
            'image': os.path.join(image_dir, 'default.gif')
        }

        # buttons
        self.buttons: dict[str, Button] = {}

    def configure(self, **kwargs):
        # https://stackoverflow.com/a/70568930
        # workaround to tkinter seemingly not having ConfigSpecs
        for key in self.config_options:
            if key in kwargs:
                setattr(self, key, kwargs.pop(key))
        if kwargs:
            super().configure(**kwargs)

    def config(self, **kwargs):
        self.configure(**kwargs)

    def cget(self, key):
        # if key in self.config_options:
        #     print (f"{key=}")
        return getattr(self, key, None) if key in self.config_options \
            else super().cget(key)

    def add(self, **details):
        """Adds a button

        ---
        Parameters:
            - name     : str
            - image    : str (Path)
            - command  : method
            - hint     : str
            - shortcut : str
            - disabled : bool
        """

        btn_height = 20
        btn_width = 20

        # define inputs and defaults
        image_file = details.get('image', '')
        if not os.path.exists(image_file) or not os.path.isfile(image_file):
            image_file = self.defaults['image']

        name = details.get('name', os.path.basename(image_file))
        callback: callable = details.get('command', lambda *_, **__: None)
        hint = details.get('hint', '')
        shortcut_key = details.get('shortcut', [])
        disabled = details.get('disabled', False)

        # define image
        image = PhotoImage(file=image_file)

        # if the image is larger than the button, roughly scale it down, so it's not auto-cropped
        # NOTE: have to save the image in object instance so that the ref does not get removed
        if btn_width < image.width() or btn_height < image.height():
            image = image.subsample(round(image.width() / btn_width),
                                    round(image.height() / btn_height))
        self.images.append(image)

        # add button
        b = Button(
            master=self,
            text=name,
            image=image,
            relief='ridge',
            bg=self.cget("button_bg"),
            activebackground=self.cget("button_bg"),
            highlightbackground=self.cget("button_highlight"),

            fg=self.cget("button_fg"),
            width=BUTTON_SIZE,
            height=BUTTON_SIZE,
            highlightthickness=BUTTON_BORDERWIDTH,
        )
        b.pack(side='left',ipadx=0, ipady=0)
        self.buttons[name] = b

        # weird behaviour, using 'command=' doesn't work, but this does
        b.bind('<Button-1>', callback)

        # add the tooltip
        if hint:
            Hovertip(b, hint, 1000)

        # make the button slightly raised when mouse hovers
        # pass image to stop it from being destroyed when this method ends
        b.bind('<Enter>', partial(button_enter, b, self.cget("button_hover_highlight"), self.mw, image), True)
        b.bind('<Leave>', partial(button_leave, b, self.cget("button_highlight"), self.mw, image), True)

        # add the bindings for key presses
        if shortcut_key:
            for sk in shortcut_key:
                self.mw.bind(f"<{sk}>", partial(lambda *_: b.invoke(), b))

        # disable the button?
        if disabled:
            b.configure(state='disabled')

    def bar(self):
        """Add a divider on the _toolbar"""
        Label(self, text='', bg=self.cget('bg'), relief='raised', borderwidth=1) \
            .pack(side='left', padx=3)

    def enable(self, button):
        """Enable a button"""
        self._state(1, button)

    def disable(self, button):
        """Disable a button"""
        self._state(0, button)

    def _state(self, action, name):
        if name in self.buttons and isinstance(self.buttons[name], Button):
            self.buttons[name].configure(state='normal' if action else 'disabled')


def button_enter(b: Button, highlight_color, mw, *_):
    b.configure(highlightbackground=highlight_color)
    mw.update()


def button_leave(b: Button, highlight_color, mw, *_):
    b.configure(highlightbackground = highlight_color)
    mw.update()
