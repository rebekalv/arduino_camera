from pyb import UART, LED
import time

# UART4, 115200 baud. Tx = pin1 (SDA i2c), Rx = pin2 (SCL i2c)
uart = UART(4, 115200, timeout_char=200)

x= 20
y = 30
distance_cm = 42

green = LED(2)
green.on()

while True:
    # Send a byte or multiple bytes
    uart.write(bytes([x,y,distance_cm]))  # or structured: uart.write(str(distance_cm)+'\n')
    time.sleep_ms(100)  # adjust to desired rate
