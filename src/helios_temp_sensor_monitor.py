
#* Helios CPU/GPU Temperature Sensor Monitor
#? Simple CPU/GPU temperature sensor monitoring software
#? Version: 0.9


import clr
import os
from tkinter import *
import win32api
import win32con
import pywintypes
import simpleaudio as sa
from datetime import datetime
import re
from bindglobal import BindGlobal


# <--- HELP
# Hardware Types = ['Motherboard','SuperIO','Cpu','Memory','GpuNvidia','GpuAmd', 'Storage']
# Sensor value fields = [sensor.Hardware.HardwareType, sensor.Hardware.Name, sensor.Index, sensor.Name, sensor.Value]
# --->

# <--- Nuitka Python to C compiler options
# nuitka-project: --disable-console
# nuitka-project: --lto=yes
# nuitka-project: --windows-icon-from-ico=icon.png
# nuitka-project: --enable-plugin=tk-inter
# nuitka-project: --onefile
# --->


# <--- Global variables section
PROGRAM_VER = '0.9'
PROGRAM_NAME = 'Helios CPU/GPU Temperature Sensor Monitor'

LOGS_FILE = 'logs.txt'

SENSORS_SHOW = 1
MENU_SHOW = 1
POSITION_EDIT_MODE = 0
LAST_CLICK_POSITION_X = 0
LAST_CLICK_POSITION_Y = 0

POSITION_X = '1600' # Default value
POSITION_Y =  '5' # Default value
FONT_SIZE = '15' # Default value
SENSORS_UPDATE_TIME = 5000 # Default value
IS_LOGGING_ACTIVE = 0 # Default value
CPU_TEMP_WARN_VALUE = 70.0 # Default value
CPU_PACKAGE_TEMP_WARN_VALUE = 70.0 # Default value
GPU_CORE_TEMP_WARN_VALUE = 75.0 # Default value
# --->


# <--- Validate and Set settings function
def validate_and_set_settings():

    try:

        with open('helios_monitor.conf', 'r') as conf_file:
            
            settings = conf_file.readline().strip().split('+')

            if (isinstance(int(settings[0]), int) and isinstance(int(settings[1]), int) and isinstance(int(settings[2]), int) and isinstance(int(settings[3]), int) and ((isinstance(int(settings[4]), int)) and (settings[4] == '1' or settings[4] == '0')) and isinstance(float(settings[5]), float) and isinstance(float(settings[6]), float) and isinstance(float(settings[7]), float)):
                # <--- DEBUG ONLY
                #print('VALIDATION SUCCESSFUL! SETTINGS WILL BE UPDATED!')
                #print(settings)
                # --->
                global POSITION_X
                POSITION_X = settings[0]

                global POSITION_Y 
                POSITION_Y = settings[1]

                global FONT_SIZE
                FONT_SIZE = settings[2]

                global SENSORS_UPDATE_TIME
                SENSORS_UPDATE_TIME = int(settings[3])

                global IS_LOGGING_ACTIVE
                IS_LOGGING_ACTIVE = int(settings[4])

                global CPU_TEMP_WARN_VALUE
                CPU_TEMP_WARN_VALUE = float(settings[5])
                
                global CPU_PACKAGE_TEMP_WARN_VALUE
                CPU_PACKAGE_TEMP_WARN_VALUE = float(settings[6])

                global GPU_CORE_TEMP_WARN_VALUE
                GPU_CORE_TEMP_WARN_VALUE = float(settings[7])

                return True
            
            else:
                # <--- DEBUG ONLY
                #print('VALIDATION ERROR! DEFAULT SETTINGS WILL BE USED!')
                #print(settings)
                # --->
                return False

    except:
        # <--- DEBUG ONLY
        #print('FILE OPEN ERROR! DEFAULT SETTINGS WILL BE USED!')
        # --->
        return False
# --->


# <--- Add Warning word to Log file function
def log_warning_add(input_data: str):
    
    output_data = re.findall(r'\d\d.\d', input_data)
    res = ''
    
    for t in output_data:

        if float(t) >= CPU_TEMP_WARN_VALUE or float(t) >= CPU_PACKAGE_TEMP_WARN_VALUE or float(t) >= GPU_CORE_TEMP_WARN_VALUE:

            res += 'WARNING!'
            break
    
    return res
