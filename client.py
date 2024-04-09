import socket
import cv2
import socket,pickle,struct
import threading


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import random
import time


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

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

# Deserialize public key from bytes
def deserialize_public_key(serialized_key):
    return serialization.load_pem_public_key(serialized_key, backend=default_backend())


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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fl_name=None
        self.frame_size = (1280, 720)
        self.name=""
        self.private=""
        self.public=""
        self.public_keys={}
        self.operation=0
    
    def listen_to_server(self):
        while True:
            msg=self.socket.recv(4096)
            if self.operation=="4":
                return
            while self.operation=="1":
                    time.sleep(2)
            if  self.operation=="2":
                print(msg.decode(errors='ignore'))

            if  self.operation==0:
                try:
                    msg=decrypt_data(self.private, msg)
                    print("\n: message recieved",msg.decode(errors='ignore'))
                except:
                    print("\n: unable to decrypt message")

            if  self.operation=="0":
                server_msg = msg.decode("utf-8")
                pairs_=server_msg.split("\n")
                for i in pairs_:
                    user_name,pub_key=i.split(":")
                    pub_key=pub_key.encode("utf-8")
                    
                    self.public_keys[user_name]=pub_key.replace(b'\\n', b'\n')

            if  self.operation=="3":
                server_msg = msg.decode("utf-8")
                print(server_msg)
                pairs_=server_msg.split("\n")
                for i in pairs_:
                    user_name,pub_key=i.split(":")
                    pub_key=pub_key.encode("utf-8")
                    
                    self.public_keys[user_name]=pub_key.replace(b'\\n', b'\n')

            self.operation=0
        

    def connect(self):
        self.socket.connect((self.host, self.port))
        server_msg = self.socket.recv(1024).decode("utf-8")

        print("connected: ",server_msg)
        
        private_key, public_key = generate_key_pair()
        self.private=private_key
        print("public key",serialize_public_key(public_key))
        self.name=input("enter your name ")
        self.public=input("enter your public key: ")
        
        self.socket.send(f"{self.name},{self.public}".encode("utf-8"))

        t1=threading.Thread(target=self.listen_to_server, args=()).start()
        while True:
            self.operation=input("enter operation 0>send Msg 1> play video 2> List all files 3>List all public keys  4> quit ")
            self.socket.send(self.operation.encode("utf-8"))
            if self.operation=="4":
                break
            elif self.operation=="0":
                try:
                    reciever=input("enter reciever name ")
                    self.socket.send(reciever.encode("utf-8"))
                    msg=input("enter message ")
                    
                    pub_key=self.public_keys[reciever]
                    reciever_pub_key=deserialize_public_key(pub_key)
                    en_msg=encrypt_data(reciever_pub_key, msg.encode("utf-8"))
                    print(en_msg)
                    self.socket.send(en_msg)
                    self.operation=0
                except Exception as e:
                    print(e)
                    self.operation=0

            elif self.operation=="1":   
                
                self.fl_name=input("enter file_name ")
                self.socket.send(self.fl_name.encode("utf-8"))
                t2=threading.Thread(target=self.receive_video_stream(), args=())
                t2.start() 
                t2.join()
                
            while self.operation!=0:
                print(self.operation)
                continue
            self.operation=0

    def receive_video_stream(self):

        data = b""
        prev="_"
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
            print(data)
            if data==b"exit":
                cv2.destroyAllWindows()
                break
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

        self.operation=0

def main():
    client_ = Client("localhost", 8888)
    client_.connect()
    
if __name__ == "__main__":
    main()
    
