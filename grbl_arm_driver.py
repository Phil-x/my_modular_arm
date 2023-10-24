from time import sleep
import serial

ser = serial.Serial('/dev/ttyACM1', 250000, timeout=1)  # open serial port
print(ser.name)
print( ser.read(size=1200))

if ser.is_open:
    print('Connected')

ser.write(b'G0 X20 Y20\n')
ser.flush()
print(ser.read(size=100))

ser.write(b'G0 X0 Y0\n')
print(ser.read(size=100))

ser.close()             
