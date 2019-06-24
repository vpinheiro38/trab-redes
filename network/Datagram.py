class Datagram:
    def __init__(self, segment, destAddress, srcAddress, headerChecksum=None):
        self.destinationIP = destAddress
        self.sourceIP = srcAddress
        self.headerChecksum = headerChecksum
        self.segment = segment