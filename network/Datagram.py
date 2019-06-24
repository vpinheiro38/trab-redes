class Datagram:
    def __init__(self, segment, destAddress, srcAddress, headerChecksum):
        self.destinationIP = destAddress[0]
        self.destinationPort = destAddress[1]
        self.sourceIP = srcAddress[0]
        self.sourcePort = srcAddress[1]
        self.headerChecksum = None
        self.segment = segment