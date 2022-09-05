import os
import struct
import wave
from ctypes import windll
from tkinter import filedialog, messagebox

import matplotlib
import numpy as np
import pyttsx3
import ttkbootstrap as ttk
import winsound
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pydub import AudioSegment
from scipy import signal
from ttkbootstrap import Style, Toplevel, END

from AudioLib.AudioProcessing import AudioProcessing

current_style = Style(theme='cosmo')  # set main theme
root = current_style.master

# icons
dark_icon = ttk.PhotoImage(file='icons/darkIcon.png')
import_icon = ttk.PhotoImage(file='icons/importIcon.png')
play_icon = ttk.PhotoImage(file='icons/playIcon.png')
stop_icon = ttk.PhotoImage(file='icons/stopIcon.png')
conv_icon = ttk.PhotoImage(file='icons/convIcon.png')
tts_icon = ttk.PhotoImage(file='icons/ttsIcon.png')
white_icon = ttk.PhotoImage(file='icons/whiteIcon.png')

# global variables
hasImported = False  # checks if a file has been imported
file_directory = "/"
directory_name = "Audio Output"
dark_mode_state = False
nChannels = 1
sampleRate = 1
num_of_frames = 1
result = [0, 0]
timeout = 0
data_out = 1
og_plot_showed = False
mod_plot_showed = False
plotting_figure = Figure()
figure_subplot = plotting_figure.add_subplot()

# UI elements
darkBtn = ttk.Button(root, image=dark_icon, style='Link.TButton')
wvFr = ttk.Frame(root, height=190, width=770)
wvFrMod = ttk.Frame(root, height=190, width=770)
length_lb = ttk.Label(root, font=("Barlow", 17))
conv_signal_frame = ttk.Frame()
mod_signal_frame = ttk.Frame()
ttk.Separator(root, orient='vertical', style='info.Vertical.TSeparator').place(x=630, y=200)


def display_elements():
    darkBtn.place(x=970, y=55)
    wvFr.place(x=37, y=240)
    wvFrMod.place(x=37, y=470)
    length_lb.place(x=530, y=205)
    return


display_elements()


def make_output_directory():
    """
    Create directory ,it's a directory name which you are going to create, try and catch block use to handle the
    exceptions.
    """
    try:
        os.mkdir(directory_name)
    except FileExistsError:
        return
    return


make_output_directory()

# set title and fav icon
root.title(' Audio Signal Manipulation')
root.iconbitmap('icons/picon.ico')
# make the window not resizable
root.resizable(False, False)
# window dimensions
window_width = 1200
window_height = 700
# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# find the center point
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')


# update the plotting frame
def update_frame(obj):
    # clear the frame when we add another plot
    for wid in obj.winfo_children():
        wid.destroy()
    return


# read the Audio Output file
def read_file(file):
    # minus one here means that all the frames of Audio Output has to be read
    raw = file.readframes(-1)
    # get the number of channels in the wave
    global nChannels
    nChannels = file.getnchannels()
    # sign it with 16-bit integers since wave files are encoded with 16 bits per sample
    global data
    data = np.frombuffer(raw, "int16")
    global sampleRate
    sampleRate = file.getframerate()
    global num_of_frames
    num_of_frames = file.getnframes()
    # get the duration of the audio file
    duration = num_of_frames / float(sampleRate)
    hours, minutes, seconds = output_duration(int(duration))
    total_time = '{}:{}:{}'.format(hours, minutes, seconds)
    length_lb.config(text=total_time)

    time = np.linspace(0, len(data) / sampleRate, num=len(data))
    return time, data


# creat another figure to hold the plot of the ave file to display it in GUI
def create_plot_fig():
    global plotting_figure
    global figure_subplot
    print("y")
    # Apply dark mode on the plot
    if not dark_mode_state:
        matplotlib.style.use('dark_background')
    else:
        matplotlib.style.use('default')
    plotting_figure = Figure(figsize=(7, 2), dpi=110)
    figure_subplot = plotting_figure.add_subplot(111)
    figure_subplot.set_ylabel("Amplitude")
    figure_subplot.grid(alpha=0.4)
    return


def play_audio(indication):
    if hasImported:
        if indication == 'OG':
            audio_file = file_directory
        else:
            audio_file = directory_name + '/Modified.wav'
        winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        print(darkBtn.state())
        messagebox.showinfo("Warning", "Please Import Audio File First")
    return


def stop_audio():
    winsound.PlaySound(None, winsound.SND_FILENAME)
    return


