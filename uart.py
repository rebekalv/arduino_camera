from pyb import UART, LED
import time
import struct  # for packing integers to bytes

# UART4, 115200 baud. Tx = pin1 (SDA i2c), Rx = pin2 (SCL i2c)
uart = UART(4, 115200, timeout_char=200)

x_start = 20
x_end = 30
distance_cm = 400

green = LED(2)
green.on()

while True:
    # Wait for request from UART
    if uart.any():
        request = uart.read(1)
        print('Request:', request)
        if request == b'r':
            # Send camera data
            data = struct.pack('<HHH', x_start, x_end, distance_cm) # 2 bytes each
            uart.write(data)
            print('Data sent')
    time.sleep_ms(10)
