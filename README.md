![](https://github.com/shalabycr7/Audio-Signal-Proccessing-App-GUI-in-Python/blob/Features/Cover%20Design.png)

# Audio Signal Processing App

> This Is A Simple GUI Application To Manipulate Audio Files By Modifying The Audio Wave Form And Display It Using
> Python

### Requirements
![image](https://user-images.githubusercontent.com/17945581/191077349-7bfcb9aa-2ea3-4f54-806f-877b48c570ae.png)


* ##### Install FFmpeg

    * You Need To Install `FFmpeg` From This
      Guide [Install FFmpeg on Windows](<https://www.wikihow.com/Install-FFmpeg-on-Windows>)

* ##### Required Packages

    * In Project Directory Open The Terminal And Type `pip install -r requirements.txt`

### Core Features

* Show Audio File Information Such As:
    * File Type (Supports Mainly `.Wav` Files)
    * > Note: `.Mp3` Initial Support Was Added In `V 0.6`
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
* The Ability To Play Both Audio Files
* Text To Speach Functionality
* Export Both The New Modified Audio File And The Transcript TTS File In A New Directory `Audio output`
* Convolution Operations For Some Elementary Signals
* LTI System Functionality:
    * Convert Between Zeros And Poles Formula To H (s) Represented In Numerator/Denominator Formula
* Support For Stereo Audio Files
* Support Dark Mode Theme

### Screenshots

#### Main Interface

![Main Interface][s1]
![Main Interface In Dark Mode][s2]

#### Convolution Interface

![Main Interface For Convolution][s3]
![Main Interface For Convolution][s4]

#### TTS Interface

![TTS Interface][s5]


[s1]: https://github.com/shalabycr7/Audio-Signal-Proccessing-App-GUI-in-Python/blob/09c5ca42142a9ed7e327bcf1f7d43a6d98bb78e0/Screenshots/11.png "Main Interface"

[s2]: https://github.com/shalabycr7/Audio-Signal-Proccessing-App-GUI-in-Python/blob/09c5ca42142a9ed7e327bcf1f7d43a6d98bb78e0/Screenshots/22.png "Main Interface In Dark Mode"

[s3]: https://github.com/shalabycr7/Audio-Signal-Proccessing-App-GUI-in-Python/blob/09c5ca42142a9ed7e327bcf1f7d43a6d98bb78e0/Screenshots/33.png "Main Interface For Convolution"

[s4]: https://github.com/shalabycr7/Audio-Signal-Proccessing-App-GUI-in-Python/blob/09c5ca42142a9ed7e327bcf1f7d43a6d98bb78e0/Screenshots/44.png "Main Interface For Convolution"

[s5]: https://github.com/shalabycr7/Audio-Signal-Proccessing-App-GUI-in-Python/blob/09c5ca42142a9ed7e327bcf1f7d43a6d98bb78e0/Screenshots/55.png "TTS Interface"

### Task List

- [x] Add Support For More Audio Formats like `.Mp3`
- [x] Add Support For Stereo Files
- [x] Remove Deprecated Audio Libraries/Functions

### Supported Versions

The App Was Tested On Windows 11 With The Following Version Of Python

| Version | Supported          |
|---------|--------------------|
| 3.10    | :white_check_mark: |

