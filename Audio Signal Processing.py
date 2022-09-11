import importlib
import os
import struct
import wave
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

# Set the splash screen if it is configured
if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
    import pyi_splash

    # close the splash screen when the GUI shows
    pyi_splash.close()

# set main theme
current_style = Style(theme='cosmo')
root = current_style.master

# Fix the DPI Bug
ttk.utility.enable_high_dpi_awareness(root)

# set title and fav icon
root.title('Audio Signal Processing')
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

# global variables
hasImported = False  # checks if a file has been imported
file_directory = '/'
directory_name = 'Audio Output'  # get the absolute path
out_file = directory_name + '/Modified.wav'
dark_mode_state = False
nChannels = 0
sampleRate = 0
max_amp = 0
num_of_frames = 0
result = (0, 0, 0)
timeout = 0
data_out = 0
og_plot_showed = False
mod_plot_showed = False
plotting_figure = Figure()
figure_subplot = plotting_figure.add_subplot()
data = np.array([])
sig = np.array([])


# check for input validation for float numbers only
def validation_callback(user_val):
    try:
        if float(user_val) >= 0:
            return True
    except ValueError:
        if user_val == '':
            return True
    return False


# icons
dark_icon = ttk.PhotoImage(file='icons/darkIcon.png')
import_icon = ttk.PhotoImage(file='icons/importIcon.png')
folderIcon = ttk.PhotoImage(file='icons/icon1.png')
channelsIcon = ttk.PhotoImage(file='icons/icon2.png')
frameRateIcon = ttk.PhotoImage(file='icons/icon3.png')
ampIcon = ttk.PhotoImage(file='icons/icon4.png')

play_icon = ttk.PhotoImage(file='icons/playIcon.png')
stop_icon = ttk.PhotoImage(file='icons/stopIcon.png')
conv_icon = ttk.PhotoImage(file='icons/convIcon.png')
tts_icon = ttk.PhotoImage(file='icons/ttsIcon.png')
white_icon = ttk.PhotoImage(file='icons/whiteIcon.png')

# UI elements
darkBtn = ttk.Button(root, image=dark_icon, style='Link.TButton')
darkBtn.place(x=970, y=55)

wvFr = ttk.Frame(root, height=190, width=770)
wvFrMod = ttk.Frame(root, height=190, width=770)
wvFr.place(x=37, y=240)
wvFrMod.place(x=37, y=470)

# Audio duration label
length_lb = ttk.Label(root, font=("Barlow", 17))
length_lb.place(x=530, y=205)

# header buttons
importBtn = ttk.Button(root, text='  Import', image=import_icon, compound=ttk.LEFT)
importBtn.place(x=1050, y=55)

# header section
ttk.Label(root, text='Audio Signal Processing', font=("Barlow", 20)).place(x=37, y=17)
ttk.Label(root, text='Audio File Overview', font=("Barlow", 17)).place(x=37, y=65)

# Waveform section
ttk.Label(root, text='Audio Wave Form', font=("Barlow", 17)).place(x=37, y=200)

# file info section
fileTypeFr = ttk.Frame(root, height=100, width=215)
ttk.Label(fileTypeFr, image=folderIcon).place(x=0, y=10)
fileTypeVal = ttk.Label(fileTypeFr, text='Unknown')
ttk.Label(fileTypeFr, text='Type Of Audio File').place(x=75, y=50)
fileTypeFr.place(x=37, y=100)
fileTypeVal.place(x=75, y=20)

channelFr = ttk.Frame(root, height=100, width=215)
ttk.Label(channelFr, image=channelsIcon).place(x=0, y=10)
channelsVal = ttk.Label(channelFr, text=nChannels)
ttk.Label(channelFr, text='Channels').place(x=75, y=50)
channelFr.place(x=270, y=100)
channelsVal.place(x=75, y=20)

frameRateFr = ttk.Frame(root, height=100, width=215)
ttk.Label(frameRateFr, image=frameRateIcon).place(x=0, y=10)
frameRateVal = ttk.Label(frameRateFr, text=num_of_frames, font=("Abel", 13))
ttk.Label(frameRateFr, text='Frame Rate').place(x=75, y=50)
frameRateFr.place(x=493, y=100)
frameRateVal.place(x=75, y=20)

