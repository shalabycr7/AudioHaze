import datetime
import importlib
import os
import sqlite3
import struct
import sys
import threading
import wave
from pathlib import Path
from tkinter import filedialog

import numpy as np
import sounddevice as sd
import soundfile as sf
import ttkbootstrap as ttk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pydub import AudioSegment
from scipy import signal
from ttkbootstrap import Toplevel
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.toast import ToastNotification

from AudioHaze import main_interface, audio_effect, utility, DATADIR


def create_wave_plot(master):
    # create the figure and canvas objects
    fig = Figure(figsize=(9, 2.4), dpi=90, facecolor='none')

    # create the axes object
    ax = fig.add_subplot(111, facecolor='none')

    for spine in ax.spines.values():
        spine.set_color('blue')
    canvas = FigureCanvasTkAgg(fig, master=master)

    return fig, ax, canvas


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = DATADIR

    return os.path.join(base_path, relative_path)


class AudioPlayer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.playing = False

    def play(self):
        if not self.playing:
            self.playing = True
            self.thread = threading.Thread(target=self._play, daemon=True)
            self.thread.start()

    def _play(self):
        data, sample_rate = sf.read(self.file_path)
        sd.play(data, sample_rate)

        while self.playing and sd.get_stream().active:
            pass

        sd.stop()
        self.playing = False

    def stop(self):
        self.playing = False


