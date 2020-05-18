import PySimpleGUI as sg
import FileIO
import serial


def getnumsensors(devname):
    ser = serial.Serial(devname, 9600, rtscts=True, dsrdtr=True, timeout=1)
    ser.reset_input_buffer()

    sensors = dict()
    ser.readline()

    cnt = 0
    loops = 16
    while True:
        line = str(ser.readline(), encoding='utf-8', errors='ignore')
        s = line.split(":")
        if s[0] not in sensors:
            print("Found sensor id: " + s[0])
            sensors[s[0]] = s[0]
            cnt += 1
        else:
            if loops > 0:
                loops -= 1
            else:
                break
    ser.close()
    return len(sensors)


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
    return ""


def main():
    mode = chooseMode()
    serialname = ""
    if mode == "norm":
        serialname = "/dev/ttyACM0"
        print("Starting in normal mode.")
    else:
        print("Starting in dev mode.")
        serialname = "/dev/pts/1"
    numsens = getnumsensors(serialname)
    print("Found " + str(numsens) + " sensors.")

    layout = [[sg.Text("FileIO Output: ")],
              [sg.Multiline(size=(120, 20), key='-LOG-')]
              [sg.Button('Cancel', key='-CANCEL-')]]

    window = sg.Window("Test Window", layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            break
    window.close

if __name__ == '__main__':
    main()
