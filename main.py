import vision
import video_stream

def main():
    # Start Wi-Fi and server
    print("Connecting to Wi-Fi...")
    server = video_stream.start_server()
    client = video_stream.accept_client(server)

    # Main loop
    while True:
        frame, info = vision.process_frame()
        video_stream.send_frame(client, frame, info)

if __name__ == "__main__":
    main()
