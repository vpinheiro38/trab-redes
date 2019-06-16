class Segment:
    def __init__(self, originSocket, destinationSocket, sequenceNumber=None, ackNumber=None, data=None, checksum=None):
        self.sourceIp = originSocket.sourceIp
        self.sourcePort = originSocket.sourcePort
        self.destinationIp = destinationSocket.sourceIp
        self.destinationPort = destinationSocket.sourcePort
        self.sequenceNumber = sequenceNumber
        self.ackNumber = ackNumber
        self.data = data
        self.SYN = False
        self.checksum = None

    def isAck(self):
        if self.ackNumber != None:
            return True
        return False
