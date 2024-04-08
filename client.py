import socket
import cv2
import numpy as np
import socket,pickle,struct
import threading


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import random

# Generate a public/private key pair
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Encrypt data with a public key
def encrypt_data(public_key, data):
    encrypted_data = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data

# Decrypt data with a private key
def decrypt_data(private_key, encrypted_data):
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.serv_port = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fl_name=None
        self.frame_size = (1280, 720)
        self.name=""
        self.private=""
        self.public=""

    def connect(self):
        self.serv_port=random.randrange(5000,9500)
        self.socket.connect((self.host, self.port))
        server_msg = self.socket.recv(1024).decode('utf-8')

        print("connected: ",server_msg)
        
        private_key, public_key = generate_key_pair()
        self.private=private_key
        print("public key",public_key)
        self.name=input("enter your name ")
        self.public=input("enter your public key: ")
        
        self.socket.send(f"{self.name},{self.public},{self.serv_port}".encode())


        operation=0
        while operation!="3":

            operation=input("enter operation 1> play video 2> List all files 3> quit ")
            self.socket.send(operation.encode())

            if operation=="1":   
                self.fl_name=input("enter file_name ")
                self.socket.send(self.fl_name.encode())
                self.receive_video_stream()
            else:
                server_msg = self.socket.recv(1024).decode('utf-8')
                print(server_msg)


    def request_public_key(self, client_name):
        # Send request for public key of client_name to server
        pass

    def secure_communication(self, data, recipient_name):
        # Encrypt data using recipient's public key and send it to server
        pass

    def request_video_stream(self):
        # Send request to server for video streaming
        pass

    def receive_video_stream(self):
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = self.socket.recv(4*1024) # 4K
                if not packet: break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size=0

            try:
                msg_size = struct.unpack("Q",packed_msg_size)[0]
            except:
                break

            while len(data) < msg_size:
                data += self.socket.recv(4*1024)

            frame_data = data[:msg_size]
            data  = data[msg_size:]
            try:
                frame = pickle.loads(frame_data)
                cv2.imshow("RECEIVING VIDEO",frame)
                key = cv2.waitKey(1) & 0xFF
                if key  == ord('q'):
                    cv2.destroyAllWindows()
                    break
            except:
                cv2.destroyAllWindows()
                break

if __name__ == "__main__":
    client = Client("localhost", 8888)
    client.connect()
