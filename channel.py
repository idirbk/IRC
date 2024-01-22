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
        for user in self.users:
            if user.username == user_to_connect.username:
                self.users_connected.append(user)

    def getConnectedUsers(self):
        return map(lambda user: user.username,self.users_connected)
    
    def send(self, message):
        for user in self.users_connected:
            print(user.username)
            try:
                user.tcp_client.send((message.sender + '|' + self.name +':' +message.payload).encode('utf-8'))
                user.messages.append(message)
                logging.info(f"Message sended to the user :{user.username}")
            except BrokenPipeError:
                logging.error('Broken pipe error user is disconnected')
                user.connected = False
