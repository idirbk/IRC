from message import Message

class Channel:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.members = []
        self.messages = []

    def getChannelMembers(self) -> list(str):
        return self.members

    def getChannelMessages(self) -> list(Message):
        return self.messages

    def publishMessage(self, message: Message) -> None:
        self.messages.append(message)

    def addMember(self, member) -> None:
        self.members.append(member)