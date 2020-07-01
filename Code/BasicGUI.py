import PySimpleGUI as sg
import serial
import threading
from time import sleep

import Code.FileIO

# def getnumsensors(devname):
#     ser = serial.Serial(devname, 9600, rtscts=True, dsrdtr=True, timeout=1)
#     ser.reset_input_buffer()
#
#     sensors = dict()
#     ser.readline()
#
#     cnt = 0
#     loops = 16
#     while True:
#         line = str(ser.readline(), encoding='utf-8', errors='ignore')
#         s = line.split(":")
#         if s[0] not in sensors:
#             print("Found sensor id: " + s[0])
#             sensors[s[0]] = s[0]
#             cnt += 1
#         else:
#             if loops > 0:
#                 loops -= 1
#             else:
#                 break
#     ser.close()
#     return len(sensors)

def getnumsensors():
    while len(Code.FileIO.sensors) == 0:
        sleep(0.01)
    return len(Code.FileIO.sensors)

def chooseMode():
    mode = "dev"
    layout = [ [sg.Text("Select a mode.")],
               [sg.Button("Normal Mode"), sg.Button("Developer Mode")] ]
    window = sg.Window("Mode Select", layout)
    while True:
        event, values = window.read()
        if event in (None, "Normal Mode"):
            mode = "norm"
            break
        elif event in (None, "Developer Mode"):
            break
    window.close()
    return mode

def buildlayout(numsensors):
    # create row of sensor values dynamically
    sensorlabels = []
    for i in range(numsensors):
        sensorlabels.append(sg.Text(str(i + 1), size=(4, 1), key="-" + str(i + 1) + "TEMP-"))

    layout = [[sg.Text("Sensor Outputs:")],
        [*sensorlabels]]
    return layout


def main():
    loggerThread = threading.Thread(target=Code.FileIO.main, name="logging")
    loggerThread.daemon = True
    loggerThread.start()

    mode = chooseMode()
    serialname = ""
    if mode == "norm":
        serialname = "/dev/ttyACM0"
        print("Starting in normal mode.")
    else:
        print("Starting in dev mode.")
        serialname = "/dev/pts/1"
    numsens = getnumsensors()
    print("Found " + str(numsens) + " sensors.")

    #layout = [[sg.Text("FileIO Output: ")],
    #          [sg.Multiline(size=(120, 20), key="-LOG-")],
    #          [sg.Button("Cancel", key="-CANCEL-")]]

    layout = buildlayout(numsens)
    window = sg.Window("Test Window", layout)
    while True:
        event, values = window.read(timeout=50)
        #if event in (None, "-CANCEL-"): # must use key name for event
        #    break
        for i in range (numsens):
            #print(str(i) + " " + Code.FileIO.sensors[str(i)]["temp"] + "\n")
            window["-" + str(i + 1) + "TEMP-"].update(Code.FileIO.sensors[str(i + 1)]["temp"])
    window.close()

if __name__ == '__main__':
    main()
