import sensor, time, pyb
from machine import I2C
from vl53l1x import VL53L1X

# Enable wifi
WIFI_STREAMING = False # Set to False to disable wifi streaming
WIFI_NAME = "Volvevegen_2G"
WIFI_KEY = "Volvevegen"

# Parameters BLOB DETECTION
OFFSET = 30  # threshold offset around mean background brightness
min_area = 300       # ignore tiny blobs
min_pixels = 300     # ignore tiny blobs
max_fraction = 0.95   # ignore blobs covering more than 90% of image (not working?)

# Camera setup
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # grayscale for detection
sensor.set_framesize(sensor.QVGA) # smaller frame size for speed
sensor.skip_frames(time=500)

# Distance sensor setup (ToF = time of flight)
i2c = I2C(2)
tof = VL53L1X(i2c)
MIN_VALID_DISTANCE = 40  # mm
MAX_VALID_DISTANCE = 2000 # mm

# Buffer (last 10 readings) for smoothing noisy detections
readings = []
MAX_READINGS = 10

# LEDs
red = pyb.LED(1)
green = pyb.LED(2) # streaming video
blue = pyb.LED(3)  # setting up stream

def leds_off():
    red.off()
    green.off()
    blue.off()

clock = time.clock()

def wifi_setup(name, key): # returns wifi client
    import network, socket

    # User instructions
    print('\n1. Activate a mobile hotspot or use wifi router')
    print('2. If not activated: Set the band to be 2.4 GHz')
    print('3. Change the wifi name and passkey parameters to match the wifi\n')

    # WiFi connection parameters
    HOST = ""
    PORT = 8080

    # Init wlan module and connect to network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(name, key)
    # Set statisk IP: (IP, netmask, gateway, DNS)
    #wlan.ifconfig(('192.168.2.30', '255.255.255.0', '192.168.2.1', '8.8.8.8'))

    print('Trying to connect to network "{:s}"'.format(name))
    print('with passkey "{:s}"\n'.format(key))

    while not wlan.isconnected():
        time.sleep(1)
        print("Status:", wlan.status())

    print("WiFi Connected\n")
    print("Open a browser and enter http://{:s}:{:d}/ \n".format(wlan.ifconfig()[0], PORT))

    # Create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.bind([HOST, PORT])
    s.listen(5)
    s.setblocking(True)

    print("Waiting for user connection...")
    client, addr = s.accept()
    client.settimeout(5.0)
    print("Connected to " + addr[0] + ":" + str(addr[1]))

    # Read request from client
    data = client.recv(1024)

    # Send multipart header
    client.sendall(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )
    return client

def wifi_stream_frame(client, img):
    # Convert to JPEG for streaming
    cframe = img.to_jpeg(quality=35, copy=True)
    header = (
        "\r\n--openmv\r\n"
        "Content-Type: image/jpeg\r\n"
        "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
    )
    client.sendall(header)
    client.sendall(cframe)

def average_object_width_mm(target,center_x,dist):

    # Get x-range of the blob, NB: pixels 0-320
    x_min = target.x()
    x_max = target.x() + target.w()

    # Store in buffer
    readings.append((x_min,x_max,dist))

    # Find average of the last N readings
    if len(readings) == MAX_READINGS:
        x_min = sum(r[0] for r in readings) // MAX_READINGS
        x_max = sum(r[1] for r in readings) // MAX_READINGS
        dist = sum(r[2] for r in readings) // MAX_READINGS
        readings.pop(0)  # remove oldest reading

    # Convert from pixel to mm
    focal_length_px = 143.0  # for QVGA
    width_px = x_max - x_min
    object_width_mm = (width_px * dist) / focal_length_px

    # offset from image center to x_start in mm (negative = left)
    x_offset_mm = ((x_min - center_x) * dist) / focal_length_px

    return int(x_offset_mm),int(object_width_mm),int(dist)


def detect_obstacles(wifi_client=None):
    clock.tick()
    img = sensor.snapshot()

    ## DISTANCE SENSOR
    dist = tof.read()  # Read distance in mm

    # Dynamic background brightness
    stats = img.get_statistics()
    mean_val = stats.l_mean()
    limit = max(0, mean_val - OFFSET)
    color_thresholds = [(0, limit)]

    # Find dark blobs
    blobs = img.find_blobs(color_thresholds, pixels_threshold=min_pixels, area_threshold=min_area)

    if blobs and dist > MIN_VALID_DISTANCE and dist < MAX_VALID_DISTANCE:
        # Center of the image (where ToF points)
        center_x = img.width() // 2
        center_y = img.height() // 2

        # Filter blobs to ignore very large ones
        max_pixels = int(img.width() * img.height() * max_fraction)
        valid_blobs = [b for b in blobs if b.pixels() < max_pixels]

        # Find the blob covering the distance sensor's line-of-sight (center)
        target = None
        for b in valid_blobs:
            if b.pixels() < (img.width() * img.height() * max_fraction):
                if b.x() <= center_x <= b.x()+b.w() and b.y() <= center_y <= b.y()+b.h():
                    target = b
                    break
        if not target:
            # If no blob covers the center, find the nearest blob
            nearest = None
            nearest_dist = float('inf')
            for b in blobs:
                # Calculate distance from blob center to image center
                dx = b.cx() - center_x
                dy = b.cy() - center_y
                distance = (dx*dx + dy*dy)**0.5
                if distance < nearest_dist:
                    nearest = b
                    nearest_dist = distance
            target = nearest

        if target:
            # Draw target square and distance
            img.draw_cross(target.cx(), target.cy(), color=(0, 255, 0))
            img.draw_rectangle(target.rect(), color=(0, 0, 0), thickness=3)
            img.draw_string(10, 10, f"Distance: {dist} mm", color=(255, 255, 255),scale=1.5)

            # Calculate average object offset, width and distance
            x_offset_mm,object_width_mm,smoothed_dist = average_object_width_mm(target,center_x,dist)
            print(x_offset_mm,object_width_mm,smoothed_dist)

    ## WIFI STREAMING
    if WIFI_STREAMING and wifi_client:
        wifi_stream_frame(wifi_client, img)

try:
    blue.on()
    wifi_client = (wifi_setup(WIFI_NAME, WIFI_KEY) if WIFI_STREAMING else None)
    blue.off()
    green.on()
    print("Offset mm, Object width mm, Distance mm")
    while True:
        detect_obstacles(wifi_client)
except:
    leds_off()
    print("\nProgram finished\n")

