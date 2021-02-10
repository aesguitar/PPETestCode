import optparse
import serial
import threading
from datetime import datetime
from time import sleep, time

# data acquisition run statues
STOPPED = 0
RUNNING = 1

# sensor run states
LOW_FAIL = 0
LOW_WARN = 1
GOOD = 2
HIGH_FAIL = 3
COMPLETE = 4

LOW_FAIL_TEMP = 15.5
LOW_WARN_TEMP = 18.5
HIGH_FAIL_TEMP = 24

# run time in seconds
runtime = 60

# logger update rate
updaterate = 1

# global time left
timeleft = runtime

# global sensor data dictionary
sensors = {}
sensors_lock = threading.Lock()

current_milli_time = lambda: int(round(time() * 1000))

loggingready = False
loggingstarted = False
loggingreset = False


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
# TODO: change all ticks to 0 when one sensor high fails?
def ticksleft(sensors):
    global timeleft
    highfail = False
    maxticks = 0
    for i in sensors.keys():
        if not highfail:
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
        if sensors[i]["ticks"] > maxticks:
            maxticks = sensors[i]["ticks"]
    timeleft = round(maxticks / 33) * updaterate
    return sensors


# format [sensorid, temperature, ticks, state, sensorid, temperature, ...]
def sensorsstring(sensors):
    tmpstr = ""
    for i in sensors.keys():
        tmpstr += sensors[i]["temp"] + "," + str(sensors[i]["ticks"]) + "," + str(sensors[i]["state"]) + ","
    return tmpstr[:-1].replace("\r\n", "")


def checkdone(sensors):
    if len(sensors) == 0:
        return False
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


def writecolumnheaders(file, sensors):
    header = "timestamp,"
    for i in sensors.keys():
        header += "Sensor " + i + " Temperature,"
        header += "Sensor " + i + " Ticks Remaining,"
        header += "Sensor " + i + " State,"
    header = header[:-1] + "\n"
    file.write(header)


def startlogging(ser):
    global sensors
    global updaterate
    global runtime
    global timeleft
    global loggingready

    loggingready = False

    parser = optparse.OptionParser(description="Temperature logging utility for the PPE Sterilization Project\nwith" +
                                               "SOMD Loves You.")
    parser.add_option("-u", action="store", dest="u", type=float, default=1)
    parser.add_option("-r", action="store", dest="r", type=float, default=60)
    parser.add_option("-f", action="store", dest="f", type=str, default='../TestLogs/'
                                                                        + datetime.now().strftime("%y%m%d_%H%M%S")
                                                                        + ".csv")

    options, args = parser.parse_args()
    updaterate = options.u
    runtime = options.r
    timeleft = runtime
    filename = options.f
    ticks = int(round(runtime / updaterate)) * 33

    sensdict = dict()
    logfile = openfile(filename)
    # enumerate sensors
    loops = 16
    ser.reset_input_buffer()
    ser.readline()

    while True:
        line = str(ser.readline(), encoding='utf-8', errors='ignore')
        if len(line) > 0:
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
    writecolumnheaders(logfile, sensors)

    loggingready = True
    return logfile

def main():
    global sensors
    global timeleft
    global loggingready
    global loggingstarted
    global loggingreset

    ser = openserialport('/dev/pts/3')
    # ser = openserialport('/dev/ttyACM0')
    logfile = startlogging(ser)

    while True:
        clearbuffer(ser)
        if loggingstarted:
            if loggingreset:
                logfile.close()
                logfile = startlogging(ser)
                loggingreset = False
            elif loggingready:
                with sensors_lock
                    if not checkdone(sensors):
                        st = current_milli_time()
                        now = datetime.now().strftime("%H:%M:%S")
                        for j in range(len(sensors)):
                            line = str(ser.readline(), 'utf-8', 'ignore')
                            s = line[:-2].split(":")  # -2 index because of /r/n (two character) line endings from the serial input
                            sensors[s[0]]["temp"] = s[1]
                        sensors = checktemps(sensors)
                        data = str(now) + "," + sensorsstring(sensors) + "\n"
                        print(data[:-1])
                        logfile.write(data)
                        sensors = ticksleft(sensors)
                        et = current_milli_time()
                        rt = et - st
                        if rt > 0:
                            waitforupdate((updaterate * 1000 - rt) / 1000, ser)
                    else:
                        timeleft = 0
                        logfile.close()
                        logfile = startlogging(ser)
        else:
            sleep(0.01)

    ser.close()


if __name__ == '__main__':
    main()
