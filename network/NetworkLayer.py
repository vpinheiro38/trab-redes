from transport.Segment import *
from network.Datagram import Datagram
from physical.PhysicalLayer import *
import threading

class NetworkLayer:
	def __init__(self, transportLayer):
		self.physicalLayer = PhysicalLayer() # Camada abaixo
		self.transportLayer = transportLayer

		self.thread = threading.Thread(target=self.rcvFrames, daemon=True)
		self.thread.start()

	def sendDatagram(self, segment, srcSocket, destSocket):
		datagram = Datagram(segment, (srcSocket.sourceIp, srcSocket.sourcePort), (destSocket.sourceIp, destSocket.sourcePort))
		self.physicalLayer.sendBits(datagram, destSocket.sourceIp)

	def appendBuffer(self, data):
		self.rcvBuffer.append(data)
	
	def rcvFrames(self):
		while True:
			data = self.physicalLayer.getData()
			if data == None: continue
			
			datagram = data[0]
			#CHECAGEM DO CHECKSUM
			self.transportLayer.demux(datagram.segment, data[1][0], data[1][1])
		

# def udt_send(segment):
#     udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     dest = (segment.destinationIp, segment.destinationPort)
#     data_string = pickle.dumps(segment)
#     udp.sendto (data_string, dest)
#     udp.close()

# def udt_rcv(mySocket, time):
#     udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     orig = (mySocket.sourceIp, mySocket.sourcePort)
#     udp.bind(orig)

    

#     udp.setblocking(0)

#     ready = select.select([udp], [], [], time)
#     if ready[0]:
#         data = udp.recv(4096)
#         segment = pickle.loads(data)
#         udp.close()
#         return segment
