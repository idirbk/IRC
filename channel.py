from message import Message

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
        index = self.users.index(user)
        if index != -1:
            self.users.pop(index)
    
    def disconnectUser(self, user):
        index = self.users_connected.index(user)
        if index != -1:
            self.users_connected.pop(index)
    
    def connectUser(self, username):
        for user in self.users:
            if user.username == username:
                users_connected.append(user)
    
    def getConnectedUsers(self):
        return filter(lambda user: user.isConnected(), self.users)
