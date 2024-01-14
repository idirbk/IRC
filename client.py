import socket
import threading
import logging
import sys

from channel import Channel
from message import Message

class IRCClient:
    def __init__(self, nickname, server, port=6667):
        self.nickname = nickname
        self.server = server
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        self.sock.connect((self.server, self.port))
        
        # Send initial registration command to the server
        self.send_command(f"/NICK {self.nickname}")
    def send_command(self, command):
        self.sock.send((command + "\r\n").encode())

    def receive_response(self):
        while True:
            response = self.sock.recv(4096).decode()
            logging.info("Received response : {}".format(response))

if __name__ == "__main__":
    port = int(sys.argv[1])
    nickname = sys.argv[2]
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    client = IRCClient(nickname, 'localhost', port)
    client.connect_to_server()
    threading.Thread(target=client.receive_response).start()
    
    while True:
        command = input('')
        client.send_command(command)