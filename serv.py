import socket, cv2, pickle,struct,imutils

# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)

# Socket Accept
while True:
    client_socket,addr = server_socket.accept()
    print('GOT CONNECTION FROM:',addr)
    if client_socket:
        # vid = cv2.VideoCapture(0)
        for x,i in enumerate(["vi_360.mp4","vi_720.mp4","vi_1080.mp4"]):
            vid=cv2.VideoCapture(f"videos/{i}")
            if not vid.isOpened():
                print("Error: Could not open video file.")
                exit()

            total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

            # Calculate the number of frames to skip (read one-third of the video) \
            for _ in range(total_frames*(x) // 3):
                img,frame = vid.read()

            # Skip frames
            for _ in range(total_frames // 3):
                img,frame = vid.read()
                # frame = imutils.resize(frame,width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q",len(a))+a
                try:
                    client_socket.sendall(message)
                except:
                    vid.release()
                    cv2.destroyAllWindows()
                    break


            