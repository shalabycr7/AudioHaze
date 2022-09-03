import os
import struct
import tkinter as tk
import wave
from ctypes import windll
from tkinter import *
from tkinter import filedialog, messagebox
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
import matplotlib.pyplot as plt


def Directory():
    # Create directory ,it's a directory name which you are going to create.
    Directory_Name = 'Audio Output'
    # try and catch block use to handle the exceptions.
    try:
        # Create  Directory
        os.mkdir(Directory_Name)
    except FileExistsError:
        return

Directory()

# Styling
style = Style(theme='cosmo')
root = style.master
style.configure('TLabel', font=('Barlow', 12))
style.configure('TRadiobutton', font=('Barlow', 12))
style.configure('TButton', width=7, font=("Barlow", 13))
style.configure('TMenubutton', font=("Barlow", 13))

# icons
import_icon = tk.PhotoImage(file='.//icons//importIcon.png')
play_icon = tk.PhotoImage(file='.//icons//playIcon.png')
conv_icon = tk.PhotoImage(file='.//icons//convIcon.png')
tts_icon = tk.PhotoImage(file='.//icons//ttsIcon.png')
dark_icon = tk.PhotoImage(file='.//icons//darkIcon.png')
white_icon=tk.PhotoImage(file='.//icons//whiteIcon.png')

root.title('Signal Manipulation')
root.iconbitmap('.//icons//picon.ico')

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
# checks if a file has been imported
hasImported = False

# update the plotting frame
def updatefr(obj):
    # clear the frame when we add another plot
    for wid in obj.winfo_children():
        wid.destroy()


# read the audio file
def readfile(file):
    # minus one here means that all the frames of audio has to be read
    raw = file.readframes(-1)
    # get the number of channels in the wave
    global nChannels
    nChannels = file.getnchannels()
    # w sign it with 16-bit integers since wave files are encoded with 16 bits per sample
    global data
    data = np.frombuffer(raw, "int16")
    global sampleRate
    sampleRate = file.getframerate()
    time = np.linspace(0, len(data) / sampleRate, num=len(data))
    return time, data

import matplotlib
# plot the audio data
def plott(time, raw, place):
    # Apply dark mod on the plot
    if darkM==True:
        matplotlib.style.use('dark_background')
    else:
        matplotlib.style.use('default')

    # creat another figure to hold the plot of the ave file to display it in GUI
    fig = Figure(figsize=(7, 2), dpi=110)
    a = fig.add_subplot(111)
    # plot the wave
    # a.plot.style.use('dark_background')
    a.plot(time, raw, color='blue',)
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
    if direc=='':
        messagebox.showinfo("info", "No File Was Selected")
    else:
        global wav
        wav = wave.open(direc, "rb")
        result = readfile(wav)
        global hasImported
        hasImported = True
        # Update displayed File info
        wavD = AudioSegment.from_file(file=direc, format="wav")
        maxAmp = wavD.max
        fileTypeVal.config(text='wav File')
        channelsVal.config(text=nChannels)
        frameRateVal.config(text=sampleRate)
        ampVal.config(text=maxAmp)
        plott(result[0], result[1], wvFr)
        # Set echo options on if the file is stereo
        if nChannels == 2:
            echoTrueVal.config(state='!selected')
            echoFalseVal.config(state='!selected')
        else:
            echoTrueVal.config(state='disabled')
            echoFalseVal.config(state='disabled')


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


def applyOperations():
    if hasImported:
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
    else:
        messagebox.showinfo("Warning", "Please Import Audio File First")


def playAudio(indication):
    if hasImported:
        if indication == 'OG':
            wave_object = sa.WaveObject.from_wave_file(direc)
            play_object = wave_object.play()
            play_object.wait_done()
        else:
            audio_file = './/audio//Modified.wav' #os.path.dirname(__file__) +
            playsound(audio_file)
    else:
        messagebox.showinfo("Warning", "Please Import Audio File First")

darkM=False
def darkMod():
    global darkM
    if darkM==False:
        Style(theme='cyborg')
        style.configure('TLabel', font=('Barlow', 12))
        style.configure('TRadiobutton', font=('Barlow', 12))
        style.configure('TButton', width=7, font=("Barlow", 13))
        style.configure('TMenubutton', font=("Barlow", 13))
        darkBtn.config(image=white_icon)
        updatefr(wvFr)
        updatefr(wvFrMod)
        darkM=True
    else:
        Style(theme='cosmo')
        style.configure('TLabel', font=('Barlow', 12))
        style.configure('TRadiobutton', font=('Barlow', 12))
        style.configure('TButton', width=7, font=("Barlow", 13))
        style.configure('TMenubutton', font=("Barlow", 13))
        darkBtn.config(image=dark_icon)
        updatefr(wvFr)
        updatefr(wvFrMod)
        darkM = False

