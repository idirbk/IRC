from message import Message
import logging
class Channel:
    def __init__(self, channel_name, users=[]):
        self.name = channel_name
        self.users = users
        self.messages = []
        self.users_connected = users

    def getChannelUsers(self):
        return self.users

    def getChannelMessages(self):
        return self.messages

    def publishMessage(self, message):
        message.id = len(self.messages)
        self.messages.append(message)

    def addMember(self, member) -> None:
        self.users.append(member)

    def removeMember(self, member):
        index = self.users.index(member)
        if index != -1:
            self.users.pop(index)
        self.disconnectUser(member)
    def disconnectUser(self, user):
        if user in self.users_connected:
            index = self.users_connected.index(user)
            if index != -1:
                self.users_connected.pop(index)

    def connectUser(self, user_to_connect):
        if not user_to_connect in self.users_connected:
            self.users_connected.append(user_to_connect)

    def getConnectedUsers(self):
        return map(lambda user: user.username,self.users_connected)

    def send(self, message, send_all_servers = None):
        logging.debug(f"Start sending messages into the channel {self.name}")
        for user in self.users_connected:
            if user.username != message.sender:
                if user.tcp_client:
                    logging.debug(f"Sending message in  channel {self.name} to {user.username}")
                    try:
                        user.tcp_client.send((message.sender + '|' + self.name +':' +message.payload).encode('utf-8'))
                        user.messages.append(message)
                        logging.info(f"Message sended to the user :{user.username}")
                    except BrokenPipeError:
                        logging.error('Broken pipe error user is disconnected')
                        user.connected = False
                else:
                    command = f'/msgc {user.username} {message.sender} {self.name} {message.payload}'
                    (status, msg)= send_all_servers(command.encode('utf-8'))
                    if not status:
                        logging.error(f'Error while sendind a message on channle {self.name} to {user.username} in another server')
                    else:
                        logging.info(f'Message sended successfully')

                
        logging.debug(f"End sending messages into the channel {self.name}")