def set_theme():
    stop_audio()
    global dark_mode_state
    global darkBtn
    global wvFr
    global wvFrMod

    if dark_mode_state:
        Style(theme='cyborg')
        darkBtn.config(image=white_icon)
        dark_mode_state = False
    else:
        Style(theme='cosmo')
        darkBtn.config(image=dark_icon)
        dark_mode_state = True

    current_style.configure('TLabel', font=('Barlow', 12))
    current_style.configure('TRadiobutton', font=('Barlow', 12))
    current_style.configure('TButton', width=7, font=("Barlow", 13))
    current_style.configure('TMenubutton', font=("Barlow", 13))
    current_style.configure('TNotebook.Tab', font=("Barlow", 12))
    update_frame(wvFr)
    update_frame(wvFrMod)
    if og_plot_showed:
        plotting(result[0], result[1], wvFr, "Original Audio")
    if mod_plot_showed:
        plotting(timeout, data_out, wvFrMod, "Modified Audio")
    return


set_theme()

darkBtn.config(command=set_theme)


def output_duration(length):
    hours = length // 3600  # calculate in hours
    length %= 3600
    minutes = length // 60  # calculate in minutes
    length %= 60
    seconds = length  # calculate in seconds

    return hours, minutes, seconds


# import Audio Output file
def import_file():
    global og_plot_showed
    global mod_plot_showed
    og_plot_showed = False
    mod_plot_showed = False

    stop_audio()
    update_frame(wvFr)
    update_frame(wvFrMod)
    # open window to select the wav file and get the path to the Audio Output dile then save in variable directory
    filename = filedialog.askopenfilename(initialdir="\\", title="Select Audio File", filetypes=(("Wav", "*wav"),))
    global file_directory
    file_directory = str(filename)
    if file_directory == '':
        messagebox.showinfo("info", "No File Was Selected")
    else:
        global wav_file
        wav_file = wave.open(file_directory, 'r')
        global result
        result = read_file(wav_file)
        global hasImported
        hasImported = True
        # Update displayed File info
        wav_d = AudioSegment.from_file(file=file_directory, format="wav")
        max_amp = wav_d.max
        fileTypeVal.config(text='wav File')
        channelsVal.config(text=nChannels)
        frameRateVal.config(text=sampleRate)
        ampVal.config(text=max_amp)
        plotting(result[0], result[1], wvFr, "Original Audio")
        og_plot_showed = True
        # Set echo options on if the file is stereo
        if nChannels == 2:
            echoTrueVal.config(state='!selected')
            echoFalseVal.config(state='!selected')
        else:
            echoTrueVal.config(state='disabled')
            echoFalseVal.config(state='disabled')


def operations(amp_amount, shift_amount, speed_amount, reverse_state, echo_state):
    update_frame(wvFrMod)
    out_file = directory_name + "\\Modified.wav"
    audio_obj = wave.open(out_file, 'wb')
    audio_obj.setnchannels(nChannels)
    audio_obj.setsampwidth(2)

    # speed OP
    speed_factor = speed_amount
    speed = sampleRate * speed_factor
    audio_obj.setframerate(speed)
    # Shift OP
    pov_shift_in_sec = shift_amount
    for i in range(int(sampleRate * pov_shift_in_sec)):
        zero_in_byte = struct.pack('<h', 0)
        audio_obj.writeframesraw(zero_in_byte)
    # Amplification OP
    amp = amp_amount
    n = len(data)
    # Reverse OP
    reverse = reverse_state
    if reverse:
        for i in range(data.__len__()):
            two_byte_sample = data[n - 1 - i] * amp
            if two_byte_sample > 32760:
                two_byte_sample = 32760
            if two_byte_sample < -32760:
                two_byte_sample = -32760
            sample = struct.pack('<h', int(two_byte_sample))
            audio_obj.writeframesraw(sample)
    else:
        for i in range(data.__len__()):
            two_byte_sampler = data[i] * amp
            if two_byte_sampler > 32760:
                two_byte_sampler = 32760
            if two_byte_sampler < -32760:
                two_byte_sampler = -32760
            sample = struct.pack('<h', int(two_byte_sampler))
            audio_obj.writeframesraw(sample)

    audio_obj.close()
    wav_file.close()
    obj = wave.open(directory_name + '\\Modified.wav', 'rb')  # open
    global data_out
    data_out = obj.readframes(-1)  # get all the frames in data out
    data_out = np.frombuffer(data_out, "int16")  # set the data to a number of two byte form data out
    sample_rate_out = obj.getframerate()  # frame rate HZ (number of frames to be reads in seconds)
    global timeout
    timeout = np.linspace(0, len(data_out) / sample_rate_out, len(data_out))  # time of the output
    plotting(timeout, data_out, wvFrMod, "Modified Audio")
    global mod_plot_showed
    mod_plot_showed = True
    # set the echo based on state
    if echo_state:
        sound1 = AudioProcessing(directory_name + '\\Modified.wav')
        sound1.set_echo(0.4)
        sound1.save_to_file(directory_name + '\\Modified.wav')
    obj.close()
    wav_file.close()
    return


