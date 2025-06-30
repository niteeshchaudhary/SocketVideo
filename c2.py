import socket
import cv2
import pickle,struct
from socket import *
import threading
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import random
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Global variables
host = "localhost"
port = 8888
socket_ = socket(AF_INET, SOCK_STREAM)
fl_name = None
frame_size = (1280, 720)
name = ""
private = ""
public = ""
public_keys = {}
operation = 0

def receive_video_stream():
    global operation
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
            while len(data) < payload_size:
                packet = socket_.recv(4*1024) # 4K
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
                data += socket_.recv(4*1024)

            frame_data = data[:msg_size]
            data  = data[msg_size:]
            # print(data)
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
    operation=0

# The rest of your functions remain the same
def generate_key_pair():
    rsa_key_pair = RSA.generate(2048)
    private_key = rsa_key_pair.export_key().decode()
    public_key = rsa_key_pair.publickey().export_key().decode()
    return private_key, public_key

# Encrypt data with a public key
def encrypt_data(recipient_public_key, data):
    print(recipient_public_key)
    recipient_public_key = RSA.import_key(recipient_public_key)
    cipher = PKCS1_OAEP.new(recipient_public_key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data

# def serialize_public_key(public_key):
#     return public_key.public_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PublicFormat.SubjectPublicKeyInfo
#     )

# # # Deserialize public key from bytes
# def deserialize_public_key(serialized_key):
#     return serialization.load_pem_public_key(serialized_key, backend=default_backend())


# Decrypt data with a private key
def decrypt_data(private_key, encrypted_data):
    private_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data
   
def listen_to_server():
        global operation, private, public_keys, socket_
        while True:
            msg=socket_.recv(4096)
            if operation=="4":
                return
           
            if  operation=="2":
                operation=0
                print(msg.decode(errors='ignore'))

            if operation==0:
                try:
                    msg=decrypt_data(private, msg)
                    print("\n: message recieved",msg.decode(errors='ignore'))
                except:
                    print("\n: unable to decrypt message")

            if operation == "0" or operation == "3":
                operation=0
                server_msg = msg.decode("utf-8")
                pairs_ = server_msg.split(",")
                print("pairs",pairs_)
                for i in pairs_:
                 if ":" in i:
                    user_name, pub_key = i.split(":")
                    print("pub_key",i)
                    pub_key = pub_key.replace('\\n', '\n')
                    public_keys[user_name] = pub_key
                    print("users",user_name)

            while operation=="1":
                    
                    time.sleep(2)
                    if(t2.is_alive()==False):
                        operation=0
                        break
        


socket_.connect((host, port))
server_msg = socket_.recv(1024).decode("utf-8")
print("connected: ",server_msg)
        
private_key, public_key = generate_key_pair()
private = private_key
name = input("Enter your name: ")
socket_.send(f"{name},{public_key}".encode("utf-8"))
#print("public key",public_key.encode())
        
# socket_.send(f"{name},{public_key.encode()}".encode("utf-8"))
#socket_.send(f"{name},{public_key}".encode("utf-8"))

t1=threading.Thread(target=listen_to_server, args=()).start()
while True:
    print("0.To Message")
    print("1.To Video")
    print("2.To List all files")
    print("3.To List all public keys")
    print("4.To quit")
    operation=input("Enter Operation Number")
    socket_.send(operation.encode("utf-8"))
    if operation=="4":
        break
    elif operation == "0":
        try:
            reciever = input("enter receiver name: ")
            socket_.send(reciever.encode("utf-8"))
            msg = input("enter message: ")
            pub_key = public_keys[reciever]
            en_msg = encrypt_data(pub_key, msg)
            socket_.send(en_msg)
            operation = 0
        except Exception as e:
            print("here",e)
        operation = 0

    elif operation == "1":   
        fl_name = input("enter file name: ")
        socket_.send(fl_name.encode("utf-8"))
        t2 = threading.Thread(target=receive_video_stream, args=())
        t2.start() 
        t2.join()
        

                
    while operation!=0:
            print(operation)
            continue
    operation=0

