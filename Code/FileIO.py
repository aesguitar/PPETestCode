from datetime import datetime
import serial
from time import sleep
import subprocess as sp


def openserialport(portname):
    ser = serial.Serial(portname, 9600, rtscts=True, dsrdtr=True, timeout=1)
    ser.reset_input_buffer()
    return ser


# clears input buffer, reads in the current line
def readnewestline(ser):
    ser.reset_input_buffer()
    ser.readline()
    return ser.readline()


def openfile(filename):
    return open(filename, "w")


def clearbuffer(ser):
    ser.reset_input_buffer()
    ser.readline()


def waitforupdate(time, ser):
    clearrate = .5
    loops = int(round(time / clearrate))
    for i in range(loops):
        clearbuffer(ser)
        sleep(clearrate)


def main():
    period = 1
    ser = openserialport('/dev/pts/1')
    sensdict = {"0": "0"}
    logfile = openfile('TestLogs/'
                       + datetime.now().strftime("%y%m%d_%H%M%S")
                       + ".csv")
    # enumerate sensors
    loops = 16
    ser.reset_input_buffer()
    ser.readline()
    while True:
        line = str(ser.readline(), encoding='utf-8', errors='ignore')
        s = line.split(":")
        if s[0] not in sensdict:
            print("Adding sensor id: " + s[0])
            sensdict[s[0]] = s[1]
        else:
            if loops > 0:
                loops -= 1
            else:
                break
    del sensdict["0"]

    sensors = dict()
    for tmp1 in sorted(sensdict):
        sensors[tmp1] = sensdict[tmp1]

    for i in range(5):
        now = datetime.now().strftime("%H:%M:%S")
        clearbuffer(ser)
        for j in range(len(sensors)):
            line = str(ser.readline(), 'utf-8', 'ignore')
            s = line[:-1].split(":")
            sensors[s[0]] = s[1]
        dictstring = str(sensors.values())
        data = str(now) + ", " + dictstring[13:-2].replace("'", "") + "\n"
        # print(str(now) + ", " + dictstring[13:-2].replace("'", ""))
        logfile.write(data)
        waitforupdate(period, ser)
    ser.close()
    logfile.close()


if __name__ == '__main__':
    main()
