import os
import struct
import tkinter as tk
import wave
from ctypes import windll
from tkinter import filedialog

import numpy as np
import pyttsx3
import simpleaudio as sa
import ttkbootstrap as ttk
from AudioLib.AudioProcessing import AudioProcessing
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from playsound import playsound
from pydub import AudioSegment
from scipy import signal
from ttkbootstrap import Style

# Styling
style = Style()
root = style.master
style.configure('TLabel', font=('Barlow', 12))
style.configure('TRadiobutton', font=('Barlow', 12))
style.configure('TButton', width=7, font=("Barlow", 13))
style.configure('TMenubutton', font=("Barlow", 13))

root.title('Signal Manipulation')
root.iconbitmap('./icons/picon.ico')
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
def updatefr(obj):
    # clear the frame when we add another plot
    for wid in obj.winfo_children():
        wid.destroy()


# read the audio file
def readfile(file):
    # minus one here means that all the frames of audio has to be read
    raw = file.readframes(-1)
    # get the namber of channels in the wave
    global nChannels
    nChannels = file.getnchannels()
    # we will sign it with 16-bit integers since wave files are encoded with 16 bits per sample
    global data
    data = np.frombuffer(raw, "int16")
    global sampleRate
    sampleRate = file.getframerate()
    time = np.linspace(0, len(data) / sampleRate, num=len(data))
    return time, data


# plot the audio data
def plott(time, raw, place):
    # creat another figure to hold the plot of the ave file to display it in GUI
    fig = Figure(figsize=(7, 2), dpi=110)
    a = fig.add_subplot(111)
    # plot the wave
    a.plot(time, raw, color='blue')
    a.set_ylabel("Amplitude")
    a.grid()
    # Creating Canvas to show it the Frame
    canv = FigureCanvasTkAgg(fig, master=place)
    canv.draw()
    get_widz = canv.get_tk_widget()
    get_widz.pack()


# import audio file
def importfunc():
    updatefr(wvFr)
    updatefr(wvFrMod)
    # open window to select the wav file and get the path to the audio dile then save in variable direc
    filename = filedialog.askopenfilename(initialdir="\\", title="Select Audio File", filetypes=(("Wav", "*wav"),))
    global direc
    direc = str(filename)
    global wav
    wav = wave.open(direc, "rb")
    result = readfile(wav)
    wavD = AudioSegment.from_file(file=direc, format="wav")
    maxAmp = wavD.max
    # Update displayed File info
    label1.config(text='wav File')
    label3.config(text=nChannels)
    label4.config(text=sampleRate)
    label5.config(text=maxAmp)
    plott(result[0], result[1], wvFr)
    # Set echo options on if the file is stereo
    if nChannels == 2:
        echoT.config(state='!selected')
        echoF.config(state='!selected')
    else:
        echoT.config(state='disabled')
        echoF.config(state='disabled')

    return


