import network, socket, time

SSID = "REBEKALV 2920"
KEY  = "}R1277v8"
HOST, PORT = "", 8080

def start_server():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, KEY)
    while not wlan.isconnected():
        time.sleep_ms(500)
    print("WiFi Connected:", wlan.ifconfig())

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    s.bind([HOST, PORT])
    s.listen(1)  # single client
    return s

def accept_client(server):
    print("Waiting for client...")
    client, addr = server.accept()
    client.settimeout(5.0)
    _ = client.recv(1024)  # HTTP request
    print("Connected to", addr)
    # Send MJPEG headers once
    client.sendall(
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )
    return client

def send_frame(client, img, info):
    frame = img.to_jpeg(quality=35, copy=True)
    header = (
        f"\r\n--openmv\r\n"
        f"Content-Type: image/jpeg\r\n"
        f"X-Zone: {info['zone']}\r\n"
        f"X-Area: {info['area']}\r\n"
        f"X-Brightness: {info['brightness']}\r\n"
        f"Content-Length: {frame.size()}\r\n\r\n"
    )
    client.sendall(header)
    client.sendall(frame)