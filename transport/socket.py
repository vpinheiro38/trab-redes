from TCP import tcp


class socketTCP:
    def __init__(self, sourceIp="0.0.0.0", sourcePort=0):
        self.sourceIp = sourceIp
        if sourcePort == 0:
            sourcePort = tcp.getFreePort()
        self.sourcePort = sourcePort
        self.destinationIp = ""
        self.destinationPort = 0

    def connect(socketTCP):
        



sla = socketTCP();
sla2 = socketTCP();
print(sla.sourceIp, sla.sourcePort);
print(sla2.sourceIp, sla2.sourcePort);