def apply_operations():
    stop_audio()
    if hasImported and (ampValueLB.get() != "" and shiftValueLB.get() != "" and speedValueLB.get() != ""):
        amp_amount = float(ampValueLB.get())
        shift_amount = float(shiftValueLB.get())
        speed_amount = float(speedValueLB.get())
        reverse_val = str(revText.get())
        echo_val = str(echoText.get())
        if reverse_val == '1':
            reverse_st = True
        else:
            reverse_st = False
        if echo_val == '3' and nChannels == 2:
            echo_state = True
        else:
            echo_state = False
        operations(amp_amount, shift_amount, speed_amount, reverse_st, echo_state)
    else:
        messagebox.showinfo("Warning", "Please Import Audio File First And Set The Values")


# header buttons
ttk.Button(root, text='  Import', command=import_file, image=import_icon, compound=ttk.LEFT, ).place(x=1050, y=55)

# header section
ttk.Label(root, text='Signal Processing with Python', font=("Barlow", 20)).place(x=37, y=17)
ttk.Label(root, text='Audio File Overview', font=("Barlow", 17)).place(x=37, y=65)

# file info section
fileTypeFr = ttk.Frame(root, height=100, width=215)
fileTypeFr.place(x=37, y=100)
folderIcon = ttk.PhotoImage(file='icons/icon1.png')
ttk.Label(fileTypeFr, image=folderIcon).place(x=0, y=10)
fileTypeVal = ttk.Label(fileTypeFr, text='Unknown', font=("Abel", 13))
fileTypeVal.place(x=75, y=20)
ttk.Label(fileTypeFr, text='Type Of Audio File', font=("Actor", 12)).place(x=75, y=50)

channelFr = ttk.Frame(root, height=100, width=215)
channelFr.place(x=270, y=100)
channelsIcon = ttk.PhotoImage(file='icons/icon2.png')
ttk.Label(channelFr, image=channelsIcon).place(x=0, y=10)
channelsVal = ttk.Label(channelFr, text='0', font=("Abel", 13))
channelsVal.place(x=75, y=20)
ttk.Label(channelFr, text='Channels', font=("Actor", 12)).place(x=75, y=50)

frameRateFr = ttk.Frame(root, height=100, width=215)
frameRateFr.place(x=493, y=100)
frameRateIcon = ttk.PhotoImage(file='icons/icon3.png')
ttk.Label(frameRateFr, image=frameRateIcon).place(x=0, y=10)
frameRateVal = ttk.Label(frameRateFr, text='0', font=("Abel", 13))
frameRateVal.place(x=75, y=20)
ttk.Label(frameRateFr, text='Frame Rate', font=("Actor", 12)).place(x=75, y=50)

ampFr = ttk.Frame(root, height=100, width=220)
ampFr.place(x=716, y=100)
ampIcon = ttk.PhotoImage(file='icons/icon4.png')
ttk.Label(ampFr, image=ampIcon).place(x=0, y=10)
ampVal = ttk.Label(ampFr, text='0', font=("Abel", 13))
ampVal.place(x=75, y=20)
ttk.Label(ampFr, text='Maximum Amplitude', font=("Actor", 12)).place(x=75, y=50)

# Waveform section
ttk.Label(root, text='Audio Wave Form', font=("Barlow", 17)).place(x=37, y=200)

# tasks section
ttk.Label(root, text='Tasks', font=("Barlow", 17)).place(x=900, y=280)
ttk.Separator(root, orient='vertical', style='info.Vertical.TSeparator').place(x=980, y=280)
ttk.Frame(root, height=300, width=270).place(x=900, y=320)

