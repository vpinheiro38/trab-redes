from transport.Checksum import makeChecksum
from transport.TransportLayer import TransportLayer
from transport.Segment import Segment
from itertools import chain
import threading
import random
from enum import Enum
import time

class SocketState(Enum):
    CLOSED = 1,
    SYN_SENT = 2,
    ESTABLISHED = 3,
    FYN_WAIT = 4,
    LISTEN = 5,
    SYN_RCVD = 6


class Socket:
    WINDOW_SIZE = 20
    MAX_SEQNUM = 1024

    def __init__(self, sourceIp="0.0.0.0", sourcePort=0):
        self.transportLayer = TransportLayer()
        self.networkLayer = self.transportLayer.networkLayer

        self.sourceIp = sourceIp
        if sourcePort == 0:
            sourcePort = self.transportLayer.getFreePort()
        self.sourcePort = sourcePort
        self.destinationSocket = None

        self.timeoutInterval = 0.5  # Tempo de espera para um pacote ser enviado e receber um ACK
        # Tempo de espera para alguma mensagem da camada de rede - igual a 0 bloqueia a thread de conexao
        self.timeoutRcv = 0

        self.state = SocketState.CLOSED
        # Buffer de segmentos q precisam ser enviados. Buffer, pois janela pode encher
        self.timerList = []
        self.sendBuffer = []
        self.transmissions = list([None, False] for i in range(
            Socket.MAX_SEQNUM))  # [ Packet, Enviado ou não ]
        self.packetRecieveList = list(None for i in range(
            Socket.MAX_SEQNUM))
        self.acknoleged = list(False for i in range(
            Socket.MAX_SEQNUM))
        self.send_base = 0
        self.nextSequenceNumber = random.randint(0, Socket.MAX_SEQNUM)
        self.nextAckNumber = 0
        self.rcvBuffer = []
        self.rcv_base = 0

        self.thread = threading.Thread(target=self.stateMachine)

    def connect(self, ip, port):
        self.destinationSocket = Socket(ip, port)
        synSegment = Segment(self, self.destinationSocket)
        synSegment.SYN = True
        synSegment.sequenceNumber = self.nextSequenceNumber
        self.send_base = self.nextSequenceNumber
        self.nextAckNumber = self.nextSequenceNumber
        self.networkLayer.sendDatagram(synSegment, self, self.destinationSocket)
        self.state = SocketState.SYN_SENT

        self.nextSequenceNumber = self.increment(self.nextSequenceNumber)

        self.timeoutRcv = 5
        print("SYN enviado")
        currentTry = 0
        while(currentTry < 3):
            currentTry += 1
            timeNow = time.time()
            while ((time.time() - timeNow) < self.timeoutRcv):
                segment = self.rcvSegment()
                if(segment == None):
                    continue
                print(segment.SYN)
                print(segment.ackNumber, self.nextAckNumber)
                print(self.isMine(segment))
                if (segment.SYN == True and segment.ackNumber == self.nextAckNumber and self.isMine(segment)):
                    self.send_base = self.increment(self.send_base)
                    self.state = SocketState.ESTABLISHED
                    newSegment = self.makeSegment(
                        self.nextSequenceNumber, segment.sequenceNumber)
                    self.rcv_base = self.increment(segment.sequenceNumber)
                    self.networkLayer.sendDatagram(newSegment, self, self.destinationSocket)
                    self.thread.start()
                    return

        if self.state == SocketState.SYN_SENT:
            self.destinationIp = None
            self.destinationPort = None
            raise TimeoutError

    def close(self):
        self.state = SocketState.CLOSED
        self.transportLayer.closeSocket(self)

    def send(self, data):
        print(data)
        self.sendBuffer.insert(0, data)  # Segmento é criado depois

    def rcvSegment(self):
        if self.rcvBuffer > 0:
            return self.rcvBuffer.pop(0)
        return None

    def recieve(self):
        while True:
            if len(self.rcvBuffer):
                data = self.rcvBuffer[0]
                self.rcvBuffer.pop(0)
                return data


    def isInSendInterval(self, Next):
        if(self.send_base < (self.send_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM):
            return self.send_base<= Next and Next < (self.send_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM
        return not (Next < self.send_base and Next > (self.send_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM)

    def isInRecieveInterval(self, Next):
        if(self.rcv_base < (self.rcv_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM):
            return self.rcv_base<= Next and Next < (self.rcv_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM
        return not (Next < self.rcv_base and Next > (self.rcv_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM)

    def stateMachine(self):
        self.transportLayer.addSocket(self)

        while self.state != SocketState.CLOSED:
            # Verifica se pode enviar algo
            if len(self.sendBuffer) > 0:
                if self.isInSendInterval(self.nextSequenceNumber):
                    print("enviou ", self.nextSequenceNumber)
                    packet = self.makeSegment(
                        self.nextSequenceNumber, data=self.sendBuffer[0])
                    self.networkLayer.se(packet)
                    self.startTimer(self.timeoutInterval,
                                    self.nextSequenceNumber)
                    self.transmissions[self.nextSequenceNumber][0] = packet
                    self.nextSequenceNumber = self.increment(
                        self.nextSequenceNumber)
                    self.sendBuffer.pop(0)
            # Verifica recebimento de ACK
            segment = network.udt_rcv(self, 0.05)
            # TODO: verificar checksum
            n = None
            if segment != None:
                n = segment.ackNumber
                if n != None:
                    print("ack ", n)
                    self.transmissions[n][1] = True
                    self.stopTimer(n)
                    while self.transmissions[self.send_base][1]:
                        print("send base ",self.send_base)
                        self.transmissions[self.send_base][1] = False
                        self.transmissions[self.send_base][0] = None
                        self.send_base = self.increment(
                            self.send_base)
                else:
                    n = segment.sequenceNumber
                    ack = self.makeSegment(ackNumber=n)
                    print("ack %d sent" %(n))
                    network.udt_send(ack)
                    if(self.isInRecieveInterval(n)):
                        self.packetRecieveList[n] = segment
                        self.acknoleged[n] = True
                        i = self.rcv_base
                        while i != (self.rcv_base+Socket.MAX_SEQNUM % Socket.WINDOW_SIZE):
                            if not self.acknoleged[i]:
                                break
                            self.rcvBuffer.append(self.packetRecieveList[i].data)
                            self.acknoleged[i] = False
                            i = self.increment(i)
                            self.rcv_base = i

            # Verifica todos os timers
            index = self.send_base
            while index != (self.send_base+Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM:
                if self.transmissions[index][0] != None and not self.transmissions[index][1] and self.isTimeout(index):
                    print("reenviou ", index)
                    network.udt_send(self.transmissions[index][0])
                    self.startTimer(self.timeoutInterval,
                                    self.transmissions[index][0].sequenceNumber)
                index = self.increment(index)

    def listen(self):
        self.state = SocketState.LISTEN

    def accept(self):
        while True:
            segment = network.udt_rcv(self, 20)
            # TODO: checar se n tiver corrupto
            if segment.SYN:
                self.destinationSocket = Socket(
                    segment.sourceIp, segment.sourcePort)
                print(self.destinationSocket)
                self.rcv_base = segment.sequenceNumber
                self.sendSYNACK()
                break
        self.thread.start()
        print("Conexão estabelecida!")

    def sendSYNACK(self):
        newSegment = Segment(self, self.destinationSocket)
        newSegment.SYN = True
        newSegment.ackNumber = self.rcv_base
        self.rcv_base = self.increment(self.rcv_base)
        self.send_base = random.randint(
            0, Socket.MAX_SEQNUM)
        newSegment.sequenceNumber = self.send_base
        network.udt_send(newSegment)

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
        t = threading.Timer(seconds, self.stopTimer, [seqnum])
        tPair = (seqnum, t)

        self.timerList.append(tPair)
        self.timerList[self.timerList.index(tPair)][1].start()

    def increment(self, number):
        number += 1
        number %= self.MAX_SEQNUM
        return number

    def makeSegment(self, sequenceNumber=None, ackNumber=None, data=None):
        segment = Segment(self, self.destinationSocket,
                          sequenceNumber, ackNumber, data)
        #seg.checksum = makeChecksum(data, amountCheckBits, gen)
        return segment

    def appendBuffer(self, segment):
        self.rcvBuffer.append(segment)
