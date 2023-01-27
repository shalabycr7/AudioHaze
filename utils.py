from tkinter.constants import END
import winsound


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
