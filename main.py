import datetime
import os
import sqlite3
import struct
import wave
import matplotlib
import numpy as np
import pyttsx3
import ttkbootstrap as ttk
import winsound

# handling images and convolution modules
from PIL import Image, ImageTk
from scipy import signal

# plotting specific modules
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ttk UI specific modules
from tkinter import filedialog, messagebox
from ttkbootstrap import Toplevel
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.style import Style
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.tooltip import ToolTip

# audio effects modules
from pydub import AudioSegment
from AudioLib import AudioEffect


class MainGUI(ttk.Window):
    # initial parameters for audio file name and location
    file_directory = ''
    directory_name = 'Audio Output'
    dark_mode_state = False
    output_file = directory_name + '/Modified.wav'

    # initial parameters for audio file data
    num_of_channels = 0
    sample_rate = 0
    max_amp = 0
    num_of_frames = 0
    result = (0, 0, 0)
    timeout = 0
    data_out = 0
    data = np.array([])

    # initial parameters for data plotting frames on the UI
    original_plot_state = False
    modified_plot_state = False
    original_id = 0
    plot_img_title = ''

    # connect to database
    connection = sqlite3.connect('signals.db')
    db = connection.cursor()

    # start the image counter at an appropriate number.
    max_id_db = db.execute("SELECT MAX(id) FROM org")
    max_id = max_id_db.fetchone()[0]
    img_count = 0

    def __init__(self, *args, **kwargs):
        super(MainGUI, self).__init__(*args, **kwargs)

        # prevent img count from increasing on startup
        if self.max_id is not None:
            self.img_count = self.max_id

        # app variables
        current_style = Style()
        echo_state = ttk.StringVar()
        rev_state = ttk.StringVar()

        # create History and Audio Output directories on launch
        self.make_output_directory()

        # register the call back function for input validation
        self.user_validation = self.register(validation_callback)

        def set_theme():
            stop_audio()
            update_frame(og_wave_frame)
            update_frame(mod_wave_frame)
            if self.dark_mode_state:
                current_style.theme_use('cyborg')
                theme_btn.config(image='themeToggleLight')
                import_btn.config(image='import-dark')
                open_conv_btn.config(image='convolution-dark')
                open_history_btn.config(image='history-dark')
                open_history_btn.config(image='history-dark')
                tts_btn.config(image='tts-dark')
                self.dark_mode_state = False
            else:
                current_style.theme_use('litera')
                import_btn.config(image='import')
                open_conv_btn.config(image='convolution')
                open_history_btn.config(image='history')
                theme_btn.config(image='themeToggleDark')
                tts_btn.config(image='tts')
                self.dark_mode_state = True
            current_style.configure('TLabel', font=('Barlow', 10))
            current_style.configure('TButton', font=("Barlow", 11))
            current_style.configure('TMenubutton', font=("Barlow", 10))
            current_style.configure('TNotebook.Tab', font=("Barlow", 10))
            if self.original_plot_state:
                self.plotting(None, self.result[0], self.result[1], og_wave_frame, "Original Audio")
            if self.modified_plot_state:
                self.plotting(None, self.timeout, self.data_out, mod_wave_frame, 'Modified Audio')

        def read_file(file):
            # minus one here means that all the frames of the file has to be read
            raw = file.readframes(-1)
            # get the number of channels in the audio file
            self.num_of_channels = file.getnchannels()
            # sign it with 16-bit ints since wave files are encoded with 16 bits per sample
            self.data = np.frombuffer(raw, "int16")
            self.sample_rate = file.getframerate()
            self.num_of_frames = file.getnframes()
            # get the duration of the audio file
            duration = self.num_of_frames / float(self.sample_rate)
            hours, minutes, seconds = output_duration(int(duration))
            total_time = f'{hours}:{minutes}:{seconds}'
            # display the duration
            length_lb.config(text=total_time)
            time = np.linspace(0, len(self.data) / self.sample_rate, num=len(self.data))
            return time, self.data

        def import_file():
            update_frame(og_wave_frame)
            update_frame(mod_wave_frame)
            # hide the plotting frames every time we import
            self.original_plot_state = False
            self.modified_plot_state = False
            stop_audio()
            # open window to select file to get the path then save in variable directory
            filename = filedialog.askopenfilename(initialdir=self.file_directory, title="Select Audio File",
                                                  filetypes=(('Wav', '*wav'), ('Mp3', '*mp3')))
            self.file_directory = filename
            # using splitext() to find file extension
            file_extension = os.path.splitext(self.file_directory)[1]
            if self.file_directory == '':
                messagebox.showerror('Error', 'No File Was Selected')
                return
            else:
                # checks if the output file is there and delete it
                if os.path.isfile(self.output_file):
                    os.remove(self.output_file)

                # convert mp3 file to wav, so it can be read by wave.open()
                if file_extension == '.mp3':
                    mp3_file = AudioSegment.from_mp3(file=self.file_directory)
                    mp3_file.export(self.directory_name + '/Mp3converted.wav', format='wav')
                    self.file_directory = self.directory_name + '/Mp3converted.wav'

                # read the new imported file
                wav_file = wave.open(self.file_directory, 'r')
                self.result = read_file(wav_file)
                # Update displayed File info
                wav_d = AudioSegment.from_file(file=self.file_directory, format="wav")
                self.max_amp = wav_d.max
                file_type_val.config(text=file_extension)
                file_channels_val.config(text=self.num_of_channels)
                file_frames_val.config(text=self.sample_rate)
                file_max_amp_val.config(text=self.max_amp)
                # start plotting
                self.plotting(None, self.result[0], self.result[1], og_wave_frame, 'Original Audio')
                self.original_plot_state = True
                # Set echo options on if the file is stereo
                if self.num_of_channels == 2:
                    echo_toggle.config(state='!selected')
                else:
                    echo_toggle.config(state='disabled')

        def play_audio(indication):
            if self.file_directory != '':
                if indication == 'OG':
                    audio_file = self.file_directory
                else:
                    if os.path.isfile(self.output_file):
                        audio_file = self.output_file
                    else:
                        messagebox.showinfo('Info', 'Apply Modification To The Audio File Then Play It')
                        return
                winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                messagebox.showwarning("Warning", "Please Import Audio File First")

        def stop_audio():
            winsound.PlaySound(None, winsound.SND_FILENAME)

        def operations(amp_amount, shift_amount, speed_amount, reverse_state, echo_st):
            update_frame(mod_wave_frame)
            audio_obj = wave.open(self.output_file, 'wb')
            audio_obj.setnchannels(self.num_of_channels)
            audio_obj.setsampwidth(2)
            # speed OP
            speed_factor = speed_amount
            speed = self.sample_rate * speed_factor
            audio_obj.setframerate(speed)
            # Shift OP
            pov_shift_in_sec = shift_amount
            for i in range(int(self.sample_rate * pov_shift_in_sec)):
                zero_in_byte = struct.pack('<h', 0)
                audio_obj.writeframesraw(zero_in_byte)
            # Amplification OP
            amp = amp_amount
            n = len(self.data)
            # Reverse OP
            reverse = reverse_state
            if reverse:
                for i in range(self.data.__len__()):
                    two_byte_sample = self.data[n - 1 - i] * amp
                    if two_byte_sample > 32760:
                        two_byte_sample = 32760
                    if two_byte_sample < -32760:
                        two_byte_sample = -32760
                    sample = struct.pack('<h', int(two_byte_sample))
                    audio_obj.writeframesraw(sample)
            else:
                for i in range(self.data.__len__()):
                    if self.data[i] * amp > 32760:
                        two_byte_sampler = 32760
                    elif self.data[i] * amp < -32760:
                        two_byte_sampler = -32760
                    else:
                        two_byte_sampler = self.data[i] * amp
                    sample = struct.pack('<h', int(two_byte_sampler))
                    audio_obj.writeframesraw(sample)
            audio_obj.close()
            obj = wave.open(self.output_file, 'rb')  # open
            self.data_out = obj.readframes(-1)  # get all the frames in data out
            self.data_out = np.frombuffer(self.data_out, "int16")  # set the data to a number of two byte form data out
            self.sample_rate_out = obj.getframerate()  # frame rate HZ (number of frames to be reads in seconds)
            self.timeout = np.linspace(0, len(self.data_out) / self.sample_rate_out, num=len(self.data_out))
            self.plotting(None, self.timeout, self.data_out, mod_wave_frame, 'Modified Audio')
            self.modified_plot_state = True
            # set the echo based on state
            if echo_st:
                AudioEffect.echo(self.output_file, self.output_file)
            obj.close()
            # show a message when done modifying the file
            toast = ToastNotification(
                title="Output File Saved",
                message="Modified.wav Was Saved To Audio Output Folder",
                duration=3000,
            )
            toast.show_toast()
            # write the modified signal into the database
            date = datetime.datetime.now()
            self.db.execute(
                'INSERT INTO modsignal(org_id,name,date,amp,shift,speed,reverse,echo) VALUES (?,?,?,?,?,?,?,?)',
                (self.original_id, self.plot_img_title, date, amp_amount, shift_amount, speed_amount,
                 bool(reverse_state),
                 bool(echo_st)))
            self.connection.commit()

        def apply_operations():
            stop_audio()
            if self.file_directory != '' and amp_entry.get() != '' and speed_entry.get() != '' \
                    and shift_entry.get() != '':
                amp_amount = float(amp_entry.get())
                shift_amount = float(shift_entry.get())
                speed_amount = float(speed_entry.get())
                if rev_state.get() == 'revOn':
                    reverse_st = True
                else:
                    reverse_st = False
                if echo_state.get() == 'echoOn' and self.num_of_channels == 2:
                    echo_st = True
                else:
                    echo_st = False
                # Validate input
                if speed_amount > 2 or speed_amount < 0.25:
                    messagebox.showinfo('Info', 'Speed Value Must Be Between 0.25 And 2')
                    return
                if shift_amount < 0:
                    messagebox.showinfo('Info', 'Shift Value Must Be Positive')
                    return
                operations(amp_amount, shift_amount, speed_amount, reverse_st, echo_st)
            else:
                messagebox.showinfo('Warning', 'Please Import Audio File First And Set Valid Values')
                return

        self.images = [
            ttk.PhotoImage(
                name='openfile',
                file='Icons/open-file-icon.png'),
            ttk.PhotoImage(
                name='channels',
                file='Icons/channels-icon.png'),
            ttk.PhotoImage(
                name='frameRate',
                file='Icons/framerate-icon.png'),
            ttk.PhotoImage(
                name='maxAmp',
                file='Icons/max-amp-icon.png'),
            ttk.PhotoImage(
                name='import',
                file='Icons/import-file.png'),
            ttk.PhotoImage(
                name='import-dark',
                file='Icons/import-file-dark.png'),
            ttk.PhotoImage(
                name='themeToggleDark',
                file='Icons/darkIcon.png'),
            ttk.PhotoImage(
                name='themeToggleLight',
                file='Icons/whiteIcon.png'),
            ttk.PhotoImage(
                name='play',
                file='Icons/play-button.png'),
            ttk.PhotoImage(
                name='stop',
                file='Icons/stop-button.png'),
            ttk.PhotoImage(
                name='convolution',
                file='Icons/conv-button.png'),
            ttk.PhotoImage(
                name='convolution-dark',
                file='Icons/conv-button-dark.png'),
            ttk.PhotoImage(
                name='tts',
                file='Icons/message-button.png'),
            ttk.PhotoImage(
                name='tts-dark',
                file='Icons/message-button-dark.png'),
            ttk.PhotoImage(
                name='history',
                file='Icons/history-button.png'),
            ttk.PhotoImage(
                name='history-dark',
                file='Icons/history-button-dark.png'),
            ttk.PhotoImage(
                name='apply',
                file='Icons/apply-button.png'),
            ttk.PhotoImage(
                name='convert',
                file='Icons/convert-button.png'),
            ttk.PhotoImage(
                name='convert-dark',
                file='Icons/convert-button-dark.png'),
        ]

        hdr_frame = ttk.Frame(self, padding=(20, 10))
        hdr_frame.pack(fill=X, padx=10)
        ttk.Label(hdr_frame, text='Audio Signal Processing', font=("Barlow", 15)).pack(fill=X)
        hdr_btn_frame = ttk.Frame(hdr_frame)
        hdr_btn_frame.pack(fill=X, pady=5)
        ttk.Label(hdr_btn_frame, text='Audio File Overview', font=("Barlow", 13)).pack(side=LEFT)
        import_btn = ttk.Button(
            master=hdr_btn_frame,
            image='import',
            compound=LEFT,
            command=import_file,
            bootstyle=LINK
        )
        import_btn.pack(side=RIGHT)

        theme_btn = ttk.Button(
            master=hdr_btn_frame,
            image='themeToggleDark',
            bootstyle=LINK,
            command=set_theme
        )

        theme_btn.pack(side=RIGHT, padx=10)

        file_overview_frame = ttk.Frame(hdr_frame)
        file_overview_frame.pack(fill=X, padx=5)
        file_name_frame = ttk.Frame(file_overview_frame)
        file_name_frame.pack(side=LEFT, padx=(0, 20))
        file_name_icon = ttk.Label(master=file_name_frame, image='openfile')
        file_name_icon.grid(row=0, column=0, rowspan=2)
        file_type_val = ttk.Label(file_name_frame, text='Unknown')
        file_type_val.grid(row=0, column=1, sticky=W, padx=5)
        ttk.Label(file_name_frame, text='Type Of Audio File').grid(row=1, column=1, sticky=W, padx=5)

        file_channels_frame = ttk.Frame(file_overview_frame)
        file_channels_frame.pack(side=LEFT, padx=20)
        file_channels_icon = ttk.Label(master=file_channels_frame, image='channels')
        file_channels_icon.grid(row=0, column=0, rowspan=2)
        file_channels_val = ttk.Label(file_channels_frame, text='0')
        file_channels_val.grid(row=0, column=1, sticky=W, padx=5)
        ttk.Label(file_channels_frame, text='Channels').grid(row=1, column=1, sticky=W, padx=5)

        file_frames_frame = ttk.Frame(file_overview_frame, )
        file_frames_frame.pack(side=LEFT, padx=20)
        file_frames_icon = ttk.Label(master=file_frames_frame, image='frameRate')
        file_frames_icon.grid(row=0, column=0, rowspan=2)
        file_frames_val = ttk.Label(file_frames_frame, text='0')
        file_frames_val.grid(row=0, column=1, sticky=W, padx=5)
        ttk.Label(file_frames_frame, text='Frame Rate').grid(row=1, column=1, sticky=W, padx=5)

        file_max_amp_frame = ttk.Frame(file_overview_frame, )
        file_max_amp_frame.pack(side=LEFT, padx=20)
        file_max_amp_icon = ttk.Label(master=file_max_amp_frame, image='maxAmp')
        file_max_amp_icon.grid(row=0, column=0, rowspan=2)
        file_max_amp_val = ttk.Label(file_max_amp_frame, text='0')
        file_max_amp_val.grid(row=0, column=1, sticky=W, padx=5)
        ttk.Label(file_max_amp_frame, text='Maximum Amplitude').grid(row=1, column=1, sticky=W, padx=5)

        # play buttons section
        file_action_frame = ttk.Frame(hdr_frame, padding=(0, 10))
        file_action_frame.pack(fill=X)
        ttk.Label(file_action_frame, text='Audio Wave Form', font=("Barlow", 13)).pack(side=LEFT)
        open_conv_btn = ttk.Button(
            master=file_action_frame,
            text=' Convolution',
            image='convolution',
            compound=LEFT,
            bootstyle=LINK,
            command=self.open_conv_window
        )
        open_conv_btn.pack(side=RIGHT, padx=(10, 0))

        open_history_btn = ttk.Button(
            master=file_action_frame,
            text=' History',
            image='history',
            compound=LEFT,
            bootstyle=LINK,
            command=self.open_history_window
        )
        open_history_btn.pack(side=RIGHT)

        og_play_btn = ttk.Button(
            master=file_action_frame,
            image='play',
            compound=LEFT,
            bootstyle=LINK,
            command=lambda: play_audio('OG')
        )
        ToolTip(og_play_btn, delay=1500, text="Play Original Audio", bootstyle=PRIMARY)
        og_play_btn.pack(side=RIGHT, padx=20)
        stop_btn = ttk.Button(
            master=file_action_frame,
            image='stop',
            compound=LEFT,
            bootstyle=LINK,
            command=stop_audio
        )
        stop_btn.pack(side=RIGHT)
        ttk.Separator(file_action_frame, orient=VERTICAL).pack(side=RIGHT, padx=20)
        length_lb = ttk.Label(file_action_frame, text='', font=("Barlow", 13))
        length_lb.pack(side=RIGHT, padx=20)

        tasks_frame = ttk.Frame(self, padding=5)
        tasks_frame.pack(side=RIGHT, fill=Y, pady=5, padx=25)

        og_wave_frame = ttk.Frame(self)
        og_wave_frame.pack(side=TOP)
        mod_wave_frame = ttk.Frame(self)
        mod_wave_frame.pack(side=TOP, pady=5)

        tasks_hdr_frame = ttk.Frame(tasks_frame)
        tasks_hdr_frame.pack(side=TOP, fill=X)
        ttk.Label(tasks_hdr_frame, text='Tasks', font=("Barlow", 13)).pack(side=LEFT)

        tts_btn = ttk.Button(
            master=tasks_hdr_frame,
            text=' Text To Speach',
            image='tts',
            compound=LEFT,
            bootstyle=LINK,
            command=self.open_tts_window
        )
        tts_btn.pack(side=RIGHT)
        ttk.Separator(tasks_hdr_frame, orient=VERTICAL).pack(side=RIGHT, padx=20)

        operations_frame = ttk.Frame(tasks_frame, padding=10)
        operations_frame.pack(side=TOP, fill=BOTH)
        ttk.Label(operations_frame, text='Amplitude').grid(row=0, column=0, padx=(0, 20), sticky=W)
        amp_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                              validatecommand=(self.user_validation, '%P'), font=("Barlow", 10))
        amp_entry.grid(row=0, column=1, pady=10)
        ttk.Label(operations_frame, text='Shift').grid(row=1, column=0, padx=(0, 20), sticky=W)
        shift_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                                validatecommand=(self.user_validation, '%P'), font=("Barlow", 10))
        shift_entry.grid(row=1, column=1, pady=10, sticky=W)
        ttk.Label(operations_frame, text='Speed').grid(row=2, column=0, padx=(0, 20), sticky=W)
        speed_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                                validatecommand=(self.user_validation, '%P'), font=("Barlow", 10))
        speed_entry.grid(row=2, column=1, pady=10)

        ttk.Label(operations_frame, text='Reverse').grid(row=3, column=0, pady=10, padx=(0, 20), sticky=W)
        reverse_toggle = ttk.Checkbutton(operations_frame, bootstyle='round-toggle', onvalue='revOn',
                                         variable=rev_state, offvalue='revOff')
        reverse_toggle.grid(row=3, column=1, sticky=W, ipady=20)
        ttk.Label(operations_frame, text='Echo').grid(row=3, column=1, pady=10, padx=(0, 60), sticky=E)
        echo_toggle = ttk.Checkbutton(operations_frame, bootstyle='round-toggle', onvalue='echoOn',
                                      variable=echo_state, offvalue='echoOff')
        echo_toggle.grid(row=3, column=1, sticky=E, ipady=20)

        apply_operations_btn = ttk.Button(
            master=operations_frame,
            text=' Apply',
            image='apply',
            compound=LEFT,
            bootstyle=LINK,
            command=apply_operations
        )
        apply_operations_btn.grid(row=4, column=0, sticky=SE, pady=100)

        mod_play_btn = ttk.Button(
            master=operations_frame,
            text=' Play',
            image='play',
            compound=LEFT,
            bootstyle=LINK,
            command=lambda: play_audio('mod'))
        mod_play_btn.grid(row=4, column=1, sticky=SW, pady=100, padx=20)
        ToolTip(mod_play_btn, delay=1500, text="Play Modified Audio", bootstyle=PRIMARY)

        set_theme()

    def make_output_directory(self):
        try:
            os.mkdir(self.directory_name)
            os.mkdir('History')
        except FileExistsError:
            return
        return

    def plotting(self, targeted_signal, time, raw, place, title):
        matplotlib.style.use('dark_background') if not self.dark_mode_state else matplotlib.style.use('default')
        plotting_figure = Figure(figsize=(7, 2), dpi=90)
        figure_subplot = plotting_figure.add_subplot(111)
        figure_subplot.set_ylabel('Amplitude')
        figure_subplot.grid(alpha=0.4)
        figure_subplot.set_title(title)

        self.plot_img_title = "History/img" + str(self.img_count) + ".png"
        if targeted_signal is not None:
            figure_subplot.plot(targeted_signal, color='blue')
        else:
            figure_subplot.plot(time, raw, color='blue')
            plotting_figure.savefig(self.plot_img_title)
            self.img_count += 1

            if title == 'Original Audio':
                text = [self.plot_img_title]
                self.db.execute('INSERT INTO org(name) VALUES (?)', text)
                self.connection.commit()
                org_id_db = self.db.execute("SELECT id FROM org WHERE name = ?", text)
                self.original_id = org_id_db.fetchone()[0]

        # Creating Canvas to show it in the Frame
        canvas = FigureCanvasTkAgg(plotting_figure, master=place)
        canvas.flush_events()
        canvas.draw()
        canvas.get_tk_widget().pack()

    def open_tts_window(self):
        TTSWindow(self.tts, self.dark_mode_state)

    def open_conv_window(self):
        ConvolutionWindow(self.plotting)

    @staticmethod
    def open_history_window():
        HistoryWindow()

    def tts(self, speach):
        if speach == '':
            messagebox.showinfo("Info", "Enter Some Text")
            return
        else:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # setting up new voice rate
            # say method on the engine that passing input text to be spoken
            engine.say(speach)
            # Saving Voice to a file
            engine.save_to_file(speach, self.directory_name + '/Transcript.mp3')
            # run and wait method, it processes the voice commands.
            engine.runAndWait()
            engine.stop()
            toast = ToastNotification(
                title="Output File Saved",
                message="Transcript.mp3 Was Saved To Audio Output Folder",
                duration=3000,
            )
            toast.show_toast()


