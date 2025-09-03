import platform
import tkinter
import tkinter as tk
import tkinter.font

root = tk.Tk()
root.geometry("300x200")

e = tk.Entry(root)
my_default_font=e.cget("font")
default_font = tk.font.nametofont(my_default_font)
print(default_font.actual())


times = []
for h in range(0,24):
    for m in (0,15,30,45):
        times.append(f"{h:2d}:{m:02d}")
print(times)
time_index = 1

# Create multiple widgets
frame = tk.Frame(root, background='pink')
frame.pack()
the_time = tkinter.Variable()
entry = tk.Entry(frame, textvariable=the_time, width=10)
entry.pack(padx=10, pady=5,side='left')
word_text = tk.Text(frame, wrap='word', padx=10, pady=10, height=6, width=10)
word_text.pack( padx=10, pady=5, side='left')
word_text.config(state='disabled')

def _zoom(event: tk.Event=None):
    global time_index
    if event is not None:
        if event.delta > 0 or event.keysym=='Up' or event.keysym=="KP_Up":
            time_index -= 1
        elif event.delta < 0 or event.keysym=='Down'or event.keysym=="KP_Down":
            time_index+= 1
    time_index = time_index%len(times)
    the_time.set(times[time_index])

    # Insert text sections
    word_text.config(state='normal')
    word_text.delete('1.0','end')
    word_text.insert('end', times[(time_index-2)%len(times)]+'\n')
    word_text.insert('end', times[(time_index-1)%len(times)]+'\n')
    word_text.insert('end', times[time_index%len(times)]+'\n')
    word_text.insert('end', times[(time_index+1)%len(times)]+'\n')
    word_text.insert('end', times[(time_index+2)%len(times)])
    word_text.tag_add('small', '1.0', '1.end')
    word_text.tag_add('med', '2.0', '2.end')
    word_text.tag_add('big', '3.0', '3.end')
    word_text.tag_add('med', '4.0', '4.end')
    word_text.tag_add('small', '5.0', '5.end')
    word_text.tag_config('big', font='arial 20 bold', lmargin1=10)  # Set font, size and style
    word_text.tag_config('small', font='arial 10')  # Set font, size and style
    word_text.tag_config('med', lmargin1=5)  # Set font, size and style
    word_text.config(state='disabled')

    root.bell()
def what_key(event: tk.Event):
    print(event)

if platform.system() == "Linux":
    print ("linux")
    word_text.bind('<4>', _zoom)
    word_text.bind('<5>', _zoom)
else:
    word_text.bind('<MouseWheel>', _zoom)
    word_text.bind('<Key>', _zoom)

_zoom()

# Tag and style text sections


tk.mainloop()