# Task labels
ttk.Label(root, text='Amplitude').place(x=915, y=345)
ampText = ttk.StringVar()
ampValueLB = ttk.Entry(root, justify="center", textvariable=ampText, width=15, font=("Barlow", 10))
ampValueLB.place(x=1015, y=345)
ttk.Label(root, text='Shift', ).place(x=915, y=385)

shiftText = ttk.StringVar()
shiftValueLB = ttk.Entry(root, justify="center", textvariable=shiftText, width=15, font=("Barlow", 10))
shiftValueLB.place(x=1015, y=385)

ttk.Label(root, text='Speed', ).place(x=915, y=425)
speedText = ttk.StringVar()
speedValueLB = ttk.Entry(root, justify="center", textvariable=speedText, width=15, font=("Barlow", 10))
speedValueLB.place(x=1015, y=425)

ttk.Label(root, text='Reverse', ).place(x=915, y=465)
revText = ttk.StringVar()
reverseTrueVal = ttk.Radiobutton(root, style='primary.TRadiobutton', text="True", variable=revText, value=1)
reverseTrueVal.place(x=1055, y=470)
reverseFalseVal = ttk.Radiobutton(root, style='primary.TRadiobutton', text="False", variable=revText, value=2, )
reverseFalseVal.place(x=1055, y=500)

ttk.Label(root, text='Echo', ).place(x=915, y=530)
echoText = ttk.StringVar()
echoTrueVal = ttk.Radiobutton(root, style='TRadiobutton', text="True", variable=echoText, value=3)
echoTrueVal.place(x=1055, y=540)
echoFalseVal = ttk.Radiobutton(root, style='primary.TRadiobutton', text="False", variable=echoText, value=4, )
echoFalseVal.place(x=1055, y=570)

# Tasks buttons
ttk.Button(root, padding=(15, 8), style='success.Outline.TButton', text='Apply', command=apply_operations).place(x=940,
                                                                                                                 y=630)

# Play buttons
ttk.Button(root, text='  Play', command=lambda: play_audio('mod'), image=play_icon, compound=ttk.LEFT, ).place(x=1050,
                                                                                                               y=630)
ttk.Button(root, text='  Play', command=lambda: play_audio('OG'), image=play_icon, compound=ttk.LEFT, ).place(x=790,
                                                                                                              y=200)
ttk.Button(root, text='  Stop', style='danger.TButton', command=lambda: stop_audio(), image=stop_icon,
           compound=ttk.LEFT, ).place(x=650,
                                      y=200)


# Plot the convolution signal
def plotting_convolution(targeted_signal, place, title):
    create_plot_fig()
    figure_subplot.set_title(title)
    figure_subplot.plot(targeted_signal, color='blue')
    canvas = FigureCanvasTkAgg(plotting_figure, master=place)
    canvas.draw()
    get_widget = canvas.get_tk_widget()
    get_widget.pack()
    return


# plot the Audio Output data
def plotting(time, raw, place, title):
    create_plot_fig()
    # plot the wave
    figure_subplot.set_title(title)
    figure_subplot.plot(time, raw, color='blue')
    # Creating Canvas to show it in the Frame
    canvas = FigureCanvasTkAgg(plotting_figure, master=place)
    canvas.draw()
    get_widget = canvas.get_tk_widget()
    get_widget.pack()
    return


# Delete the values from the textbox
def delete_entries(wid):
    wid.delete(0, END)


def lti_sys(widget):
    if widget == 1:
        # get the values of the textbox as an array
        num = list(map(int, trFuncValueLB.get().strip().split()))
        den = list(map(int, tr_func_value_lb2.get().strip().split()))
        # represent the lti_system as transfer function
        lti_system = signal.lti(num, den)
        # display the values in the textbox after rounding
        for z in lti_system.zeros:
            z_rounded = np.round(z, 2)
            zeros_val_lb.insert(0, str(z_rounded) + "  ")
        for p in lti_system.poles:
            p_rounded = np.round(p, 2)
            poles_val_lb.insert(0, str(p_rounded) + "  ")

    else:
        zeros = list(map(complex, zeros_val_lb.get().strip().split()))
        poles = list(map(complex, poles_val_lb.get().strip().split()))
        # get the num and den from the z and p
        hs_rep = signal.zpk2tf(zeros, poles, k=1)
        for z in hs_rep[0]:
            z_rounded = np.round(z, 2)
            trFuncValueLB.insert(0, str(z_rounded) + "  ")
        for p in hs_rep[1]:
            p_rounded = np.round(p, 2)
            tr_func_value_lb2.insert(0, str(p_rounded) + "  ")


