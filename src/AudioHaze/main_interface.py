import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip

from AudioHaze import main
from AudioHaze import utility


def create_main_ui(master, import_file=None, set_theme=None, apply_operations=None,
                   play_audio=None, open_tts_window=None, open_conv_window=None, stop_audio=None,
                   open_history_window=None):
    icon_names = [
        'open-file', 'channels', 'frame-rate', 'max-amp', 'import-file', 'import-file-dark',
        'theme-toggle-dark', 'theme-toggle', 'play-button', 'stop-button', 'conv-button',
        'conv-button-dark', 'tts', 'tts-dark', 'history-button', 'history-button-dark', 'apply-button',
        'convert-button', 'convert-button-dark'
    ]
    master.images = [
        ttk.PhotoImage(name=name, file=main.resource_path(f'{name}-icon.png'))
        for name in icon_names
    ]
    user_validation = master.register(utility.validation_callback)
    # app variables
    echo_state = ttk.StringVar()
    rev_state = ttk.StringVar()

    # main header
    hdr_frame = ttk.Frame(master, padding=(20, 10))
    hdr_frame.pack(fill='x', padx=10)
    ttk.Label(hdr_frame, text='Audio Signal Processing', font="-family Barlow -size 15").pack(fill='x')
    hdr_btn_frame = ttk.Frame(hdr_frame)
    hdr_btn_frame.pack(fill='x', pady=5)
    ttk.Label(hdr_btn_frame, text='Audio File Overview', font="-family Barlow -size 13").pack(side='left')
    import_btn = ttk.Button(
        master=hdr_btn_frame,
        image='import-file',
        compound='left',
        bootstyle='link',
        command=import_file
    )
    import_btn.pack(side='right')

    theme_btn = ttk.Button(
        master=hdr_btn_frame,
        image='theme-toggle-dark',
        bootstyle='link',
        command=set_theme
    )
    theme_btn.pack(side='right', padx=10)

    # file info header
    file_overview_frame = ttk.Frame(hdr_frame)
    file_overview_frame.pack(fill='x', padx=5)
    file_name_frame = ttk.Frame(file_overview_frame)
    file_name_frame.pack(side='left', padx=(0, 20))
    file_name_icon = ttk.Label(master=file_name_frame, image='open-file')
    file_name_icon.grid(row=0, column=0, rowspan=2)
    file_type_val = ttk.Label(file_name_frame, text='Unknown')
    file_type_val.grid(row=0, column=1, sticky='w', padx=5)
    ttk.Label(file_name_frame, text='Type Of Audio File').grid(row=1, column=1, sticky='w', padx=5)
    file_channels_frame = ttk.Frame(file_overview_frame)
    file_channels_frame.pack(side='left', padx=20)
    file_channels_icon = ttk.Label(master=file_channels_frame, image='channels')
    file_channels_icon.grid(row=0, column=0, rowspan=2)
    file_channels_val = ttk.Label(file_channels_frame, text='0')
    file_channels_val.grid(row=0, column=1, sticky='w', padx=5)
    ttk.Label(file_channels_frame, text='Channels').grid(row=1, column=1, sticky='w', padx=5)

    file_frames_frame = ttk.Frame(file_overview_frame, )
    file_frames_frame.pack(side='left', padx=20)
    file_frames_icon = ttk.Label(master=file_frames_frame, image='frame-rate')
    file_frames_icon.grid(row=0, column=0, rowspan=2)
    file_frames_val = ttk.Label(file_frames_frame, text='0')
    file_frames_val.grid(row=0, column=1, sticky='w', padx=5)
    ttk.Label(file_frames_frame, text='Frame Rate').grid(row=1, column=1, sticky='w', padx=5)

    file_max_amp_frame = ttk.Frame(file_overview_frame, )
    file_max_amp_frame.pack(side='left', padx=20)
    file_max_amp_icon = ttk.Label(master=file_max_amp_frame, image='max-amp')
    file_max_amp_icon.grid(row=0, column=0, rowspan=2)
    file_max_amp_val = ttk.Label(file_max_amp_frame, text='0')
    file_max_amp_val.grid(row=0, column=1, sticky='w', padx=5)
    ttk.Label(file_max_amp_frame, text='Maximum Amplitude').grid(row=1, column=1, sticky='w', padx=5)

    # play buttons section
    file_action_frame = ttk.Frame(hdr_frame, padding=(0, 10))
    file_action_frame.pack(fill='x')
    ttk.Label(file_action_frame, text='Audio Wave Form', font="-family Barlow -size 13").pack(side='left')
    open_conv_btn = ttk.Button(
        master=file_action_frame,
        text=' Convolution',
        image='conv-button',
        compound='left',
        bootstyle='link',
        command=open_conv_window
    )
    open_conv_btn.pack(side='right', padx=(10, 0))

    open_history_btn = ttk.Button(
        master=file_action_frame,
        text=' History',
        image='history-button',
        compound='left',
        bootstyle='link',
        command=open_history_window
    )
    open_history_btn.pack(side='right')

    og_play_btn = ttk.Button(
        master=file_action_frame,
        image='play-button',
        compound='left',
        bootstyle='link',
        command=lambda: play_audio('OG')
    )
    ToolTip(og_play_btn, delay=1500, text="Play Original Audio", bootstyle='primary')
    og_play_btn.pack(side='right', padx=20)
    stop_btn = ttk.Button(
        master=file_action_frame,
        image='stop-button',
        compound='left',
        bootstyle='link',
        command=stop_audio
    )
    stop_btn.pack(side='right')
    ttk.Separator(file_action_frame, orient='vertical').pack(side='right', padx=20)
    length_lb = ttk.Label(file_action_frame, text='', font='-family Barlow -size 13')
    length_lb.pack(side='right', padx=20)

    # tasks frame
    tasks_frame = ttk.Frame(master, padding=5)
    tasks_frame.pack(side='right', fill='both', pady=5, padx=25)

    original_wave_frame = ttk.Frame(master, padding=5)
    original_wave_frame.pack(expand=1)
    modified_wave_frame = ttk.Frame(master, padding=5)
    modified_wave_frame.pack(pady=5, expand=1)

    tasks_hdr_frame = ttk.Frame(tasks_frame)
    tasks_hdr_frame.pack(fill='both')
    ttk.Label(tasks_hdr_frame, text='Tasks', font='-family Barlow -size 13').pack(side='left')

    tts_btn = ttk.Button(
        master=tasks_hdr_frame,
        text=' Text To Speach',
        image='tts',
        compound='left',
        bootstyle='link',
        command=open_tts_window
    )
    tts_btn.pack(side='right')
    ttk.Separator(tasks_hdr_frame, orient='vertical').pack(side='right', padx=20)

    operations_frame = ttk.Frame(tasks_frame, padding=10)
    operations_frame.pack(side='top', fill='both')
    ttk.Label(operations_frame, text='Amplitude').grid(row=0, column=0, padx=(0, 20), sticky='w')
    amp_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                          validatecommand=(user_validation, '%P'), font='-family Barlow -size 10')
    amp_entry.grid(row=0, column=1, pady=10)
    ttk.Label(operations_frame, text='Shift').grid(row=1, column=0, padx=(0, 20), sticky='w')
    shift_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                            validatecommand=(user_validation, '%P'), font='-family Barlow -size 10')
    shift_entry.grid(row=1, column=1, pady=10, sticky='w')
    ttk.Label(operations_frame, text='Speed').grid(row=2, column=0, padx=(0, 20), sticky='w')
    speed_entry = ttk.Entry(operations_frame, justify='center', validate='key', width=15,
                            validatecommand=(user_validation, '%P'), font='-family Barlow -size 10')
    speed_entry.grid(row=2, column=1, pady=10)

    ttk.Label(operations_frame, text='Reverse').grid(row=3, column=0, pady=10, padx=(0, 20), sticky='w')
    reverse_toggle = ttk.Checkbutton(operations_frame, bootstyle='round-toggle', onvalue='revOn',
                                     variable=rev_state, offvalue='revOff')
    reverse_toggle.grid(row=3, column=1, sticky='w', ipady=20)
    ttk.Label(operations_frame, text='Echo').grid(row=3, column=1, pady=10, padx=(0, 60), sticky='e')
    echo_toggle = ttk.Checkbutton(operations_frame, bootstyle='round-toggle', onvalue='echoOn',
                                  variable=echo_state, offvalue='echoOff')
    echo_toggle.grid(row=3, column=1, sticky='e', ipady=20)

    apply_operations_btn = ttk.Button(
        master=operations_frame,
        text=' Apply',
        image='apply-button',
        compound='left',
        bootstyle='link',
        command=apply_operations
    )
    apply_operations_btn.grid(row=4, column=0, sticky='se', pady=100)

    mod_play_btn = ttk.Button(
        master=operations_frame,
        text=' Play',
        image='play-button',
        compound='left',
        bootstyle='link',
        command=lambda: play_audio('MOD'))
    mod_play_btn.grid(row=4, column=1, sticky='sw', pady=100, padx=20)
    ToolTip(mod_play_btn, delay=1500, text="Play Modified Audio", bootstyle='primary')
    required_elements = {'original_wave_frame': original_wave_frame, 'modified_wave_frame': modified_wave_frame,
                         'length_lb': length_lb, 'file_max_amp_val': file_max_amp_val,
                         'file_frames_val': file_frames_val, 'file_channels_val': file_channels_val,
                         'file_type_val': file_type_val, 'echo_toggle': echo_toggle, 'tts_btn': tts_btn,
                         'open_history_btn': open_history_btn, 'open_conv_btn': open_conv_btn, 'import_btn': import_btn,
                         'theme_btn': theme_btn, 'shift_entry': shift_entry, 'speed_entry': speed_entry,
                         'amp_entry': amp_entry, 'echo_state': echo_state, 'rev_state': rev_state,
                         'og_play_btn': og_play_btn, 'mod_play_btn': mod_play_btn, 'stop_btn': stop_btn}
    return required_elements
