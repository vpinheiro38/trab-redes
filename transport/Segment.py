class Segment:
    def __init__(self, originSocket, destinationSocket):
        self.sourceIp = originSocket.sourceIp
        self.sourcePort = originSocket.sourcePort
        self.destinationIp = destinationSocket.sourceIp
        self.destinationPort = destinationSocket.sourcePort
        self.sequenceNumber = None
        self.data = None
        self.SYN = None