def apply_convolution(conv_val):
    update_frame(mod_signal_frame)
    update_frame(conv_signal_frame)
    # get the value of the option radiobutton
    option_val = str(zp_to_hs_text.get())
    if option_val == '1':
        # update the values each time the button is pressed
        delete_entries(zeros_val_lb)
        delete_entries(poles_val_lb)
        zeros_val_lb.config(state="normal")
        poles_val_lb.config(state="normal")
        if trFuncValueLB.get() != "" and tr_func_value_lb2.get() != "":
            lti_sys(1)
    if option_val == '2':
        delete_entries(trFuncValueLB)
        delete_entries(tr_func_value_lb2)
        trFuncValueLB.config(state="normal")
        tr_func_value_lb2.config(state="normal")
        if zeros_val_lb.get() != "" and poles_val_lb.get() != "":
            lti_sys(2)

    if conv_val == 'Sine Wave':
        win = signal.windows.hann(50)
        plotting_convolution(win, mod_signal_frame, 'Impulse Response')
        filtered = signal.convolve(sig, win, mode='same') / sum(win)
        plotting_convolution(filtered, conv_signal_frame, 'Filtered Signal')
        select_wave_menu.config(text="Sine Wave")
    if conv_val == 'Rec Wave':
        win = np.repeat([0., 1., 0.], 50)
        plotting_convolution(win, mod_signal_frame, 'Impulse Response')
        filtered = signal.convolve(sig, win, mode='same') / sum(win)
        plotting_convolution(filtered, conv_signal_frame, 'Filtered Signal')
        select_wave_menu.config(text="Rec Wave")


# disable and enable the desired textbox based on the state of the option radiobutton
def disable_box(num):
    delete_entries(zeros_val_lb)
    delete_entries(poles_val_lb)
    delete_entries(trFuncValueLB)
    delete_entries(tr_func_value_lb2)
    if num == 1:
        zeros_val_lb.config(state="readonly")
        poles_val_lb.config(state="readonly")
        trFuncValueLB.config(state="normal")
        tr_func_value_lb2.config(state="normal")
    else:
        trFuncValueLB.config(state="readonly")
        tr_func_value_lb2.config(state="readonly")
        zeros_val_lb.config(state="normal")
        poles_val_lb.config(state="normal")


