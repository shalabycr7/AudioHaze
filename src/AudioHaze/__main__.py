import datetime
import sqlite3
import struct
import wave
from pathlib import Path
from tkinter import filedialog

import matplotlib
import numpy as np
import ttkbootstrap as ttk
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pydub import AudioSegment
from scipy import signal
from ttkbootstrap import Toplevel, PRIMARY, OUTLINE, LINK, BOTH, TOP, RIGHT, YES, HORIZONTAL, W, EW, LEFT, X
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.toast import ToastNotification

from src.AudioHaze import main_interface, audio_effect
from src.AudioHaze import utility

parent_dir = Path(__file__).parent


class MainApp(ttk.Frame):
    # initial parameters for audio file name and location
    file_directory = ''
    directory_name = parent_dir.parents[1] / 'Audio Output'
    dark_mode_state = False
    output_file = str(directory_name / 'Modified.wav')

    # initial parameters for audio file data
    original_file_data = {}
    modified_file_data = {}

    # initial parameters for data plotting frames on the UI
    original_plot_state = False
    modified_plot_state = False
    original_id = 0
    plot_img_title = ''

    # connect to database
    connection = sqlite3.connect(parent_dir / 'signals.db')
    db = connection.cursor()

    # start the image counter at an appropriate number.
    max_id_db = db.execute("SELECT MAX(id) FROM org")
    max_id = max_id_db.fetchone()[0]
    img_count = 0

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=BOTH, expand=YES)
        self.current_style = ttk.Style()
        utility.mixer.init()
        self.make_output_directory()
        # load user created themes
        self.ui_elements = main_interface.create_main_ui(self, self.import_file,
                                                         self.set_theme, self.apply_operations, self.play_audio,
                                                         self.open_tts_window, self.open_conv_window)
        self.set_theme()

    def make_output_directory(self):
        Path(parent_dir / 'History').mkdir(exist_ok=True)
        Path(self.directory_name).mkdir(exist_ok=True)

    def set_theme(self):
        utility.update_frame(self.ui_elements['original_wave_frame'])
        utility.update_frame(self.ui_elements['modified_wave_frame'])
        # toggle between dark and light mode
        if self.dark_mode_state:
            self.current_style.theme_use('midnight')
            self.ui_elements['theme_btn'].config(image='themeToggleLight')
            self.ui_elements['import_btn'].config(image='import-dark')
            self.ui_elements['open_conv_btn'].config(image='convolution-dark')
            self.ui_elements['open_history_btn'].config(image='history-dark')
            self.ui_elements['tts_btn'].config(image='tts-dark')
            self.dark_mode_state = False
        else:
            self.current_style.theme_use('litera')
            self.ui_elements['import_btn'].config(image='import')
            self.ui_elements['open_conv_btn'].config(image='convolution')
            self.ui_elements['open_history_btn'].config(image='history')
            self.ui_elements['theme_btn'].config(image='themeToggleDark')
            self.ui_elements['tts_btn'].config(image='tts')
            self.dark_mode_state = True
        # set global font size for widgets
        self.current_style.configure('TLabel', font='-family Barlow -size 10')
        self.current_style.configure('TButton', font='-family Barlow -size 11')
        self.current_style.configure('TMenubutton', font='-family Barlow -size 10')
        self.current_style.configure('TNotebook.Tab', font='-family Barlow -size 10')
        # re-plot the data upon theme changing
        if self.original_plot_state:
            self.plotting(None, self.original_file_data[5], self.original_file_data[4],
                          self.ui_elements['original_wave_frame'],
                          'Original Audio')
        if self.modified_plot_state:
            self.plotting(None, self.modified_file_data.get(5), self.modified_file_data.get(4),
                          self.ui_elements['modified_wave_frame'],
                          'Modified Audio')

    def read_file(self, file, indicator):
        # create a dictionary to hold file data
        data_dict = {1: file.channels, 2: file.frame_rate, 3: file.frame_count(),
                     4: np.frombuffer(file.raw_data, 'int16')}
        time = np.linspace(0, len(data_dict.get(4)) / data_dict.get(2),
                           num=len(data_dict.get(4)))
        data_dict.update({5: time})
        if indicator == 'original':
            # get the duration of the audio file
            duration = data_dict.get(3) / float(data_dict.get(2))
            hours, minutes, seconds = utility.output_duration(int(duration))
            total_time = f'{hours}:{minutes}:{seconds}'
            # display the duration
            self.ui_elements['length_lb'].config(text=total_time)
        return data_dict

    def import_file(self):
        utility.update_frame(self.ui_elements['original_wave_frame'])
        utility.update_frame(self.ui_elements['modified_wave_frame'])

        # # hide the plotting frames every time we import
        self.original_plot_state = False
        self.modified_plot_state = False
        # open window to select file to get the path then save in variable directory
        filename = filedialog.askopenfilename(initialdir=self.file_directory, title="Select Audio File",
                                              filetypes=(('Wav', '*wav'), ('Mp3', '*mp3')))
        self.file_directory = filename
        if not len(self.file_directory):
            utility.messagebox.showerror('Error', 'No File Was Selected')
            return
        else:
            file_extension = Path(filename).suffix
            # convert mp3 file to wav, so it can be read
            if file_extension == '.mp3':
                mp3_file = AudioSegment.from_mp3(file=self.file_directory)
                mp3_file.export(self.directory_name / 'Mp3converted.wav', format='wav')
                self.file_directory = self.directory_name / 'Mp3converted.wav'
            wav_original = AudioSegment.from_file(file=self.file_directory)
            self.original_file_data = self.read_file(wav_original, 'original')
            # update displayed File info
            self.ui_elements['file_type_val'].config(text=file_extension)
            self.ui_elements['file_channels_val'].config(text=self.original_file_data.get(1))
            self.ui_elements['file_frames_val'].config(text=self.original_file_data.get(2))
            self.ui_elements['file_max_amp_val'].config(text=wav_original.max)
            # start plotting
            self.plotting(None, self.original_file_data.get(5), self.original_file_data.get(4),
                          self.ui_elements['original_wave_frame'],
                          'Original Audio')
            self.original_plot_state = True
            # Set echo options on if the file is stereo
            if self.original_file_data.get(1) == 2:
                self.ui_elements['echo_toggle'].config(state='!selected')
            else:
                self.ui_elements['echo_toggle'].config(state='disabled')

    def plotting(self, targeted_signal, time, raw, place, title):
        matplotlib.style.use('dark_background') if not self.dark_mode_state else matplotlib.style.use('default')
        plotting_figure = Figure(figsize=(7, 2), dpi=90)
        figure_subplot = plotting_figure.add_subplot(111)
        figure_subplot.set_ylabel('Amplitude')
        figure_subplot.grid(alpha=0.4)
        figure_subplot.set_title(title)

        self.plot_img_title = parent_dir / 'History' / ("img" + str(self.img_count) + ".png")
        if targeted_signal is not None:
            figure_subplot.plot(targeted_signal, color='blue')
        else:
            figure_subplot.plot(time, raw, color='blue')
            plotting_figure.savefig(self.plot_img_title)
            self.img_count += 1

            if title == 'Original Audio':
                text = [str(self.plot_img_title)]
                self.db.execute('INSERT INTO org(name) VALUES (?)', text)
                self.connection.commit()
                org_id_db = self.db.execute("SELECT id FROM org WHERE name = ?", text)
                self.original_id = org_id_db.fetchone()[0]

        # Creating Canvas to show it in the Frame
        canvas = FigureCanvasTkAgg(plotting_figure, master=place)
        canvas.get_tk_widget().pack()

    def operations(self, amp_amount, shift_amount, speed_amount, reverse_state, echo_state):
        utility.update_frame(self.ui_elements['modified_wave_frame'])

        # create a new output WAV file to write the new modified audio data
        audio_obj = wave.open(self.output_file, 'wb')
        audio_obj.setnchannels(self.original_file_data.get(1))
        audio_obj.setsampwidth(2)

        # changing audio speed
        speed = self.original_file_data.get(2) * speed_amount
        audio_obj.setframerate(speed)

        # Shifting audio process
        for i in range(int(self.original_file_data.get(2) * shift_amount)):
            zero_in_byte = struct.pack('<h', 0)
            audio_obj.writeframesraw(zero_in_byte)

        # Amplification process
        n = len(self.original_file_data.get(4))

        # Reverse process
        if reverse_state:
            for i in range(self.original_file_data.get(4).__len__()):
                two_byte_sample = self.original_file_data.get(4)[n - 1 - i] * amp_amount
                if two_byte_sample > 32760:
                    two_byte_sample = 32760
                if two_byte_sample < -32760:
                    two_byte_sample = -32760
                sample = struct.pack('<h', int(two_byte_sample))
                audio_obj.writeframesraw(sample)
        else:
            for i in range(self.original_file_data.get(4).__len__()):
                if self.original_file_data.get(4)[i] * amp_amount > 32760:
                    two_byte_sampler = 32760
                elif self.original_file_data.get(4)[i] * amp_amount < -32760:
                    two_byte_sampler = -32760
                else:
                    two_byte_sampler = self.original_file_data.get(4)[i] * amp_amount
                sample = struct.pack('<h', int(two_byte_sampler))
                audio_obj.writeframesraw(sample)

        # close and save the modified output file
        audio_obj.close()

        audio_file = AudioSegment.from_file(file=self.output_file, format="wav")
        self.modified_file_data = self.read_file(audio_file, 'modified')

        # plot the modified data
        self.plotting(None, self.modified_file_data.get(5), self.modified_file_data.get(4),
                      self.ui_elements['modified_wave_frame'],
                      'Modified Audio')
        self.modified_plot_state = True

        # set the echo based on button state
        if echo_state:
            audio_effect.echo(self.output_file, self.output_file)

        # show a message when done modifying the file
        toast = ToastNotification(
            title="Output File Saved",
            message="Modified.wav Was Saved To Audio Output Folder",
            duration=3000,
            alert=True,
        )
        toast.show_toast()

        # write the modified signal into the database
        date = datetime.datetime.now()
        self.db.execute(
            'INSERT INTO modsignal(org_id,name,date,amp,shift,speed,reverse,echo) VALUES (?,?,?,?,?,?,?,?)',
            (self.original_id, str(self.plot_img_title), date, amp_amount, shift_amount, speed_amount,
             bool(reverse_state),
             bool(echo_state)))
        self.connection.commit()

    def apply_operations(self):
        utility.stop_audio()
        amp_value = self.ui_elements['amp_entry'].get()
        speed_value = self.ui_elements['speed_entry'].get()
        shift_value = self.ui_elements['shift_entry'].get()
        # check if the user had entered values or not, if so process them, if not show an error message
        if self.file_directory != '' and amp_value != '' and speed_value != '' and shift_value != '':
            # get the values from entry box
            amp_amount = float(amp_value)
            shift_amount = float(shift_value)
            speed_amount = float(speed_value)
            if self.ui_elements['rev_state'].get() == 'revOn':
                reverse_st = True
            else:
                reverse_st = False
            if self.ui_elements['echo_state'].get() == 'echoOn' and self.original_file_data.get(1) == 2:
                echo_st = True
            else:
                echo_st = False

            # Validate input
            if speed_amount > 2 or speed_amount < 0.25:
                utility.messagebox.showinfo('Info', 'Speed Value Must Be Between 0.25 And 2')
                return
            if shift_amount < 0:
                utility.messagebox.showinfo('Info', 'Shift Value Must Be Positive')
                return
            self.operations(amp_amount, shift_amount, speed_amount, reverse_st, echo_st)
        else:
            utility.messagebox.showinfo('Info', 'Please Import Audio File First And Set Valid Values')
            return

    def play_audio(self, indication):
        # check if a file has been imported then play it, if not show an error message
        if self.file_directory != '':
            # toggle between playing the original file or the modified version
            if indication == 'OG':
                audio_file = str(self.file_directory)
            else:
                if Path(self.output_file).is_file():
                    audio_file = self.output_file
                else:
                    utility.messagebox.showinfo('Info', 'Apply Modification To The Audio File Then Play It')
                    return
            utility.mixer.music.load(audio_file)
            utility.mixer.music.play()
        else:
            utility.messagebox.showwarning('Warning', 'Please Import Audio File First')

    def open_tts_window(self):
        TTSWindow(utility.tts, self.dark_mode_state)

    def open_conv_window(self):
        ConvolutionWindow(self.plotting)


