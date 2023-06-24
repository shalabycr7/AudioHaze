![Cover Design](https://user-images.githubusercontent.com/17945581/191078771-0af9a028-595e-4907-a32a-105166c3a42a.png)

# AudioHaze (An Audio Wave Processing App)

> This Is A Simple GUI Application To Manipulate Audio Files By Modifying The Audio Wave Form And Display It Using
> Python

![GitHub release (latest by date)](https://img.shields.io/github/v/release/shalabycr7/AudioHaze)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/shalabycr7/AudioHaze)
![GitHub forks](https://img.shields.io/github/forks/shalabycr7/AudioHaze?style=social)

> App Binaries Are Available In The Releases

### Running Via `pip`

You can Install The App Locally By Following These Steps:

1. Run ```pip install AudioHaze```
2. Now In The Terminal Run```AudioHaze```

### Running Locally Via [GitHub](https://github.com/shalabycr7/AudioHaze)

#### Requirements

#### On Windows

* You Need To Install `FFmpeg` From This
  Guide [Install FFmpeg on Windows](<https://www.wikihow.com/Install-FFmpeg-on-Windows>)
* Install [Visual C++ Redistributable for Visual Studio 2015
  ](<https://www.microsoft.com/en-us/download/details.aspx?id=48145>)

#### On Linux

* Make Sure `espeak` Is Installed On Your System By Executing `sudo apt-get install espeak`

You can Run This App Locally By Following These Steps:

1. Clone/Download The [Repo](https://github.com/shalabycr7/AudioHaze)
2. Open Cmd/Terminal And `cd` Into The Project Root Directory
3. Execute ```pip install -e .```

Now To Run The Application, Execute ```python -m AudioHaze```

### Core Features

* Show Audio File Information Such As:
    * File Type (Supports Mainly `.Wav` Files)
    * > `.Mp3` Initial Support Was Added In `V 0.6`
    * Number Of Channels
    * Audio Frame Rate
    * Maximum Audio Amplitude
    * Audio File Duration
* Modify The Audio File By:
    * Increasing/Decreasing The Amplitude
    * Increasing/Decreasing Audio Speed
    * Increasing/Decreasing Audio Delay (Shift)
    * Reversing The Audio
    * Add An Echo Effect
* Represent The Audio Wave Form For Both Original And Modified Files
* Show A History Of Previous Modified Audio Files
* The Ability To Play Both Audio Files
* Text To Speach Functionality
* Export Both The New Modified Audio File And The Transcript TTS File In A New Directory `Audio output`
* Convolution Operations For Some Elementary Signals
* LTI System Functionality:
    * Convert Between Zeros And Poles Formula To H (s) Represented In Numerator/Denominator Formula
* Support For Stereo Audio Files
* Support Dark Mode Theme
* Support User Customized Themes Using `user.json` File Located In `Theme`
  Folder

### Screenshots

#### Main Interface

![s1](https://user-images.githubusercontent.com/17945581/201343392-f82d0995-d7f6-44c7-9c82-eecbf695dfdc.png)
![s3](https://user-images.githubusercontent.com/17945581/201343489-d9844cdc-612e-4e6c-b748-052a6061b1c7.png)

#### Convolution Interface

![s2](https://user-images.githubusercontent.com/17945581/201343642-07d3f5d1-8b6b-44ba-ae51-473e6bf1ed05.png)
![s4](https://user-images.githubusercontent.com/17945581/201343647-d24cd73c-2560-4fdd-810e-983aae215934.png)

#### TTS Interface

![s5](https://user-images.githubusercontent.com/17945581/201343775-1ff48888-38b7-4153-b168-5201d9a8910d.png)

#### History Interface

![s6](https://user-images.githubusercontent.com/17945581/201343908-f86291ff-da4c-4673-97f9-99c83fb2cb2e.png)

### Tasks List

- [x] Add History Window For Previous Imported Files
- [x] Revamp The UI
- [x] Add Support For More Audio Formats like `.Mp3`
- [x] Add Support For Stereo Files
- [x] Remove Deprecated Audio Libraries/Functions
- [x] Added Support For User Created Themes

### Supported Versions

The App Was Tested With The Following Version Of Python

| Version | Windows            | Linux              | MacOS              |
|---------|--------------------|--------------------|--------------------|
| 3.11    | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| 3.10    | :white_check_mark: | :white_check_mark: | :white_check_mark: |

