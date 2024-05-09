- create a virtual environment
- python -m venv venv
- activate it:
    - in windows : venv/Scripts/activate
    - in linux : source venv/bin/activate
- install requirements
- pip install -r requirements.txt
- run server: python server.py
- run client: python client.py
- after running client it will generate public key: copy entire key in 'single quotes' without quotes and paste it when it asks for public key

# About
- here we have established a connection between clients server using socket.
- server can steam video to client as asked by client.(video will play in all available resolution).
- users can chat to each other by sending msg to server(encrypted msg using recievers public key).
- message will be broadcasted to all the clients on network but only reciever will be able to decrypt the message.
-   
