from datetime import datetime
import serial


def openserialport(portname):
    ser = serial.Serial(portname, 9600, rtscts=True, dsrdtr=True, timeout=1)
    ser.reset_input_buffer()
    return ser


# clears input buffer, reads in the current line
def readnewestline(ser):
    ser.reset_input_buffer
    ser.readline()
    return ser.readline()


def main():
    ser = openserialport('/dev/pts/1')
    sensors = {"0": "0"}
    # enumerate sensors
    loops = 16
    ser.flush()
    ser.readline()
    while True:
        line = str(ser.readline(), encoding='utf-8', errors='ignore')
        s = line.split(":")
        if s[0] not in sensors:
            print("Adding sensor id: " + s[0])
            sensors[s[0]] = s[1]
        else:
            if loops > 0:
                loops -= 1
            else:
                break
    ser.close()


if __name__ == '__main__':
    main()
