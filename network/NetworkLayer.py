from transport.Segment import *
from network.Datagram import Datagram
from physical.PhysicalLayer import *
import threading

class NetworkLayer:
	def __init__(self, transportLayer, port=0):
		self.physicalLayer = PhysicalLayer(port) # Camada abaixo
		self.transportLayer = transportLayer

		self.thread = threading.Thread(target=self.rcvFrames, daemon=True)
		self.thread.start()

	def sendDatagram(self, segment, srcSocket, destSocket):
		# if srcSocket.sourceIp == destSocket[0] or destSocket[0] in ['localhost', '127.0.0.1']:
		# 	print('Same Local: ', (srcSocket.sourceIp, srcSocket.sourcePort), destSocket)
		# 	self.transportLayer.demux(segment, srcSocket.sourceIp, srcSocket.sourcePort)
		# else:
		datagram = Datagram(segment, srcSocket.sourceIp, destSocket[0])
		# print('SendDatagram: ', datagram, srcSocket.sourceIp, destSocket[0])
		self.physicalLayer.sendBits(datagram, (destSocket[0], destSocket[1]))

	def appendBuffer(self, data):
		self.rcvBuffer.append(data)
	
	def rcvFrames(self):
		while True:
			data = self.physicalLayer.getData()
			if data == None: continue
			# print('RcvFrames: ', data)
			datagram = data[0]
			#CHECAGEM DO CHECKSUM
			self.transportLayer.demux(datagram.segment, data[1][0], data[1][1])