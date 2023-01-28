import setuptools
from setuptools import setup

long_description = """
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

### Supported Versions

The App Was Tested On Windows 11 With The Following Version Of Python

| Version | Supported          |
|---------|--------------------|
| 3.10    | :white_check_mark: |

"""

setup(
    name='Audio-Signal-Processing-App-GUI-in-Python',
    version='0.2.0',
    package_dir={"": "AudioLib"},
    packages=setuptools.find_packages(where="AudioLib"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shalabycr7/Audio-Signal-Processing-App-GUI-in-Python',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
    license='MIT',
    author='Abdulrahman Shalaby',
    author_email='abdoshalaby.dev@gmail.com',
    keywords=['gui', 'audio'],
    install_requires=['numpy==1.24.1', 'scipy==1.10.0', 'matplotlib==3.6.3', 'pyttsx3==2.90', 'ttkbootstrap==1.10.1',
                      'Pillow==9.4.0', 'pydub==0.25.1'],
    python_requires='>=3.10',

    description='Simple GUI Application To Manipulate Audio Files By Modifying The Audio Wave Form And Display It '
                'Using Python'
)
