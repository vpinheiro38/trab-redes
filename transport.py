import threading
import time 

STATE = ['WAIT_CALL', 'WAIT_ACK0', 'WAIT_ACK1']
buffer = []
actual_state = STATE[0]
actual_id = 0
timerList = []

def rdt_send(data):
    global actual_id, actual_state

    if len(buffer) > 0:
        buffer.insert(0, data)
        data = buffer.pop()
    elif actual_state != STATE[0]:
        buffer.insert(0, data)

    if (actual_state == STATE[0]):
        checkSum = makeCheckSum(data)
        packet = makePacket(actual_id, data, checkSum)
        udt_send(packet)
        startTimer(60, actual_id)
        actual_state = STATE[actual_id+1]
        waitAck(actual_id, packet)

def waitAck(ackNum, packet):
    global actual_id, actual_state

    rcvPacket = rdt_rcv()
    while True:
        if (rcvPacket != '' and (isCorrupt(rcvPacket) or isAck(rcvPacket, int(ackNum == 0)))):
            rcvPacket = rdt_rcv()
        elif rcvPacket != '' and (not isCorrupt(rcvPacket) and isAck(rcvPacket, ackNum)):
            actual_state = STATE[0]
            increaseID()
            break

        if isTimeOut(actual_id):
            udt_send(packet)
            startTimer(60, actual_id)

def isTimeOut(actual_id):
    for gettPair in timerList:
        if actual_id in gettPair:
            return False

    return True

def stopTimer(actual_id):
    for gettPair in timerList:
        if actual_id in gettPair:
            timerList.remove(gettPair)

def startTimer(seconds, actual_id):
    t = threading.Timer(seconds, stopTimer, [actual_id])
    tPair = (actual_id, t)

    timerList.append(tPair)
    timerList[timerList.index(tPair)][1].start()
    
def increaseID():
    global actual_id

    actual_id += 1
    if actual_id > 1:
        actual_id = 0