class HistoryWindow:
    def __init__(self):
        new_conv_window = Toplevel(title='History', size=[1200, 740])
        new_conv_window.place_window_center()

        # creat a main frame.
        hist_fr = ScrolledFrame(new_conv_window, autohide=True)
        hist_fr.pack(side=TOP, expand=True, fill=BOTH)
        # fetch the data from the database
        org_signal_list_db = MainApp.db.execute("SELECT id, name FROM org")
        org_signal_list = org_signal_list_db.fetchall()
        row = 1
        clm = 1
        for org_signal in org_signal_list:
            org_signal_list_db = MainApp.db.execute(
                "SELECT name,date,amp,shift,speed,reverse,echo FROM modsignal WHERE org_id = (?)",
                [(org_signal[0])])
            mod_signal_info_list = org_signal_list_db.fetchall()
            for mod_signal_info in mod_signal_info_list:
                # add the information of the  manipulation operation.
                utility.add_info_label(row, hist_fr, mod_signal_info[1], mod_signal_info[2], mod_signal_info[3],
                                       mod_signal_info[4],
                                       mod_signal_info[5], mod_signal_info[6])
                # add the original signal in the row
                utility.add_img(org_signal[1], row, clm, hist_fr)
                clm += 1
                # add the modified signal
                utility.add_img(mod_signal_info[0], row, clm, hist_fr)
                row += 1
                clm -= 1


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
        self.select_wave_menu = ttk.Menubutton(select_wave_frame, text='Select Wave', bootstyle=(PRIMARY, OUTLINE))
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
        utility.update_frame(self.mod_signal_frame)
        utility.update_frame(self.conv_signal_frame)

        # get the value of the option radiobutton
        option_val = str(self.zp_to_hs_text.get())
        if option_val == '1':
            # update the values each time the button is pressed
            utility.delete_entries(self.zeros_val_lb)
            utility.delete_entries(self.poles_val_lb)
            self.zeros_val_lb.config(state="normal")
            self.poles_val_lb.config(state="normal")
            if self.trFuncValueLB.get() != "" and self.tr_func_value_lb2.get() != "":
                self.lti_sys(1)
        if option_val == '2':
            utility.delete_entries(self.trFuncValueLB)
            utility.delete_entries(self.tr_func_value_lb2)
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
        utility.delete_entries(self.zeros_val_lb)
        utility.delete_entries(self.poles_val_lb)
        utility.delete_entries(self.trFuncValueLB)
        utility.delete_entries(self.tr_func_value_lb2)
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


class TTSWindow:
    def __init__(self, speach_func, theme_state):
        new_window = Toplevel(title='Text To Speach', size=[400, 200], resizable=[False, False])
        self.speach_func = speach_func
        new_window.place_window_center()
        # A Label widget to show in toplevel
        ttk.Label(new_window, text="Please Write The Transcript").pack(pady=10)
        tts_value_lb = ttk.Entry(new_window, justify="center", font='-family Barlow -size 10')
        tts_value_lb.pack(fill=X, pady=5, padx=10)
        convert_btn = ttk.Button(new_window, bootstyle=LINK,
                                 command=lambda: self.get_my_input_value(tts_value_lb))
        if theme_state:
            convert_btn.config(image='convert')

        else:
            convert_btn.config(image='convert-dark')
        convert_btn.pack(pady=5)

    def get_my_input_value(self, widget):
        getresult = widget.get()
        self.speach_func(str(getresult))


if __name__ == '__main__':
    window_width = 1200
    window_height = 700
    app = ttk.Window(title='AudioHaze', iconphoto=str(parent_dir / 'Icons/favIcon.png'),
                     size=[window_width, window_height])
    app.place_window_center()
    app.style.load_user_themes(parent_dir / 'user.json')
    MainApp(app)
    app.mainloop()
