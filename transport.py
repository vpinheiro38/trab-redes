STATE = ['WAIT_CALL', 'WAIT_ACK0', 'WAIT_ACK1']
buffer = []
actual_state = STATE[0]
actual_id = 0

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
        startTimer()
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

        if isTimeOut():
            udt_send(packet)
            start_timer()

def increaseID():
    global actual_id

    actual_id += 1
    if actual_id > 1:
        actual_id = 0