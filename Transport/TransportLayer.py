from network.NetworkLayer import NetworkLayer

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
        return self.freePorts.pop(0)

    def initPort(self, ip, port):
        self.networkLayer.physicalLayer.initPort(ip, port)

    def closeSocket(self, socket):
        self.freePorts.append(socket.sourcePort)
        self.openSockets.remove(socket)

    def demux(self, data, sourceIp, sourcePort):
        for socket in self.openSockets:
            # print('Demux: ', socket.destinationAddress, (socket.sourceIp, socket.sourcePort), sourceIp, sourcePort, data.destinationPort)
            if sourceIp == '127.0.0.1':
                sourceIp = 'localhost'
            
            if ((socket.destinationAddress == None or 
                (socket.destinationAddress != None and 
                    socket.destinationAddress[0] == sourceIp and
                    socket.destinationAddress[1] == sourcePort)) 
                and socket.sourcePort == data.destinationPort):

                socket.appendBuffer(data)
                break