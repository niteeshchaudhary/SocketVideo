import socket
import threading
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os
import socket, cv2, pickle,struct,imutils

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Dictionary to store clients' public keys
        self.video_folder = "videos/"  # Path to video file
        self.video_files=[]
        self.video_chunks={}

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.socket.accept()
            print(client_address)
            threading.Thread(target=self.handle_client, args=(client_socket,client_address)).start()

    def handle_client(self, client_socket,client_address):
        # Handle client connection
        # Add code to receive client's public key and store it in self.clients dictionary
        # Also notify existing clients about the new connection
        print("Recieved connection from : ",client_address)
        client_socket.send('Thank you for connecting'.encode('utf-8'))

        client_data = client_socket.recv(1024).decode('utf-8')
        name,public_key,port=client_data.split(",")
        self.clients[name]=[public_key,client_address[0],port]
        # Receive data from the client
        while True:
            client_data = client_socket.recv(1024).decode('utf-8')
            print(f'Client sent: .{client_data}.')

            if client_data=="1":
                file_initial = client_socket.recv(1024).decode('utf-8')
            
                self.video_files=self.get_files_with_initial(initial=file_initial,folder_path="videos")

                self.send_video_stream(client_socket)
            elif client_data=="2":
                files=self.get_files_with_initial(initial="",folder_path="videos")
                print(files)
                client_socket.send(" , ".join(files).encode('utf-8'))
            else:
                # Close the connection with the client
                client_socket.close()
                break

    def get_files_with_initial(self,initial,folder_path="videos"):
        # Get list of files in the folder
        print(initial)
        files = os.listdir(folder_path)
        print(files)
        if initial=="":
            return files

        # Filter files that start with the given initial
        filtered_files = [folder_path+"/"+file for file in files if file.startswith(initial)]
        return filtered_files


    def send_video_stream(self, client_socket):
        # Stream video frames proportionately in sequence from each available resolution video file
        if client_socket:
            # vid = cv2.VideoCapture(0)
            for x,i in enumerate(self.video_files):
                print(f"{i}")
                vid=cv2.VideoCapture(f"{i}")
                if not vid.isOpened():
                    print("Error: Could not open video file.")
                    exit()

                total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

                # Calculate the number of frames to skip (read one-third of the video) \
                for _ in range(total_frames*(x) // len(self.video_files)):
                    img,frame = vid.read()

                # Skip frames
                for _ in range(total_frames // len(self.video_files)):
                    img,frame = vid.read()
                    # frame = imutils.resize(frame,width=320)
                    a = pickle.dumps(frame)
                    message = struct.pack("Q",len(a))+a
                    try:
                        client_socket.sendall(message)
                    except:
                        vid.release()
                        break

    def request_public_key(self, client_name):
        # Retrieve public key for client_name from self.clients dictionary
        pass

    def secure_communication(self, client_socket, data, client_name):
        # Use client's public key to encrypt and send data securely
        pass

    def handle_client_request(self, client_socket, data):
        # Handle client's request (e.g., secure communication or video streaming)
        pass

if __name__ == "__main__":
    server = Server("localhost", 8888)
    server.start()


