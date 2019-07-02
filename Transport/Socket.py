from transport.ComplementChecksum import makeChecksum, isCorrupt
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
    WINDOW_SIZE = 10
    MAX_SEQNUM = 20
    MAX_TIMEOUT = 3

    def __init__(self, sourceIp="localhost", sourcePort=0, transportLayer=None):
        self.transportLayer = transportLayer

        if self.transportLayer == None:
            self.transportLayer = TransportLayer(sourcePort)

        self.networkLayer = self.transportLayer.networkLayer

        self.sourceIp = sourceIp
        self.sourcePort = sourcePort
        if (transportLayer == None):
            self.sourcePort = self.transportLayer.initPort(self.sourceIp, self.sourcePort)
        self.destinationAddress = None
        
        self.state = SocketState.CLOSED

        self.numTimeOuts = 0
        self.timeoutInterval = 1  # Tempo de espera para um pacote ser enviado e receber um ACK        
        self.timeoutRcv = 0 # Tempo de espera para alguma mensagem da camada de rede - igual a 0 bloqueia a thread de conexao
        self.timerList = []

        self.transmissions = list([None, False, 0] for i in range(
            Socket.MAX_SEQNUM))  # [ Packet, Enviado ou não ]
        self.packetRecieveList = list(None for i in range(
            Socket.MAX_SEQNUM))
        self.acknoleged = list(False for i in range(
            Socket.MAX_SEQNUM))

        self.nextSequenceNumber = random.randint(0, Socket.MAX_SEQNUM-1)
        self.nextAckNumber = 0

        self.rcvBuffer = []
        self.rcv_base = 0
        self.sendBuffer = [] # Buffer de segmentos q precisam ser enviados. Buffer, pois janela pode encher
        self.send_base = 0

        self.thread = threading.Thread(target=self.stateMachine)
        self.transportLayer.addSocket(self)


        self.appBuffer = [] # PARA TESTEEEE

    def connect(self, ip, port):
        self.destinationAddress = (ip, port)

        synSegment = Segment(self, self.destinationAddress)
        synSegment.SYN = True
        synSegment.sequenceNumber = self.nextSequenceNumber
        synSegment.checksum = makeChecksum(synSegment)
        self.send_base = self.nextSequenceNumber
        self.nextAckNumber = self.nextSequenceNumber
        self.networkLayer.sendDatagram(synSegment, self, self.destinationAddress)
        self.state = SocketState.SYN_SENT

        self.nextSequenceNumber = self.increment(self.nextSequenceNumber)

        self.timeoutRcv = 5
        print("SYN enviado")
        currentTry = 0
        while(currentTry < 3):
            currentTry += 1
            segment = self.rcvSegment(5)
            if(segment == None):
                continue

            if (segment.SYN == True and segment.ackNumber == self.nextAckNumber):
                self.send_base = self.increment(self.send_base)
                self.state = SocketState.ESTABLISHED
                newSegment = self.makeSegment(
                    self.nextSequenceNumber, segment.sequenceNumber)
                self.rcv_base = self.increment(segment.sequenceNumber)
                self.networkLayer.sendDatagram(newSegment, self, self.destinationAddress)
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
        if self.state == SocketState.CLOSED:
            raise ConnectionError
        self.sendBuffer.insert(0, data)  # Segmento é criado depois

    def rcvSegment(self, amount_time=0):
        timeNow = time.time()
        while (amount_time and time.time() - timeNow < amount_time) or (amount_time == 0 and True):
            if self.state == SocketState.CLOSED:
                raise ConnectionError

            if len(self.rcvBuffer):
                data = self.rcvBuffer.pop(0)
                checksum = data.checksum
                data.checksum = 0
                if not isCorrupt(data, checksum):
                    return data
        return None

    def isInSendInterval(self, Next):
        if(self.send_base < (self.send_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM):
            return self.send_base<= Next and Next < (self.send_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM
        return not (Next < self.send_base and Next > (self.send_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM)

    def isInRecieveInterval(self, Next):
        if(self.rcv_base < (self.rcv_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM):
            return self.rcv_base<= Next and Next < (self.rcv_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM
        return not (Next < self.rcv_base and Next > (self.rcv_base + Socket.WINDOW_SIZE) % Socket.MAX_SEQNUM)

    def stateMachine(self):
        while self.state != SocketState.CLOSED:
            # Verifica se pode enviar algo
            if len(self.sendBuffer):
                if self.isInSendInterval(self.nextSequenceNumber):
                    # print("enviou ", self.nextSequenceNumber)
                    packet = self.makeSegment(
                        self.nextSequenceNumber, data=self.sendBuffer[0])
                    self.networkLayer.sendDatagram(packet, self, self.destinationAddress)
                    self.startTimer(self.timeoutInterval,
                                    self.nextSequenceNumber)
                    self.transmissions[self.nextSequenceNumber][0] = packet
                    self.nextSequenceNumber = self.increment(
                        self.nextSequenceNumber)
                    self.sendBuffer.pop(0)

            # Verifica recebimento de ACK
            segment = self.rcvSegment(1)
            # TODO: verificar checksum
            n = None
            if segment != None:
                n = segment.ackNumber
                if n != None:
                    # print("ack ", n)
                    self.transmissions[n][1] = True
                    self.stopTimer(n)
                    self.numTimeOuts = 0
                    while self.transmissions[self.send_base][1]:
                        # print("send base ",self.send_base)
                        self.transmissions[self.send_base][1] = False
                        self.transmissions[self.send_base][0] = None
                        self.send_base = self.increment(
                            self.send_base)
                else:
                    n = segment.sequenceNumber
                    self.appBuffer.append(segment.data)
                    ack = self.makeSegment(ackNumber=n)
                    # print("ack %d sent" %(n))
                    self.networkLayer.sendDatagram(ack, self, self.destinationAddress)
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
                    # print("reenviou ", index)
                    self.networkLayer.sendDatagram(self.transmissions[index][0], self, self.destinationAddress)
                    self.startTimer(self.timeoutInterval,
                                    self.transmissions[index][0].sequenceNumber)
                    self.numTimeOuts += 1
                index = self.increment(index)
            
            if self.numTimeOuts > self.MAX_TIMEOUT:
                self.close()

    def listen(self):
        self.state = SocketState.LISTEN

    def accept(self):
        threadSocket = None
        while True:
            segment = self.rcvSegment()

            # TODO: checar se n tiver corrupto
            if segment != None and segment.SYN:
                threadSocket = Socket('localhost', 5001, transportLayer=self.transportLayer)
                threadSocket.destinationAddress = (segment.sourceIp, segment.sourcePort)
                threadSocket.state = SocketState.ESTABLISHED
                threadSocket.thread.start()
                
                threadSocket.rcv_base = segment.sequenceNumber
                threadSocket.sendSYNACK()
                break

        print('Conexao estabelecida!')
        return threadSocket
    def sendSYNACK(self):
        newSegment = Segment(self, self.destinationAddress)
        newSegment.SYN = True
        newSegment.ackNumber = self.rcv_base
        self.rcv_base = self.increment(self.rcv_base)
        self.send_base = random.randint(
            0, Socket.MAX_SEQNUM)
        newSegment.sequenceNumber = self.send_base
        newSegment.checksum = makeChecksum(newSegment)
        self.networkLayer.sendDatagram(newSegment, self, self.destinationAddress)

    def isTimeout(self, seqnum):
        for gettPair in self.timerList:
            if seqnum in gettPair:
                return False

        return True

    def isMine(self, segment):
        return segment.sourceIp == self.destinationAddress[0] and segment.sourcePort == self.destinationAddress[1]

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
        segment = Segment(self, self.destinationAddress,
                          sequenceNumber, ackNumber, data)

        segment.checksum = makeChecksum(segment)
        return segment

    def appendBuffer(self, segment):
        self.rcvBuffer.append(segment)