# --->


# <--- Initialize Libre Hardware Monitor DLL function
def librehardwaremonitor_init():

    file = 'LibreHardwareMonitorLib.dll'
    clr.AddReference(os.path.abspath(file))

    from LibreHardwareMonitor import Hardware  # type: ignore

    computer = Hardware.Computer()
    computer.IsMotherboardEnabled = True
    computer.IsMemoryEnabled = True
    computer.IsCpuEnabled = True
    computer.IsGpuEnabled = True
    computer.IsStorageEnabled = True
    computer.Open()

    return computer
# --->


# <--- Parse Sensors Values function
def sensor_parse_value(sensor):

    if sensor.Value:

        if str(sensor.SensorType) == 'Temperature' and (str(sensor.Hardware.HardwareType) in ['SuperIO', 'Cpu', 'GpuNvidia', 'GpuAmd']) and str(sensor.Name) in ['GPU Core', 'CPU Package', 'CPU']:

            result_parse = str(sensor.Name) + ': ' + str(sensor.Value) + '\u00B0C'

            if (str(sensor.Name) == 'CPU Package' and sensor.Value >= CPU_PACKAGE_TEMP_WARN_VALUE) or (str(sensor.Name) == 'CPU' and sensor.Value >= CPU_TEMP_WARN_VALUE) or (str(sensor.Name) == 'GPU Core' and sensor.Value >= GPU_CORE_TEMP_WARN_VALUE):
                # <--- DEBUG ONLY
                #print('WARNING! Temperature of ' + str(sensor.Name) + ': ' + str(sensor.Value) + '\u00B0C' + ' >= TEMP_WARN_VALUE')
                # --->
                filename = 'warning.wav'
                wave_obj = sa.WaveObject.from_wave_file(filename)
                play_obj = wave_obj.play()
                play_obj.wait_done()

            return result_parse
# --->


# <--- Get Sensor Values function
def sensor_get_value(computer):

    result_value = ''

    for i in computer.Hardware:
        i.Update()

        for sensor in i.Sensors:
            if isinstance(sensor_parse_value(sensor), str):
                result_value += sensor_parse_value(sensor) + '\n'

        for j in i.SubHardware:
            j.Update()

            for subsensor in j.Sensors:
                if isinstance(sensor_parse_value(subsensor), str):
                    result_value += sensor_parse_value(subsensor) +'\n'
    
    if IS_LOGGING_ACTIVE == 1:

        with open(LOGS_FILE, 'a+', encoding='utf8') as log_file:
            log_time_stamp = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            log_file.write(log_time_stamp + '\t' + result_value.replace('\n', ' ') + log_warning_add(result_value) + '\n')

    return result_value
# --->


# <--- Call settings validation function and then check IS_LOGGING_ACTIVE
validate_and_set_settings()


if IS_LOGGING_ACTIVE == 1:

    if not os.path.exists(LOGS_FILE):
        open(LOGS_FILE, 'w').close()
# --->


# <--- Libre Hardware Monitor Instance Init (Computer) for getting sensors values
LibreHardwareMonitorInstance = librehardwaremonitor_init()
# --->


# <--- Temperature Sensors Label section
root = Tk()
temp_mon_text = Label(master=root, font=('Calibri',FONT_SIZE), fg='dark orange', bg='white', justify='left')
temp_mon_text.master.overrideredirect(True)
temp_mon_text.master.geometry('+'+POSITION_X+'+'+POSITION_Y)
temp_mon_text.master.lift()
#temp_mon_text.master.wm_attributes("-fullscreen", True)
temp_mon_text.master.wm_attributes("-topmost", True)
temp_mon_text.master.wm_attributes("-disabled", True)
temp_mon_text.master.wm_attributes("-transparentcolor", "white")

hWindow = pywintypes.HANDLE(int(temp_mon_text.master.frame(), 16))
exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)


