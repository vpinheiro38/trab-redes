import Transport.Segment
import socket, pickle

def udt_send(segment):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (segment.destinationIp, segment.destinationPort)
    data_string = pickle.dumps(segment)
    print("send",data_string);
    udp.sendto (data_string, dest)
    udp.close()

def udt_rcv(mySocket):
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    orig = (mySocket.sourceIp, mySocket.sourcePort)
    udp.bind(orig)
    data = udp.recv(4096)
    print("rcv", data);
    segment = pickle.loads(data)
    udp.close()
    return segment
