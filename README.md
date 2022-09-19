![Cover Design](https://user-images.githubusercontent.com/17945581/191078771-0af9a028-595e-4907-a32a-105166c3a42a.png)

# Audio Signal Processing App

> This Is A Simple GUI Application To Manipulate Audio Files By Modifying The Audio Wave Form And Display It Using
> Python

### Requirements

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

![s1](https://user-images.githubusercontent.com/17945581/191077543-bc2716ce-67a6-4a20-9308-5eaf74245a34.png)
![s3](https://user-images.githubusercontent.com/17945581/191077567-235d355d-530d-4ecf-9a11-4ca12bff2b4b.png)



#### Convolution Interface


![s2](https://user-images.githubusercontent.com/17945581/191077555-21788fe5-800c-4519-8cee-4bdacb5a3d99.png)
![s4](https://user-images.githubusercontent.com/17945581/191077599-4185ed6a-b5bb-4784-bcd9-64c198715a69.png)


#### TTS Interface

![s5](https://user-images.githubusercontent.com/17945581/191077629-c4f748cb-7021-4d75-ba7a-06cc67bb8dd5.png)



### Task List

- [x] Add Support For More Audio Formats like `.Mp3`
- [x] Add Support For Stereo Files
- [x] Remove Deprecated Audio Libraries/Functions

### Supported Versions

The App Was Tested On Windows 11 With The Following Version Of Python

| Version | Supported          |
|---------|--------------------|
| 3.10    | :white_check_mark: |