# header buttons
ttk.Button(
    root,
    text='  Import',
    command=importfunc,
    image=import_icon,
    compound=tk.LEFT,
).place(x=1050, y=55)


darkBtn=ttk.Button(
    root,
    command=darkMod,
    image=dark_icon,
    compound=tk.LEFT,
    width=1,
    style='Link.TButton'
)
darkBtn.place(x=970, y=55)
# header section
ttk.Label(root, text='Signal Processing with Python', font=("Barlow", 20)).place(x=37, y=17)
ttk.Label(root, text='Audio File Overview', font=("Barlow", 17)).place(x=37, y=65)

# file info section
fileTypeFr = tk.Frame(root, height=100, width=215)
fileTypeFr.place(x=37, y=100)
folderIcon = tk.PhotoImage(file='./icons/icon1.png')
ttk.Label(fileTypeFr, image=folderIcon).place(x=0, y=10)
fileTypeVal = ttk.Label(fileTypeFr, text='Unknown', font=("Abel", 13))
fileTypeVal.place(x=75, y=20)
ttk.Label(fileTypeFr, text='Type Of Audio File', font=("Actor", 12)).place(x=75, y=50)

channelFr = tk.Frame(root, height=100, width=215)
channelFr.place(x=270, y=100)
channelsIcon = tk.PhotoImage(file='./icons/icon2.png')
ttk.Label(channelFr, image=channelsIcon).place(x=0, y=10)
channelsVal = ttk.Label(channelFr, text='0', font=("Abel", 13))
channelsVal.place(x=75, y=20)
ttk.Label(channelFr, text='Channels', font=("Actor", 12)).place(x=75, y=50)

frameRateFr = tk.Frame(root, height=100, width=215)
frameRateFr.place(x=493, y=100)
frameRateIcon = tk.PhotoImage(file='./icons/icon3.png')
ttk.Label(frameRateFr, image=frameRateIcon).place(x=0, y=10)
frameRateVal = ttk.Label(frameRateFr, text='0', font=("Abel", 13))
frameRateVal.place(x=75, y=20)
ttk.Label(frameRateFr, text='Frame Rate', font=("Actor", 12)).place(x=75, y=50)

ampFr = tk.Frame(root, height=100, width=220)
ampFr.place(x=716, y=100)
ampIcon = tk.PhotoImage(file='./icons/icon4.png')
ttk.Label(ampFr, image=ampIcon).place(x=0, y=10)
ampVal = tk.Label(ampFr, text='0', font=("Abel", 13))
ampVal.place(x=75, y=20)
ttk.Label(ampFr, text='Maximum Amplitude', font=("Actor", 12)).place(x=75, y=50)

# Waveform section
tk.Label(root, text='Audio Wave Form', font=("Barlow", 17)).place(x=37, y=200)

wvFr = tk.Frame(root, height=190, width=770)
wvFr.place(x=37, y=240)
wvFrMod = tk.Frame(root, height=190, width=770)
wvFrMod.place(x=37, y=470)

# tasks section
tasksLB = tk.Label(root, text='Tasks', font=("Barlow", 17)).place(x=900, y=280)
tasksVB = ttk.Separator(root, orient='vertical', style='info.Vertical.TSeparator')
tasksVB.place(x=980, y=280)
tasksFr = ttk.Frame(root, height=300, width=270)
tasksFr.place(x=900, y=320)

# Task labels
ttk.Label(root, text='Amplitude').place(x=915, y=345)
ampText = tk.StringVar()
ampValueLB = ttk.Entry(root,
                       justify="center",
                       textvariable=ampText,
                       width=15,
                       font=("Barlow", 10)
                       )
ampValueLB.place(x=1015, y=345)
ttk.Label(root, text='Shift', ).place(x=915, y=385)

shiftText = tk.StringVar()
shiftValueLB = ttk.Entry(root,
                         justify="center",
                         textvariable=shiftText,
                         width=15,
                         font=("Barlow", 10)
                         )
shiftValueLB.place(x=1015, y=385)

ttk.Label(root, text='Speed', ).place(x=915, y=425)
speedText = tk.StringVar()
speedValueLB = ttk.Entry(root,
                         justify="center",
                         textvariable=speedText,
                         width=15,
                         font=("Barlow", 10)
                         )
