# PPETestCode

Project for developing the logging software for the SOMD Loves You PPE Sterilization Project.
Written in python, it simply logs the temperatures outputted by the multiple sensors to a .csv file.
Currently can read the temperatures provided to a serial port via an arduino in the following format:
[sensor number]:[temperature in celsius]

Writes to a .csv file. Internal data structure is
[timestamp],[sensor 1 temperature],[sensor 2 temperature],...,[sensor 12 temperature]

Script is smart enough to only write data if a sensor exists. If there are only N sensors in the serial data stream,
then the file will only contain data for N sensors.

Uses a variable runtime and constant update rate polling method. Runtime varies with the sensor readings accoring to 
the following rules:
1. If temperature is above allowable, the cycle aborts
2. If temperature is below a warning threshold (not quite hot enough, but not too cold), the cycle extends 3.3x for
   the duration the temperature remains at that level.
3. If temperature is below a cold cut-off, the cycle pauses, but continues to record.

TODO:
1. Individual sensor cycle tracking (DONE)
2. Fractional tick at end of cycle (DONE)
3. GUI using the Matplotlib python module (DELAYED)
4. Keep running average of measurements (spike filtering)
5. Implement RPI config file for certain options
6. Error detection and logging for overall system
7. GUI alert for errors/problems