def operations(AmpAmount, ShiftAmount, SpeedAmount, ReverseState, echoState):
    updatefr(wvFrMod)
    obj = wave.open('.\\audio\\Modified.wav', 'wb')
    obj.setnchannels(nChannels)
    obj.setsampwidth(2)
    # speed OP
    speed_factor = SpeedAmount
    speed = sampleRate * speed_factor
    obj.setframerate(speed)
    # Shift OP
    pov_sheft_in_sec = ShiftAmount
    for i in range(int(sampleRate * pov_sheft_in_sec)):
        zeroinbyte = struct.pack('<h', 0)
        obj.writeframesraw(zeroinbyte)
    # Amplification OP
    amp = AmpAmount
    n = len(data)
    # Reverse OP
    reverse = ReverseState
    if reverse:
        for i in range(data.__len__()):
            twobytesample = data[n - 1 - i] * amp
            if twobytesample > 32760:
                twobytesample = 32760
            if twobytesample < -32760:
                twobytesample = -32760
            sample = struct.pack('<h', int(twobytesample))
            obj.writeframesraw(sample)
    else:
        for i in range(data.__len__()):
            twobytesampler = data[i] * amp
            if twobytesampler > 32760:
                twobytesampler = 32760
            if twobytesampler < -32760:
                twobytesampler = -32760
            sample = struct.pack('<h', int(twobytesampler))
            obj.writeframesraw(sample)

    obj.close()
    wav.close()

    obj = wave.open('.\\audio\\Modified.wav', 'rb')  # open
    dataout = obj.readframes(-1)  # get all the frames in data out
    dataout = np.frombuffer(dataout, "int16")  # set the data to a sumber of two byte form data out
    sampleRateOut = obj.getframerate()  # frame rate HZ (number of frames to be reads in seconds)
    Timeout = np.linspace(0, len(dataout) / sampleRateOut, len(dataout))  # time of the output
    plott(Timeout, dataout, wvFrMod)
    # set the echo based on state
    if echoState:
        sound1 = AudioProcessing('.\\audio\\Modified.wav')
        sound1.set_echo(0.4)
        sound1.save_to_file('.\\audio\\Modified.wav')
    return


# icons & header buttons
import_icon = tk.PhotoImage(file='.//icons//importIcon.png')
play_icon = tk.PhotoImage(file='.//icons//playIcon.png')
conv_icon = tk.PhotoImage(file='.//icons//convIcon.png')
tts_icon = tk.PhotoImage(file='.//icons//ttsIcon.png')

importBtn = ttk.Button(
    root,
    text='  Import',
    command=importfunc,
    image=import_icon,
    compound=tk.LEFT,
)
importBtn.pack(
    ipadx=10,
    ipady=15,
    padx=10, pady=15,
    expand=True
)
importBtn.place(x=1050, y=55)

# header section
titleLB = ttk.Label(
    root,
    text='Signal Processing with Python', font=("Barlow", 20))
titleLB.pack(ipadx=10, ipady=10)
titleLB.place(x=37, y=17)

subTitleLB = ttk.Label(
    root,
    text='Audio File Overview', font=("Barlow", 17))
subTitleLB.pack(ipadx=10, ipady=10)
subTitleLB.place(x=37, y=65)

# file info section
frame1 = tk.Frame(root, height=100, width=215)
frame1.place(x=37, y=100)

photo1 = tk.PhotoImage(file='./icons/icon1.png')
image_label1 = ttk.Label(
    frame1,
    image=photo1
)
image_label1.pack()
image_label1.place(x=0, y=10)

label1 = tk.Label(
    frame1,
    text='Unknown', font=("Abel", 13))

label1.pack(ipadx=10, ipady=10)
label1.place(x=75, y=20)
label2 = tk.Label(
    frame1,
    text='Type Of Audio File', font=("Actor", 12))

label2.pack(ipadx=10, ipady=10)
label2.place(x=75, y=50)

frame2 = tk.Frame(root, height=100, width=215)
frame2.place(x=270, y=100)
photo2 = tk.PhotoImage(file='./icons/icon2.png')
image_label2 = ttk.Label(
    frame2,
    image=photo2
)
image_label2.pack()
image_label2.place(x=0, y=10)

label3 = tk.Label(
    frame2,
    text='0', font=("Abel", 13))

label3.pack(ipadx=10, ipady=10)
label3.place(x=75, y=20)
label4 = tk.Label(
    frame2,
    text='Channels', font=("Actor", 12))

label4.pack(ipadx=10, ipady=10)
label4.place(x=75, y=50)

frame3 = tk.Frame(root, height=100, width=215)
frame3.place(x=493, y=100)
photo3 = tk.PhotoImage(file='./icons/icon3.png')
image_label3 = ttk.Label(
    frame3,
    image=photo3
)
image_label3.pack()
image_label3.place(x=0, y=10)

label4 = tk.Label(
    frame3,
    text='0', font=("Abel", 13))