class MainApp(ttk.Frame):
    # initial parameters for audio file name and location
    file_directory = ''
    output_directory_name = Path('./Audio Output')
    dark_mode_state = False
    output_file = str(output_directory_name / 'Modified.wav')

    # initial parameters for audio file data
    original_file_data = {}
    modified_file_data = {}

    # initial parameters for data plotting frames on the UI
    original_id = 0
    plot_img_title = ''

    # connect to database
    connection = sqlite3.connect(resource_path("signals.db"))
    db = connection.cursor()

    # start the image counter at an appropriate number.
    max_id_db = db.execute("SELECT MAX(id) FROM org")
    max_id = max_id_db.fetchone()[0]
    img_count = 0

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.thread = None
        self.audio_player = None
        self.pack(fill='both', expand=1)
        self.current_style = ttk.Style()
        self.theme_images = {
            True: {
                'toggle': 'theme-toggle-dark',
                'import': 'import-file-dark',
                'conv': 'conv-button-dark',
                'history': 'history-button-dark',
                'tts': 'tts-dark',
            },
            False: {
                'toggle': 'theme-toggle',
                'import': 'import-file',
                'conv': 'conv-button',
                'history': 'history-button',
                'tts': 'tts',
            },
        }

        # create 'Audio Output' & 'History'
        self.make_output_directory()

        self.ui_elements = main_interface.create_main_ui(self, self.import_file,
                                                         self.set_theme, self.apply_operations, self.play_audio,
                                                         self.open_tts_window, self.open_conv_window,
                                                         self.stop_playback, self.open_history_window)
        # create the original wave plot
        self.fig, self.ax, self.original_canvas = create_wave_plot(self.ui_elements['original_wave_frame'])

        # create the modified wave plot
        self.fig2, self.ax2, self.modified_canvas = create_wave_plot(self.ui_elements['modified_wave_frame'])
        self.original_canvas.get_tk_widget().pack()
        self.modified_canvas.get_tk_widget().pack()

        self.set_theme()

        self.ui_elements['stop_btn'].config(state='disabled')

    def make_output_directory(self):
        Path('./History').mkdir(exist_ok=True)
        Path(self.output_directory_name).mkdir(exist_ok=True)

    def set_theme(self):
        font_size = 10
        theme_name = 'midnight' if self.dark_mode_state else 'litera'
        current_images = self.theme_images[self.dark_mode_state]

        self.current_style.theme_use(theme_name)
        self.dark_mode_state = not self.dark_mode_state

        # Configure fonts
        font_config = f'-family Barlow -size {font_size}'
        label_font_config = {'font': font_config}
        button_font_config = {'font': f'-family Barlow -size {font_size + 1}'}
        menu_font_config = {'font': font_config}
        tab_font_config = {'font': font_config}
        self.current_style.configure('TLabel', **label_font_config)
        self.current_style.configure('TButton', **button_font_config)
        self.current_style.configure('TMenubutton', **menu_font_config)
        self.current_style.configure('TNotebook.Tab', **tab_font_config)

        # Update widget images
        widget_images = {
            'theme_btn': current_images['toggle'],
            'import_btn': current_images['import'],
            'open_conv_btn': current_images['conv'],
            'open_history_btn': current_images['history'],
            'tts_btn': current_images['tts']
        }
        for widget_name, image in widget_images.items():
            self.ui_elements[widget_name].config(image=image)

        # Plot data
        plots = [
            {
                'file_data': self.original_file_data,
                'frame': self.ax,
                'title': 'Original Audio',
                'canvas': self.original_canvas,
                'figure': self.fig,
                'plot_state': self.ax.has_data()
            },
            {
                'file_data': self.modified_file_data,
                'frame': self.ax2,
                'title': 'Modified Audio',
                'canvas': self.modified_canvas,
                'figure': self.fig2,
                'plot_state': self.ax2.has_data()

            },
        ]
        for plot in plots:
            if plot['plot_state']:
                self.plotting(None, plot['file_data'].get(5), plot['file_data'].get(4),
                              plot['frame'], plot['title'], plot['canvas'], plot['figure'])

    def read_file(self, file, indicator):
        # create a dictionary to hold file data
        data_dict = {
            1: file.channels,
            2: file.frame_rate,
            3: file.frame_count(),
            4: np.frombuffer(file.raw_data, 'int16'),
            6: file.sample_width,
        }
        time = np.linspace(0, len(data_dict[4]) / data_dict[2], num=len(data_dict[4]))
        data_dict[5] = time

        if indicator == 'original':
            self.display_audio_duration(data_dict)

        return data_dict

    def display_audio_duration(self, data_dict):
        # get the duration of the audio file
        frame_count = data_dict[3]
        frame_rate = float(data_dict[2])
        duration = frame_count / frame_rate
        hours, minutes, seconds = utility.output_duration(int(duration))
        total_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        # display the duration
        self.ui_elements['length_lb'].config(text=total_time)

    def import_file(self):
        # Hide the plotting frames every time we import
        self.ax.clear()
        self.ax2.clear()
        self.original_canvas.draw()
        self.modified_canvas.draw()

        # Open window to select file to get the path then save in variable directory
        self.file_directory = filedialog.askopenfilename(initialdir=self.file_directory, title="Select Audio File",
                                                         filetypes=(('Wav', '*wav'), ('Mp3', '*mp3')))
        if not self.file_directory:
            utility.messagebox.showerror('Error', 'No File Was Selected')
            return

        file_extension = Path(self.file_directory).suffix

        # Convert mp3 file to wav, so it can be read
        if file_extension == '.mp3':
            mp3_file = AudioSegment.from_mp3(file=self.file_directory)
            mp3_file.export(self.output_directory_name / 'Mp3converted.wav', format='wav')
            self.file_directory = str(self.output_directory_name / 'Mp3converted.wav')

        # Read the imported file
        wav_original = AudioSegment.from_file(file=self.file_directory)
        self.original_file_data = self.read_file(wav_original, 'original')

        # Update displayed file info
        self.ui_elements['file_type_val'].config(text=file_extension)
        self.ui_elements['file_channels_val'].config(text=self.original_file_data.get(1))
        self.ui_elements['file_frames_val'].config(text=self.original_file_data.get(2))
        self.ui_elements['file_max_amp_val'].config(text=wav_original.max)

        # Start plotting
        self.plotting(None, self.original_file_data.get(5), self.original_file_data.get(4), self.ax,
                      'Original Audio', self.original_canvas, self.fig)

        # Set echo options on if the file is stereo
        self.ui_elements['echo_toggle'].config(state='!selected' if self.original_file_data.get(1) == 2 else 'disabled')

    def plotting(self, targeted_signal, time, raw, place, title, canv, figure):
        plt.style.use('dark_background' if not self.dark_mode_state else 'default')
        # clear the previous plot
        place.clear()
        place.set_ylabel('Amplitude')
        place.grid(alpha=0.4)
        place.set_title(title)

        if targeted_signal is not None:
            # If a targeted signal is provided, plot it
            place.plot(targeted_signal, color='blue')
        else:
            # Otherwise, plot the raw data
            place.plot(time, raw, color='blue')

            # Save the figure to disk and update the image count
            self.plot_img_title = Path('History') / ("img" + str(self.img_count) + ".png")
            figure.savefig(self.plot_img_title)
            self.img_count += 1

            # If this is the original audio plot, add it to the database
            if title == 'Original Audio':
                text = [str(self.plot_img_title)]
                self.db.execute('INSERT INTO org(name) VALUES (?)', text)
                self.connection.commit()
                org_id_db = self.db.execute("SELECT id FROM org WHERE name = ?", text)
                self.original_id = org_id_db.fetchone()[0]

        canv.draw()

    def operations(self, amp_amount, shift_amount, speed_amount, reverse_state, echo_state):
        # Update modified wave frame

        # Create output WAV file and configure audio object
        audio_obj = wave.open(self.output_file, 'wb')
        audio_obj.setnchannels(self.original_file_data.get(1))
        audio_obj.setsampwidth(self.original_file_data.get(6))

        # Change audio speed
        speed = self.original_file_data.get(2) * speed_amount
        audio_obj.setframerate(speed)

        # Shift audio process
        shift_frames = int(self.original_file_data.get(2) * shift_amount)
        zero_in_byte = struct.pack('<h', 0)
        if reverse_state:
            for i in range(shift_frames):
                audio_obj.writeframesraw(zero_in_byte)
        else:
            for i in range(shift_frames):
                audio_obj.writeframesraw(zero_in_byte)

        # Amplification & Reverse process
        amp_frames = [sample * amp_amount for sample in self.original_file_data.get(4)]
        if reverse_state:
            amp_frames = reversed(amp_frames)
        for two_byte_sample in amp_frames:
            if two_byte_sample > 32760:
                two_byte_sample = 32760
            if two_byte_sample < -32760:
                two_byte_sample = -32760
            sample = struct.pack('<h', int(two_byte_sample))
            audio_obj.writeframesraw(sample)

        # Close modified output file stream
        audio_obj.close()

        # Read modified audio file and plot the modified data
        audio_file = AudioSegment.from_file(file=self.output_file, format="wav")
        self.modified_file_data = self.read_file(audio_file, 'modified')
        self.plotting(None, self.modified_file_data.get(5), self.modified_file_data.get(4),
                      self.ax2, 'Modified Audio', self.modified_canvas, self.fig2)

        # Apply echo effect if echo_state is True
        if echo_state:
            audio_effect.echo(self.output_file, self.output_file)

        # Show a message when done modifying the file
        toast = ToastNotification(
            title="Output File Saved",
            message="Modified.wav Was Saved To Audio Output Folder",
            duration=3000,
            alert=True,
        )
        toast.show_toast()

        # Write the modified signal into the database
        date = datetime.datetime.now()
        self.db.execute(
            'INSERT INTO modsignal(org_id,name,date,amp,shift,speed,reverse,echo) VALUES (?,?,?,?,?,?,?,?)',
            (self.original_id, str(self.plot_img_title), date, amp_amount, shift_amount, speed_amount,
             bool(reverse_state),
             bool(echo_state)))
        self.connection.commit()

    def apply_operations(self):
        # Stop audio playback if it is currently playing
        if self.audio_player:
            self.stop_playback()

        # Get values from entry boxes
        amp_value = self.ui_elements['amp_entry'].get()
        speed_value = self.ui_elements['speed_entry'].get()
        shift_value = self.ui_elements['shift_entry'].get()

        # Check if all necessary values are entered, else show an error message
        if not all([len(self.file_directory), len(amp_value), len(speed_value), len(shift_value)]):
            utility.messagebox.showinfo('Info', 'Please Import Audio File First And Set Valid Values')
            return

        try:
            # Convert values to the appropriate data types
            amp_amount = float(amp_value)
            shift_amount = float(shift_value)
            speed_amount = float(speed_value)

            # Check if speed input is within the recommended range
            if speed_amount > 2 or speed_amount < 0.25:
                utility.messagebox.showinfo('Info', 'Speed Value Is Advised To Be Between 0.25 And 2')
                return

            reverse_st = self.ui_elements['rev_state'].get() == 'revOn'
            echo_st = self.ui_elements['echo_state'].get() == 'echoOn' and self.original_file_data.get(1) == 2

            # Apply operations
            self.operations(amp_amount, shift_amount, speed_amount, reverse_st, echo_st)
        except ValueError:
            utility.messagebox.showinfo('Info', 'Please Enter Valid Numerical Values')

    def play_audio(self, indication):
        # Check if a file has been imported
        if not self.file_directory:
            utility.messagebox.showwarning('Warning', 'Please Import Audio File First')
            return

        # Determine file to play based on indication
        if indication == "OG":
            audio_file = str(self.file_directory)
        elif indication == "MOD" and Path(self.output_file).is_file() and self.ax2.has_data():
            audio_file = str(self.output_file)
        else:
            utility.messagebox.showinfo('Info', 'Apply Modification To The Audio File Then Play It')
            return

        # Play the audio file
        if self.audio_player:
            self.stop_playback()
        self.audio_player = AudioPlayer(audio_file)
        self.start_playback()

    def start_playback(self):
        # Disable play buttons and enable stop button
        self.ui_elements['og_play_btn'].config(state='disabled')
        self.ui_elements['mod_play_btn'].config(state='disabled')
        self.ui_elements['stop_btn'].config(state='normal')

        # Start audio playback in a separate thread
        self.audio_player.play()

        # Periodically check if audio playback has finished
        self.check_id = self.master.after(100, self.check_playback)

    def check_playback(self):
        # Check if audio playback is still ongoing
        if self.audio_player.playing:
            self.check_id = self.master.after(100, self.check_playback)
        else:
            # Enable play buttons and disable stop button
            self.ui_elements['og_play_btn'].config(state='normal')
            self.ui_elements['mod_play_btn'].config(state='normal')
            self.ui_elements['stop_btn'].config(state='disabled')

            # Cancel the check_id to prevent it from firing again
            self.master.after_cancel(self.check_id)

    def stop_playback(self):
        self.audio_player.stop()

    def open_tts_window(self):
        TTSWindow(utility.tts, self.dark_mode_state)

    def open_conv_window(self):
        ConvolutionWindow(self.plotting, create_wave_plot)

    def open_history_window(self):
        HistoryWindow()