# Convolution PopUp
def open_conv_window():
    stop_audio()
    # be treated as a new window
    new_conv_window = Toplevel(root)
    new_conv_window.title("Convolution")
    new_conv_window.iconbitmap('./icons/picon.ico')
    new_conv_window.resizable(False, False)
    new_conv_window.geometry("1200x740")
    # Three plotting frames
    global og_signal_frame
    og_signal_frame = ttk.Frame(new_conv_window, height=190, width=770)
    og_signal_frame.place(x=10, y=10)
    global mod_signal_frame
    mod_signal_frame = ttk.Frame(new_conv_window, height=190, width=770)
    mod_signal_frame.place(x=10, y=250)
    global conv_signal_frame
    conv_signal_frame = ttk.Frame(new_conv_window, height=190, width=770)
    conv_signal_frame.place(x=10, y=490)

    tabs_fr = ttk.Frame(new_conv_window, height=700, width=350)
    tabs_fr.place(x=800, y=10)
    notebook = ttk.Notebook(tabs_fr)
    notebook.pack(pady=10, expand=True)

    # create frames
    frame1 = ttk.Frame(notebook, width=350, height=400)
    frame2 = ttk.Frame(notebook, width=350, height=400)
    ttk.Label(frame2, text='Numerator').place(x=10, y=10)
    tr_func_text = ttk.StringVar()
    global trFuncValueLB
    trFuncValueLB = ttk.Entry(frame2, justify="center", textvariable=tr_func_text, width=15, font=("Barlow", 10),
                              state="disabled")
    trFuncValueLB.place(x=130, y=10)
    ttk.Label(frame2, text='Denominator').place(x=10, y=60)
    tr_func_text2 = ttk.StringVar()
    global tr_func_value_lb2
    tr_func_value_lb2 = ttk.Entry(frame2, justify="center", textvariable=tr_func_text2, width=15, font=("Barlow", 10),
                                  state="disabled")
    tr_func_value_lb2.place(x=130, y=60)
    ttk.Separator(frame2, orient='horizontal', style='info.horizontal.TSeparator').place(x=10, y=115)
    ttk.Label(frame2, text='Zeros').place(x=10, y=130)
    zeros_text = ttk.StringVar()
    global zeros_val_lb
    zeros_val_lb = ttk.Entry(frame2, justify="center", textvariable=zeros_text, width=15, font=("Barlow", 10),
                             state="disabled")
    zeros_val_lb.place(x=130, y=130)

    ttk.Label(frame2, text='Poles').place(x=10, y=180)
    poles_text = ttk.StringVar()
    global poles_val_lb
    poles_val_lb = ttk.Entry(frame2, justify="center", textvariable=poles_text, width=15, font=("Barlow", 10),
                             state="disabled"

                             )
    poles_val_lb.place(x=130, y=180)

    ttk.Label(frame2, text='Option', ).place(x=10, y=250)
    global zp_to_hs_text
    zp_to_hs_text = ttk.StringVar()
    zp_to_hs_true_val = ttk.Radiobutton(frame2, style='primary.TRadiobutton', text="H (s) To Zeros",
                                        command=lambda: disable_box(1), variable=zp_to_hs_text, value=1)
    zp_to_hs_true_val.place(x=130, y=250)
    zp_to_hs_false_val = ttk.Radiobutton(frame2, style='primary.TRadiobutton', text="Zeros To H (s)",
                                         command=lambda: disable_box(2), variable=zp_to_hs_text, value=2, )
    zp_to_hs_false_val.place(x=130, y=280)

    frame1.pack(fill='both', expand=True)
    frame2.pack(fill='both', expand=True)

    # add frames to notebook

    notebook.add(frame1, text='Wave')
    notebook.add(frame2, text='Transfer Function')

    # menu selection
    global select_wave_menu
    select_wave_menu = ttk.Menubutton(frame1, text='Select Wave', style='info.Outline.TMenubutton', )
    select_wave_menu.place(x=10, y=100)
    # create menu
    menu = ttk.Menu(select_wave_menu, font=("Barlow", 13))
    # add options
    option_var = ttk.StringVar()
    for option in ['Sine Wave', 'Rec Wave']:
        menu.add_radiobutton(label=option, value=option, variable=option_var)
    # associate menu with menubutton
    select_wave_menu['menu'] = menu
    ttk.Label(frame1, text="Select Impulse Response").place(x=10, y=10)
    ttk.Button(new_conv_window, text='Apply', command=lambda: apply_convolution(option_var.get()), ).place(x=940, y=500)
    # plot the original signal based on the imported Audio Output file
    global sig
    sig = np.repeat([0., 1., 0.], 100)
    # plot the original signal
    plotting_convolution(sig, og_signal_frame, 'Original Signal')


# convolution button on the main interface
ttk.Button(root, text='  Convolution', command=open_conv_window, image=conv_icon, compound=ttk.LEFT, width=11,
           style='warning.TButton').place(x=1000, y=200)


# Text To Speach Function
def tts(speach):
    if speach == "":
        messagebox.showinfo("info", "Enter Some Text")
    else:
        engine = pyttsx3.init()
        engine.setProperty('rate', 300)  # setting up new voice rate

        # say method on the engine that passing input text to be spoken
        engine.say(speach)
        # Saving Voice to a file
        engine.save_to_file(speach, directory_name + '/Transcript.mp3')
        # run and wait method, it processes the voice commands.
        engine.runAndWait()
        engine.stop()


def open_tts_window():
    stop_audio()
    new_window = Toplevel(root)
    new_window.title("Text To Speach")
    new_window.iconbitmap('icons/picon.ico')
    new_window.resizable(False, False)
    new_window.geometry("400x200")
    # A Label widget to show in toplevel
    ttk.Label(new_window, text="Please Write The Transcript").pack(pady=10)
    tts_text = ttk.StringVar()
    tts_value_lb = ttk.Entry(new_window, justify="center", textvariable=tts_text, font=("Barlow", 12), )
    tts_value_lb.pack(fill='x', pady=10)

    # Get the text value function
    def get_my_input_value(widget):
        getresult = widget.get()
        tts(str(getresult))
        return

    ttk.Button(new_window, text='Convert', command=lambda: get_my_input_value(tts_value_lb), ).pack(pady=20)


# TTS Button
ttk.Button(root, text=' Text To Speach', command=open_tts_window, image=tts_icon, compound=ttk.LEFT,
           style='success.TButton', width=14, ).place(x=1000, y=280)

# Fix the DPI Bug
windll.shcore.SetProcessDpiAwareness(1)

root.mainloop()
