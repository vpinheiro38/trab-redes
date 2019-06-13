class Segment:
    def __init__(self, originSocket, destinationSocket, data=None):
        self.sourceIp = originSocket.sourceIp
        self.sourcePort = originSocket.sourcePort
        self.destinationIp = destinationSocket.sourceIp
        self.destinationPort = destinationSocket.sourcePort
        self.sequenceNumber = None
        self.ackNumber = None
        self.data = data
        self.SYN = None
