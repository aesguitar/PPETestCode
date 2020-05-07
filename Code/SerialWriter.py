import serial
from random import uniform

rrange = [15, 25]


def openserialport():
    serport = "/dev/pts/2"
    ser = serial.Serial(serport, 9600, rtscts=True, dsrdtr=True)
    return ser


def createsensors(number):
    sdict = {0: 0}
    for i in range(1, number + 1):
        sdict[i] = round(uniform(rrange[0], rrange[1]), 2)
    del sdict[0]
    return sdict


def readsensor(sensors, number):
    if number in sensors:
        return round(uniform(rrange[0], rrange[1]), 2)
    else:
        return 0


def main():
    ser = openserialport()
    sensors = createsensors(8)
    loops = int(len(sensors) * 3)
    for i in range(loops):
        ind = (i % 7) + 1
        sensors[ind] = readsensor(sensors, ind)
        payload = str(ind) + ":" + str(sensors[ind]) + '\n'
        # print(payload)
        ser.write(bytearray(payload, encoding='utf-8'))
    ser.close()


if __name__ == '__main__':
    main()
