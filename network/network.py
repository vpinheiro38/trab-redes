from transport.Segment import *
import socket, pickle
import select

def udt_send(segment):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (segment.destinationIp, segment.destinationPort)
    data_string = pickle.dumps(segment)
    udp.sendto (data_string, dest)
    udp.close()

def udt_rcv(mySocket, time):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    orig = (mySocket.sourceIp, mySocket.sourcePort)
    udp.bind(orig)

    

    udp.setblocking(0)

    ready = select.select([udp], [], [], time)
    if ready[0]:
        data = udp.recv(4096)
        segment = pickle.loads(data)
        udp.close()
        return segment
