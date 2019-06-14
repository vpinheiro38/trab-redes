from ..transport import tcp
from ..transport import Segment
from ..transport import Checksum
from Checksum import makeChecksum, isCorrupt
from itertools import chain
import threading
import socket
import random
from enum import Enum
import time
from ..network.network import *

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
        self.destinationSocket = None

        self.timeoutInterval = 5  # Tempo de espera para um pacote ser enviado e receber um ACK
        # Tempo de espera para alguma mensagem da camada de rede - igual a 0 bloqueia a thread de conexao
        self.timeoutRcv = 5

        self.state = SocketState.CLOSED
        # Buffer de segmentos q precisam ser enviados. Buffer, pois janela pode encher
        self.sendBuffer = []
        self.transmission = list([None, False] for i in range(
            Socket.MAX_SEQNUM))  # [ Packet, Enviado ou não ]
        self.sendBase = 0
        self.nextSequenceNumber = random.randint(0, Socket.MAX_SEQNUM)
        self.nextAckNumber = 0
        self.rcvBuffer = []

        self.thread = threading.Thread(target=self.stateMachine)
        self.thread.start()

    def connect(self, destinationSocket):
        self.destinationSocket = destinationSocket
        synSegment = Segment(self, destinationSocket)
        synSegment.SYN = 1
        synSegment.sequenceNumber = self.nextSequenceNumber
        self.sendBase = self.nextSequenceNumber
        self.nextAckNumber = self.sequenceNumber;
        udt_send(synSegment)

        self.nextSequenceNumber = increment(self.nextSequenceNumber)
        self.state = SocketState.SYN_SENT

        
        currentTry = 0
        while(currentTry > 3):
            currentTry += 1
            time = time.time()
            while (self.timeoutRcv > 0 and time.time() - time < self.timeoutRcv):
                if len(self.rcvBuffer) > 0:
                    for segment in self.rcvBuffer:
                        if (segment.SYN == True and segment.ackNumber == self.nextAckNumber and isMine(segment)):
                            self.state = SocketState.ESTABLISHED
                            newSegment = self.makeSegment(self.nextSequenceNumber, ackNumber=self.increment(segment.sequenceNumber))
                            udt_send(newSegment)
                            break

        if self.state == SocketState.SYN_SENT:
            self.destinationIp = None
            self.destinationPort = None
            raise TimeoutError

    # def close(self):

    def send(self, data):
        self.sendBuffer.insert(0, data) #Segmento é criado depois

    def getInterval(self):
        interval = list(
            range(self.sendBase, self.sendBase + Socket.WINDOW_SIZE))
        if Socket.MAX_SEQNUM in interval:
            return list(chain(range(self.sendBase, Socket.MAX_SEQNUM), range(Socket.WINDOW_SIZE)))
        return interval

    def stateMachine(self):
        while True:
            # Verifica se pode enviar algo
            if len(self.sendBuffer) > 0:
                if self.nextSequenceNumber in self.getInterval():
                    packet = self.makeSegment(
                        self.nextSequenceNumber, data=self.sendBuffer[0])
                    udt_send(packet)
                    self.startTimer(self.timeoutInterval,
                                    self.nextSequenceNumber)
                    self.transmissions[self.nextSequenceNumber][0] = packet
                    self.nextSequenceNumber = increment(
                        self.nextSequenceNumber, Socket.MAX_SEQNUM)

            # Verifica recebimento de ACK
            packet = udt_rcv()
            n = Segment.isAck(packet)
            if n > -1:
                self.transmissions[n][1] = True
                self.stopTimer(n)
                while self.transmissions[self.sendBase][1]:
                    self.sendBase = increment(
                        self.sendBase, Socket.MAX_SEQNUM)

            # Verifica todos os timers
            for ind in range(Socket.MAX_SEQNUM):
                if not self.transmissions[ind][1] and isTimeout(ind):
                    udt_send(self.transmissions[ind][0])
                    self.startTimer(self.timeoutInterval,
                                    self.transmissions[ind][0].sequencenumber)

    def listen(self):
        self.state = SocketState.LISTEN

    def accept(self):
        while True:
            if len(self.rcvBuffer) > 0:
                for segment in self.rcvBuffer:
                    if segment.SYN:
                        self.destinationSocket = Socket(segment.sourceIp, segment.sourcePort)
                        self.destinationSequenceNumber = self.increment(segment.sequenceNumber)
                        self.sendSYNACK()

    def sendSYNACK(self):
        newSegment = Segment(self, self.destinationSocket)
        newSegment.SYN = True
        newSegment.ackNumber = self.destinationSequenceNumber
        self.sequenceNumber = random.randint(
            0, Socket.MAX_SEQNUM)
        self.sendBuffer.insert(0, newSegment)
        

    def isTimeout(self, seqnum):
        for gettPair in self.timerList:
            if seqnum in gettPair:
                return False

        return True

    def isMine(self, segment):
        return segment.sourceIp == self.destinationSocket.sourceIp and segment.sourcePort == self.destinationSocket.sourcePort

    def stopTimer(self, seqnum):
        for gettPair in self.timerList:
            if seqnum in gettPair:
                self.timerList.remove(gettPair)

    def startTimer(self, seconds, seqnum):
        t = threading.Timer(seconds, stopTimer, [seqnum])
        tPair = (seqnum, t)

        self.timerList.append(tPair)
        self.timerList[self.timerList.index(tPair)][1].start()

    def increment(number):
        number += 1
        number %= MAX_SEQNUM
        return number

    def makeSegment(self, seqenceNumber, ackNumber=None, data=None):
        seg = Segment(self, destinationSocket, sequenceNumber, ackNumber, data)        
        seg.checksum = makeChecksum(data, amountCheckBits, gen)
        return seg

sla = Socket()
sla2 = Socket()
print(sla.sourceIp, sla.sourcePort)
print(sla2.sourceIp, sla2.sourcePort)