label4.pack(ipadx=10, ipady=10)
label4.place(x=75, y=20)
label5 = tk.Label(
    frame3,
    text='Frame Rate', font=("Actor", 12))

label5.pack(ipadx=10, ipady=10)
label5.place(x=75, y=50)

frame4 = tk.Frame(root, height=100, width=220)
frame4.place(x=716, y=100)
photo4 = tk.PhotoImage(file='./icons/icon4.png')
image_label4 = ttk.Label(
    frame4,
    image=photo4
)
image_label4.pack()
image_label4.place(x=0, y=10)

label5 = tk.Label(
    frame4,
    text='0', font=("Abel", 13))

label5.pack(ipadx=10, ipady=10)
label5.place(x=75, y=20)
label6 = tk.Label(
    frame4,
    text='Maximum Amplitude', font=("Actor", 12))

label6.pack(ipadx=10, ipady=10)
label6.place(x=75, y=50)

# Wave form section
wvLB = tk.Label(
    root,
    text='Audio Wave Form', font=("Barlow", 17))

wvLB.pack(ipadx=10, ipady=10)
wvLB.place(x=37, y=200)

wvFr = tk.Frame(root, height=190, width=770)
wvFr.place(x=37, y=240)
wvFrMod = tk.Frame(root, height=190, width=770)
wvFrMod.place(x=37, y=470)

# tasks section
tasksLB = tk.Label(
    root,
    text='Tasks', font=("Barlow", 17))

tasksLB.pack(ipadx=10, ipady=10)
tasksLB.place(x=900, y=280)
tasksVB = ttk.Separator(root, orient='vertical', style='info.Vertical.TSeparator')
tasksVB.pack()
tasksVB.place(x=980, y=280)
tasksFr = tk.Frame(root, height=300, width=270, bg="#D9DFE8")
tasksFr.place(x=900, y=320)

# Task buttons
ampLB = ttk.Label(
    root,
    text='Amplitude',
)
ampLB.pack(ipady=5)
ampLB.place(x=915, y=345)

ampText = tk.StringVar()
ampValueLB = ttk.Entry(root,
                       justify="center",
                       textvariable=ampText,
                       width=15,
                       font=("Barlow", 10)
                       )
ampValueLB.pack()
ampValueLB.place(x=1015, y=345)
shiftLB = ttk.Label(
    root,
    text='Shift',
)
shiftLB.pack(ipady=5)
shiftLB.place(x=915, y=385)

shiftText = tk.StringVar()
shiftValueLB = ttk.Entry(root,
                         justify="center",
                         textvariable=shiftText,
                         width=15,
                         font=("Barlow", 10)
                         )
shiftValueLB.pack()
shiftValueLB.place(x=1015, y=385)

speedLB = ttk.Label(
    root,
    text='Speed',
)
speedLB.pack(ipady=5)
speedLB.place(x=915, y=425)

speedText = tk.StringVar()
speedValueLB = ttk.Entry(root,
                         justify="center",
                         textvariable=speedText,
                         width=15,
                         font=("Barlow", 10)
                         )
speedValueLB.pack()
speedValueLB.place(x=1015, y=425)

# label
revLB = ttk.Label(
    root,
    text='Reverse',
)
revLB.pack(ipady=5)
revLB.place(x=915, y=465)

revText = tk.StringVar()
R1 = ttk.Radiobutton(root, style='primary.TRadiobutton', text="True", variable=revText, value=1)
R1.pack()
R1.place(x=1055, y=470)

R2 = ttk.Radiobutton(root, style='primary.TRadiobutton', text="False", variable=revText, value=2, )
R2.pack()
R2.place(x=1055, y=500)

echoLB = ttk.Label(
    root,
    text='Echo',

)
echoText = tk.StringVar()
echoT = ttk.Radiobutton(root, style='TRadiobutton', text="True", variable=echoText, value=3)

echoF = ttk.Radiobutton(root, style='primary.TRadiobutton', text="False", variable=echoText, value=4, )