class HistoryWindow:
    def __init__(self):
        # Create a new window
        self.new_conv_window = Toplevel(title='History', size=[1500, 750])
        self.new_conv_window.place_window_center()

        # Create a scrolled frame to hold the history information
        hist_fr = ScrolledFrame(self.new_conv_window, autohide=True)
        hist_fr.pack(side='top', expand=True, fill='both')

        # Fetch data from the database
        org_signal_list_db = MainApp.db.execute("SELECT id, name FROM org")
        org_signal_list = org_signal_list_db.fetchall()

        # Iterate over the original signals and their corresponding modified signals
        for org_signal in org_signal_list:
            mod_signal_info_list_db = MainApp.db.execute(
                "SELECT name,date,amp,shift,speed,reverse,echo FROM modsignal WHERE org_id = (?)",
                [(org_signal[0])])
            mod_signal_info_list = mod_signal_info_list_db.fetchall()
            row = 1
            clm = 1
            # Iterate over the modified signals
            for mod_signal_info in mod_signal_info_list:
                # Add information about the manipulation operation
                utility.add_info_label(row, hist_fr, mod_signal_info[1], mod_signal_info[2], mod_signal_info[3],
                                       mod_signal_info[4], mod_signal_info[5], mod_signal_info[6])

                # Add the original signal
                utility.add_img(org_signal[1], row, clm, hist_fr)

                # Add the modified signal
                utility.add_img(mod_signal_info[0], row, clm + 1, hist_fr)

                # Update the row and column counters
                row += 1

            # Increment the column counter for the next original signal
            clm += 2


