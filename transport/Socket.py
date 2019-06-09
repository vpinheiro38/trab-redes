from TCP import tcp
from Segment import Segment
import random


class SocketTCP:
    def __init__(self, sourceIp="0.0.0.0", sourcePort=0):
        self.sourceIp = sourceIp
        if sourcePort == 0:
            sourcePort = tcp.getFreePort()
        self.sourcePort = sourcePort
        self.destinationIp = ""
        self.destinationPort = 0

    def connect(self, destinationSocket):
        segment = Segment(self, destinationSocket);
        segment.SYN = 1;
        segment.sequenceNumber = random.randint(0, 1024)
        self.send(segment);


sla = SocketTCP()
sla2 = SocketTCP()
print(sla.sourceIp, sla.sourcePort)
print(sla2.sourceIp, sla2.sourcePort)