class TTSWindow:
    def __init__(self, speach_func, theme_state):
        new_window = Toplevel(title='Text To Speach', size=[400, 200], resizable=[False, False])
        self.speach_func = speach_func
        new_window.place_window_center()
        # A Label widget to show in toplevel
        ttk.Label(new_window, text="Please Write The Transcript").pack(pady=10)
        tts_value_lb = ttk.Entry(new_window, justify="center", font=("Barlow", 10))
        tts_value_lb.pack(fill=X, pady=10)
        convert_btn = ttk.Button(new_window, text=' Convert', image='convert', bootstyle=LINK,
                                 compound=LEFT, command=lambda: self.get_my_input_value(tts_value_lb))
        if theme_state:
            convert_btn.config(image='convert')

        else:
            convert_btn.config(image='convert-dark')
        convert_btn.pack(pady=20)

    def get_my_input_value(self, widget):
        getresult = widget.get()
        self.speach_func(str(getresult))


class ConvolutionWindow:
    def __init__(self, plotting_func):
        new_conv_window = Toplevel(title='Convolution', size=[1200, 740])
        new_conv_window.place_window_center()
        self.plotting_func = plotting_func
        self.zp_to_hs_text = ttk.StringVar()

        tabs_fr = ttk.Frame(new_conv_window)
        tabs_fr.pack(side=RIGHT, fill=BOTH, padx=30)
        self.og_signal_frame = ttk.Frame(new_conv_window)
        self.og_signal_frame.pack(side=TOP, pady=10)
        self.mod_signal_frame = ttk.Frame(new_conv_window)
        self.mod_signal_frame.pack(side=TOP, pady=10)
        self.conv_signal_frame = ttk.Frame(new_conv_window)
        self.conv_signal_frame.pack(side=TOP, pady=10)

        notebook = ttk.Notebook(tabs_fr)
        notebook.pack(side=TOP, pady=10)
        select_wave_frame = ttk.Frame(notebook, width=350, height=400, padding=(10, 20))
        transfer_func_frame = ttk.Frame(notebook, width=350, height=400, padding=(10, 20))
        ttk.Label(transfer_func_frame, text='Numerator').grid(row=0, column=0, sticky=W, padx=10)
        self.trFuncValueLB = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.trFuncValueLB.grid(row=0, column=1, pady=10)
        ttk.Label(transfer_func_frame, text='Denominator').grid(row=1, column=0, sticky=W, padx=10)
        self.tr_func_value_lb2 = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.tr_func_value_lb2.grid(row=1, column=1, pady=10)
        ttk.Separator(transfer_func_frame, orient=HORIZONTAL).grid(row=2, column=0, columnspan=2, pady=10, sticky=EW)
        ttk.Label(transfer_func_frame, text='Zeros').grid(row=3, column=0, sticky=W, padx=10)
        self.zeros_val_lb = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.zeros_val_lb.grid(row=3, column=1, pady=10)
        ttk.Label(transfer_func_frame, text='Poles').grid(row=4, column=0, sticky=W, padx=10)
        self.poles_val_lb = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.poles_val_lb.grid(row=4, column=1, pady=10)
        ttk.Label(transfer_func_frame, text='Option').grid(row=5, column=0, sticky=W, padx=10, pady=15)

        zp_to_hs_true_val = ttk.Radiobutton(transfer_func_frame, text="H (s) To Zeros",
                                            command=lambda: self.disable_box(1), variable=self.zp_to_hs_text, value=1)
        zp_to_hs_true_val.grid(row=5, column=1, sticky=W, padx=10)
        zp_to_hs_false_val = ttk.Radiobutton(transfer_func_frame, text="Zeros To H (s)",
                                             command=lambda: self.disable_box(2), variable=self.zp_to_hs_text, value=2)
        zp_to_hs_false_val.grid(row=6, column=1, sticky=W, padx=10)

        select_wave_frame.pack(fill=BOTH, expand=True)
        transfer_func_frame.pack(fill=BOTH, expand=True)

        # add frames to notebook
        notebook.add(select_wave_frame, text='Wave')
        notebook.add(transfer_func_frame, text='Transfer Function')

        ttk.Label(select_wave_frame, text='Select Impulse Response').pack(side=TOP)
        # menu selection
        self.select_wave_menu = ttk.Menubutton(select_wave_frame, text='Select Wave', bootstyle=(INFO, OUTLINE))
        self.select_wave_menu.pack(side=TOP, pady=20)
        # create menu
        menu = ttk.Menu(self.select_wave_menu)
        # add options
        option_var = ttk.StringVar()
        for option in ['Sine Wave', 'Rec Wave']:
            menu.add_radiobutton(label=option, value=option, variable=option_var)
        # associate menu with menubutton
        self.select_wave_menu['menu'] = menu

        ttk.Button(
            tabs_fr, text=' Apply',
            image='apply',
            compound=LEFT,
            bootstyle=LINK,
            command=lambda: self.apply_convolution(option_var.get())).pack(side=TOP)

        # plot the original signal based on the imported Audio Output file
        self.sig = np.repeat([0., 1., 0.], 100)
        self.plotting_func(self.sig, None, None, self.og_signal_frame, 'Original Signal')

    def lti_sys(self, widget):
        if widget == 1:
            # get the values of the textbox as an array
            num = list(map(float, self.trFuncValueLB.get().strip().split()))
            den = list(map(float, self.tr_func_value_lb2.get().strip().split()))
            # represent the lti_system as transfer function
            lti_system = signal.lti(num, den)
            # display the values in the textbox after rounding
            for z in lti_system.zeros:
                z_rounded = np.round(z, 2)
                self.zeros_val_lb.insert(0, str(z_rounded) + "  ")
            for p in lti_system.poles:
                p_rounded = np.round(p, 2)
                self.poles_val_lb.insert(0, str(p_rounded) + "  ")
        else:
            zeros = list(map(int, self.zeros_val_lb.get().strip().split()))
            poles = list(map(int, self.poles_val_lb.get().strip().split()))
            # get the num and den from the z and p
            hs_rep = signal.zpk2tf(zeros, poles, k=1)
            for z in hs_rep[0]:
                z_rounded = np.round(z, 2)
                self.trFuncValueLB.insert(0, str(z_rounded) + "  ")
            for p in hs_rep[1]:
                p_rounded = np.round(p, 2)
                self.tr_func_value_lb2.insert(0, str(p_rounded) + "  ")

    def apply_convolution(self, conv_val):
        update_frame(self.mod_signal_frame)
        update_frame(self.conv_signal_frame)

        # get the value of the option radiobutton
        option_val = str(self.zp_to_hs_text.get())
        if option_val == '1':
            # update the values each time the button is pressed
            delete_entries(self.zeros_val_lb)
            delete_entries(self.poles_val_lb)
            self.zeros_val_lb.config(state="normal")
            self.poles_val_lb.config(state="normal")
            if self.trFuncValueLB.get() != "" and self.tr_func_value_lb2.get() != "":
                self.lti_sys(1)
        if option_val == '2':
            delete_entries(self.trFuncValueLB)
            delete_entries(self.tr_func_value_lb2)
            self.trFuncValueLB.config(state="normal")
            self.tr_func_value_lb2.config(state="normal")
            if self.zeros_val_lb.get() != "" and self.poles_val_lb.get() != "":
                self.lti_sys(2)

        if conv_val == 'Sine Wave':
            win = signal.windows.hann(50)
            self.plotting_func(win, None, None, self.mod_signal_frame, 'Impulse Response')
            filtered = signal.convolve(self.sig, win, mode='same') / sum(win)
            self.plotting_func(filtered, None, None, self.conv_signal_frame, 'Filtered Signal')
            self.select_wave_menu.config(text="Sine Wave")
        if conv_val == 'Rec Wave':
            win = np.repeat([0., 1., 0.], 50)
            self.plotting_func(win, None, None, self.mod_signal_frame, 'Impulse Response')
            filtered = signal.convolve(self.sig, win, mode='same') / sum(win)
            self.plotting_func(filtered, None, None, self.conv_signal_frame, 'Filtered Signal')
            self.select_wave_menu.config(text="Rec Wave")
        return

    def disable_box(self, num):
        delete_entries(self.zeros_val_lb)
        delete_entries(self.poles_val_lb)
        delete_entries(self.trFuncValueLB)
        delete_entries(self.tr_func_value_lb2)
        if num == 1:
            self.zeros_val_lb.config(state="readonly")
            self.poles_val_lb.config(state="readonly")
            self.trFuncValueLB.config(state="normal")
            self.tr_func_value_lb2.config(state="normal")
        else:
            self.trFuncValueLB.config(state="readonly")
            self.tr_func_value_lb2.config(state="readonly")
            self.zeros_val_lb.config(state="normal")
            self.poles_val_lb.config(state="normal")


