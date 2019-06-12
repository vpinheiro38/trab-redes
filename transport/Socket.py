from TCP import tcp
from Segment import Segment
from itertools import chain
import threading
import random
import time

class SocketState(Enum):
    CLOSED = 1,
    SYN_SENT = 2,
    ESTABLISHED = 3,
    FYN_WAIT = 4,
    LISTEN = 5,
    SYN_RCVD = 6

class Socket:
    WINDOW_SIZE = 10
    MAX_SEQNUM = 1024

    def __init__(self, sourceIp="0.0.0.0", sourcePort=0):
        self.sourceIp = sourceIp
        if sourcePort == 0:
            sourcePort = tcp.getFreePort()
        self.sourcePort = sourcePort
        self.destinationIp = ""
        self.destinationPort = 0

        self.timeOutInterval = 20 # TimeOut para esperar um pacote ser enviado e receber um ACK
        self.timeOutRcv = 0 # TimeOut para esperar alguma mensagem da camada de rede - igual a 0 bloqueia a thread de conexao

        self.state = SocketState.CLOSED
        self.sendbuffer = [] # Buffer de segmentos q precisam ser enviados. Buffer, pois janela pode encher
        self.transmission =  list([None, False] for i in range(Socket.MAX_SEQNUM)) # [ Packet, Enviado ou não ]
        self.sendbase = 0
        self.nextseqnum = 0

        self.rcvbuffer = []

        self.thread = threading.Thread(target=self.stateMachine)
        self.thread.start()

    def connect(self, destinationSocket):
        self.destinationIp   = destinationSocket.sourceIp
        self.destinationPort = destinationSocket.sourcePort

        segment = Segment(self, destinationSocket)
        segment.SYN = 1
        segment.sequenceNumber = random.randint(0, Socket.MAX_SEQNUM)
        self.sendbase = segment.sequenceNumber
        self.nextseqnum = segment.sequenceNumber
        
        self.udt_send(segment)
        self.state = SocketState.SYN_SENT

        time = time.time()
        while (self.timeOutRcv > 0 and time.time() - time < self.timeOutRcv) or (self.timeOutRcv <= 0 and True):
            if len(self.rcvbuffer) > 0:
                for segm in self.rcvbuffer:
                    if (segm.SYN == True and segm.sequenceNumber == self.increment(segment.sequenceNumber, Socket.MAX_SEQNUM) and 
                        segm.sourceIp == destinationSocket.sourceIp and segm.sourcePort == destinationSocket.sourcePort):
                        self.state = SocketState.ESTABLISHED
                        newSegment = makeSegment(self.increment(segm.sequenceNumber, Socket.MAX_SEQNUM), None)
                        self.udt_send(newSegment)
                        break

        if self.state == SocketState.SYN_SENT:
            self.destinationIp   = None
            self.destinationPort = None
            raise TimeoutError

    # def close(self):

    def send(self, segment):
        self.sendbuffer.insert(0, segment)

    def getInterval(self):
        interval = list(range(self.sendbase, self.sendbase + Socket.WINDOW_SIZE))
        if Socket.MAX_SEQNUM in interval:
            return list(chain(range(self.sendbase, Socket.MAX_SEQNUM), range(Socket.WINDOW_SIZE)))
        return interval

    def stateMachine(self):
        while True:
            # Verifica se pode enviar algo
            if len(self.sendbuffer) > 0:
                if self.nextseqnum in self.getInterval():
                    packet = makeSegment(self.nextseqnum, self.sendbuffer[0])
                    udt_send(packet)
                    self.startTimer(self.timeOutInterval, self.nextseqnum)
                    self.transmissions[self.nextseqnum][0] = packet
                    self.nextseqnum = self.increment(self.nextseqnum, Socket.MAX_SEQNUM)
            
            # Verifica recebimento de ACK
            packet = udt_rcv()
            n = isAck(packet)
            if n > -1:
                self.transmissions[n][1] = True
                self.stopTimer(n)
                while self.transmissions[self.sendbase][1] == True:
                    self.sendbase = self.increment(self.sendbase, Socket.MAX_SEQNUM)

            # Verifica todos os timers
            for ind in range(Socket.MAX_SEQNUM):
                if self.transmissions[ind][1] == False and isTimeOut(ind):
                    udt_send(self.transmissions[ind][0])
                    self.startTimer(self.timeOutInterval, self.transmissions[ind][0].sequencenumber)

    def listen(self):
        self.state = SocketState.LISTEN

    # def accept(self):
    #     if self.state == SocketState.LISTEN:
    #         while True:
    #             if len(self.rcvbuffer) > 0:
    #                 for segment in self.rcvbuffer:
    #                     if segment.SYN == True:
    #                         newSegment = Segment(self, Socket(segment.sourceIp, segment.sourcePort))
    #                         newSegment.SYN = True
    #                         newSegment.sequenceNumber = segment.sequenceNumber + 1
                        
    def isTimeOut(self, seqnum):
        for gettPair in self.timerList:
            if seqnum in gettPair:
                return False

        return True

    def stopTimer(self, seqnum):
        for gettPair in self.timerList:
            if seqnum in gettPair:
                self.timerList.remove(gettPair)

    def startTimer(self, seconds, seqnum):
        t = threading.Timer(seconds, stopTimer, [seqnum])
        tPair = (seqnum, t)

        self.timerList.append(tPair)
        self.timerList[self.timerList.index(tPair)][1].start()

    def increment(var, maximum):
        var += 1
        if var >= maximum:
            var = 0
        return var

sla = Socket()
sla2 = Socket()
print(sla.sourceIp, sla.sourcePort)
print(sla2.sourceIp, sla2.sourcePort)
