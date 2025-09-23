import sensor, time
from machine import I2C
from vl53l1x import VL53L1X

# Enable wifi
WIFI_STREAMING = False # Set to False to disable wifi streaming

# Camera setup
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # grayscale for detection
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# Distance sensor setup (ToF = time of flight)
i2c = I2C(2)
tof = VL53L1X(i2c)
MIN_VALID_DISTANCE = 40  # mm

clock = time.clock()

# Parameters BLOB DETECTION
THRESHOLD_TYPE = "dark"  # "dark" or "bright"
min_area = 300       # ignore tiny blobs
min_pixels = 300     # ignore tiny blobs
OFFSET = 30  # threshold offset around mean brightness

# Buffer (last 5 readings) for smoothing noisy detections
readings = []
MAX_READINGS = 10

def wifi_setup():
    import network, socket

    # User instructions
    print('\n1. Activate a mobile hotspot ')
    print('2. Set the band to be 2.4 GHz')
    print('3. Change the wifi name and passkey parameters to match the wifi\n')


    # WiFi connection parameters
    WIFI_NAME = "REBEKALV"
    KEY = "12345678"
    HOST = ""
    PORT = 8080

    # Init wlan module and connect to network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_NAME, KEY)

    print('Trying to connect to network "{:s}"'.format(WIFI_NAME))
    print('with passkey "{:s}"'.format(KEY))

    while not wlan.isconnected():
        time.sleep_ms(1000)

    print("WiFi Connected ", wlan.ifconfig())

    # Create server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.bind([HOST, PORT])
    s.listen(5)
    s.setblocking(True)

    print("Waiting for connections..")
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

def stream_frame(client, img):
    # Convert to JPEG for streaming
    cframe = img.to_jpeg(quality=35, copy=True)
    header = (
        "\r\n--openmv\r\n"
        "Content-Type: image/jpeg\r\n"
        "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
    )
    client.sendall(header)
    client.sendall(cframe)

def detect_obstacles(wifi_client=None):
    while True:
        clock.tick()
        img = sensor.snapshot()

        ## DISTANCE SENSOR
        dist = tof.read()  # Read distance

        ## BLOB DETECTION

        # Dynamic background brightness
        stats = img.get_statistics()
        mean_val = stats.l_mean()
        if THRESHOLD_TYPE == "dark":
           limit = max(0, mean_val - OFFSET)
           thresholds = [(0, limit)]
        else:
           limit = min(255, mean_val + OFFSET)
           thresholds = [(limit, 255)]


        # Find dark or light blobs
        blobs = img.find_blobs(thresholds, pixels_threshold=min_pixels, area_threshold=min_area)

        if blobs and dist > MIN_VALID_DISTANCE:
            # Center of the image (where ToF points)
            center_x = img.width() // 2
            center_y = img.height() // 2

            # Find the blob covering the ToF line-of-sight
            target = None
            for b in blobs:
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

                # Get x-range of the blob, NB: pixels 0-320
                x_min = target.x()
                x_max = target.x() + target.w()

                # Store in buffer
                readings.append((x_min,x_max,dist))

                # Print the average of the last N readings
                if len(readings) == MAX_READINGS:
                    x_min = sum(r[0] for r in readings) // MAX_READINGS
                    x_max = sum(r[1] for r in readings) // MAX_READINGS
                    dist = sum(r[2] for r in readings) // MAX_READINGS
                    print(x_min, x_max, dist)
                    readings.pop(0)  # remove oldest reading

        ## WIFI STREAMING
        if WIFI_STREAMING and wifi_client:
            stream_frame(wifi_client, img)


while True:
    try:
        if WIFI_STREAMING:
            client = wifi_setup()
            detect_obstacles(client)
        else:
            detect_obstacles()
    except OSError as e:
        print("socket error:", e)

