from tkinter import ttk
from tkinter.constants import END, NW

import winsound
from PIL import Image, ImageTk

def delete_entries(wid):
    wid.delete(0, END)


# clear the frame when we add another plot.
def update_frame(obj):
    if len(obj.winfo_children()) >= 1:
        obj.winfo_children()[0].destroy()


# check for input validation for float numbers only
def validation_callback(user_val):
    try:
        if float(user_val) >= 0:
            return True
    except ValueError:
        if user_val == '':
            return True
    return False


# calculate audio file length
def output_duration(length):
    hours = length // 3600  # calculate in hours
    length %= 3600
    minutes = length // 60  # calculate in minutes
    length %= 60
    seconds = length  # calculate in seconds
    return hours, minutes, seconds


def stop_audio():
    winsound.PlaySound(None, winsound.SND_FILENAME)


def add_img(name, row, column, frame):
    load = Image.open(name)
    width, height = load.size
    # Setting the points for cropped image
    left = 0
    top = 0
    right = width
    bottom = height
    # Cropped image of above dimension (It will not change original image)
    im1 = load.crop((left, top, right, bottom))
    new_size = (width - 100, height)
    im1 = im1.resize(new_size)
    render = ImageTk.PhotoImage(im1)
    img = ttk.Label(frame, image=render, width=300)
    img.image = render
    img.grid(row=row, column=column)


def add_info_label(row, frame, date, amp, shift, speed, reverse, echo):
    # information label
    label_frame = ttk.Frame(frame)
    label_frame.grid(row=row, column=0, sticky="nsew")
    ttk.Label(label_frame, text="").pack(side="top")
    ttk.Label(label_frame, text="").pack(side="top")
    ttk.Label(label_frame, text="Date: " + date[5:18]).pack(side="top", anchor=NW)
    amp_lib = ttk.Label(label_frame, text="Amplitude: " + str(amp))
    shift_lib = ttk.Label(label_frame, text="Shift:         " + str(shift))
    speed_lib = ttk.Label(label_frame, text="Speed:      " + str(speed))
    reverse_lib = ttk.Label(label_frame, text="Reverse:   " + str(bool(reverse)))
    ttk.Label(label_frame, text="Echo: " + str(bool(echo))).pack(side="top", anchor=NW)
    amp_lib.pack(side="top", anchor=NW)
    shift_lib.pack(side="top", anchor=NW)
    speed_lib.pack(side="top", anchor=NW)
    reverse_lib.pack(side="top", anchor=NW)