class HistoryWindow:
    def __init__(self):
        new_conv_window = Toplevel(title='History', size=[1200, 740])
        new_conv_window.place_window_center()

        # creat a main frame.
        hist_fr = ScrolledFrame(new_conv_window, autohide=True)
        hist_fr.pack(side=TOP, expand=True, fill=BOTH)
        # fetch the data from the database
        org_signal_list_db = MainGUI.db.execute("SELECT id, name FROM org")
        org_signal_list = org_signal_list_db.fetchall()
        row = 1
        clm = 1
        for org_signal in org_signal_list:
            org_signal_list_db = MainGUI.db.execute(
                "SELECT name,date,amp,shift,speed,reverse,echo FROM modsignal WHERE org_id = (?)",
                [(org_signal[0])])
            mod_signal_info_list = org_signal_list_db.fetchall()
            for mod_signal_info in mod_signal_info_list:
                # add the information of the  manipulation operation.
                self.add_info_label(row, hist_fr, mod_signal_info[1], mod_signal_info[2], mod_signal_info[3],
                                    mod_signal_info[4],
                                    mod_signal_info[5], mod_signal_info[6])
                # add the original signal in the row
                self.add_img(org_signal[1], row, clm, hist_fr)
                clm += 1
                # add the modified signal
                self.add_img(mod_signal_info[0], row, clm, hist_fr)
                row += 1
                clm -= 1

    @staticmethod
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

    @staticmethod
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


if __name__ == '__main__':

    # check for input validation for float numbers only
    def validation_callback(user_val):
        try:
            if float(user_val) >= 0:
                return True
        except ValueError:
            if user_val == '':
                return True
        return False


    # clear the frame when we add another plot.
    def update_frame(obj):
        if len(obj.winfo_children()) >= 1:
            obj.winfo_children()[0].destroy()


    def output_duration(length):
        hours = length // 3600  # calculate in hours
        length %= 3600
        minutes = length // 60  # calculate in minutes
        length %= 60
        seconds = length  # calculate in seconds
        return hours, minutes, seconds


    def delete_entries(wid):
        wid.delete(0, END)


    window_width = 1200
    window_height = 700
    app = MainGUI(title='Audio Signal Processing', iconphoto='Icons/favIcon.png', size=[window_width, window_height])
    app.place_window_center()
    app.mainloop()