class ConvolutionWindow:
    def __init__(self, plotting_func, create_plots_figures):
        self.og_signal_frame = None
        self.new_conv_window = Toplevel(title='Convolution', size=[1200, 850])
        self.new_conv_window.place_window_center()
        self.new_conv_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.plotting_func = plotting_func

        self.zp_to_hs_text = ttk.StringVar()
        self.m = create_plots_figures

        self.create_ui()

    def create_ui(self):

        tabs_fr = ttk.Frame(self.new_conv_window)
        tabs_fr.pack(side='right', fill='both', padx=30)
        self.og_signal_frame = ttk.Frame(self.new_conv_window, bootstyle='info')
        self.og_signal_frame.pack(side='top', pady=10)
        self.mod_signal_frame = ttk.Frame(self.new_conv_window)
        self.mod_signal_frame.pack(side='top', pady=10)
        self.conv_signal_frame = ttk.Frame(self.new_conv_window)
        self.conv_signal_frame.pack(side='top', pady=10)

        notebook = ttk.Notebook(tabs_fr)
        notebook.pack(side='top', pady=10)
        select_wave_frame = ttk.Frame(notebook, width=350, height=400, padding=(10, 20))
        transfer_func_frame = ttk.Frame(notebook, width=350, height=400, padding=(10, 20))
        ttk.Label(transfer_func_frame, text='Numerator').grid(row=0, column=0, sticky='w', padx=10)
        self.trFuncValueLB = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.trFuncValueLB.grid(row=0, column=1, pady=10)
        ttk.Label(transfer_func_frame, text='Denominator').grid(row=1, column=0, sticky='w', padx=10)
        self.tr_func_value_lb2 = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.tr_func_value_lb2.grid(row=1, column=1, pady=10)
        ttk.Separator(transfer_func_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, pady=10,
                                                                     sticky='ew')
        ttk.Label(transfer_func_frame, text='Zeros').grid(row=3, column=0, sticky='w', padx=10)
        self.zeros_val_lb = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.zeros_val_lb.grid(row=3, column=1, pady=10)
        ttk.Label(transfer_func_frame, text='Poles').grid(row=4, column=0, sticky='w', padx=10)
        self.poles_val_lb = ttk.Entry(transfer_func_frame, justify="center", state="disabled")
        self.poles_val_lb.grid(row=4, column=1, pady=10)
        ttk.Label(transfer_func_frame, text='Option').grid(row=5, column=0, sticky='w', padx=10, pady=15)

        zp_to_hs_true_val = ttk.Radiobutton(transfer_func_frame, text="H (s) To Zeros",
                                            command=lambda: self.disable_box(1), variable=self.zp_to_hs_text, value=1)
        zp_to_hs_true_val.grid(row=5, column=1, sticky='w', padx=10)
        zp_to_hs_false_val = ttk.Radiobutton(transfer_func_frame, text="Zeros To H (s)",
                                             command=lambda: self.disable_box(2), variable=self.zp_to_hs_text, value=2)
        zp_to_hs_false_val.grid(row=6, column=1, sticky='w', padx=10)

        select_wave_frame.pack(fill='both', expand=True)
        transfer_func_frame.pack(fill='both', expand=True)

        # add frames to notebook
        notebook.add(select_wave_frame, text='Wave')
        notebook.add(transfer_func_frame, text='Transfer Function')

        ttk.Label(select_wave_frame, text='Select Impulse Response').pack(side='top')

        # menu selection
        self.select_wave_menu = ttk.Menubutton(select_wave_frame, text='Select Wave', bootstyle=('primary', 'outline'))
        self.select_wave_menu.pack(side='top', pady=20)

        # create menu
        menu = ttk.Menu(self.select_wave_menu)

        # add options
        option_var = ttk.StringVar()
        for option in ['Sine Wave', 'Rec Wave']:
            menu.add_radiobutton(label=option, value=option, variable=option_var,
                                 command=lambda option=option: utility.update_menu_text(self.select_wave_menu, option))

        # associate menu with menubutton
        self.select_wave_menu['menu'] = menu

        ttk.Button(
            tabs_fr, text=' Apply',
            image='apply-button',
            compound='left',
            bootstyle='link',
            command=lambda: self.apply_convolution(option_var.get())).pack(side='top')
        self.original_figure, self.original_plot, self.original_canvas = self.m(self.og_signal_frame)
        self.conv_figure, self.conv_plot, self.conv_canvas = self.m(self.conv_signal_frame)
        self.mod_figure, self.mod_plot, self.mod_canvas = self.m(self.mod_signal_frame)

        self.original_canvas.get_tk_widget().pack()
        self.mod_canvas.get_tk_widget().pack()
        self.conv_canvas.get_tk_widget().pack()

        # plot the original signal based on the imported Audio Output file
        self.sig = np.repeat([0., 1., 0.], 100)
        self.plotting_func(self.sig, None, None, self.original_plot, 'Original Signal', self.original_canvas, None)

    def lti_sys(self, widget):
        if widget == 1:
            # Get the values of the textbox as an array
            num = [float(x) for x in self.trFuncValueLB.get().strip().split()]
            den = [float(x) for x in self.tr_func_value_lb2.get().strip().split()]

            # Represent the LTI system as a transfer function
            lti_system = signal.lti(num, den)

            # Display the values in the textbox after rounding
            self.zeros_val_lb.delete(0, 'end')
            self.poles_val_lb.delete(0, 'end')
            self.zeros_val_lb.insert(0, ', '.join(['{:.2f}'.format(z) for z in lti_system.zeros]))
            self.poles_val_lb.insert(0, ', '.join(['{:.2f}'.format(p) for p in lti_system.poles]))
        else:
            zeros = [int(x) for x in self.zeros_val_lb.get().strip().split()]
            poles = [int(x) for x in self.poles_val_lb.get().strip().split()]

            # Get the num and den from the zeros and poles
            hs_rep = signal.zpk2tf(zeros, poles, k=1)
            self.trFuncValueLB.delete(0, 'end')
            self.tr_func_value_lb2.delete(0, 'end')
            self.trFuncValueLB.insert(0, ', '.join(['{:.2f}'.format(n) for n in hs_rep[0]]))
            self.tr_func_value_lb2.insert(0, ', '.join(['{:.2f}'.format(d) for d in hs_rep[1]]))

    def apply_convolution(self, conv_val):
        # Get the value of the option radiobutton
        option_val = str(self.zp_to_hs_text.get())

        # Update the values each time the button is pressed
        if option_val == '1':
            self.update_transfer_function_inputs()
        elif option_val == '2':
            self.update_zeros_and_poles()

        win = None
        if conv_val == 'Sine Wave':
            win = signal.windows.hann(50)
        elif conv_val == 'Rec Wave':
            win = np.repeat([0., 1., 0.], 50)

        if win is not None:
            self.plot_impulse_response(win, 'Impulse Response')
            self.plot_filtered_signal(win, 'Filtered Signal')
            self.select_wave_menu.config(text=conv_val)

    def update_transfer_function_inputs(self):
        # Clear the text in the transfer function input boxes
        self.zeros_val_lb.delete(0, 'end')
        self.poles_val_lb.delete(0, 'end')

        # Enable the input boxes
        self.zeros_val_lb.config(state="normal")
        self.poles_val_lb.config(state="normal")

        # Update the transfer function inputs if values are available
        if self.trFuncValueLB.get() and self.tr_func_value_lb2.get():
            self.lti_sys(1)

    def update_zeros_and_poles(self):
        # Delete the entries in the zeros and poles input boxes
        utility.delete_entries(self.trFuncValueLB)
        utility.delete_entries(self.tr_func_value_lb2)

        # Enable the input boxes
        self.trFuncValueLB.config(state="normal")
        self.tr_func_value_lb2.config(state="normal")

        # Update the zeros and poles if values are available
        if self.zeros_val_lb.get() != "" and self.poles_val_lb.get() != "":
            self.lti_sys(2)

    def plot_impulse_response(self, window, title):
        self.plotting_func(window, None, None, self.mod_plot, title, self.mod_canvas, None)

    def plot_filtered_signal(self, window, title):
        filtered = signal.convolve(self.sig, window, mode='same') / sum(window)
        self.plotting_func(filtered, None, None, self.conv_plot, title, self.conv_canvas, None)

    def disable_box(self, num):
        self.clear_input_boxes()

        if num == 1:
            utility.enable_inputs(self.trFuncValueLB, self.tr_func_value_lb2)
            utility.disable_inputs(self.zeros_val_lb, self.poles_val_lb)
        else:
            utility.disable_inputs(self.trFuncValueLB, self.tr_func_value_lb2)
            utility.enable_inputs(self.zeros_val_lb, self.poles_val_lb)

    def clear_input_boxes(self):
        # Delete the entries in all input boxes
        for entry in [self.zeros_val_lb, self.poles_val_lb, self.trFuncValueLB, self.tr_func_value_lb2]:
            utility.delete_entries(entry)

    def on_close(self):
        self.new_conv_window.destroy()


