from transport.Segment import *
from network.Datagram import Datagram
from physical.PhysicalLayer import *
from link.LinkLayer import *
import threading

class NetworkLayer:
	def __init__(self, transportLayer, port=0):
		self.linkLayer = LinkLayer(port) # Camada abaixo
		self.transportLayer = transportLayer
		self.physicalLayer = self.linkLayer.physicalLayer

		self.thread = threading.Thread(target=self.rcvFrames, daemon=True)
		self.thread.start()

	def sendDatagram(self, segment, srcSocket, destSocket):
		if srcSocket.sourceIp == destSocket[0] or destSocket[0] in ['localhost', '127.0.0.1']:
			datagram = Datagram(segment, srcSocket.sourceIp, destSocket[0])
			self.physicalLayer.sendBits(datagram, (destSocket[0], destSocket[1]))
		else:
			datagram = Datagram(segment, srcSocket.sourceIp, destSocket[0])
			self.linklayer.sendFrame(datagram, destSocket)

	def rcvFrames(self):
		while True:
			data = self.linkLayer.getData()
			if data == None: continue
			datagram = data[0]
			#CHECAGEM DO CHECKSUM
			self.transportLayer.demux(datagram.segment, data[1][0], data[1][1])