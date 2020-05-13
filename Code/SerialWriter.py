import serial
from random import uniform, normalvariate
from time import sleep
import os
import psutil

# ***********NOTE************
# run 'socat -d -d pty,raw,echo=0,b9600 pty,raw,echo=0,b9600'
# before executing. This sets up a serial port this program
# can write to in order to emulate the arduino output to the
# pi.
#
# Make sure the serport variable represents the serial port
# that the above command set up.
tempmean = 21
stddev = 1.1

def openserialport():
    serport = "/dev/pts/2"
    ser = serial.Serial(serport, 9600)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser


def createsensors(number):
    sdict = {0: 0}
    for i in range(1, number + 1):
        sdict[i] = round(normalvariate(tempmean, stddev), 2)
    del sdict[0]
    return sdict


def readsensor(sensors, number):
    if number in sensors:
        return round(normalvariate(tempmean, stddev), 2)
    else:
        return 0


def main():
    # parentid = os.getppid()
    numsensors = 8
    ser = openserialport()
    sensors = createsensors(numsensors)
    loops = int(len(sensors) * 50000)
    for i in range(loops):
        # if psutil.Process(parentid).status() != psutil.STATUS_RUNNING:
        #     ser.reset_output_buffer()
        #     break
        ind = (i % numsensors) + 1
        sensors[ind] = readsensor(sensors, ind)
        payload = str(ind) + ":" + str(sensors[ind]) + '\n'
        # print(str(datetime.now()) + ": " + payload)
        data = bytearray(payload, encoding='utf-8')
        for d in data:
            db = d.to_bytes(1, 'big')
            ser.write(db)
            sleep(1 / 9600 * 8)
    ser.close()


if __name__ == '__main__':
    main()
