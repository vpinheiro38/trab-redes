class Frame:
    def __init__(self,datagram,sourceAddress,destinationAddress):
        self.datagram = datagram
        self.sourceAddress = sourceAddress
        self.destinationAddress = destinationAddress