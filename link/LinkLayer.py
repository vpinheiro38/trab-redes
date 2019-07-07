import threading,random,string
from physical.PhysicalLayer import *
from link.Frame import Frame

class LinkLayer:
    def __init__(self, port):
        self.physicalLayer = PhysicalLayer(self, port=port)
        # self.reciever = threading.Thread#fazer thread
        # self.sender = threading.Thread#fazer thread
        self.interfaceTable = []
        self.rcvBuffer = []
        # self.sendBuffer = []
        self.address = self.generateAddress()

    def sendFrame(self, datagram, destSocket):
        # self.sendBuffer.push(datagram)
        frame = Frame(datagram, '', '') #TODO COLOCAR ADDR DE ENLACE NO FRAME
        self.physicalLayer.sendBits(frame, (destSocket[0], destSocket[1]))

    def getData(self):
        if len(self.rcvBuffer):
            return self.rcvBuffer.pop(0)
        return None

    def generateAddress(self):
        address = ""
        for i in range(1,18):
            if i % 3 == 0:
                address+="-"
            else:
                char = random.choice(string.ascii_uppercase + string.digits)
                address+=char
        return address