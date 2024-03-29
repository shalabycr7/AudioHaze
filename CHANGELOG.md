# Changelog

All Notable Changes To This Project Will Be Documented In This File.

## [Stable]

## V 0.3.0

> App Binary Are New Available In The Releases

### Changed

* Created A New Package & Build The App Binaries For Windows :heavy_check_mark:

### Fixed

* Data Files Paths :heavy_check_mark:
* The App Can Now Be Installed As A Regular `pip` Package :heavy_check_mark:

## V 0.2.7

> This an overhaul new version of the app's under-the-hood functionality

### Changed

* Replaced `pygame` Module With `sounddevice` :heavy_check_mark:
* Implemented `Multithreading` To Improve Performance :heavy_check_mark:
* Created A Thread To Play & Stop Audio Playback Async :heavy_check_mark:

### Fixed

* Interface Lagging When Plotting Or Changing Theme :heavy_check_mark:
* Changed The Data Type Of `output_audio` In `set_echo` To `float32` To Avoid Overflow And To Allow For High Dynamic
  Range Audio Signals :heavy_check_mark:
* Used The `np.max(np.abs(output_audio))` To Normalize The Output Audio Signal Before Casting It As `int16` This Ensures
  That The Signal Is Scaled Properly Within The Range Of `-32768` to `32767` :heavy_check_mark:
* Improved Plotting Speed :heavy_check_mark:
* Squashed Some Bugs :heavy_check_mark:

## V 0.2.6

### Fixed

* Fixed An Issue Playing Audio File Async :heavy_check_mark:
* Fixed Minor Bugs :heavy_check_mark:
* Fixed Using Relative Paths :heavy_check_mark:

## V 0.2.5

### Added

* Added Initial Support For Playing Async Audio On Linux Using `Pygame` :heavy_check_mark:
    * > Only Fedora 37 Tested For Now

### Fixed

* Fixed An Issue Regarding Offline TTS  :heavy_check_mark:
    * > Somthing Broke The New `pyttsx3` Library Update

### Changed

* Removed The Ability To Save TTS Transcript File Due To `espeak` Engine Unhandled Exception :heavy_check_mark:

## V 0.2.4

### Changed

* Changed Files Paths :heavy_check_mark:

### Fixed

* Fixed Minor Issues :heavy_check_mark:
* Fixed Not Able To Play Audio While Changing Theme :heavy_check_mark:

## V 0.2.1

### Changed

* Files Structure Main Files Moved To `AudioHaze` Folder :heavy_check_mark:
* Updated `setup.py` & `requirements.txt` :heavy_check_mark

## V 0.2.0

### Added

* Added The Ability To Create User Customized Themes Using `user.json` File :heavy_check_mark:

### Changed

* Updated Used Packages :heavy_check_mark:
* Moved Some Static Functions To `utils.py` :heavy_check_mark
* Renamed The Main File To `main.py` :heavy_check_mark

### Fixed

* Fixed An Issue Regarding Reading The File Multiple Times In A Row :heavy_check_mark:
* Removed Repeated Code :heavy_check_mark:
* Minor Bugs :heavy_check_mark
* Code Revamping And Improvements :heavy_check_mark

## V 0.1.1

### Added

* Added Tooltip For `Play` Button And Toast Messages That Appear When The Output Is Ready :heavy_check_mark:
* Added Scroll Frame Instead Of Scroll Canvas :heavy_check_mark:

### Changed

* New UI And Icons For better Visibility :heavy_check_mark:

### Fixed

* Fixed Applying Changes Despite The File Has Not Been Imported :heavy_check_mark:
* Fixed History Error Caused By Recent Modification :heavy_check_mark:
* Fixed Some Database Problems :heavy_check_mark:
* Minor Audio Issues :heavy_check_mark:

## V 0.0.9

> This Is A New Build With A Lot Of Changes To The Layout Under The Hood If There Is Any problem Revert To `v 0.0.7`

### Changed

* Updated `requirements.txt` :heavy_check_mark:

### Fixed

* Minor UI Improvements :heavy_check_mark:

## V 0.0.8

### Added

* Initial Release With Responsive Layout :heavy_check_mark:

### Changed

* Improved Code Structure Using Classes :heavy_check_mark:
* New UI Improvements Using `Pack` Layout Manger Instead Of `place` :heavy_check_mark:

### Fixed

* Minor Bugs Fixes :heavy_check_mark:

## V 0.0.7

### Added

* Added `Requirements.txt` File :heavy_check_mark:

### Changed

* Rearranged Reverse And Echo Buttons :heavy_check_mark:
* Reformatted AudioLib Files :heavy_check_mark:

### Fixed

* Fixed Some Echo Issues When Speeding Up Audio :heavy_check_mark:
* Fixed Some Minor Bugs :heavy_check_mark:

## [Beta / Unreleased]

## V 0.2.3

### Changed

* Updated Database Path :heavy_check_mark:
* Updated Project Build Metadata :heavy_check_mark:

## V 0.2.2

### Changed

* Updated File Structure To Support Packaging Format :heavy_check_mark:
* Split The Main Functions Into Sub-Module Files :heavy_check_mark:

### Fixed

* Fixed Some Issues Regarding File Paths :heavy_check_mark:

## V 0.1.0

### Added

* Added A History Section To Save Every Original And Modified Signal :heavy_check_mark:
* Created A Database To Store Each Signals :heavy_check_mark:
* Created A Connection In The Database To Connect Every Modified Signals With Its Original Signal :heavy_check_mark:
* Added History Window To Display All The Modified Operation, Original And Modified Signals :heavy_check_mark:

### Fixed

* Some UI Icons Not Showing Correctly :heavy_check_mark:

## V 0.0.6

### Added

* Initial Support for `.Mp3` Files :heavy_check_mark:

### Fixed

* Fixed User Input Validation Bugs :heavy_check_mark:
* Fixed Some Bugs Regarding Audio Playing :heavy_check_mark:

## V 0.0.5

### Added

* Added Validation For User Input :heavy_check_mark:
* Added Splash Screen :heavy_check_mark:

## V 0.0.4  `Pre-Release`

### Fixed

* Fixed Dark Mode Interface Issues :heavy_check_mark:
* Fixed Some Echo Issues When Importing Stereo Files :heavy_check_mark:

### Changed

* Code Reformat :heavy_check_mark:

## V 0.0.3

> Playing Audio Does Not Freeze The App Anymore

### Added

* Added Support For Playing Audio Async :heavy_check_mark:
* Added Stop Button :heavy_check_mark:
* Display Audio File Duration :heavy_check_mark:

### Fixed

* Some minor improvements to the code :heavy_check_mark:
* Fixed Minor Bugs And Improved Optimizations :heavy_check_mark:

## V 0.0.2

### Added

* Added Support For Stereo Audio Files :heavy_check_mark:
* Added Convolution For Some Elementary Signals :heavy_check_mark:
* Support For Dark Mode :heavy_check_mark:

### Fixed

* Fixed Minor Bugs And Improved Optimizations :heavy_check_mark:

## V 0.0.1

* Initial Version :warning:
