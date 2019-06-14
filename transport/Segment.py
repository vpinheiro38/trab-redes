class Segment:
    def __init__(self, originSocket, destinationSocket, data=None, checksum=None):
        self.sourceIp = originSocket.sourceIp
        self.sourcePort = originSocket.sourcePort
        self.destinationIp = destinationSocket.sourceIp
        self.destinationPort = destinationSocket.sourcePort
        self.sequenceNumber = None
        self.ackNumber = None
        self.data = data
        self.SYN = None
        self.checksum = None

    def isAck(self, segment):
        if segment.ackNumber != None:
            return True
        return False