def temp_mon_text_update():

    temp_mon_text.config(text = '' + sensor_get_value(LibreHardwareMonitorInstance))
    root.after(SENSORS_UPDATE_TIME, temp_mon_text_update)


def root_window_start_move(event):
    
    global LAST_CLICK_POSITION_X
    global LAST_CLICK_POSITION_Y
    
    LAST_CLICK_POSITION_X = event.x
    LAST_CLICK_POSITION_Y = event.y


def root_window_dragging_move(event):

    x_coord = event.x - LAST_CLICK_POSITION_X + root.winfo_x()
    y_coord = event.y - LAST_CLICK_POSITION_Y + root.winfo_y()
    root.geometry("+%s+%s" % (x_coord , y_coord))
# --->


# <--- Menu Window section
def menu_set_sensors_position(position: str):

    global POSITION_X
    global POSITION_Y

    if position == '1':
        temp_mon_text.master.geometry('+1600+5')
        POSITION_X = '1600'
        POSITION_Y = '5'

    elif position == '2':
        temp_mon_text.master.geometry('+1600+970')
        POSITION_X = '1600'
        POSITION_Y = '970'

    elif position == '3':
        temp_mon_text.master.geometry('+100+970')
        POSITION_X = '100'
        POSITION_Y = '970'

    elif position == '4':
        temp_mon_text.master.geometry('+100+5')
        POSITION_X = '100'
        POSITION_Y = '5'


def menu_set_font_size(modifier: str):
    
    global FONT_SIZE

    if modifier == '+':
        temp_mon_text.configure(font=('Calibri', int(FONT_SIZE)+1))
        font_size_tmp = int(FONT_SIZE) + 1
        FONT_SIZE = ''
        FONT_SIZE += str(font_size_tmp)
        # <--- DEBUG ONLY
        #print('FONT_SIZE:', FONT_SIZE)
        # --->

    elif modifier == '-':
        if int(FONT_SIZE) == 1:
            pass
            # <--- DEBUG ONLY
            #print('FONT_SIZE:', FONT_SIZE)
            # --->
        elif int(FONT_SIZE) > 1:
            temp_mon_text.configure(font=('Calibri', int(FONT_SIZE)-1))
            font_size_tmp = int(FONT_SIZE) - 1
            FONT_SIZE = ''
            FONT_SIZE += str(font_size_tmp)
            # <--- DEBUG ONLY
            #print('FONT_SIZE:', FONT_SIZE)
            # --->


def menu_show_hide_sensors():
    
    global SENSORS_SHOW

    if SENSORS_SHOW == 1:
        SENSORS_SHOW = 0
        show_hide_sensors_button.configure(bg = 'red')
        root.withdraw()

    elif SENSORS_SHOW == 0:
        SENSORS_SHOW = 1
        show_hide_sensors_button.configure(bg = 'SystemButtonFace')
        root.deiconify()


def menu_position_edit_mode():

    global POSITION_EDIT_MODE
    global POSITION_X
    global POSITION_Y

    if POSITION_EDIT_MODE == 0:
        POSITION_EDIT_MODE = 1
        position_edit_mode_button.configure(bg = 'lime')
        root.overrideredirect(False)
        root.wm_attributes("-disabled", False)
        root.resizable(False, False)
        # <--- DEBUG ONLY
        #print('POSITION_X:', root.geometry().split('+')[1])
        #print('POSITION_Y:', root.geometry().split('+')[2])
        # --->
    
    elif POSITION_EDIT_MODE == 1:
        POSITION_EDIT_MODE = 0
        position_edit_mode_button.configure(bg = 'SystemButtonFace')
        root.overrideredirect(True)
        root.wm_attributes("-disabled", True)
        hWindow = pywintypes.HANDLE(int(temp_mon_text.master.frame(), 16))
        exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
        win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)
        POSITION_X = ''
        POSITION_Y = ''
        POSITION_X += root.geometry().split('+')[1]
        POSITION_Y += root.geometry().split('+')[2]
        # <--- DEBUG ONLY
        #print('POSITION_X:', root.geometry().split('+')[1])
        #print('POSITION_Y:', root.geometry().split('+')[2])
        # --->