ampFr = ttk.Frame(root, height=100, width=220)
ampFr.place(x=716, y=100)
ttk.Label(ampFr, image=ampIcon).place(x=0, y=10)
ampVal = ttk.Label(ampFr, text=max_amp)
ampVal.place(x=75, y=20)
ttk.Label(ampFr, text='Maximum Amplitude').place(x=75, y=50)

# tasks section
ttk.Label(root, text='Tasks', font=("Barlow", 17)).place(x=900, y=285)

# Task labels
ttk.Label(root, text='Amplitude').place(x=915, y=350)
ampValueLB = ttk.Entry(root, justify="center", width=15, font=("Barlow", 12))
ampValueLB.place(x=1015, y=345)

ttk.Label(root, text='Shift').place(x=915, y=390)
shiftValueLB = ttk.Entry(root, justify="center", width=15, font=("Barlow", 12))
shiftValueLB.place(x=1015, y=385)

ttk.Label(root, text='Speed').place(x=915, y=430)
speedValueLB = ttk.Entry(root, justify="center", width=15, font=("Barlow", 12))
speedValueLB.place(x=1015, y=425)

ttk.Label(root, text='Reverse').place(x=915, y=475)
revText = ttk.StringVar()
reverseTrueVal = ttk.Radiobutton(root, text="True", variable=revText, value=1)
reverseTrueVal.place(x=1015, y=480)
reverseFalseVal = ttk.Radiobutton(root, text="False", variable=revText, value=2)
reverseFalseVal.place(x=1090, y=480)

ttk.Label(root, text='Echo').place(x=915, y=520)
echoText = ttk.StringVar()
echoTrueVal = ttk.Radiobutton(root, text="True", variable=echoText, value=3)
echoTrueVal.place(x=1015, y=525)
echoFalseVal = ttk.Radiobutton(root, text="False", variable=echoText, value=4)
echoFalseVal.place(x=1090, y=525)

# Tasks buttons
applyOpBtn = ttk.Button(root, padding=(15, 8), style='success.Outline.TButton', text='Apply')
applyOpBtn.place(x=940, y=630)

# Play buttons
ttk.Button(root, text='  Play', command=lambda: play_audio('mod'), image=play_icon, compound=ttk.LEFT).place(x=1050,
                                                                                                             y=630)
ttk.Button(root, text='  Play', command=lambda: play_audio('OG'), image=play_icon, compound=ttk.LEFT).place(x=790,
                                                                                                            y=200)
ttk.Button(root, text='  Stop', style='danger.TButton', command=lambda: stop_audio(), image=stop_icon,
           compound=ttk.LEFT).place(x=650,
                                    y=200)
# TTS Button
ttsBtn = ttk.Button(root, text=' Text To Speach', image=tts_icon, compound=ttk.LEFT, style='success.TButton',
                    width=14)
ttsBtn.place(x=1000, y=280)

# separator section
ttk.Separator(root, orient='vertical', style='info.Vertical.TSeparator').place(x=630, y=200)
ttk.Separator(root, orient='vertical', style='info.Vertical.TSeparator').place(x=980, y=280)

# convolution frames
conv_signal_frame = ttk.Frame()
mod_signal_frame = ttk.Frame()
og_signal_frame = ttk.Frame()
tr_func_value_lb2 = ttk.Entry()
trFuncValueLB = ttk.Entry()
zeros_val_lb = ttk.Entry()
poles_val_lb = ttk.Entry()
zp_to_hs_text = ttk.StringVar()
select_wave_menu = ttk.Menubutton()

# register the call back function for validation
user_validation = root.register(validation_callback)


# Create directory if it is not there
def make_output_directory():
    try:
        os.mkdir(directory_name)
    except FileExistsError:
        return
    return


make_output_directory()


# update the plotting frame
def update_frame(obj):
    # clear the frame when we add another plot
    for wid in obj.winfo_children():
        wid.destroy()
    return


