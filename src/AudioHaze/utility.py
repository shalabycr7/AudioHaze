import tkinter.messagebox as messagebox
from tkinter import ttk

import pyttsx3
from PIL import Image, ImageTk

from AudioHaze.__main__ import HistoryWindow


def delete_entries(wid: ttk.Entry):
    wid.delete(0, 'end')


# check for input validation for float numbers only
def validation_callback(user_val: str) -> bool:
    try:
        if float(user_val) >= 0:
            return True
    except ValueError:
        if user_val == '':
            return True
    return False


# calculate audio file length
def output_duration(length: int) -> tuple:
    hours, remainder = divmod(length, 3600)
    minutes, seconds = divmod(remainder, 60)
    return hours, minutes, seconds


def open_history_window():
    HistoryWindow()


def add_img(name: str, row: int, column: int, frame: ttk.Frame):
    with Image.open(name) as load:
        width, height = load.size
        left, top, right, bottom = 0, 0, width, height
        im1 = load.crop((left, top, right, bottom))

        new_width, new_height = width - 100, height
        im1 = im1.resize((new_width, new_height))
        render = ImageTk.PhotoImage(im1)

        img = ttk.Label(frame, image=render, width=300)
        img.image = render
        img.grid(row=row, column=column)


def add_info_label(row: int, frame: ttk.Frame, date: str, amp: float, shift: float, speed: float, reverse: bool,
                   echo: bool):
    # information label
    label_frame = ttk.Frame(frame)
    label_frame.grid(row=row, column=0, sticky="nsew")
    ttk.Label(label_frame, text="\n\nDate: " + date[5:18] + "\n" +
                                "Amplitude: " + str(amp) + "\n" +
                                "Shift:         " + str(shift) + "\n" +
                                "Speed:      " + str(speed) + "\n" +
                                "Reverse:   " + str(reverse) + "\n" +
                                "Echo: " + str(echo),
              anchor='nw').pack(side="top")


def tts(speech: str):
    if speech is None or not speech.strip():
        messagebox.showinfo("Info", "Enter Some Text")
        return
    engine = pyttsx3.init()
    engine.setProperty('rate', 100)
    engine.say(speech)
    engine.runAndWait()
    engine.stop()


def update_menu_text(menu_button, selected_option):
    menu_button.configure(text=selected_option)


def enable_inputs(*inputs):
    # Enable input boxes
    for input_box in inputs:
        input_box.config(state="normal")


def disable_inputs(*inputs):
    # Disable input boxes
    for input_box in inputs:
        input_box.config(state="readonly")
