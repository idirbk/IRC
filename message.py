
class Message:
    count = 0
    def __init__(self, sender, payload, receiver=None, receiverIsChannel=False):
        self.id = Message.count
        Message.count += 1
        self.sender = sender
        self.receiver = receiver
        self.payload = payload
        self.receiverIsChannel = receiverIsChannel
    
    def __str__(self):
        return ';'.join([self.sender, self.receiver, self.payload, self.receiverIsChannel])