# read the Audio Output file
def read_file(file):
    global nChannels, data, sampleRate, num_of_frames

    raw = file.readframes(-1)  # minus one here means that all the frames of Audio Output has to be read
    nChannels = file.getnchannels()  # get the number of channels in the wave
    data = np.frombuffer(raw, "int16")  # sign it with 16-bit ints since wave files are encoded with 16 bits per sample
    sampleRate = file.getframerate()
    num_of_frames = file.getnframes()

    # get the duration of the audio file
    duration = num_of_frames / float(sampleRate)
    hours, minutes, seconds = output_duration(int(duration))
    total_time = '{}:{}:{}'.format(hours, minutes, seconds)

    # display the duration
    length_lb.config(text=total_time)

    time = np.linspace(0, len(data) / sampleRate, num=len(data))
    return time, data


# import Audio Output file
def import_file():
    global og_plot_showed, mod_plot_showed, file_directory, result, hasImported, max_amp

    # hide the plotting frames every time we import
    og_plot_showed = False
    mod_plot_showed = False

    # stop playing audio
    stop_audio()

    # update plotting frames
    update_frame(wvFr)
    update_frame(wvFrMod)

    # open window to select the wav file and get the path to the Audio Output dile then save in variable directory
    filename = filedialog.askopenfilename(initialdir=file_directory, title="Select Audio File",
                                          filetypes=(('Wav', '*wav'), ('Mp3', '*mp3')))
    file_directory = str(filename)

    # using splitext() to find file extension
    file_extension = os.path.splitext(file_directory)[1]

    if file_directory == '':
        messagebox.showinfo('info', 'No File Was Selected')
        hasImported = False
        return
    else:
        # checks if the output file is there and delete it
        if os.path.isfile(out_file):
            os.remove(out_file)

        # convert mp3 file to wav, so it can be read by wave.open()
        if file_extension == '.mp3':
            mp3_file = AudioSegment.from_mp3(file=file_directory)
            mp3_file.export('./Audio Output/Mp3converted.wav', format='wav')
            file_directory = './Audio Output/Mp3converted.wav'

        # read the new imported file
        wav_file = wave.open(file_directory, 'r')

        result = read_file(wav_file)
        hasImported = True

        # Update displayed File info
        wav_d = AudioSegment.from_file(file=file_directory, format="wav")
        max_amp = wav_d.max
        fileTypeVal.config(text=file_extension)
        channelsVal.config(text=nChannels)
        frameRateVal.config(text=sampleRate)
        ampVal.config(text=max_amp)

        # start plotting
        plotting(result[0], result[1], wvFr, 'Original Audio')
        og_plot_showed = True

        # Set echo options on if the file is stereo
        if nChannels == 2:
            echoTrueVal.config(state='!selected')
            echoFalseVal.config(state='!selected')
        else:
            echoTrueVal.config(state='disabled')
            echoFalseVal.config(state='disabled')
    return


def create_plot_fig():
    global plotting_figure, figure_subplot

    # toggle between light and dark mode
    matplotlib.style.use('dark_background') if not dark_mode_state else matplotlib.style.use('default')
    plotting_figure = Figure(figsize=(7, 2), dpi=110)
    figure_subplot = plotting_figure.add_subplot(111)
    figure_subplot.set_ylabel('Amplitude')
    figure_subplot.grid(alpha=0.4)
    return


def play_audio(indication):
    if hasImported:
        if indication == 'OG':
            audio_file = file_directory
        else:
            if os.path.isfile(out_file):
                audio_file = out_file
            else:
                messagebox.showinfo('Info', 'Apply Modification To The Audio File Then Play It')
                return
        winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        messagebox.showinfo("Warning", "Please Import Audio File First")
    return


# stop current playing audio
def stop_audio():
    winsound.PlaySound(None, winsound.SND_FILENAME)
    return


