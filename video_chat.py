import cv2
import numpy as np
import streamlit as st
import socket
import threading
import os

# Set the IP address and port number
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP address and port number
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

# Create a thread to handle each client
def handle_client(client_socket):
    # Get the client's IP address
    client_ip = client_socket.getpeername()[0]

    # Create a video capture object
    capture = cv2.VideoCapture(0)

    # Start a loop to read frames from the camera
    while True:
        # Read a frame from the camera
        _, frame = capture.read()

        # Convert the frame to a NumPy array
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.array(frame)

        # Send the frame to the client
        try:
            client_socket.sendall(frame.tobytes())
        except:
            break

    # Close the video capture object
    capture.release()

    # Close the client socket
    client_socket.close()

# Start the video chat
def start_video_chat():
    st.title("Video Chat")

    # Create a list to store the client threads
    client_threads = []

    # Create a flag to indicate whether the server should continue running or not
    running = True

    # Start a loop to accept incoming connections
    while running:
        # Wait for an incoming connection
        client_socket, client_address = server_socket.accept()

        # Create a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

        # Add the thread to the list of client threads
        client_threads.append(thread)

        # Display the video from the client
        video_placeholder = st.empty()
        while True:
            # Receive the frame from the client
            try:
                frame_bytes = client_socket.recv(1024)
                frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(480, 640, 3)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_placeholder.image(frame, channels="BGR")
            except:
                break

        # Remove the thread from the list of client threads
        client_threads.remove(thread)

    # Wait for all client threads to finish
    for thread in client_threads:
        thread.join()

# Run the video chat
if __name__ == '__main__':
    start_video_chat()
