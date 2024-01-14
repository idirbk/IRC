import socket
import threading
import logging
import sys

class IRCServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.channels = {}

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        logging.info(f"IRC Server started on {self.host}:{self.port}")

        while True:
            client, address = self.sock.accept()
            logging.info(f"Connection from {address}")
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        #TO-DO
        pass
if __name__ == "__main__":

    port = int(sys.argv[1])
    server = IRCServer('localhost', port)
    server.start_server()
