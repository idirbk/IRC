
class Message:
    def __init__(self,id, sender, receiver, payload, receiverIsChannel=False):
        
        self.sender = sender
        self.receiver = receiver
        self.payload = payload
        self.receiverIsChannel = receiverIsChannel
    
    def __str__(self):
        return ';'.join([self.sender, self.receiver, self.payload, self.receiverIsChannel])