import socket
import threading
import logging
import sys
from utils import getHelps, flat_map
from user import User
from channel import Channel

class IRCServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.channels = []

    def channelExists(self, channel_name):
        channel = [c for c in self.channels if c.name == channel_name]
        return len(channel) == 1

    def getChannel(self, channel_name):
        channel = [c for c in self.channels if c.name == channel_name]
        if len(channel) > 0:
            return channel[0]
        else:
            return None

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

        client_nick = None
        client_channel = None
        client_user = None
        
        while True:
            try:
                message = client.recv(1024).decode().strip()
                if not message:
                    continue
                logging.debug(f"Received message {message}")
                if message.startswith('/'):
                    command, *args = message[1:].split()
                    logging.debug(f"command: {command.lower()}")
                    match command.lower():
                        case 'nick':
                            client_nick = args[0]
                            self.clients.append({'name': client_nick, 'client': client})
                            logging.info(f"User logged {client_nick}")
                            client_user = User(client_nick)
                            self.clients.append(client_user)

                        case 'list':
                            channel_list = list(map(lambda channel: channel.name, self.channels))
                            if len(channel_list) > 0:
                                client.send(("\n".join(channel_list)).encode('utf-8'))
                            else:
                                client.send("no channels available".encode('utf-8'))

                        case 'help':
                            client.send(getHelps().encode('utf-8'))
                            
                        case 'join':
                            if len(args) == 0:
                                logging.error('invalid args for join command')
                            else:
                                if client_channel:
                                    client_channel.disconnectUser(client_user)
                                new_channel = args[0]
                                if self.channelExists(new_channel):
                                    channel = self.getChannel(new_channel)
                                    client_channel = channel
                                    channel.addMember(client_user)
                                    channel.connectUser(client_user)
                                else:
                                    client_channel = Channel(new_channel, [client_user])
                                    self.channels.append(client_channel)

                        case 'names':
                            canal = None
                            if len(args) > 0:
                                channel = self.getChannel(args[0])
                                client.send(' | '.join(channel.getConnectedUsers()).encode('utf-8'))
                            else:
                                all_users = list(set(flat_map(lambda x: x.getConnectedUsers(), self.channels)))
                                client.send(' | '.join(all_users).encode('utf-8'))
                        case _:
                            logging.error(f"Invalid command : {command}")
                        
                        

            except ConnectionResetError:
                if client_nick:
                    logging.info(f"{client_nick} has disconnected")
                    client.close()
                    for channel in self.channels.values():
                        if client_nick in channel:
                            channel.remove(client_nick)
                    if client_nick in self.clients:
                        del self.clients[client_nick]
                break
if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    port = int(sys.argv[1])
    server = IRCServer('localhost', port)
    server.start_server()
