from tkinter import *

MOVABLE_TAG_NAME = "movable"


def main():
    mw: Tk = Tk()

    canvas: Canvas = Canvas(mw)
    canvas.pack(expand=1, fill='both')


    canvas.tag_bind(MOVABLE_TAG_NAME, "<Button-1>", lambda e: select_gui_block_to_move(canvas, e))

    r1: int = canvas.create_rectangle(50, 50, 150, 150, fill='blue', tags=(MOVABLE_TAG_NAME, "obj1"))
    s1: int = canvas.create_text(100, 100, text="A", tags=(MOVABLE_TAG_NAME, "obj1"))
    r2: int = canvas.create_rectangle(70, 70, 170, 170, fill='red', tags=(MOVABLE_TAG_NAME, "obj2"))
    s2: int = canvas.create_text(120, 120, text="B", tags=(MOVABLE_TAG_NAME, "obj2"))
    mw.mainloop()


def select_gui_block_to_move(canvas: Canvas, event: Event):
    obj: tuple[int, ...] = canvas.find_withtag('current')
    print(obj)
    current_tags = canvas.gettags(obj[0])
    print(current_tags)
    tags: tuple[str] = tuple(filter(lambda x: x != MOVABLE_TAG_NAME and x != 'current', canvas.gettags(obj[0])))
    print(tags)
    canvas.tag_raise(tags, 'all')

    # unbind any previous binding for clicking and motion, just in case
    canvas.bind("<Motion>", "")
    canvas.bind("<ButtonRelease-1>", "")
    canvas.tag_bind(MOVABLE_TAG_NAME, "<Button-1>", "")

    # bind for mouse motion
    canvas.bind("<Motion>",
                lambda e: gui_block_is_moving(canvas, tags[0], event.x, event.y, e))

    # bind for release of mouse up
    canvas.bind("<ButtonRelease-1>", lambda e: gui_block_has_stopped_moving(canvas, tags[0], e))


def gui_block_is_moving(canvas, tag, x, y, event):
    # unbind moving while we process
    canvas.bind("<Motion>", "")

    # move the widget
    canvas.move(tag, event.x - x, event.y - y)

    # rebind for motion
    canvas.bind("<Motion>",
                lambda e: gui_block_is_moving(canvas, tag, event.x, event.y, e))


def gui_block_has_stopped_moving(canvas, tag, event):
    canvas.tag_bind(MOVABLE_TAG_NAME, "<Button-1>", lambda e: select_gui_block_to_move(canvas, e))
    canvas.bind("<Motion>", "")
    canvas.bind("<ButtonRelease-1>", "")


if __name__ == "__main__":
    main()

