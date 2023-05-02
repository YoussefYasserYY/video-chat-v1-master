import io
import socket
import struct
import time
import threading
import picamera
import streamlit as st

# Set the IP address and port number
HOST = "0.0.0.0"
PORT = 8000

# Create a socket
server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the IP address and port number
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

# Create a thread to handle each client
def handle_client(client_socket):
    # Get the client's IP address
    client_ip = client_socket.getpeername()[0]

    # Start a loop to read frames from the camera
    try:
        connection = client_socket.makefile('wb')
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 30
            time.sleep(2)
            start = time.time()
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                # Write the length of the capture to the stream and flush to ensure it actually gets sent
                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()
                # Rewind the stream and send the image data over the wire
                stream.seek(0)
                connection.write(stream.read())
                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
                # Check if the client has closed the connection
                if time.time() - start > 300:
                    break
    finally:
        connection.close()
        client_socket.close()

# Start the video chat
def start_video_chat():
    st.title("Video Chat")

    # Create a list to store the client threads
    client_threads = []

    # Start a loop to accept incoming connections
    while True:
        # Wait for an incoming connection
        client_socket, client_address = server_socket.accept()

        # Create a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

        # Add the thread to the list of client threads
        client_threads.append(thread)

    # Wait for all client threads to finish
    for thread in client_threads:
        thread.join()

start_video_chat()
