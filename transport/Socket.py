from TCP import tcp
from Segment import Segment
import threading
import random


class SocketTransport:
    STATE = ['WAIT_CALL', 'WAIT_ACK0', 'WAIT_ACK1']
    WINDOW_SIZE = 10
    MAX_SEQNUM = 1024

    def __init__(self, sourceIp="0.0.0.0", sourcePort=0):
        self.sourceIp = sourceIp
        if sourcePort == 0:
            sourcePort = tcp.getFreePort()
        self.sourcePort = sourcePort
        self.destinationIp = ""
        self.destinationPort = 0

        self.buffer = []
        self.transmission =  list([None, False] for i in range(SocketTransport.MAX_SEQNUM))
        self.sendbase = 0
        self.nextseqnum = 0

        self.thread = threading.Thread(target=self.stateMachine)
        self.thread.start()

    def connect(self, destinationSocket):
        segment = Segment(self, destinationSocket);
        segment.SYN = 1;
        segment.sequenceNumber = random.randint(0, SocketTransport.MAX_SEQNUM)
        self.send(segment);

    def send(self, segment):
        self.buffer.insert(0, segment)

    def getInterval(self):
        size = self.sendbase + SocketTransport.WINDOW_SIZE
        if size >= SocketTransport.MAX_SEQNUM:
            return size - SocketTransport.MAX_SEQNUM, True
        return size, False

    def stateMachine(self):
        if len(self.buffer) > 0:
            interval, passed = self.getInterval()

            if self.nextseqnum <= interval or (passed and SocketTransport.MAX_SEQNUM):
                checkSum = makeCheckSum(segment)
                packet = makePacket(self.nextseqnum, segment, checkSum)
                udt_send(packet)
                startTime(self.nextseqnum)
                self.transmissions[self.nextseqnum][0] = packet
                self.nextseqnsum += 1
                if self.nextseqnum > SocketTransport.MAX_SEQNUM:
                    self.nextseqnum = 0
        
        packet = udt_rcv()
        n = isAck(packet)
        if n > -1:
            self.transmissions[n][1] = True
            while self.transmissions[self.sendbase][1] == True:
                self.sendbase += 1
                if self.sendbase > SocketTransport.MAX_SEQNUM:
                    self.sendbase = 0

        for ind in range(SocketTransport.MAX_SEQNUM):
            if self.transmissions[ind][1] == False and isTimeOut(ind):
                udt_send(self.transmissions[ind][0])
                startTimer()

sla = SocketTransport()
sla2 = SocketTransport()
print(sla.sourceIp, sla.sourcePort)
print(sla2.sourceIp, sla2.sourcePort)