def set_theme():
    global dark_mode_state

    stop_audio()
    if dark_mode_state:
        Style(theme='cyborg')
        darkBtn.config(image=white_icon)
        dark_mode_state = False
    else:
        Style(theme='cosmo')
        darkBtn.config(image=dark_icon)
        dark_mode_state = True

    current_style.configure('TLabel', font=('Barlow', 13))
    current_style.configure('TRadiobutton', font=('Barlow', 12))
    current_style.configure('TButton', width=7, font=("Barlow", 13))
    current_style.configure('TMenubutton', font=("Barlow", 13))
    current_style.configure('TNotebook.Tab', font=("Barlow", 12))

    update_frame(wvFr)
    update_frame(wvFrMod)

    # update plot upon changing themes
    if og_plot_showed:
        plotting(result[0], result[1], wvFr, "Original Audio")
    if mod_plot_showed:
        plotting(timeout, data_out, wvFrMod, 'Modified Audio')
    return


set_theme()


def output_duration(length):
    hours = length // 3600  # calculate in hours
    length %= 3600
    minutes = length // 60  # calculate in minutes
    length %= 60
    seconds = length  # calculate in seconds
    return hours, minutes, seconds


def operations(amp_amount, shift_amount, speed_amount, reverse_state, echo_state):
    global data_out, timeout, mod_plot_showed

    update_frame(wvFrMod)
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
    obj = wave.open(out_file, 'rb')  # open
    data_out = obj.readframes(-1)  # get all the frames in data out
    data_out = np.frombuffer(data_out, "int16")  # set the data to a number of two byte form data out
    sample_rate_out = obj.getframerate()  # frame rate HZ (number of frames to be reads in seconds)
    timeout = np.linspace(0, len(data_out) / sample_rate_out, len(data_out))  # time of the output
    plotting(timeout, data_out, wvFrMod, 'Modified Audio')
    mod_plot_showed = True

    # set the echo based on state
    if echo_state:
        sound1 = AudioProcessing(out_file)
        sound1.set_echo(0.5)
        sound1.save_to_file(out_file)
    obj.close()
    return


# Delete the values from the textbox
def delete_entries(wid):
    wid.delete(0, END)


def apply_operations():
    stop_audio()
    if hasImported and ampValueLB.get() != '' and speedValueLB.get() != '' and shiftValueLB.get() != '':
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

        preferred_amp_amount = int(32760 / max_amp)

        # Validate input
        if speed_amount > 2 or speed_amount < 0.25:
            messagebox.showinfo('Info', 'Speed Value Must Be Between 0.25 And 2')
            return
        if amp_amount > preferred_amp_amount and echo_state:
            messagebox.showinfo('Info',
                                'Amplitude Value Can\'t Exceed {}x Or There Will Be Distortion When Using Echo'.format(
                                    preferred_amp_amount))
            return
        if shift_amount < 0:
            messagebox.showinfo('Info', 'Shift Value Must Be Positive')
            return
        operations(amp_amount, shift_amount, speed_amount, reverse_st, echo_state)
    else:
        messagebox.showinfo('Warning', 'Please Import Audio File First And Set Valid Values')
        return
    return


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


