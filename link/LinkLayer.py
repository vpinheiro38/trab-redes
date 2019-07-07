import threading,random,string
class LinkLayer:
    def __init__(self):
        self.reciever = threading.Thread#fazer thread
        self.sender = threading.Thread#fazer thread
        self.interfaceTable = []
        self.recieveBuffer = []
        self.sendBuffer = []
        self.address = self.generateAddress()

    def send(self,datagram):
        self.sendBuffer.push(datagram)

    def recieve(self):
        data = self.recieveBuffer.pop(-1)
        return data

    def generateAddress(self):
        address = ""
        for i in range(1,18):
            if i % 3 == 0:
                address+="-"
            else:
                char = random.choice(string.ascii_uppercase + string.digits)
                address+=char
        return address

teste = LinkLayer()
print(teste.address)