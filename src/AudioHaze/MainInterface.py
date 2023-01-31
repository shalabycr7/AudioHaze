import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from src.AudioHaze import Utils
from src.AudioHaze.__main__ import parent_dir


def create_main_ui(master, import_file=None, set_theme=None, apply_operations=None,
                   play_audio=None, open_tts_window=None, open_conv_window=None):
    master.images = [
        ttk.PhotoImage(
            name='openfile',
            file=parent_dir / 'Icons/open-file-icon.png'),
        ttk.PhotoImage(
            name='channels',
            file=parent_dir / 'Icons/channels-icon.png'),
        ttk.PhotoImage(
            name='frameRate',
            file=parent_dir / 'Icons/framerate-icon.png'),
        ttk.PhotoImage(
            name='maxAmp',
            file=parent_dir / 'Icons/max-amp-icon.png'),
        ttk.PhotoImage(
            name='import',
            file=parent_dir / 'Icons/import-file.png'),
        ttk.PhotoImage(
            name='import-dark',
            file=parent_dir / 'Icons/import-file-dark.png'),
        ttk.PhotoImage(
            name='themeToggleDark',
            file=parent_dir / 'Icons/darkIcon.png'),
        ttk.PhotoImage(
            name='themeToggleLight',
            file=parent_dir / 'Icons/whiteIcon.png'),
        ttk.PhotoImage(
            name='play',
            file=parent_dir / 'Icons/play-button.png'),
        ttk.PhotoImage(
            name='stop',
            file=parent_dir / 'Icons/stop-button.png'),
        ttk.PhotoImage(
            name='convolution',
            file=parent_dir / 'Icons/conv-button.png'),
        ttk.PhotoImage(
            name='convolution-dark',
            file=parent_dir / 'Icons/conv-button-dark.png'),
        ttk.PhotoImage(
            name='tts',
            file=parent_dir / 'Icons/message-button.png'),
        ttk.PhotoImage(
            name='tts-dark',
            file=parent_dir / 'Icons/message-button-dark.png'),
        ttk.PhotoImage(
            name='history',
            file=parent_dir / 'Icons/history-button.png'),
        ttk.PhotoImage(
            name='history-dark',
            file=parent_dir / 'Icons/history-button-dark.png'),
        ttk.PhotoImage(
            name='apply',
            file=parent_dir / 'Icons/apply-button.png'),
        ttk.PhotoImage(
            name='convert',
            file=parent_dir / 'Icons/convert-button.png'),
        ttk.PhotoImage(
            name='convert-dark',
            file=parent_dir / 'Icons/convert-button-dark.png'),
    ]
    user_validation = master.register(Utils.validation_callback)
    # app variables
    echo_state = ttk.StringVar()
    rev_state = ttk.StringVar()

    # main header
    hdr_frame = ttk.Frame(master, padding=(20, 10))
    hdr_frame.pack(fill=X, padx=10)
    ttk.Label(hdr_frame, text='Audio Signal Processing', font="-family Barlow -size 15").pack(fill=X)
    hdr_btn_frame = ttk.Frame(hdr_frame)
    hdr_btn_frame.pack(fill=X, pady=5)
    ttk.Label(hdr_btn_frame, text='Audio File Overview', font="-family Barlow -size 13").pack(side=LEFT)
    import_btn = ttk.Button(
        master=hdr_btn_frame,
        image='import',
        compound=LEFT,
        bootstyle=LINK,
        command=import_file
    )
    import_btn.pack(side=RIGHT)

    theme_btn = ttk.Button(
        master=hdr_btn_frame,
        image='themeToggleDark',
        bootstyle=LINK,
        command=set_theme
    )
    theme_btn.pack(side=RIGHT, padx=10)

    # file info header
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
    ttk.Label(file_action_frame, text='Audio Wave Form', font="-family Barlow -size 13").pack(side=LEFT)
    open_conv_btn = ttk.Button(
        master=file_action_frame,
        text=' Convolution',
        image='convolution',
        compound=LEFT,
        bootstyle=LINK,
        command=open_conv_window
    )
    open_conv_btn.pack(side=RIGHT, padx=(10, 0))

    open_history_btn = ttk.Button(
        master=file_action_frame,
        text=' History',
        image='history',
        compound=LEFT,
        bootstyle=LINK,
        command=Utils.open_history_window
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
        command=Utils.stop_audio
    )
    stop_btn.pack(side=RIGHT)
    ttk.Separator(file_action_frame, orient=VERTICAL).pack(side=RIGHT, padx=20)
    length_lb = ttk.Label(file_action_frame, text='', font='-family Barlow -size 13')
    length_lb.pack(side=RIGHT, padx=20)

    # tasks frame
    tasks_frame = ttk.Frame(master, padding=5)
    tasks_frame.pack(side=RIGHT, fill=Y, pady=5, padx=25)

    original_wave_frame = ttk.Frame(master)
    original_wave_frame.pack(side=TOP)
    modified_wave_frame = ttk.Frame(master)
    modified_wave_frame.pack(side=TOP, pady=5)

    tasks_hdr_frame = ttk.Frame(tasks_frame)
    tasks_hdr_frame.pack(side=TOP, fill=X)
    ttk.Label(tasks_hdr_frame, text='Tasks', font='-family Barlow -size 13').pack(side=LEFT)

    tts_btn = ttk.Button(
        master=tasks_hdr_frame,
        text=' Text To Speach',
        image='tts',
        compound=LEFT,
        bootstyle=LINK,
        command=open_tts_window
    )
    tts_btn.pack(side=RIGHT)
    ttk.Separator(tasks_hdr_frame, orient=VERTICAL).pack(side=RIGHT, padx=20)

    operations_frame = ttk.Frame(tasks_frame, padding=10)
    operations_frame.pack(side=TOP, fill=BOTH)
    ttk.Label(operations_frame, text='Amplitude').grid(row=0, column=0, padx=(0, 20), sticky=W)
    amp_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                          validatecommand=(user_validation, '%P'), font='-family Barlow -size 10')
    amp_entry.grid(row=0, column=1, pady=10)
    ttk.Label(operations_frame, text='Shift').grid(row=1, column=0, padx=(0, 20), sticky=W)
    shift_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                            validatecommand=(user_validation, '%P'), font='-family Barlow -size 10')
    shift_entry.grid(row=1, column=1, pady=10, sticky=W)
    ttk.Label(operations_frame, text='Speed').grid(row=2, column=0, padx=(0, 20), sticky=W)
    speed_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                            validatecommand=(user_validation, '%P'), font='-family Barlow -size 10')
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
    required_elements = {'original_wave_frame': original_wave_frame, 'modified_wave_frame': modified_wave_frame,
                         'length_lb': length_lb, 'file_max_amp_val': file_max_amp_val,
                         'file_frames_val': file_frames_val, 'file_channels_val': file_channels_val,
                         'file_type_val': file_type_val, 'echo_toggle': echo_toggle, 'tts_btn': tts_btn,
                         'open_history_btn': open_history_btn, 'open_conv_btn': open_conv_btn, 'import_btn': import_btn,
                         'theme_btn': theme_btn, 'shift_entry': shift_entry, 'speed_entry': speed_entry,
                         'amp_entry': amp_entry, 'echo_state': echo_state, 'rev_state': rev_state}
    return required_elements