echoLB.pack()
echoLB.place(x=915, y=530)
echoF.pack()
echoF.place(x=1055, y=570)
echoT.pack()
echoT.place(x=1055, y=540)


def apl():
    ampAmount = float(ampValueLB.get())
    shiftAmount = float(shiftValueLB.get())
    speedAmount = float(speedValueLB.get())
    reverseVal = str(revText.get())
    echoVal = str(echoText.get())

    if reverseVal == '1':
        reverseSt = True
    else:
        reverseSt = False

    if echoVal == '3':
        echoState = True
    else:
        echoState = False

    operations(ampAmount, shiftAmount, speedAmount, reverseSt, echoState)


applyBtn = ttk.Button(
    root,
    style='success.Outline.TButton',
    text='Apply',
    command=apl
)
applyBtn.pack(
    ipadx=10,
    ipady=15,
    padx=10, pady=15,
    expand=True
)
applyBtn.place(x=940, y=630)


def playAudioMod():
    audio_file = os.path.dirname(__file__) + '/audio/Modified.wav'
    playsound(audio_file)


def playAudio():
    wave_object = sa.WaveObject.from_wave_file(direc)
    play_object = wave_object.play()
    play_object.wait_done()
    return


play1 = ttk.Button(
    root,
    text='  Play',
    command=playAudioMod,
    image=play_icon,
    compound=tk.LEFT,
)
play1.pack(
    ipadx=10,
    ipady=15,
    padx=10, pady=15,
    expand=True
)
play1.place(x=1050, y=630)
play2 = ttk.Button(
    root,
    text='  Play',
    command=playAudio,
    image=play_icon,
    compound=tk.LEFT,
)
play2.pack(
    ipadx=10,
    ipady=15,
    padx=10, pady=15,
    expand=True
)
play2.place(x=735, y=200)


def plottCon(signal, place, title):
    fig = Figure(figsize=(7, 2), dpi=110)
    a = fig.add_subplot(111)
    # plot the wave
    a.plot(signal, color='blue')
    a.set_ylabel("Amplitude")
    a.set_title(title)
    a.grid()
    # Creating Canvas to show it the Frame
    canv = FigureCanvasTkAgg(fig, master=place)
    canv.draw()
    get_widz = canv.get_tk_widget()
    get_widz.pack()
    return


def ApplyConvolution(convVal):
    updatefr(ModSginalFr)
    updatefr(ConvSginalFr)
    if convVal == 'Sine Wave':
        win = signal.windows.hann(50)
        plottCon(win, ModSginalFr, 'Impulse Response')
        filtered = signal.convolve(sig, win, mode='same') / sum(win)
        plottCon(filtered, ConvSginalFr, 'Filtered Signal')

    else:
        win = np.repeat([0., 1., 0.], 50)
        plottCon(win, ModSginalFr, 'Impulse Response')
        filtered = signal.convolve(sig, win, mode='same') / sum(win)
        plottCon(filtered, ConvSginalFr, 'Filtered Signal')

    return


