# Helios CPU/GPU Temperature Sensor Monitor
Helios is a simple hardware temperature sensor monitor for your GPU and CPU written in Python. It uses **LibreHardwareMonitor.dll** from this [repository](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor). Latest varsion: **0.9**

## Features
- Works like a widget on top of all of your applications (even games)
- Customizable sensors values text (size), sensor values update time and sensors position (with 4 default presets)
- Show/Hide sensors using main menu button
- Show/Hide main menu using **HOME** key
- Logging of your CPU/GPU sensors values
- Audio notification if temperature sensor values exceed custom values (customizable)

## Configuration file

Default configuration file ```helios_monitor.conf``` contains this string:
```
1600+5+15+5000+0+70.0+70.0+75.0
```
Where (from left to right):
* ```1600``` - Sensors position X coordinate
* ```5``` - Sensors position Y coordinate
* ```15``` - Font Size
* ```5000``` - Sensors update time (ms)
* ```0``` - Logging mode active? (```0``` - Disabled, ```1``` - Enabled)
* ```70.0``` - CPU temperature warning value
* ```70.0``` - CPU Package temperature warning value
* ```75.0``` - GPU temperature warning value

## How to use

* Always run the program as Admin
* To change default position (4 presets) just click the **Screen Position** button
* To make font bigger/smaller click the **Font Bigger (+1)/Font Smaller (-1)** button
* To Show/Hide sensors click the **Show/Hide Sensors** button
* To Show/Hide main menu window press **HOME** key on your keyboard
* To enter position edit mode click the **Position Edit Mode** (it turns green) and then:
* 1) Drag the sensors widget with your Left Mouse Button pressing on sensors text
  2) When done press **Position Edit Mode** again
* To activate Log file replace **+0+** in settings file with **+1+**. For example:
* * **No logging**: ```1600+5+15+5000+0+70.0+70.0+75.0```
  * **Active logging**: ```1600+5+15+5000+1+70.0+70.0+75.0```
* To change sensors values update time (by default: 5000 ms = 5 seconds) just replace it with your desired value like this:
* * **2 seconds**: ```1600+5+15+2000+0+70.0+70.0+75.0```
* To change dangerous temperature values (in Celcius) just replace them with your desired values like this:
* * New values CPU - **80**, CPU Package - **85**, GPU - **85**: ```1600+5+15+5000+1+80.0+85.0+85.0```
* When the content of configuration file is corrupted, it will be rewritten with the default values; if the config file is empty just click on some Position Preset and the default values will be activated and will be written to config file

## How to compile EXE for Windows OS

You will need **Nuitka** software to build executable. Run this command in your terminal:

```
python -m nuitka helios_temp_sensor_monitor.py
```

The Python source file already contains needed instructions for building the EXE. But be warned that some antiviruses may be triggered by the output EXE (false positive), so add it to to exclusions list.

## Known issues/problems

- Not all fullscreen apps support this widget
- Low sensors text rendering quality (may consider increasing the size of it)

## Dependencies

* [LibreHardwareMonitor.dll](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) (just dll file, already included)
* [pywin32](https://pypi.org/project/pywin32/)
* [simpleaudio](https://pypi.org/project/simpleaudio/)
* [bindglobal](https://pypi.org/project/bindglobal/)
* [Nuitka](https://nuitka.net/) (only for Windows EXE compilation)

## Referencis

* https://stackoverflow.com/questions/21840133/how-to-display-text-on-the-screen-without-a-window-using-python
* https://stackoverflow.com/questions/4055267/tkinter-mouse-drag-a-window-without-borders-eg-overridedirect1
* https://www.reddit.com/r/learnpython/comments/nbnhx9/how_do_you_move_tkinter_window_without_the_title/
