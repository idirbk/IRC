from message import Message

class channel():
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.members = []
        self.messages = []

    def getChannelMembers(self) -> list:
        return self.members

    def getChannelMessages(self) -> list(Message):
        return self.messages

    def publishMessage(self, message: Message):
        self.messages.append(message)

    def addMember(self, member):
        self.members.append(member)