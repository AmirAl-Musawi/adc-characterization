import serial
import time

with serial.Serial(port="COM3", baudrate=115200, timeout=1) as ser:
    time.sleep(2)
    ser.reset_input_buffer()

    for _ in range(10):
        raw = ser.readline()
        text = raw.decode(errors="ignore")
        line = text.strip()
        print(line)