speedValueLB.place(x=1015, y=425)

ttk.Label(root, text='Reverse', ).place(x=915, y=465)
revText = tk.StringVar()
reverseTrueVal = ttk.Radiobutton(root, style='primary.TRadiobutton', text="True", variable=revText, value=1)
reverseTrueVal.place(x=1055, y=470)
reverseFalseVal = ttk.Radiobutton(root, style='primary.TRadiobutton', text="False", variable=revText, value=2, )
reverseFalseVal.place(x=1055, y=500)

ttk.Label(root, text='Echo', ).place(x=915, y=530)
echoText = tk.StringVar()
echoTrueVal = ttk.Radiobutton(root, style='TRadiobutton', text="True", variable=echoText, value=3)
echoTrueVal.place(x=1055, y=540)
echoFalseVal = ttk.Radiobutton(root, style='primary.TRadiobutton', text="False", variable=echoText, value=4, )
echoFalseVal.place(x=1055, y=570)

# Tasks buttons
ttk.Button(
    root,
    style='success.Outline.TButton',
    text='Apply',
    command=applyOperations
).place(x=940, y=630)

# Play buttons
ttk.Button(
    root,
    text='  Play',
    command=lambda: playAudio('mod'),
    image=play_icon,
    compound=tk.LEFT,
).place(x=1050, y=630)
ttk.Button(
    root,
    text='  Play',
    command=lambda: playAudio('OG'),
    image=play_icon,
    compound=tk.LEFT,
).place(x=735, y=200)


# Plot the convolution signal
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


# Covolution PopUp
def openConvWindow():
    # checking if the user has imported a file or not
    if hasImported:
        # be treated as a new window
        newConvWindow = Toplevel(root)
        newConvWindow.title("Convolution")
        newConvWindow.iconbitmap('./icons/picon.ico')
        newConvWindow.resizable(False, False)
        newConvWindow.geometry("1200x740")
        # Three plotting frames
        global OGSginalFr
        OGSginalFr = ttk.Frame(newConvWindow, style='TFrame', height=190, width=770)
        OGSginalFr.place(x=10, y=10)
        global ModSginalFr
        ModSginalFr = ttk.Frame(newConvWindow, style='TFrame', height=190, width=770)
        ModSginalFr.place(x=10, y=250)
        global ConvSginalFr
        ConvSginalFr = ttk.Frame(newConvWindow, style='TFrame', height=190, width=770)
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
        ttk.Label(newConvWindow, text="Select Impulse Response").place(x=810, y=230)
        ttk.Button(
            newConvWindow,
            text='Apply',
            command=lambda: ApplyConvolution(option_var.get()),
        ).place(x=910, y=500)
        # plot the original signal based on the imported audio file
        global sig
        sig = data
        # plot the original signal
        plottCon(sig, OGSginalFr, 'Original Signal')
    else:
        messagebox.showinfo("Warning", "Please Import Audio File First")



# convlution button on the main interface
ttk.Button(
    root,
    text='  Convolution',
    command=openConvWindow,
    image=conv_icon,
    compound=tk.LEFT,
    width=9,
    style='warning.TButton'
).place(x=1000, y=200)


# Text To Speach Function
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
    engine.save_to_file(speach, './/audio//Transcript.mp3')
    engine.runAndWait()


def openTTSWindow():
    newWindow = Toplevel(root)
    newWindow.title("Text To Speach")
    newWindow.iconbitmap('./icons/picon.ico')
    newWindow.resizable(False, False)
    newWindow.geometry("400x200")
    # A Label widget to show in toplevel
    ttk.Label(newWindow, text="Please Write The Transcript").pack(pady=10)
    ttsText = tk.StringVar()
    ttsValueLB = ttk.Entry(newWindow,
                           justify="center",
                           textvariable=ttsText,
                           font=("Barlow", 12),
                           )
    ttsValueLB.pack(fill='x', pady=10)

    # Get the text value function
    def Get_MyInputValue(widg):
        getresult = widg.get()
        tts(str(getresult))
        return

    ttk.Button(
        newWindow,
        text='Convert',
        command=lambda: Get_MyInputValue(ttsValueLB),
    ).pack(pady=20)


# TTS Button
ttk.Button(
    root,
    text=' Text To Speach',
    command=openTTSWindow,
    image=tts_icon,
    compound=tk.LEFT,
    style='success.TButton',
    width=12,
).place(x=1000, y=280)

# Fix the DPI Bug
windll.shcore.SetProcessDpiAwareness(1)
root.mainloop()
