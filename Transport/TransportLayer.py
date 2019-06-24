from network.NetworkLayer import NetworkLayer

class TransportLayer:
    def __init__(self):
        self.networkLayer = NetworkLayer()
        self.freePorts = list(range(1024, 65535))
        self.openSockets = []
        # Cada posição da lista será uma lista com as informações
        # para identificar a porta associada a um socket(sourceIp, SourcePort, destinationIp,destinationPort)

    def addSocket(self, socket):
        self.openSockets.append(socket)

    def getFreePort(self):
        return self.freePorts.pop(0)

    def closeSocket(self, socket):
        self.freePorts.append(socket.sourcePort)
        self.openSockets.remove(socket)

    def demux(self, data, sourceIp, sourcePort):
        for socket in self.openSockets:
            if (socket.destinationSocket.sourceIp == sourceIp and
               socket.destinationSocket.sourcePort == sourcePort and
               socket.sourcePort == data.destinationPort):

                socket.appendBuffer(data)
                break

    # def getFreePort(self, sourceIp, sourcePort, destinationIp, destinationPort): #Essa funcao é chamada somente quando
    #     #um socket é criado, então aqui deve ser feita a associação entre a porta e o socket
    #     freePort = self.freePorts[0]                                                            
    #     portSocket = [sourceIp, sourcePort, destinationIp, destinationPort]  #Cria uma lista com as informações para identificar
    #     #o socket
    #     self.openSockets.append(portSocket)  #Adiciona esse socket na lista de sockets abertos
    #     del self.freePorts[0]
    #     return freePort
    
    # def demux(self, sourceIp, sourcePort, destinationIp, destinationPort):
    #     #Cria uma lista com as informações, que então será comparada com cada posição da lista de sockets abertos
    #     comparisonElement = []
    #     comparisonElement.append(sourceIp)
    #     comparisonElement.append(sourcePort)
    #     comparisonElement.append(destinationIp)
    #     comparisonElement.append(destinationPort)
    #     i = 0
    #     while i < len(self.openSockets):  #compara as informações com os sockets lista de sockets abertos
    #     	if comparisonElement == self.openSockets[i]: #Se é dado um match, retornamos a porta associada ao socket
    #     		return i + 1024 #Se achou, retorna a porta
    #     	i += 1
    #     return -1	#Se não achou, retorna -1