def lti_sys(widget):
    if widget == 1:
        # get the values of the textbox as an array
        num = list(map(float, trFuncValueLB.get().strip().split()))
        den = list(map(float, tr_func_value_lb2.get().strip().split()))

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
        zeros = list(map(int, zeros_val_lb.get().strip().split()))
        poles = list(map(int, poles_val_lb.get().strip().split()))

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
    global og_signal_frame, mod_signal_frame, conv_signal_frame, select_wave_menu, sig, trFuncValueLB, tr_func_value_lb2, zeros_val_lb, poles_val_lb, zp_to_hs_text

    stop_audio()

    # be treated as a new window
    new_conv_window = Toplevel(root)
    new_conv_window.title("Convolution")
    new_conv_window.iconbitmap('icons/picon.ico')
    new_conv_window.resizable(False, False)
    new_conv_window.geometry("1200x740")

    # Three plotting frames
    og_signal_frame = ttk.Frame(new_conv_window, height=190, width=770)
    og_signal_frame.place(x=10, y=10)
    mod_signal_frame = ttk.Frame(new_conv_window, height=190, width=770)
    mod_signal_frame.place(x=10, y=250)
    conv_signal_frame = ttk.Frame(new_conv_window, height=190, width=770)
    conv_signal_frame.place(x=10, y=490)

    tabs_fr = ttk.Frame(new_conv_window, height=700, width=350)
    tabs_fr.place(x=800, y=10)
    notebook = ttk.Notebook(tabs_fr)
    notebook.pack(pady=10)

    # create frames
    frame1 = ttk.Frame(notebook, width=350, height=400)
    frame2 = ttk.Frame(notebook, width=350, height=400)

    ttk.Label(frame2, text='Numerator').place(x=10, y=10)
    trFuncValueLB = ttk.Entry(frame2, justify="center", width=15, state="disabled", font=("Barlow", 12))
    trFuncValueLB.place(x=130, y=10)

    ttk.Label(frame2, text='Denominator').place(x=10, y=60)
    tr_func_value_lb2 = ttk.Entry(frame2, justify="center", width=15, state="disabled", font=("Barlow", 12))
    tr_func_value_lb2.place(x=130, y=60)

    ttk.Separator(frame2, orient='horizontal', style='info.horizontal.TSeparator').place(x=10, y=115)

    ttk.Label(frame2, text='Zeros').place(x=10, y=130)
    zeros_val_lb = ttk.Entry(frame2, justify="center", width=15, state="disabled", font=("Barlow", 12))
    zeros_val_lb.place(x=130, y=130)

    ttk.Label(frame2, text='Poles').place(x=10, y=180)
    poles_val_lb = ttk.Entry(frame2, justify="center", width=15, state="disabled", font=("Barlow", 12))
    poles_val_lb.place(x=130, y=180)

    ttk.Label(frame2, text='Option', ).place(x=10, y=250)
    zp_to_hs_true_val = ttk.Radiobutton(frame2, text="H (s) To Zeros",
                                        command=lambda: disable_box(1), variable=zp_to_hs_text, value=1)
    zp_to_hs_true_val.place(x=130, y=250)
    zp_to_hs_false_val = ttk.Radiobutton(frame2, text="Zeros To H (s)",
                                         command=lambda: disable_box(2), variable=zp_to_hs_text, value=2, )
    zp_to_hs_false_val.place(x=130, y=280)

    frame1.pack(fill='both', expand=True)
    frame2.pack(fill='both', expand=True)

    # add frames to notebook
    notebook.add(frame1, text='Wave')
    notebook.add(frame2, text='Transfer Function')

    # menu selection
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
    ttk.Label(frame1, text='Select Impulse Response').place(x=10, y=10)
    ttk.Button(new_conv_window, padding=(15, 8), text='Apply',
               command=lambda: apply_convolution(option_var.get()), ).place(x=940, y=500)

    # plot the original signal based on the imported Audio Output file
    sig = np.repeat([0., 1., 0.], 100)

    # plot the original signal
    plotting_convolution(sig, og_signal_frame, 'Original Signal')


# convolution button on the main interface
ttk.Button(root, text='  Convolution', command=open_conv_window, image=conv_icon, compound=ttk.LEFT, width=11,
           style='warning.TButton').place(x=1000, y=203)


# Text To Speach Function
def tts(speach):
    if speach == "":
        messagebox.showinfo("info", "Enter Some Text")
        return
    else:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # setting up new voice rate

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
    tts_value_lb = ttk.Entry(new_window, justify="center", font=("Barlow", 12))
    tts_value_lb.pack(fill='x', pady=10)

    # Get the text value function
    def get_my_input_value(widget):
        getresult = widget.get()
        tts(str(getresult))
        return

    ttk.Button(new_window, text='Convert', command=lambda: get_my_input_value(tts_value_lb), ).pack(pady=20)


# configure buttons commands
darkBtn.config(command=set_theme)
importBtn.config(command=import_file)
applyOpBtn.config(command=apply_operations)
ttsBtn.config(command=open_tts_window)
ampValueLB.config(validate="key", validatecommand=(user_validation, '%P'))
shiftValueLB.config(validate="key", validatecommand=(user_validation, '%P'))
speedValueLB.config(validate="key", validatecommand=(user_validation, '%P'))

root.mainloop()