menu_window = Toplevel()
menu_window.title(PROGRAM_NAME + ' ' + PROGRAM_VER)
menu_window.resizable(False, False)
menu_window.focus()

menu_window_w = 450
menu_window_h = 300
screen_w = menu_window.winfo_screenwidth()
screen_h = menu_window.winfo_screenheight()
x = (screen_w/2) - (menu_window_w/2)
y = (screen_h/2) - (menu_window_h/2)
menu_window.geometry('%dx%d+%d+%d' % (menu_window_w, menu_window_h, x, y))

show_hide_sensors_button = Button(master=menu_window, width=16, height=1, text='Show/Hide Sensors', command = lambda: menu_show_hide_sensors())
position_1_button = Button(master=menu_window, width=16, height=1, text='Screen Position 1', command = lambda: menu_set_sensors_position('1'))
position_2_button = Button(master=menu_window, width=16, height=1, text='Screen Position 2', command = lambda: menu_set_sensors_position('2'))
position_3_button = Button(master=menu_window, width=16, height=1, text='Screen Position 3', command = lambda: menu_set_sensors_position('3'))
position_4_button = Button(master=menu_window, width=16, height=1, text='Screen Position 4', command = lambda: menu_set_sensors_position('4'))

show_hide_sensors_button.place(anchor=CENTER, relx=0.5, rely=0.5)
position_1_button.place(anchor=NE, relx=1.0, rely=0)
position_2_button.place(anchor=SE, relx=1.0, rely=1.0)
position_3_button.place(anchor=SW, relx=0, rely=1.0)
position_4_button.place(anchor=NW, relx=0, rely=0)

font_size_bigger_button = Button(master=menu_window, width=16, height=1, text='Font Bigger (+1)', command = lambda: menu_set_font_size('+'))
font_size_smaller_button = Button(master=menu_window, width=16, height=1, text='Font Smaller (-1)', command = lambda: menu_set_font_size('-'))

font_size_bigger_button.pack(pady= 5)
font_size_smaller_button.pack(pady= 5)

position_edit_mode_button = Button(master=menu_window, width=16, height=1, text='Position Edit Mode', command = lambda: menu_position_edit_mode())

position_edit_mode_button.pack(pady= 5)


def menu_window_show_hide(event):

    global MENU_SHOW

    if MENU_SHOW == 1:
        MENU_SHOW = 0
        menu_window.withdraw()
        # <--- DEBUG ONLY
        #print('MENU_SHOW:', MENU_SHOW)
        # --->

    elif MENU_SHOW == 0:
        MENU_SHOW = 1
        menu_window.deiconify()
        # <--- DEBUG ONLY
        #print('MENU_SHOW:', MENU_SHOW)
        # --->
 

def menu_window_on_close():

    global POSITION_X
    global POSITION_Y
    global FONT_SIZE
    global SENSORS_UPDATE_TIME
    global IS_LOGGING_ACTIVE
    global CPU_TEMP_WARN_VALUE
    global CPU_PACKAGE_TEMP_WARN_VALUE
    global GPU_CORE_TEMP_WARN_VALUE

    with open('helios_monitor.conf', 'w') as conf_file:

        configuration = str(POSITION_X) + '+' + str(POSITION_Y) + '+' + str(FONT_SIZE) + '+' + str(SENSORS_UPDATE_TIME) + '+' + str(IS_LOGGING_ACTIVE) + '+' + str(CPU_TEMP_WARN_VALUE) + '+' + str(CPU_PACKAGE_TEMP_WARN_VALUE) + '+' + str(GPU_CORE_TEMP_WARN_VALUE)
        conf_file.writelines(configuration)

    root.destroy()
# --->


# <--- Initialize global key binding for Menu window show/hide
bg = BindGlobal(widget=menu_window)
bg.gbind('<Home>', menu_window_show_hide)
# --->


# <--- Main functions to execute program
menu_window.protocol('WM_DELETE_WINDOW', menu_window_on_close)
root.bind('<Button-1>', root_window_start_move)
root.bind('<B1-Motion>', root_window_dragging_move)
temp_mon_text_update()
temp_mon_text.pack()
root.mainloop()
# --->
