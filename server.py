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
    def get_clients(self):
        users = []
        for client in self.clients:
            users.append(client.username)
        return users
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
            
            if not server_sender or server_sender != server['port']:
                logging.debug(f"sending to server {server['port']}")
                
                server['lock'].acquire()
                logging.debug(f"sending to server {command} {server['port']}")
                server['server'].send(command)
                server['server'].settimeout(5)
                msg = server['server'].recv(1024).decode('utf-8')
                logging.info(f"msg '{msg}'")
                server['server'].settimeout(0.5)
                server['lock'].release()
                if msg.startswith('True'):
                    return (True, msg[5:])
        return (False, '')

    def get_names(self, channel=None,server_sender = None):
        command = ''
        names = []
        if channel:
            if channel_destination := self.getChannel(channel):
                return channel_destination.getConnectedUsers()
            else:
                command = f'/names {channel}'
        else:
            command = '/names'
            names += self.get_clients()
        for server in self.servers:
            if not server_sender or server_sender != server['port']:
                logging.debug(f"Getting names from {server['port']}")
                server['lock'].acquire()
                server['server'].send(command.encode('utf-8'))
                server['server'].settimeout(5)
                msg = server['server'].recv(1024).decode('utf-8')
                server['server'].settimeout(0.5)
                logging.info(f"names '{msg}'")
                server['lock'].release()
                if msg.startswith('True'):
                    data= msg[5:].split(',')
                    names += data
                    if channel:
                        return names
        return names
    
    def get_list(self, server_sender = None):
        channel_list = list(map(lambda channel: channel.name, self.channels))
        
        for server in self.servers:
            if not server_sender or server_sender != server['port']:
                logging.debug(f"Getting names from {server['port']}")
                server['lock'].acquire()
                server['server'].send('/list'.encode('utf-8'))
                server['server'].settimeout(5)
                msg = server['server'].recv(1024).decode('utf-8')
                server['server'].settimeout(0.5)
                logging.info(f"names '{msg}'")
                server['lock'].release()
                if msg.startswith('True'):
                    channel_list += msg[5:].split(',')
        return channel_list
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
                        case 'list':
                            channel_list = self.get_list(server_sender=port)
                            if len(channel_list) > 0:
                                server.send(("True|"+','.join(channel_list)).encode('utf-8'))
                            else:
                                server.send("False|".encode('utf-8'))

                        case 'msgc':
                            username = args[0]
                            sender = args[1]
                            channelname = args[2]
                            payload = ' '.join(args[3:])
                            if user_dest := self.getUser(username):
                                user_dest.tcp_client.send(f'{channelname}|{sender}: {payload}'.encode('utf-8'))
                                server.send('True|'.encode('utf-8'))
                            else:
                                (status, msg) =self.send_to_all_servers(message.encode('utf-8'), port)
                                if status:
                                    server.send('True|'.encode('utf-8'))
                                else:
                                    server.send('False|'.encode('utf-8'))
                            
                        case 'msg':
                            if len(args) < 2:
                                logging.error('invalid args for msg command')
                            else:
                                destination = args[1]
                                sender = args[0]
                                msg = Message(sender=sender, payload=' '.join(args[2:]))
                                
                                if channel_destination := self.getChannel(destination):
                                    server.send('True|'.encode('utf-8'))
                                    lock.release()
                                    channel_destination.send(msg, self.send_to_all_servers)
                                    logging.info(f"Message sended to the channel :{destination}")
                                    continue

                                elif user_dest := self.getUser(destination):
                                    msg.receiver = user_dest.username
                                    user_dest.send(msg)
                                    server.send('True|'.encode('utf-8'))
                                else:
                                    (status, msg)= self.send_to_all_servers(message.encode('utf-8'), port)
                                    server.send(('True|' if status else 'False|').encode('utf-8'))
                        case 'names':
                            channel = None
                            if len(args) == 1:
                                channel = args[0]
                            names = self.get_names(channel=channel,server_sender=port)
                            server.send(('True|'+','.join(names) if names else 'False|').encode('utf-8'))
                        case 'join':
                            if len(args) != 2:
                                logging.error('invalid args for join command')
                            else:
                                new_channel = args[0]
                                username = args[1]
                                if channel := self.getChannel(new_channel):
                                    user = User(username)
                                    channel.addMember(user)
                                    channel.connectUser(user)
                                    server.send('True|'.encode('utf-8'))
                                    logging.info(f'Client {username} from another server added to the channel {new_channel}')
                                else:
                                    (status, msg) = self.send_to_all_servers(message.encode('utf-8'), port)
                                    if status:
                                        server.send('True|'.encode('utf-8'))
                                    else:
                                        server.send('False|'.encode('utf-8'))
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
                            channel_list = self.get_list()
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
                                if channel := self.getChannel(new_channel):
                                    client_channel = channel
                                    client_channel.addMember(client_user)
                                    client_channel.connectUser(client_user)
                                else:
                                    command = f'/join {new_channel} {client_user.username}'
                                    (status, msg) = self.send_to_all_servers(command.encode('utf-8'))
                                    if status:
                                        logging.info('The channel exist in another server and the user is added to the channel')
                                    else:
                                        client_channel = Channel(new_channel, [client_user])
                                        self.channels.append(client_channel)
                                        logging.info('The channel was created successfully in the current server and the user was added')
                        case 'msg':
                            if len(args) < 2:
                                logging.error('invalid args for msg command')
                            else:
                                destination = args[0]
                                msg = Message(sender=client_user.username, payload=' '.join(args[1:]))
                                if channel_destination := self.getChannel(destination):
                                    msg.sender = client_user.username
                                    channel_destination.send(msg, self.send_to_all_servers)
                                    logging.info(f"msg sended to the channel :{destination}")
                                elif user_dest := self.getUser(destination):
                                    msg.receiver = user_dest.username
                                    user_dest.send(msg)
                                else:
                                    threading.Thread(target=self.send_to_all_servers, args=(('/msg '+client_user.username + ' '+' '.join(args)).encode('utf-8'), self.port,)).start()
                                   
                                
                        case 'names':
                            
                            channel_names = None
                            if len(args) > 0:
                                channel_names= args[0]
                            names = self.get_names(channel=channel_names)
                            client.send(' | '.join(names).encode('utf-8'))
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