# Covolution PopUp
def openConvWindow():
    # be treated as a new window
    newConvWindow = Toplevel(root)
    newConvWindow.title("Convolution")
    newConvWindow.iconbitmap('./icons/picon.ico')
    # make the window not resizable
    newConvWindow.resizable(False, False)
    # sets the geometry of toplevel
    newConvWindow.geometry("1200x740")
    # Three plotting frames
    global OGSginalFr
    OGSginalFr = ttk.Frame(newConvWindow, style='TFrame', height=190, width=770)
    OGSginalFr.pack()
    OGSginalFr.place(x=10, y=10)
    global ModSginalFr
    ModSginalFr = ttk.Frame(newConvWindow, style='TFrame', height=190, width=770)
    ModSginalFr.pack()
    ModSginalFr.place(x=10, y=250)
    global ConvSginalFr
    ConvSginalFr = ttk.Frame(newConvWindow, style='TFrame', height=190, width=770)
    ConvSginalFr.pack()
    ConvSginalFr.place(x=10, y=490)
    # menu selection
    mb = ttk.Menubutton(newConvWindow, text='Select Wave', style='info.Outline.TMenubutton', )
    mb.pack()
    mb.place(x=1000, y=230)
    # create menu
    menu = tk.Menu(mb, font=("Barlow", 13))
    # add options
    option_var = tk.StringVar()
    for option in ['Sine Wave', 'Rec Wave']:
        menu.add_radiobutton(label=option, value=option, variable=option_var)
    # associate menu with menubutton
    mb['menu'] = menu
    ImResLB = ttk.Label(newConvWindow, text="Select Impulse Response")
    ImResLB.pack()
    ImResLB.place(x=750, y=230)

    apllyConvBtn = ttk.Button(
        newConvWindow,
        text='Apply',
        command=lambda: ApplyConvolution(option_var.get()),
    )
    apllyConvBtn.pack(
        expand=True
    )
    apllyConvBtn.place(x=900, y=500)
    # plot the orignal signal based on the imported audio file
    global sig
    sig = data
    # plot the original signal
    plottCon(sig, OGSginalFr, 'Original Signal')
    return


# convlution button on the main interface
conv = ttk.Button(
    root,
    text='  Convolution',
    command=openConvWindow,
    image=conv_icon,
    compound=tk.LEFT,
    width=9,
    style='warning.TButton'
)
conv.pack(
    ipadx=10,
    ipady=15,
    padx=10, pady=15,
    expand=True
)
conv.place(x=1000, y=200)

from tkinter import *


def tts(speach):
    engine = pyttsx3.init()  # object creation

    """ RATE"""
    rate = engine.getProperty('rate')  # getting details of current speaking rate
    engine.setProperty('rate', 220)  # setting up new voice rate

    """VOLUME"""
    volume = engine.getProperty('volume')  # getting to know current volume level (min=0 and max=1)
    engine.setProperty('volume', 1.0)  # setting up volume level  between 0 and 1

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    engine.setProperty('voice', voices[1].id)  # changing index, changes voices. 1 for female

    engine.say(speach)
    engine.runAndWait()
    engine.stop()

    """Saving Voice to a file"""
    # On linux make sure that 'espeak' and 'ffmpeg' are installed
    engine.save_to_file(speach, './audio/Transcript.mp3')
    engine.runAndWait()


def openNewWindow():
    # be treated as a new window
    newWindow = Toplevel(root)
    # sets the title of the
    # Toplevel widget
    newWindow.title("Text To Speach")
    newWindow.iconbitmap('./icons/picon.ico')
    # make the window not resizable
    newWindow.resizable(False, False)
    # sets the geometry of toplevel
    newWindow.geometry("400x200")

    # A Label widget to show in toplevel
    ttsLB = ttk.Label(newWindow, text="Please Write The Transcript")
    ttsLB.pack()

    ttsText = tk.StringVar()
    ttsValueLB = ttk.Entry(newWindow,
                           justify="center",
                           textvariable=ttsText,
                           font=("Barlow", 12),
                           )
    ttsValueLB.pack(fill='x')

    def Get_MyInputValue(widg):
        getresult = widg.get()
        tts(str(getresult))
        return

    convBtn = ttk.Button(
        newWindow,
        text='Convert',
        command=lambda: Get_MyInputValue(ttsValueLB),
    )
    convBtn.pack(
        expand=True
    )


ttsBtn = ttk.Button(
    root,
    text=' Text To Speach',
    command=openNewWindow,
    image=tts_icon,
    compound=tk.LEFT,
    style='success.TButton',
    width=12,

)
ttsBtn.pack(
    ipadx=10,
    ipady=15,
    padx=10, pady=15,
    expand=True
)
ttsBtn.place(x=1000, y=280)

# Fix the DPI Bug
windll.shcore.SetProcessDpiAwareness(1)

root.mainloop()
