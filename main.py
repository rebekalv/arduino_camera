from vision import detect
from network import stream

def main():
    # Start Wi-Fi and server
    server = stream.start_server()
    client = stream.accept_client(server)

    # Main loop
    while True:
        frame, info = detect.process_frame()
        stream.send_frame(client, frame, info)

if __name__ == "__main__":
    main()
