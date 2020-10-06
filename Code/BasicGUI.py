import PySimpleGUI as sg
import threading
from time import sleep
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure

import Code.FileIO

stateswitcher = {
    Code.FileIO.LOW_FAIL: "low fail!",
    Code.FileIO.LOW_WARN: "low warn",
    Code.FileIO.GOOD: "good",
    Code.FileIO.HIGH_FAIL: "high fail!",
    Code.FileIO.COMPLETE: "complete"
}

colorswitcher = {
    Code.FileIO.LOW_FAIL: "blue",
    Code.FileIO.LOW_WARN: "lightblue",
    Code.FileIO.GOOD: "green",
    Code.FileIO.HIGH_FAIL: "red",
    Code.FileIO.COMPLETE: "purple"
}


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
    while not Code.FileIO.loggingready:
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
    sensortext = []
    sensorvalues = []
    #sensorcanvases = []

    for i in range(numsensors):
        sensortext.append(sg.Text(str(i + 1), size=(11, 1), text_color="white", key="-" + str(i + 1) + "INFO-"))
    for i in range(numsensors):
        sensorvalues.append(sg.Text(str(i + 1), size=(11, 1), text_color="white", background_color="grey", key="-" + str(i + 1) + "TEMP-"))
    #for i in range(numsensors):
    #    sensorcanvases.append(sg.Canvas(size=(20, 20), key="-" + str(i + 1) + "CANVAS-"))

    layout = [[sg.Button("Start"), sg.Button("Stop"), sg.Button("Reset")],
        [sg.Text("Sensor Outputs:")],
        [*sensortext],
        [*sensorvalues],
        #[*sensorcanvases]
        [sg.Text("Time remaining: 00:00:00", key="-TIMEREMAINING-")]]

    return layout


def main():
    loggerthread = threading.Thread(target=Code.FileIO.main, name="logging")
    loggerthread.daemon = True
    loggerthread.start()

    # TODO: this currently doesn't do anything
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
        if event in (None, "Start"):
            Code.FileIO.loggingstarted = True
        if event in (None, "Stop"):
            Code.FileIO.loggingstarted = False
        if event in (None, "Reset"):
            Code.FileIO.loggingstarted = True
            Code.FileIO.loggingreset = True
        if Code.FileIO.loggingstarted:
            for i in range (numsens):
                #print(str(i) + " " + Code.FileIO.sensors[str(i)]["temp"] + "\n")
                window["-" + str(i + 1) + "INFO-"].update(str(i + 1) + ": " + stateswitcher.get(Code.FileIO.sensors[str(i + 1)]["state"], "unknown"))
                window["-" + str(i + 1) + "TEMP-"].update(Code.FileIO.sensors[str(i + 1)]["temp"], background_color=colorswitcher.get(Code.FileIO.sensors[str(i + 1)]["state"], "grey"))
            window["-TIMEREMAINING-"].update("Time remaining: " + "{:0>2d}".format((Code.FileIO.timeleft // 3600) % 60) + ":" + "{:0>2d}".format((Code.FileIO.timeleft // 60) % 60) + ":" + "{:0>2d}".format((Code.FileIO.timeleft % 60)))
    window.close()


if __name__ == '__main__':
    main()
