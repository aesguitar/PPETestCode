from datetime import datetime
import serial


def openserialport(portname):
    ser = serial.Serial(portname, 9600, rtscts=True, dsrdtr=True)


def main():
    ser = openserialport('/dev/pts/1')


if __name__ = '__main__':
    main()