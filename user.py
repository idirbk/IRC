
class User:
    def __init__(self, username, connected=True):
        self.username = username
        self.connected = connected
    
    def disconcteUser(self):
        self.connected = False
    
    def connectUser(self):
        self.connected = True
    
    def isConnected(self):
        return self.connected