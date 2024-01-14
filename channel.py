from message import Message

class Channel:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.users = []
        self.messages = []

    def getChannelUsers(self) -> list(str):
        return self.users

    def getChannelMessages(self) -> list(Message):
        return self.messages

    def publishMessage(self, message: Message) -> None:
        message.id = len(self.messages)
        self.messages.append(message)

    def addUember(self, member) -> None:
        self.users.append(member)
    
    def disconnectUser(self, username):
        for user in self.users:
            if user.username == username:
                user.disconnect()
    
    def connectUser(self, username):
        for user in self.users:
            if user.username == username:
                user.connect()
    
    def getConnectedUsers(self):
        return filter(lambda user: user.isConnected(), self.users)
