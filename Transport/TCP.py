class TCP:
    def __init__(self):
        self.freePorts = list(range(1024, 65535))
        self.openSockets = []           #Lista de listas.Cada posição da lista será uma lista com as informações
        #para identificar a porta associada a um socket(sourceIp, SourcePort, destinationIp,destinationPort)

    def getFreePort(self, sourceIp, sourcePort, destinationIp, destinationPort): #Essa funcao é chamada somente quando
        #um socket é criado, então aqui deve ser feita a associação entre a porta e o socket
        freePort = self.freePorts[0]                                                            
        portSocket = [sourceIp, sourcePort, destinationIp, destinationPort]  #Cria uma lista com as informações para identificar
        #o socket
        self.openSockets.append(portSocket)  #Adiciona esse socket na lista de sockets abertos
        del self.freePorts[0]
        return freePort
    
    def demux(self, sourceIp, sourcePort, destinationIp, destinationPort):
        #Cria uma lista com as informações, que então será comparada com cada posição da lista de sockets abertos
        comparisonElement = []
        comparisonElement.append(sourceIp)
        comparisonElement.append(sourcePort)
        comparisonElement.append(destinationIp)
        comparisonElement.append(destinationPort)
        i = 0
        while i < len(self.openSockets):  #compara as informações com os sockets lista de sockets abertos
        	if comparisonElement == self.openSockets[i]: #Se é dado um match, retornamos a porta associada ao socket
        		return i + 1024 #Se achou, retorna a porta
        	i += 1
        return -1	#Se não achou, retorna -1


tcp = TCP()
tcp.getFreePort(1,2,3,4)
tcp.getFreePort(1,2,4,3)
tcp.getFreePort(1,3,2,4)
tcp.getFreePort(3,4,1,2)
tcp.getFreePort(2,1,4,3)
a1=int(input( ))
a2=int(input( ))
a3=int(input( ))
a4=int(input( ))
#print("A porta foi: ",tcp.demux(a1,a2,a3,a4))
