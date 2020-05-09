from datetime import datetime
import serial
from time import sleep
import optparse


# run states
LOW_FAIL = 0
LOW_WARN = 1
GOOD = 2
HIGH_FAIL = 3
COMPLETE = 4

LOW_FAIL_TEMP = 15.5
LOW_WARN_TEMP = 18.5
HIGH_FAIL_TEMP = 24

# run time in seconds
runTime = 5

# logger update rate
updateRate = 1


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


def checktemps(sensors):
    states = {"0":GOOD}
    for i in sensors.keys():
        tmp = float(sensors[i][:-1])
        if tmp <= LOW_FAIL_TEMP:
            states[i] = LOW_FAIL
        elif tmp <= LOW_WARN_TEMP:
            states[i] = LOW_WARN
        elif tmp >= HIGH_FAIL_TEMP:
            states[i] = HIGH_FAIL
        else:
            states[i] = GOOD
    del states["0"]
    return states


def ticksLeft(states, ticks):
    dec = 33
    for i in states.values():
        # print(i)
        if i == HIGH_FAIL:
            ticks = 0
            break
        elif i == LOW_WARN:
            dec = 10
        elif i == LOW_FAIL:
            dec = 0
    return ticks - dec


def main():
    parser = optparse.OptionParser(description="Temperature logging utility for the PPE Sterilization Project\nwith" +
                                               "SOMD Loves You.")
    parser.add_option("-u", action="store", dest="u", type=float, default=.5)
    parser.add_option("-r", action="store", dest="r", type=float, default=30)

    options, args = parser.parse_args()
    updateRate = options.u
    runTime = options.r
    ticks = int(round(runTime/updateRate))*33

    ser = openserialport('/dev/pts/1')
    # ser = openserialport('/dev/ttyACM0')
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
    states = checktemps(sensors)

    while ticks > 0:
        print("Ticks left: " + str(ticks/33))
        now = datetime.now().strftime("%H:%M:%S")
        clearbuffer(ser)
        for j in range(len(sensors)):
            line = str(ser.readline(), 'utf-8', 'ignore')
            s = line[:-1].split(":")
            sensors[s[0]] = s[1]
        states = checktemps(sensors)
        dictstring = str(sensors.values())
        data = str(now) + "," + dictstring[13:-2].replace("'", "").replace('\\',"").replace('r', '').replace(' ','') + "\n"
        # print(data[:-1])
        logfile.write(data)
        waitforupdate(updateRate, ser)
        ticks = ticksLeft(states, ticks)
    ser.close()
    logfile.close()


if __name__ == '__main__':
    main()
