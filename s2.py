import socket
import threading
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os
import socket, cv2, pickle, struct

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    while True:
        client_socket, client_address = server_socket.accept()
        print(client_address)
        print("Recieved connection from : ", client_address)
        client_socket.send('Thank you for connecting'.encode("utf-8"))
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

def broadcast(clients, reciever, message):
    for k, v in clients.items():
        try:
            if len(v) > 0:
                v[1].send(message)
        except:
            clients[k] = []

def get_public_keys(clients):
    lst = []
    for v in clients.values():
        if len(v) > 0:
            lst.append(v[0])
    return lst

def get_public_keys_name(clients):
    lst = []
    for n, v in clients.items():
        if len(v) > 0:
            lst.append(n + ":" + v[0])
    return lst

def handle_client(client_socket, client_address):
    # Handle client connection
    # Add code to receive client's public key and store it in clients dictionary
    # Also notify existing clients about the new connection
   

    client_data = client_socket.recv(1024).decode("utf-8")
    name, public_key = client_data.split(",")
    clients[name] = [public_key, client_socket]
    # Receive data from the client
    while True:
        client_data = client_socket.recv(1024).decode("utf-8")
        print(f'Client sent: .{client_data}.')

        if client_data == "0":
            client_socket.send(",".join(get_public_keys_name(clients)).encode("utf-8"))
            # Message to other peer
            to_user = client_socket.recv(1024).decode("utf-8")
            message = client_socket.recv(4 * 1024)
            broadcast(clients, to_user, message)

        elif client_data == "1":
            file_initial = client_socket.recv(1024).decode("utf-8")

            video_files = get_files_with_initial(file_initial, "videos")
            client_socket.send("pause".encode("utf-8"))
            send_video_stream(client_socket, video_files)

        elif client_data == "2":
            files = get_files_with_initial("", "videos")
            print(files)
            client_socket.send(" , ".join(files).encode("utf-8"))

        elif client_data == "3":
            print(get_public_keys_name(clients))
            client_socket.send(",".join(get_public_keys_name(clients)).encode("utf-8"))
        else:
            break

    try:
        clients.pop(name)
        client_socket.send("closing")
    except:
        pass
    client_socket.close()

def get_files_with_initial(initial, folder_path="videos"):
    # Get list of files in the folder
    print(initial)
    files = os.listdir(folder_path)
    print(files)
    if initial == "":
        return files

    # Filter files that start with the given initial
    filtered_files = [folder_path + "/" + file for file in files if file.startswith(initial)]
    return filtered_files

def send_video_stream(client_socket, video_files):
    # Stream video frames proportionately in sequence from each available resolution video file
    if client_socket:
        fl = 0
        # vid = cv2.VideoCapture(0)
        for x, i in enumerate(video_files):
            print(f"{i}")
            vid = cv2.VideoCapture(f"{i}")
            if not vid.isOpened():
                print("Error: Could not open video file.")
                exit()

            total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

            # Calculate the number of frames to skip (read one-third of the video) \
            for _ in range(total_frames * (x) // len(video_files)):
                img, frame = vid.read()

            # Send frames
            try:
                while True:
                    img, frame = vid.read()
                    if not img:
                        break  # No more frames in the video
                    # frame = imutils.resize(frame,width=320)
                    a = pickle.dumps(frame)
                    message = struct.pack("Q", len(a)) + a
                    client_socket.sendall(message)
            except Exception as e:
                print("Error sending frames:", e)
                fl = 1

            vid.release()

            if fl == 1:
                break

    client_socket.sendall("exit".encode())
    print("done")


if __name__ == "__main__":
    clients = {}  # Dictionary to store clients' public keys
    video_folder = "videos/"  # Path to video file
    start_server("localhost", 8888)
