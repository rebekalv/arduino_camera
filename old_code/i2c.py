from pyb import UART
import time

# UART1, 115200 baud, tx=Pin X, rx=Pin Y (adjust to your wiring)
uart = UART(1, 115200)

distance_cm = 400

while True:
    # Send data as bytes
    uart.write(bytes([distance_cm]))  # or send string: uart.write(str(distance_cm) + '\n')
    time.sleep_ms(100)  # adjust rate

# send one byte -> receive 6 bytes, 2 per number sent.
