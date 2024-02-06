import socket
import threading
import logging
import sys
from utils import getHelps, get_all_users
from user import User
from channel import Channel
from message import Message
import time

class IRCServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.channels = []
        self.servers = []

    def channelExists(self, channel_name):
        channel = [c for c in self.channels if c.name == channel_name]
        return len(channel) == 1

    def getChannel(self, channel_name):
        channel = [c for c in self.channels if c.name == channel_name]
        if len(channel) > 0:
            return channel[0]
        else:
            return None
    def getUser(self, username):
        channel = [u for u in self.clients if u.username == username]
        if len(channel) > 0:
            return channel[0]
        else:
            return None

    def start_server(self, servers_ports):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        logging.info(f"IRC Server started on {self.host}:{self.port}")
        self.connect_to_servers(servers_ports)
        while True:
            client, address = self.sock.accept()
            client.settimeout(0.5)
            logging.info(f"Connection from {address}")
            threading.Thread(target=self.handle_connection, args=(client,)).start()

    def handle_connection(self, connection):
        message = connection.recv(1024).decode().strip()
        if message.startswith('/'):
            command, *args = message[1:].split()
            logging.debug(f"Handling connection {command} {args}")
            if command.lower() == 'nick':
                if len(args) > 0:
                    nickname = args[0]
                    self.handle_client(connection, nickname=nickname)
            if command.lower() == 'server':
                if len(args) > 0:
                    port = int(args[0])
                    self.handle_server(connection, port=port)
            connection.close()

    def connect_to_servers(self, servers_ports):
        for server_port in servers_ports:
            port = int(server_port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', port))
            sock.send((f'/server {self.port}').encode('utf-8'))
            sock.settimeout(0.5)
            threading.Thread(target=self.handle_server, args=(sock, port,)).start()

    def send_to_all_servers(self, command, server_sender = None):
        for server in self.servers:
            
            if server_sender and server_sender != server['port']:
                logging.debug(f"sending to server {server['port']}")
                
                server['lock'].acquire()
                logging.debug(f"sending to server {command} {server['port']}")
                server['server'].send(command)
                msg = server['server'].recv(1024).decode('utf-8')
                logging.info(f"msg '{msg}'")
                server['lock'].release()
                if msg.startswith('True'):
                    return (True, msg[5:])
        return (False, '')

    def handle_server(self, server, port):
        lock = threading.Lock()
        self.servers.append({"port": port, "server": server, "lock": lock})
        while True:
            try:
                lock.acquire()
                message = server.recv(1024).decode().strip()
                logging.debug(f"Server message: {message}")
                if not message:
                    continue
                if message.startswith('/'):
                    command, *args = message[1:].split()
                    match command.lower():
                        case 'msg':
                            if len(args) < 2:
                                logging.error('invalid args for msg command')
                            else:
                                destination = args[1]
                                sender = args[0]
                                message = Message(sender=sender, payload=' '.join(args[2:]))
                                if channel_destination := self.getChannel(destination):
                                    channel_destination.send(message)
                                    logging.info(f"Message sended to the channel :{destination}")
                                    server.send('True|'.encode('utf-8'))
                                elif user_dest := self.getUser(destination):
                                    message.receiver = user_dest.username
                                    user_dest.send(message)
                                    server.send('True|'.encode('utf-8'))
                                else:
                                    (status, msg)= self.send_to_all_servers(message.payload.encode('utf-8'), port)
                                    server.send(('True|' if status else 'False|').encode('utf-8'))
                                
                        case _:
                            logging.error(f"Invalid command : {command}")
                lock.release()
                time.sleep(0.000001)
            except TimeoutError:
                lock.release()
                time.sleep(0.000001)
                continue

    def handle_client(self, client, nickname):

        client_user = User(nickname, tcp_client= client)
        self.clients.append(client_user)
        logging.info(f"User logged {nickname}")

        client_channel = None
        while True:
            try:
                if client_user:
                    client_user.lock.acquire()
                message = client.recv(1024).decode().strip()
                if not message:
                    continue
                logging.debug(f"Received message Client {message}")
                if message.startswith('/'):
                    command, *args = message[1:].split()
                    match command.lower():
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
                                logging.debug(f'Client {client_user.username} Join channel {args[0]}')
                                if client_channel:
                                    client_channel.disconnectUser(client_user)
                                new_channel = args[0]
                                if channel := self.channelExists(new_channel):
                                    client_channel = self.getChannel(new_channel)
                                    client_channel.addMember(client_user)
                                    client_channel.connectUser(client_user)
                                else:
                                    client_channel = Channel(new_channel, [client_user])
                                    self.channels.append(client_channel)
                        case 'msg':
                            if len(args) < 2:
                                logging.error('invalid args for msg command')
                            else:
                                destination = args[0]
                                msg = Message(sender=client_user.username, payload=' '.join(args[1:]))
                                if channel_destination := self.getChannel(destination):
                                    msg.sender = client_user.username
                                    channel_destination.send(msg)
                                    logging.info(f"msg sended to the channel :{destination}")
                                elif user_dest := self.getUser(destination):
                                    msg.receiver = user_dest.username
                                    user_dest.send(msg)
                                else:
                                    
                                    (status, msg)= self.send_to_all_servers(('/msg '+client_user.username + ' '+' '.join(args)).encode('utf-8'), self.port)
                                    client.send(('True|' if status else 'False|').encode('utf-8'))
                                   
                                
                        case 'names':
                            canal = None
                            if len(args) > 0:
                                channel = self.getChannel(args[0])
                                client.send(' | '.join(channel.getConnectedUsers()).encode('utf-8'))
                            else:
                                all_users = get_all_users(self.channels)
                                client.send(' | '.join(all_users).encode('utf-8'))
                        case _:
                            logging.error(f"Invalid command : {command}")
                    client_user.lock.release()
                        

            except ConnectionResetError:
                if nickname:
                    logging.info(f"{nickname} has disconnected")
                    client.close()
                    for channel in self.channels:
                            channel.removeMember(client_user)
                    if client_user in self.clients:
                        index = self.clients.index(client_user)
                        del self.clients[index]
                break
            except TimeoutError:
                client_user.lock.release()
                continue

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    port = int(sys.argv[1])
    logging.debug(f'port: {port}')
    servers_ports = []
    if len(sys.argv) > 2:
        servers_ports = sys.argv[2:]
        
    server = IRCServer('localhost', port)
    server.start_server(servers_ports)
