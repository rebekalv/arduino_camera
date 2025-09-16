import sensor, image, time, network, socket

SSID = "REBEKALV"
KEY = "12345678"
HOST = ""
PORT = 8080

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

print("WiFi Connected ", wlan.ifconfig())

# Create server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
s.bind([HOST, PORT])
s.listen(5)
s.setblocking(True)

# Init sensor
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)   # grayscale for detection
sensor.set_framesize(sensor.QVGA)        # 320x240
sensor.skip_frames(time=2000)

width = 320
zone_left = width // 3
zone_right = 2 * width // 3

# Parameters
MIN_AREA = 200
MAX_AREA = 20000
OFFSET = 30

def start_streaming(s):
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

    clock = time.clock()

    while True:
        clock.tick()
        img = sensor.snapshot()

        # Dynamic background brightness
        stats = img.get_statistics()
        mean_val = stats.l_mean()
        low = max(0, mean_val - OFFSET)
        thresholds = [(0, low)]  # detect darker objects

        blobs = img.find_blobs(thresholds, area_threshold=MIN_AREA, pixels_threshold=MIN_AREA)

        nearest = None
        nearest_area = 0
        for b in blobs:
            area = b.w() * b.h()
            if MIN_AREA < area < MAX_AREA:
                if area > nearest_area:
                    nearest = b
                    nearest_area = area

        if nearest:
            cx = nearest.cx()
            cy = nearest.cy()
            img.draw_rectangle(nearest.rect(), color=127)
            img.draw_cross(cx, cy, color=255)

            # Decide zone
            if cx < zone_left:
                zone = "LEFT"
            elif cx < zone_right:
                zone = "CENTER"
            else:
                zone = "RIGHT"

            print("Nearest obstacle:", zone, "area:", nearest_area, "mean:", mean_val)

            # Draw zone dividers
            img.draw_line((zone_left, 0, zone_left, 240), color=200)
            img.draw_line((zone_right, 0, zone_right, 240), color=200)

        # Convert to JPEG for streaming
        cframe = img.to_jpeg(quality=35, copy=True)
        header = (
            "\r\n--openmv\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
        )
        client.sendall(header)
        client.sendall(cframe)
        print(clock.fps(), "fps")

while True:
    try:
        start_streaming(s)
    except OSError as e:
        print("socket error:", e)
