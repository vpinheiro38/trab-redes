class Segment:
    def __init__(self, originSocket, destinationAddress, sequenceNumber=None, ackNumber=None, data=None):
        self.sourceIp = originSocket.sourceIp
        self.sourcePort = originSocket.sourcePort
        self.destinationIp = destinationAddress[0]
        self.destinationPort = destinationAddress[1]
        self.sequenceNumber = sequenceNumber
        self.ackNumber = ackNumber
        self.SYN = False
        self.checksum = 0
        self.data = data

    def isAck(self):
        if self.ackNumber != None:
            return True
        return False
