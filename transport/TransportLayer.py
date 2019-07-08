from network.NetworkLayer import NetworkLayer
import random

class TransportLayer:
    def __init__(self, port=0):
        self.networkLayer = NetworkLayer(self, port)
        self.freePorts = list(range(1024, 65535))
        self.openSockets = []
        # Cada posição da lista será uma lista com as informações
        # para identificar a porta associada a um socket(sourceIp, SourcePort, destinationIp,destinationPort)

    def addSocket(self, socket):
        self.openSockets.append(socket)

    def getFreePort(self):
        randIndex = random.randint(0, len(self.freePorts)-1)
        return self.freePorts.pop(randIndex)

    def initPort(self, ip, port):
        if port == 0:
            port = self.getFreePort()

        while not self.networkLayer.physicalLayer.initPort(ip, port):
            self.freePorts.append(port)
            port = self.getFreePort()
            
        return port

    def closeSocket(self, socket):
        self.freePorts.append(socket.sourcePort)
        self.openSockets.remove(socket)

    def demux(self, data, sourceIp, sourcePort):
        if sourceIp == '127.0.0.1':
            sourceIp = 'localhost'
        for socket in self.openSockets:
            print('Demux: ', socket.destinationAddress, (socket.sourceIp, socket.sourcePort), sourceIp, sourcePort, data.destinationPort)
            
            if ((socket.destinationAddress != None and 
                    socket.destinationAddress[0] == sourceIp and
                    socket.destinationAddress[1] == sourcePort) 
                and socket.sourcePort == data.destinationPort):
                socket.appendBuffer(data)
                return

        for socket in self.openSockets:            
            if socket.destinationAddress == None:
                socket.appendBuffer(data)
                return