class TTSWindow:
    def __init__(self, speech_func, theme_state):
        self.speech_func = speech_func

        self.new_window = Toplevel(title='Text To Speech', size=[400, 200], resizable=[False, False])
        self.new_window.place_window_center()
        self.new_window.protocol("WM_DELETE_WINDOW", self.on_close)

        # A Label widget to show in toplevel
        ttk.Label(self.new_window, text="Please Write The Transcript").pack(pady=10)

        tts_value_lb = ttk.Entry(self.new_window, justify="center", font='-family Barlow -size 10')
        tts_value_lb.pack(fill='x', pady=5, padx=10)

        convert_btn = ttk.Button(self.new_window, bootstyle='link', command=self.on_convert_button_click)
        if theme_state:
            convert_btn.config(image='convert-button')
        else:
            convert_btn.config(image='convert-button-dark')

        convert_btn.pack(pady=5)

        self.tts_value_lb = tts_value_lb
        self.tts_value_lb.focus()

    def on_convert_button_click(self):
        get_result = self.tts_value_lb.get()
        self.speech_func(str(get_result))

    def on_close(self):
        self.new_window.destroy()


def main() -> None:
    # load a splash screen
    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash

        pyi_splash.close()

    window_width = 1300
    window_height = 800
    app = ttk.Window(title='AudioHaze', iconphoto=resource_path("favIcon.png"),
                     size=[window_width, window_height])
    app.place_window_center()

    # load user created themes
    app.style.load_user_themes(resource_path('user.json'))

    MainApp(app)
    app.mainloop()


if __name__ == '__main__':
    main()
