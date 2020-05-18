import optparse
import serial
from datetime import datetime
from time import sleep, time

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

current_milli_time = lambda: int(round(time() * 1000))


def openserialport(portname):
    ser = serial.Serial(portname, 9600, rtscts=True, dsrdtr=True, timeout=1)
    ser.reset_input_buffer()
    return ser


# clears input buffer, reads in the current line
def readnewestline(ser):
    ser.reset_input_buffer()
    ser.readline()
    return ser.readline()


# creates and opens the log file
def openfile(filename):
    return open(filename, "w")


# clears the serial buffer and reads a line to ensure the next line is a full line
def clearbuffer(ser):
    ser.reset_input_buffer()
    ser.readline()


# waits for the next time the log file is to be updated. periodically clears the buffer
def waitforupdate(time, ser):
    clearrate = 0.1
    loops = int(round(time / clearrate))
    for i in range(loops):
        clearbuffer(ser)
        sleep(clearrate)


# checks the received temperatures and outputs states according the boundary variables
def checktemps(sensors):
    for i in sensors.keys():
        tmp = float(sensors[i]["temp"].replace("\n", ""))
        if sensors[i]["state"] != COMPLETE:
            if sensors[i]["ticks"] <= 0:
                sensors[i]["state"] = COMPLETE
            elif tmp <= LOW_FAIL_TEMP:
                sensors[i]["state"] = LOW_FAIL
            elif tmp <= LOW_WARN_TEMP:
                sensors[i]["state"] = LOW_WARN
            elif tmp >= HIGH_FAIL_TEMP:
                sensors[i]["state"] = HIGH_FAIL
            else:
                sensors[i]["state"] = GOOD
    return sensors


# decrements the tick counter according to the state of the sensor temperature
def ticksLeft(sensors):
    highfail = False
    for i in sensors.keys():
        if ~highfail:
            if sensors[i]["state"] == HIGH_FAIL:
                highfail = True
            elif sensors[i]["state"] == LOW_FAIL or sensors[i]["state"] == COMPLETE:
                continue
            elif sensors[i]["state"] == LOW_WARN:
                sensors[i]["ticks"] -= 10
            else:
                sensors[i]["ticks"] -= 33
        else:
            sensors[i]["ticks"] = 0
    return sensors


# format [sensorid, temperature, ticks, state, sensorid, temperature, ...]
def sensorsstring(sensors):
    tmpstr = ""
    for i in sensors.keys():
        tmpstr += sensors[i]["temp"] + "," + str(sensors[i]["ticks"]) + "," + str(sensors[i]["state"]) + ","
    return tmpstr[:-1].replace("\n", "")


def checkdone(sensors):
    done = True
    for i in sensors.keys():
        if sensors[i]["state"] == HIGH_FAIL:
            return True
        else:
            if done:
                done = done and (sensors[i]["state"] == COMPLETE)
            else:
                break

    return done


def writecolumndeaders(file, sensors):
    header = "timestamp,"
    for i in sensors.keys():
        header += "Sensor " + i + " Temperature,"
        header += "Sensor " + i + " Ticks Remaining,"
        header += "Sensor " + i + " State,"
    header = header[:-1] + "\n"
    file.write(header)


def main():
    parser = optparse.OptionParser(description="Temperature logging utility for the PPE Sterilization Project\nwith" +
                                               "SOMD Loves You.")
    parser.add_option("-u", action="store", dest="u", type=float, default=.5)
    parser.add_option("-r", action="store", dest="r", type=float, default=5)
    parser.add_option("-f", action="store", dest="f", type=str, default='../TestLogs/'
                                                                        + datetime.now().strftime("%y%m%d_%H%M%S")
                                                                        + ".csv")

    options, args = parser.parse_args()
    updateRate = options.u
    runTime = options.r
    filename = options.f
    ticks = int(round(runTime / updateRate)) * 33

    ser = openserialport('/dev/pts/1')
    # ser = openserialport('/dev/ttyACM0')
    sensdict = dict()
    logfile = openfile(filename)
    # enumerate sensors
    loops = 16
    ser.reset_input_buffer()
    ser.readline()

    while True:
        line = str(ser.readline(), encoding='utf-8', errors='ignore')
        s = line.split(":")
        if s[0] not in sensdict:
            print("Adding sensor id: " + s[0])
            sensdict[s[0]] = {"temp": s[1], "ticks": ticks, "state": GOOD}
        else:
            if loops > 0:
                loops -= 1
            else:
                break

    sensors = dict()
    for tmp1 in sorted(sensdict):
        sensors[tmp1] = sensdict[tmp1]
    sensors = checktemps(sensors)
    print(sensorsstring(sensors))
    writecolumndeaders(logfile, sensors)

    while not checkdone(sensors):
        st = current_milli_time()
        now = datetime.now().strftime("%H:%M:%S")

        clearbuffer(ser)
        for j in range(len(sensors)):
            line = str(ser.readline(), 'utf-8', 'ignore')
            s = line[:-1].split(":")
            sensors[s[0]]["temp"] = s[1]
        sensors = checktemps(sensors)
        data = str(now) + "," + sensorsstring(sensors) + "\n"
        print(data[:-1])
        logfile.write(data)
        sensors = ticksLeft(sensors)
        et = current_milli_time()
        rt = et - st
        if rt > 0:
            waitforupdate((updateRate * 1000 - rt) / 1000, ser)

    ser.close()
    logfile.close()


if __name__ == '__main__':
    main()
