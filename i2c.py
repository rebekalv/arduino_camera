import pyb

# Setup I2C in SLAVE mode
i2c = pyb.I2C(1, pyb.I2C.SLAVE, addr=0x12)  # I2C bus 1, address 0x12

# Dummy distance value (replace later with ToF reading)
distance_cm = 42

print("I2C Slave running on address 0x12")

wait = 0

green = pyb.LED(2)
green.on()

while True:
    try:
        # Wait for master to request data
        if i2c.is_ready(0x12):
            # Send distance (as 1 byte for now)
            i2c.send(bytes([distance_cm]), timeout=1000)
            print("Sent:", distance_cm, "cm")

    except Exception:
        wait = wait +1
        if wait % 200000 == 0:
            print("Waiting for master")
