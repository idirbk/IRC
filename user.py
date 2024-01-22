import logging

class User:
    def __init__(self, username, connected=True, tcp_client=None):
        self.username = username
        self.connected = connected
        self.tcp_client = tcp_client
        self.messages = []
    
    def disconcteUser(self):
        self.connected = False
    
    def connectUser(self):
        self.connected = True
    
    def isConnected(self):
        return self.connected

    def send(self, message):
        try:
            self.tcp_client.send((message.sender + ':' +message.payload).encode('utf-8'))
            self.messages.append(message)
            logging.info(f"Message sended to the user :{message.receiver}")
        except BrokenPipeError:
            logging.error('Broken pipe error user is disconnected')
            self.connected = False
            
            
    def __eq__(self, other):
        return self.username == other.username
    def __str__(self):
        return f'''
                username: {self.username}
                connected: {self.connected}
                client: {self.tcp_client}
                '''
   